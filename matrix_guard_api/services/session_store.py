# matrix_guard_api/services/session_store.py
import sqlite3
import secrets
from datetime import datetime, timezone
from typing import Annotated
from fastapi import Depends

from matrix_guard_api.config_service import ConfigService


class SessionStore:
    """SQLite-basierter SessionStore"""

    def __init__(self, config: Annotated[ConfigService, Depends()]):
        self.config = config
        self.conn = sqlite3.connect(self.config.session_db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    pad_name TEXT,
                    room_id TEXT,
                    expires_at TEXT NOT NULL
                )
                """
            )

    def create_session(
        self,
        user_id: str,
        pad_name: str | None = None,
        room_id: str | None = None
    ) -> str:
        session_id = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + self.config.session_lifetime
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO sessions (session_id, user_id, pad_name, room_id, expires_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, user_id, pad_name, room_id, expires_at.isoformat())
            )
        return session_id

    def get_session(self, session_id: str) -> dict | None:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT session_id, user_id, pad_name, room_id, expires_at "
            +"FROM sessions "
            +"WHERE session_id = ?",
            (session_id,)
        )

        if not (row := cur.fetchone()):
            return None

        session_id, user_id, pad_name, room_id, expires_at = row
        if (expires_at_dt := datetime.fromisoformat(expires_at)) < datetime.now(timezone.utc):
            self.destroy_session(session_id)
            return None

        return {
            "session_id": session_id,
            "user_id": user_id,
            "pad_name": pad_name,
            "room_id": room_id,
            "expires_at": expires_at_dt,
        }

    def destroy_session(self, session_id: str):
        with self.conn:
            self.conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
