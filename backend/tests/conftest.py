"""Shared fixtures for the backend test suite."""

import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    """App settings with the offline mock provider and no rate limiting."""
    return Settings(
        TRANSLATION_PROVIDER="mock",
        RATE_LIMIT_ENABLED=False,
    )


@pytest.fixture
def app(settings: Settings):
    return create_app(settings=settings)


@pytest.fixture
def client(app) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client