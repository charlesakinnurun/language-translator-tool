"""Translation endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_translation_service
from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.translation_service import TranslationService

router = APIRouter(tags=["translation"])


@router.post(
    "/translate",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate text",
)
def translate(
    payload: TranslationRequest,
    service: Annotated[
        TranslationService, Depends(get_translation_service)
    ],
) -> TranslationResponse:
    """Translate ``payload.text`` from ``source_language`` to ``target_language``.

    The response never contains provider credentials or internal error detail.
    """
    return service.translate(payload)