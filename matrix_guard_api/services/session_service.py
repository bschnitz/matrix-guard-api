# matrix_guard_api/services/session_service.py
from typing import Annotated
from fastapi import Depends

from matrix_guard_api.services.session_store import SessionStore


class SessionService:
    """Business-Logik für Sessions"""

    def __init__(self, store: Annotated[SessionStore, Depends()]):
        self.store = store

    def create_session(
        self,
        user_id: str,
        pad_name: str | None = None,
        room_id: str | None = None
    ) -> str:
        return self.store.create_session(user_id, pad_name, room_id)

    def get_session(self, session_id: str):
        return self.store.get_session(session_id)

    def destroy_session(self, session_id: str):
        self.store.destroy_session(session_id)
