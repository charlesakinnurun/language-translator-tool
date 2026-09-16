"""Liveness/readiness endpoint."""

from fastapi import APIRouter, Request, status

from app.schemas.translation import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
)
def health(request: Request) -> HealthResponse:
    """Return service status, version and the active translation provider."""
    service = request.app.state.translation_service
    return HealthResponse(
        status="ok",
        version=request.app.version,
        provider=service.provider_name,
    )