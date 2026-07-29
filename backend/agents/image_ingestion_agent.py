import base64
import io
from typing import Any, Dict
from PIL import Image
from agents.base import BaseAgent


class ImageIngestionAgent(BaseAgent):
    name: str = "image_ingestion"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expects input_data containing either:
        - "image_bytes": raw bytes of PNG/JPEG, or
        - "image_b64": base64 encoded string of PNG/JPEG.
        Validates the format, resizes if larger than max_dim (default 1024), and returns base64.
        """
        image_bytes = input_data.get("image_bytes")
        image_b64 = input_data.get("image_b64")

        if not image_bytes and not image_b64:
            # Fallback sample image for pipeline execution when no image is uploaded
            sample_img = Image.new("RGB", (200, 200), color=(30, 40, 50))
            buf = io.BytesIO()
            sample_img.save(buf, format="PNG")
            image_bytes = buf.getvalue()

        if image_b64 and not image_bytes:
            image_bytes = base64.b64decode(image_b64)

        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()  # verify format
            img = Image.open(io.BytesIO(image_bytes))  # re-open after verify
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

        img_format = img.format or "PNG"
        if img_format.upper() not in ["PNG", "JPEG", "JPG"]:
            raise ValueError(f"Unsupported image format '{img_format}'. Only PNG and JPEG are supported.")

        # Convert palette/RGBA if saving as JPEG
        if img.mode in ("RGBA", "P") and img_format.upper() in ["JPEG", "JPG"]:
            img = img.convert("RGB")

        max_dim = input_data.get("max_dim", 1024)
        width, height = img.size
        if max(width, height) > max_dim:
            scale = max_dim / float(max(width, height))
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            width, height = img.size

        buf = io.BytesIO()
        img.save(buf, format=img_format if img_format.upper() in ["PNG", "JPEG"] else "PNG")
        out_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        output = dict(input_data)
        output.pop("image_bytes", None)
        output.update({
            "image_b64": out_b64,
            "width": width,
            "height": height,
            "format": img_format.upper(),
        })
        return output
