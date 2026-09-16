"""FastAPI dependency helpers."""

from fastapi import Request

from app.services.translation_service import TranslationService


def get_translation_service(request: Request) -> TranslationService:
    """Resolve the process-wide :class:`TranslationService` instance."""
    return request.app.state.translation_service