import secrets
from typing import Annotated
from fastapi import Depends
from matrix_guard_api.services.session_store import SessionStore
from matrix_guard_api.config_service import ConfigService


class SessionService:
    def __init__(
        self,
        store: Annotated[SessionStore, Depends()],
        config: Annotated[ConfigService, Depends()],
    ):
        self.store = store
        self.config = config

    def create_session(self, user_id: str, pad_name: str | None, room_id: str | None):
        session_id = secrets.token_hex(32)

        self.store.create(session_id, {
            "user_id": user_id,
            "authenticated": True,
            "pad_name": pad_name,
            "room_id": room_id,
        })

        return session_id

    def get_session(self, session_id: str):
        return self.store.get(session_id)

    def destroy_session(self, session_id: str):
        self.store.delete(session_id)
