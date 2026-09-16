"""Centralised, typed application configuration loaded from environment \
variables and an optional local ``.env`` file.

Values can be provided through the shell environment or a ``.env`` file
placed next to where the API is launched (``backend/.env``). No secrets are
ever hardcoded here.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with safe defaults for local development."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application metadata -------------------------------------------
    APP_NAME: str = "Language Translation Tool API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # --- Translation -----------------------------------------------------
    # "google" -> Google Cloud Translation API, "mock" -> offline mock.
    TRANSLATION_PROVIDER: str = "mock"
    # Required when TRANSLATION_PROVIDER=google.
    GOOGLE_CLOUD_PROJECT: str | None = None
    # Path to a Google service-account key file (Application Default Credentials).
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    TRANSLATION_LOCATION: str = "global"
    # Per-call timeout (seconds) for the translation provider.
    TRANSLATE_TIMEOUT_SECONDS: float = 10.0

    # --- Input constraints ----------------------------------------------
    MAX_TEXT_LENGTH: int = 5000
    DEFAULT_SOURCE_LANGUAGE: str = "en"

    # --- HTTP / CORS -----------------------------------------------------
    # Comma-separated list of allowed browser origins.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Rate limiting (in-process) --------------------------------------
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # --- Logging ---------------------------------------------------------
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parsed CORS origins as a list."""
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance (read once per process)."""
    return Settings()