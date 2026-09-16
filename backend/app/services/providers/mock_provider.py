"""Deterministic offline mock provider.

Used when ``TRANSLATION_PROVIDER=mock`` so the full stack can be exercised
end-to-end without network access or credentials. Its output is clearly
labelled as mock data so it is never mistaken for real translations.
"""

from app.services.providers.base import TranslatedText, TranslationProvider

# Canned translations for the well-known demo phrase "hello".
_DEMO_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "de": "Hallo",
        "es": "Hola",
        "fr": "Bonjour",
        "hi": "नमस्ते",
        "ja": "こんにちは",
        "ko": "안녕하세요",
        "zh": "你好",
    },
    "de": {"en": "Hello"},
    "es": {"en": "Hello"},
    "fr": {"en": "Hello"},
    "ja": {"en": "Hello"},
    "ko": {"en": "Hello"},
    "zh": {"en": "Hello"},
    "hi": {"en": "Hello"},
}


class MockTranslationProvider(TranslationProvider):
    """Offline provider returning canned translations for demo purposes."""

    name = "mock"

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        timeout: float,
    ) -> TranslatedText:
        canned = _DEMO_TRANSLATIONS.get(source_language, {}).get(target_language)
        if canned is not None and text.strip().lower() == "hello":
            return TranslatedText(text=canned, detected_language=source_language)
        return TranslatedText(
            text=f"[mock: {source_language}->{target_language}] {text.strip()}",
            detected_language=source_language,
        )