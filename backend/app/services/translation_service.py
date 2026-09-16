"""Application service layer orchestrating translation requests.

The service depends only on the :class:`TranslationProvider` abstraction,
so switching providers (or adding new ones) never touches this code.
"""

import logging

from app.config.settings import get_settings
from app.core.exceptions import SameLanguageError
from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.providers.base import TranslationProvider

logger = logging.getLogger(__name__)


class TranslationService:
    """Thin orchestrator between validated requests and any provider."""

    def __init__(self, provider: TranslationProvider) -> None:
        self._provider = provider

    @property
    def provider_name(self) -> str:
        """Name of the active provider (used by health checks)."""
        return self._provider.name

    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate a validated request and return a normalised response."""
        if request.source_language == request.target_language:
            raise SameLanguageError("Source and target languages must be different.")

        settings = get_settings()
        logger.info(
            "translation_requested",
            extra={
                "provider": self._provider.name,
                "source_language": request.source_language,
                "target_language": request.target_language,
                "text_length": len(request.text),
                "timeout_seconds": settings.TRANSLATE_TIMEOUT_SECONDS,
            },
        )

        result = self._provider.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            timeout=settings.TRANSLATE_TIMEOUT_SECONDS,
        )

        logger.info(
            "translation_completed",
            extra={
                "provider": self._provider.name,
                "target_language": request.target_language,
                "translated_length": len(result.text),
            },
        )

        return TranslationResponse(
            translated_text=result.text,
            source_language=request.source_language,
            target_language=request.target_language,
            detected_language=result.detected_language,
        )