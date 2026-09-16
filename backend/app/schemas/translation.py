"""Pydantic schemas for the translation API.

Validation rules live here so the API contract rejects malformed input with
HTTP 422 before any provider call is made.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.config.settings import get_settings
from app.services.languages import SUPPORTED_LANGUAGES


class TranslationRequest(BaseModel):
    """Validated payload for ``POST /api/v1/translate``."""

    text: str = Field(description="The text to translate.")
    source_language: str = Field(
        default="en",
        max_length=8,
        description="ISO 639-1 source language code.",
    )
    target_language: str = Field(
        ...,
        max_length=8,
        description="ISO 639-1 target language code.",
    )

    @field_validator("text", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if not isinstance(value, str):
            raise ValueError("text must be a string")
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must not be empty or whitespace only")
        return stripped

    @field_validator("text")
    @classmethod
    def limit_text_length(cls, value: str) -> str:
        max_length = get_settings().MAX_TEXT_LENGTH
        if len(value) > max_length:
            raise ValueError(f"text exceeds the {max_length} character limit")
        return value

    @field_validator("source_language", "target_language", mode="before")
    @classmethod
    def normalize_language(cls, value):
        if not isinstance(value, str):
            raise ValueError("language code must be a string")
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_LANGUAGES:
            supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
            raise ValueError(
                f"unsupported language code '{value}'. Supported codes: {supported}"
            )
        return normalized


class TranslationResponse(BaseModel):
    """Success response for ``POST /api/v1/translate``."""

    translated_text: str
    source_language: str
    target_language: str
    detected_language: str | None = None


class HealthResponse(BaseModel):
    """Response for ``GET /api/v1/health``."""

    status: Literal["ok"]
    version: str
    provider: str


class ErrorDetail(BaseModel):
    """Machine-readable error payload returned on failure."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Uniform error envelope: ``{"detail": {"code": ..., "message": ...}}``."""

    detail: ErrorDetail