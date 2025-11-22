# matrix_guard_api/config_service.py
from datetime import timedelta
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    MATRIX_HOMESERVER: str = "http://tuwunel:6167"
    ETHERPAD_URL: str = "http://etherpad:9001"
    ALLOWED_USERS: str = ""  # comma separated
    SESSION_LIFETIME_HOURS: int = 24
    SESSION_COOKIE_NAME: str = "session"
    ORIGINS: str = ""
    SESSION_DB_PATH: str = "sessions.db"
    SERVER_ADMIN_TOKEN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ConfigService:
    """DI-friendly config wrapper"""

    def __init__(self):
        raw = Config()

        self.matrix_homeserver = raw.MATRIX_HOMESERVER
        self.pad_url = raw.ETHERPAD_URL
        self.allowed_users = (
            [u.strip() for u in raw.ALLOWED_USERS.split(",") if u.strip()]
            if raw.ALLOWED_USERS else []
        )
        self.session_cookie_name = raw.SESSION_COOKIE_NAME
        self.session_lifetime = timedelta(hours=raw.SESSION_LIFETIME_HOURS)
        self.allowed_origins = [o.strip() for o in raw.ORIGINS.split(",") if o.strip()]
        self.session_db_path = raw.SESSION_DB_PATH
        self.server_admin_token = raw.SERVER_ADMIN_TOKEN
