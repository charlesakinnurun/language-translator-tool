"""FastAPI application factory and process entrypoint.

Run locally with::

    uvicorn app.main:app --reload --port 8000
"""
# FastAPI application entrypoint

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config.settings import Settings, get_settings
from app.core.exceptions import TRANSLATION_ERRORS_BY_ROLE
from app.core.logging import configure_logging
from app.core.middleware import RateLimitMiddleware, RequestContextMiddleware
from app.core.rate_limit import SlidingWindowRateLimiter
from app.services.providers.base import TranslationProvider
from app.services.providers.mock_provider import MockTranslationProvider
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


def _build_provider(settings: Settings) -> TranslationProvider:
    """Instantiate the configured translation provider."""
    provider_name = settings.TRANSLATION_PROVIDER.lower()
    if provider_name == "google":
        from app.services.providers.google_translate import GoogleTranslationProvider

        return GoogleTranslationProvider(
            project_id=settings.GOOGLE_CLOUD_PROJECT or "",
            location=settings.TRANSLATION_LOCATION,
        )
    if provider_name == "mock":
        return MockTranslationProvider()
    raise ValueError(
        f"Unknown TRANSLATION_PROVIDER '{settings.TRANSLATION_PROVIDER}'. "
        "Use 'google' or 'mock'."
    )


def _register_exception_handlers(app: FastAPI) -> None:
    """Register uniform JSON error handlers that never leak internals."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        locations = "; ".join(
            ".".join(str(part) for part in error.get("loc", []))
            + ": "
            + str(error.get("msg"))
            for error in exc.errors()
        )
        detail = {
            "code": "validation_error",
            "message": locations or "Invalid request body.",
        }
        return JSONResponse(status_code=422, content={"detail": detail})

    for error_class in TRANSLATION_ERRORS_BY_ROLE:
        app.add_exception_handler(error_class, _make_translation_handler(error_class))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            extra={"request_id": getattr(request.state, "request_id", None)},
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred. Please try again.",
                }
            },
        )


def _make_translation_handler(error_class):
    """Build a handler for one translation error class (avoids closure bugs)."""

    def handler(request: Request, exc) -> JSONResponse:
        logger.warning(
            "translation_error",
            extra={
                "code": exc.code,
                "error_class": error_class.__name__,
                "request_id": getattr(request.state, "request_id", None),
            },
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={"detail": {"code": exc.code, "message": exc.user_message}},
        )

    return handler


def create_app(
    settings: Settings | None = None,
    provider: TranslationProvider | None = None,
) -> FastAPI:
    """Build the FastAPI application.

    ``settings`` / ``provider`` can be injected for tests; production uses the
    process-wide :func:`get_settings` configuration.
    """
    settings = settings or get_settings()
    configure_logging(settings.LOG_LEVEL)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Backend API for the Language Translation Tool. "
            "Translates text through a configurable provider (Google Cloud "
            "Translation API by default)."
        ),
        debug=settings.DEBUG,
    )

    resolved_provider = provider or _build_provider(settings)
    app.state.translation_service = TranslationService(resolved_provider)

    limiter = SlidingWindowRateLimiter(
        max_requests=settings.RATE_LIMIT_REQUESTS,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    app.state.rate_limiter = limiter

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        limiter=limiter,
        enabled=settings.RATE_LIMIT_ENABLED,
    )
    app.add_middleware(RequestContextMiddleware)

    _register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "docs": "/docs",
            "health": f"{settings.API_V1_PREFIX}/health",
        }

    return app


app = create_app()