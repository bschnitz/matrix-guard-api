import logging
from typing import Annotated
from fastapi import Depends
import requests

from matrix_guard_api.config_service import ConfigService

logger = logging.getLogger(__name__)


class TuwunelAdminService:
    def __init__(self, config: Annotated[ConfigService, Depends()]):
        self.config = config
        self.base_url = config.matrix_homeserver
        self.token = config.server_admin_token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def join_room(self, room_id: str) -> bool:
        """
        Lässt den Admin-User einem Raum beitreten.

        Args:
            room_id: Die Raum-ID (z.B. "!abc123:curiosity-summit.org")

        Returns:
            True bei Erfolg, False bei Fehler
        """
        url = f"{self.base_url}/_matrix/client/v3/rooms/{room_id}/join"

        logger.info("Joining room: %s", room_id)

        try:
            resp = requests.post(url, headers=self._headers(), json={}, timeout=10)
        except requests.exceptions.RequestException as e:
            logger.error("Error joining room: %s", e)
            return False

        if resp.status_code == 200:
            logger.info("Successfully joined room: %s", room_id)
            return True

        logger.warning("Failed to join room: %s - %s", resp.status_code, resp.text)
        return False

    def get_event(self, room_id: str, event_id: str) -> dict | None:
        """
        Liest einen einzelnen Event aus einem Raum.

        Args:
            room_id: Die Raum-ID
            event_id: Die Event-ID (z.B. "$abc123")

        Returns:
            Das Event als dict oder None bei Fehler
        """
        url = f"{self.base_url}/_matrix/client/v3/rooms/{room_id}/event/{event_id}"

        logger.info("Fetching event %s from room %s", event_id, room_id)

        try:
            resp = requests.get(url, headers=self._headers(), timeout=10)
        except requests.exceptions.RequestException as e:
            logger.error("Error fetching event: %s", e)
            return None

        if resp.status_code == 200:
            event = resp.json()
            logger.info("Event fetched, sender: %s", event.get("sender"))
            return event

        logger.warning("Failed to fetch event: %s - %s", resp.status_code, resp.text)
        return None
