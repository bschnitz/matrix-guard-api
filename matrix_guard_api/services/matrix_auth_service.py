import logging
from typing import Annotated
from fastapi import Depends
import requests

from matrix_guard_api.config_service import ConfigService

logger = logging.getLogger(__name__)


class MatrixAuthService:
    def __init__(self, config: Annotated[ConfigService, Depends()]):
        self.config = config

    def validate_openid_token(
        self,
        access_token: str,
        matrix_server_name: str
    ) -> str | None:
        """
        Validiert ein OpenID Connect Token über die Matrix Federation API.

        Args:
            access_token: Das OpenID Token
            matrix_server_name: Der Homeserver des Users (aus credentials.matrix_server_name)

        Returns:
            Die Matrix User-ID oder None bei Fehler
        """
        if not access_token or not matrix_server_name:
            logger.warning("Missing access_token or matrix_server_name")
            return None

        # Federation API Endpoint für OpenID Token Validierung
        # Wichtig: matrix_server_name verwenden, nicht fest codierten Server!
        validation_url = (
            f"https://{matrix_server_name}/_matrix/federation/v1/openid/userinfo"
        )

        logger.info("Validating OpenID token against: %s", validation_url)
        try:
            resp = requests.get(
                validation_url,
                params={"access_token": access_token},
                timeout=10
            )
        except requests.exceptions.RequestException as e:
            logger.error("Error validating OpenID token: %s", e)
            return None

        if resp.status_code == 200:
            data = resp.json()
            user_id = data.get("sub")  # Federation API gibt "sub" zurück
            logger.info("Token validated successfully for user: %s", user_id)
            return user_id

        logger.warning(
            "Token validation failed: %s - %s",
            resp.status_code,
            resp.text
        )
        return None

    def is_user_allowed(self, user_id: str) -> bool:
        """Prüft ob der User in der Allowlist ist."""
        if not self.config.allowed_users:
            return True
        return user_id in self.config.allowed_users
