import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DB_PATH = Path(__file__).parent.parent / "audit_logs.db"


class AuditStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    output_summary TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def log_event(
        self, agent_name: str, input_data: Dict[str, Any], output_data: Dict[str, Any], duration_ms: float
    ) -> None:
        try:
            input_bytes = json.dumps(input_data, sort_keys=True, default=str).encode("utf-8")
            input_hash = hashlib.sha256(input_bytes).hexdigest()[:12]
        except Exception:
            input_hash = "unhashable"

        try:
            out_str = json.dumps(output_data, default=str)
            summary = out_str[:120] + "..." if len(out_str) > 120 else out_str
        except Exception:
            summary = str(output_data)[:120]

        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (agent_name, input_hash, output_summary, duration_ms, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (agent_name, input_hash, summary, duration_ms, now_iso),
            )
            conn.commit()

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, agent_name, input_hash, output_summary, duration_ms, timestamp FROM audit_logs ORDER BY id ASC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def clear_logs(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM audit_logs")
            conn.commit()


audit_store = AuditStore()
