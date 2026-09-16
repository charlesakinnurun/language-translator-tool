"""Endpoint-level tests for the translation API."""

import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.core.exceptions import (
    InvalidProviderResponseError,
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.main import create_app
from app.services.providers.base import TranslatedText, TranslationProvider

VALID_PAYLOAD = {
    "text": "Good morning",
    "source_language": "en",
    "target_language": "fr",
}


class EchoProvider(TranslationProvider):
    """Deterministic provider used for happy-path assertions."""

    name = "echo"

    def translate(self, text, source_language, target_language, timeout):
        return TranslatedText(
            text=f"{source_language}->{target_language}:{text}",
            detected_language=source_language,
        )


class FailingProvider(TranslationProvider):
    """Provider that always raises the given exception."""

    name = "failing"

    def __init__(self, error):
        self._error = error

    def translate(self, text, source_language, target_language, timeout):
        raise self._error


def make_client(
    provider: TranslationProvider, settings: Settings | None = None
) -> TestClient:
    test_settings = settings or Settings(
        TRANSLATION_PROVIDER="mock", RATE_LIMIT_ENABLED=False
    )
    return TestClient(create_app(settings=test_settings, provider=provider))


# --- Happy path ------------------------------------------------------------


def test_successful_translation_with_response_shape():
    client = make_client(EchoProvider())

    response = client.post("/api/v1/translate", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["translated_text"] == "en->fr:Good morning"
    assert body["source_language"] == "en"
    assert body["target_language"] == "fr"
    assert body["detected_language"] == "en"


def test_mock_provider_returns_canned_translation(client):
    response = client.post(
        "/api/v1/translate",
        json={"text": "hello", "source_language": "en", "target_language": "fr"},
    )

    assert response.status_code == 200
    assert response.json()["translated_text"] == "Bonjour"


def test_response_includes_correlation_id(client):
    response = client.post("/api/v1/translate", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_language_codes_are_case_insensitive(client):
    response = client.post(
        "/api/v1/translate",
        json={
            "text": "Good morning",
            "source_language": "EN",
            "target_language": "FR",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source_language"] == "en"
    assert body["target_language"] == "fr"


def test_leading_and_trailing_whitespace_is_trimmed(client):
    response = client.post(
        "/api/v1/translate",
        json={
            "text": "  Hello, world!  ",
            "source_language": "en",
            "target_language": "es",
        },
    )

    assert response.status_code == 200
    assert "Hello, world!" in response.json()["translated_text"]


# --- Validation failures ---------------------------------------------------


def test_empty_text_is_rejected(client):
    response = client.post(
        "/api/v1/translate",
        json={**VALID_PAYLOAD, "text": ""},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_whitespace_only_text_is_rejected(client):
    response = client.post(
        "/api/v1/translate",
        json={**VALID_PAYLOAD, "text": "   \n\t  "},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_missing_text_is_rejected(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "text"}
    response = client.post("/api/v1/translate", json=payload)
    assert response.status_code == 422


def test_text_longer_than_limit_is_rejected(client):
    from app.config.settings import get_settings

    too_long = "a" * (get_settings().MAX_TEXT_LENGTH + 1)
    response = client.post(
        "/api/v1/translate",
        json={**VALID_PAYLOAD, "text": too_long},
    )
    assert response.status_code == 422


def test_unsupported_source_language_is_rejected(client):
    response = client.post(
        "/api/v1/translate",
        json={**VALID_PAYLOAD, "source_language": "xx"},
    )
    assert response.status_code == 422


def test_unsupported_target_language_is_rejected(client):
    response = client.post(
        "/api/v1/translate",
        json={**VALID_PAYLOAD, "target_language": "zz"},
    )
    assert response.status_code == 422


def test_non_string_text_is_rejected(client):
    response = client.post(
        "/api/v1/translate",
        json={**VALID_PAYLOAD, "text": 123},
    )
    assert response.status_code == 422


def test_same_source_and_target_language_returns_400(client):
    response = client.post(
        "/api/v1/translate",
        json={
            "text": "Hello",
            "source_language": "en",
            "target_language": "en",
        },
    )
    assert response.status_code == 400
    body = response.json()["detail"]
    assert body["code"] == "same_language"
    assert body["message"]


# --- Provider failure handling ----------------------------------------------


@pytest.mark.parametrize(
    "error,expected_status,expected_code",
    [
        (ProviderTimeoutError("boom"), 504, "provider_timeout"),
        (ProviderUnavailableError("boom"), 503, "provider_unavailable"),
        (ProviderAuthError("boom"), 502, "provider_authentication_error"),
        (ProviderRateLimitError("boom"), 429, "provider_rate_limit"),
        (InvalidProviderResponseError("boom"), 502, "invalid_provider_response"),
    ],
)
def test_provider_failures_map_to_status_codes(
    error, expected_status, expected_code
):
    client = make_client(FailingProvider(error))

    response = client.post("/api/v1/translate", json=VALID_PAYLOAD)

    assert response.status_code == expected_status
    body = response.json()["detail"]
    assert body["code"] == expected_code
    assert body["message"]


def test_provider_error_details_are_not_leaked_to_clients():
    client = make_client(
        FailingProvider(ProviderAuthError("secret-internal-config 123"))
    )

    response = client.post("/api/v1/translate", json=VALID_PAYLOAD)

    assert response.status_code == 502
    assert "secret-internal-config" not in response.text
    assert "123" not in response.text


def test_generic_provider_failure_is_mapped():
    from app.core.exceptions import ProviderError

    client = make_client(FailingProvider(ProviderError("boom")))
    response = client.post("/api/v1/translate", json=VALID_PAYLOAD)
    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "provider_error"


# --- Rate limiting ----------------------------------------------------------


def test_rate_limit_returns_429_after_budget_is_exhausted():
    settings = Settings(
        TRANSLATION_PROVIDER="mock",
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=2,
        RATE_LIMIT_WINDOW_SECONDS=60,
    )
    client = make_client(EchoProvider(), settings)

    first = client.post("/api/v1/translate", json=VALID_PAYLOAD)
    second = client.post("/api/v1/translate", json=VALID_PAYLOAD)
    third = client.post("/api/v1/translate", json=VALID_PAYLOAD)

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json()["detail"]["code"] == "rate_limited"