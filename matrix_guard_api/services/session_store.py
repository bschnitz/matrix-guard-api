from typing import Annotated
from datetime import datetime, timezone
from fastapi import Depends
from matrix_guard_api.config_service import ConfigService


class SessionStore:
    def __init__(self, config: Annotated[ConfigService, Depends()]):
        self.config = config
        self.sessions: dict[str, dict] = {}

    def create(self, session_id: str, data: dict):
        expires = datetime.now(timezone.utc) + self.config.session_lifetime
        self.sessions[session_id] = {"data": data, "expires": expires}

    def get(self, session_id: str) -> dict | None:
        if not (entry := self.sessions.get(session_id)):
            return None

        if entry["expires"] < datetime.now(timezone.utc):
            self.sessions.pop(session_id, None)
            return None

        return entry["data"]

    def delete(self, session_id: str):
        self.sessions.pop(session_id, None)
