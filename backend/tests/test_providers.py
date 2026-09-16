"""Tests for translation provider implementations."""

import pytest

from app.services.providers.base import TranslatedText, TranslationProvider
from app.services.providers.mock_provider import MockTranslationProvider


class ConcreteProvider(TranslationProvider):
    """Small concrete provider used to exercise the base contract."""

    name = "concrete"

    def translate(self, text, source_language, target_language, timeout):
        return TranslatedText(text=text[::-1])


def test_translation_provider_is_abstract():
    with pytest.raises(TypeError):
        TranslationProvider()  # type: ignore[abstract]


def test_concrete_provider_returns_normalised_payload():
    provider = ConcreteProvider()
    result = provider.translate("hello", "en", "fr", 5.0)

    assert isinstance(result, TranslatedText)
    assert result.text == "olleh"
    assert result.detected_language is None


def test_mock_provider_translates_known_phrase():
    provider = MockTranslationProvider()

    result = provider.translate("Hello", "en", "fr", 5.0)

    assert result.text == "Bonjour"
    assert result.detected_language == "en"


def test_mock_provider_marks_unknown_phrase_as_mock():
    provider = MockTranslationProvider()

    result = provider.translate("the quick brown fox", "en", "de", 5.0)

    assert result.text.startswith("[mock:")
    assert "the quick brown fox" in result.text


def test_google_provider_requires_project_id():
    from app.services.providers.google_translate import GoogleTranslationProvider

    with pytest.raises(ValueError):
        GoogleTranslationProvider(project_id="")