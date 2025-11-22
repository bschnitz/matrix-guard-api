from typing import Annotated
from fastapi import Depends
import requests
from matrix_guard_api.config_service import ConfigService


class MatrixAuthService:
    def __init__(self, config: Annotated[ConfigService, Depends()]):
        self.config = config

    def validate_token(self, auth_header: str | None) -> str | None:
        if not auth_header:
            return None

        token = auth_header.replace("Bearer ", "")

        try:
            resp = requests.get(
                f"{self.config.matrix_homeserver}/_matrix/client/v3/account/whoami",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get("user_id")
        except Exception:
            return None

        return None

    def is_user_allowed(self, user_id: str) -> bool:
        if not self.config.allowed_users:
            return True
        return user_id in self.config.allowed_users
