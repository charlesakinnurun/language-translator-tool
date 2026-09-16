"""Unit tests for the translation service layer."""

import pytest

from app.core.exceptions import SameLanguageError
from app.schemas.translation import TranslationRequest
from app.services.providers.base import TranslatedText, TranslationProvider
from app.services.translation_service import TranslationService


class FakeProvider(TranslationProvider):
    name = "fake"

    def __init__(self):
        self.calls = []

    def translate(self, text, source_language, target_language, timeout):
        self.calls.append(
            {
                "text": text,
                "source": source_language,
                "target": target_language,
                "timeout": timeout,
            }
        )
        return TranslatedText(
            text=f"translated:{text}",
            detected_language=source_language,
        )


def _request(text="Hello", source="en", target="fr") -> TranslationRequest:
    return TranslationRequest(
        text=text,
        source_language=source,
        target_language=target,
    )


def test_service_returns_normalised_response():
    provider = FakeProvider()
    service = TranslationService(provider)

    response = service.translate(_request(text="Hello world", source="en", target="es"))

    assert response.translated_text == "translated:Hello world"
    assert response.source_language == "en"
    assert response.target_language == "es"
    assert response.detected_language == "en"
    assert provider.calls[0]["timeout"] > 0


def test_service_forwards_request_to_provider():
    provider = FakeProvider()
    service = TranslationService(provider)

    service.translate(_request(text="Hola", source="es", target="de"))

    assert provider.calls == [
        {
            "text": "Hola",
            "source": "es",
            "target": "de",
            "timeout": pytest.approx(10.0),
        }
    ]


def test_service_rejects_same_source_and_target():
    service = TranslationService(FakeProvider())

    with pytest.raises(SameLanguageError):
        service.translate(_request(source="en", target="en"))


def test_service_exposes_provider_name():
    assert TranslationService(FakeProvider()).provider_name == "fake"