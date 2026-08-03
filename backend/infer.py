from __future__ import annotations

import base64
import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import networkx as nx
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from config import DEFAULT_CONFIG, RoadSegmentationConfig
from model import KRATOSRoadSegModel
from utils import ensure_dir, overlay_mask, warn_suspicious_prediction


@dataclass
class RoadInferenceResult:
    probability_map: np.ndarray
    binary_mask: np.ndarray
    postprocessed_mask: np.ndarray
    overlay: np.ndarray
    segments: List[List[int]]
    graph: Dict[str, object]
    confidence: float


class RoadSegmentationInferencer:
    def __init__(
        self,
        checkpoint_path: Path | str | None = None,
        architecture: str | None = None,
        device: torch.device | None = None,
        image_size: int | None = None,
        tile_size: int | None = None,
        tile_overlap: int | None = None,
        threshold: float | None = None,
        min_component_size: int | None = None,
    ) -> None:
        self.config = DEFAULT_CONFIG
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.architecture = architecture or self.config.architecture
        self.image_size = image_size or self.config.image_size
        self.tile_size = tile_size or self.config.tile_size
        self.tile_overlap = tile_overlap if tile_overlap is not None else self.config.tile_overlap
        self.threshold = threshold if threshold is not None else self.config.mask_threshold
        self.min_component_size = min_component_size if min_component_size is not None else self.config.min_component_size
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else self._resolve_default_checkpoint()
        self.model = self._load_model()
        self.model.to(self.device)
        self.model.eval()
        should_compile = bool(hasattr(torch, "compile") and self.device.type == "cuda")
        if should_compile:
            try:
                import importlib.util

                if importlib.util.find_spec("triton") is None:
                    should_compile = False
            except Exception:
                should_compile = False
        if should_compile:
            try:
                self.model = torch.compile(self.model)
            except Exception:
                pass

    def _resolve_default_checkpoint(self) -> Path:
        candidates = [
            self.config.best_checkpoint_path,
            self.config.latest_checkpoint_path,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return self.config.best_checkpoint_path

    def _load_model(self) -> torch.nn.Module:
        model = KRATOSRoadSegModel(self.architecture, pretrained=False)
        if self.checkpoint_path.exists():
            checkpoint = torch.load(self.checkpoint_path, map_location="cpu", weights_only=False)
            state_dict = checkpoint.get("model_state_dict") if isinstance(checkpoint, dict) else None
            if state_dict is None and isinstance(checkpoint, dict) and all(isinstance(key, str) for key in checkpoint.keys()):
                state_dict = checkpoint
            if state_dict is not None:
                model.load_state_dict(state_dict, strict=True)
        return model

    def _normalize_image(self, image_array: np.ndarray) -> torch.Tensor:
        image = image_array.astype(np.float32) / 255.0
        image = (image - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array(
            [0.229, 0.224, 0.225], dtype=np.float32
        )
        tensor = torch.from_numpy(image.transpose(2, 0, 1)).unsqueeze(0)
        return tensor

    def _predict_tile(self, tile_rgb: np.ndarray) -> np.ndarray:
        tile_h, tile_w = tile_rgb.shape[:2]
        original_shape = (tile_h, tile_w)
        if tile_h != self.tile_size or tile_w != self.tile_size:
            padded = np.zeros((self.tile_size, self.tile_size, 3), dtype=np.uint8)
            padded[:tile_h, :tile_w] = tile_rgb
            tile_rgb = padded
        tensor = self._normalize_image(tile_rgb).to(self.device)
        with torch.inference_mode():
            with torch.autocast(device_type=self.device.type, enabled=self.device.type == "cuda"):
                logits = self.model(tensor)
                if logits.shape[-2:] != (self.tile_size, self.tile_size):
                    logits = F.interpolate(logits, size=(self.tile_size, self.tile_size), mode="bilinear", align_corners=False)
                probs = torch.sigmoid(logits)[0, 0].detach().float().cpu().numpy()
        probs = probs[: original_shape[0], : original_shape[1]]
        return probs

    def _tile_positions(self, length: int) -> List[int]:
        if length <= self.tile_size:
            return [0]
        stride = max(1, self.tile_size - self.tile_overlap)
        positions = list(range(0, length - self.tile_size + 1, stride))
        last = length - self.tile_size
        if positions[-1] != last:
            positions.append(last)
        return positions

    def _predict_probabilities(self, image_rgb: np.ndarray) -> np.ndarray:
        height, width = image_rgb.shape[:2]
        if height <= self.tile_size and width <= self.tile_size:
            return self._predict_tile(image_rgb)

        probability_map = np.zeros((height, width), dtype=np.float32)
        weight_map = np.zeros((height, width), dtype=np.float32)
        window = np.outer(np.hanning(self.tile_size) if self.tile_size > 1 else np.ones(1), np.hanning(self.tile_size) if self.tile_size > 1 else np.ones(1)).astype(np.float32)
        if np.all(window == 0):
            window = np.ones((self.tile_size, self.tile_size), dtype=np.float32)
        window = window / window.max()

        for top in self._tile_positions(height):
            for left in self._tile_positions(width):
                tile = image_rgb[top : top + self.tile_size, left : left + self.tile_size]
                tile_probs = self._predict_tile(tile)
                tile_weight = window[: tile_probs.shape[0], : tile_probs.shape[1]]
                probability_map[top : top + tile_probs.shape[0], left : left + tile_probs.shape[1]] += tile_probs * tile_weight
                weight_map[top : top + tile_probs.shape[0], left : left + tile_probs.shape[1]] += tile_weight

        weight_map = np.maximum(weight_map, 1e-6)
        return probability_map / weight_map

    def _postprocess_mask(self, binary_mask: np.ndarray) -> np.ndarray:
        mask = (binary_mask > 0).astype(np.uint8) * 255
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        cleaned = np.zeros_like(mask)
        for label_index in range(1, num_labels):
            area = stats[label_index, cv2.CC_STAT_AREA]
            if area >= self.min_component_size:
                cleaned[labels == label_index] = 255

        try:
            from skimage.morphology import remove_small_holes, remove_small_objects, skeletonize
        except Exception:
            return cleaned

        cleaned_bool = cleaned > 0
        cleaned_bool = remove_small_objects(cleaned_bool, min_size=self.min_component_size)
        cleaned_bool = remove_small_holes(cleaned_bool, area_threshold=max(self.min_component_size, 64))
        skeleton = skeletonize(cleaned_bool)
        repaired = cv2.morphologyEx((skeleton.astype(np.uint8) * 255), cv2.MORPH_CLOSE, kernel, iterations=1)
        return repaired

    def _skeleton_to_graph(self, skeleton_mask: np.ndarray) -> nx.Graph:
        graph = nx.Graph()
        skeleton = skeleton_mask > 0
        height, width = skeleton.shape
        points = np.argwhere(skeleton)
        neighbor_offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]
        for y, x in points:
            graph.add_node((int(x), int(y)))
        for y, x in points:
            for dy, dx in neighbor_offsets:
                ny, nx_ = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx_ < width and skeleton[ny, nx_]:
                    graph.add_edge((int(x), int(y)), (int(nx_), int(ny)))
        return graph

    def _graph_to_segments(self, graph: nx.Graph) -> List[List[int]]:
        if graph.number_of_nodes() == 0:
            return []

        important_nodes = {node for node in graph.nodes if graph.degree[node] != 2}
        if not important_nodes:
            important_nodes = {next(iter(graph.nodes))}

        visited_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
        segments: List[List[int]] = []

        for start_node in important_nodes:
            for neighbor in graph.neighbors(start_node):
                edge = tuple(sorted((start_node, neighbor)))
                if edge in visited_edges:
                    continue
                path = [start_node, neighbor]
                visited_edges.add(edge)
                previous = start_node
                current = neighbor
                while graph.degree[current] == 2:
                    next_nodes = [node for node in graph.neighbors(current) if node != previous]
                    if not next_nodes:
                        break
                    next_node = next_nodes[0]
                    edge = tuple(sorted((current, next_node)))
                    if edge in visited_edges:
                        break
                    path.append(next_node)
                    visited_edges.add(edge)
                    previous, current = current, next_node
                if len(path) >= 2:
                    segments.append([path[0][0], path[0][1], path[-1][0], path[-1][1]])

        if not segments:
            for component in nx.connected_components(graph):
                nodes = list(component)
                if len(nodes) >= 2:
                    start = nodes[0]
                    end = nodes[-1]
                    segments.append([start[0], start[1], end[0], end[1]])
        return segments

    def predict(self, image: Image.Image | np.ndarray | str | Path) -> RoadInferenceResult:
        if isinstance(image, (str, Path)):
            image = Image.open(image)
        if isinstance(image, Image.Image):
            image_rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
        else:
            image_rgb = np.asarray(image, dtype=np.uint8)
            if image_rgb.ndim == 2:
                image_rgb = np.repeat(image_rgb[..., None], 3, axis=2)
        probability_map = self._predict_probabilities(image_rgb)
        binary_mask = (probability_map >= self.threshold).astype(np.uint8)
        postprocessed = self._postprocess_mask(binary_mask)
        graph = self._skeleton_to_graph(postprocessed)
        segments = self._graph_to_segments(graph)
        overlay = overlay_mask(image_rgb, postprocessed > 0)
        confidence = float(probability_map.mean())
        warn_suspicious_prediction(probability_map, threshold=self.threshold)
        return RoadInferenceResult(
            probability_map=probability_map,
            binary_mask=binary_mask,
            postprocessed_mask=(postprocessed > 0).astype(np.uint8),
            overlay=overlay,
            segments=segments,
            graph={
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
                "components": nx.number_connected_components(graph) if graph.number_of_nodes() else 0,
            },
            confidence=confidence,
        )

    def predict_b64(self, image_b64: str) -> RoadInferenceResult:
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return self.predict(image)
