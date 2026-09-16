"""Supported language catalogue shared by the API and service layers.

Keyed by ISO 639-1 (or 639-2) language codes understood by the Google Cloud
Translation API. Extend this mapping to add more languages.
"""

SUPPORTED_LANGUAGES: dict[str, str] = {
    "ar": "Arabic",
    "bn": "Bengali",
    "de": "German",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "hi": "Hindi",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "nl": "Dutch",
    "pl": "Polish",
    "pt": "Portuguese",
    "ru": "Russian",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "zh": "Chinese (Simplified)",
}


def is_supported(code: str) -> bool:
    """Return whether ``code`` is a supported language code."""
    return code in SUPPORTED_LANGUAGES