"""Domain-level exceptions and their HTTP mapping.

Each exception carries a machine-readable ``code`` (returned to clients), an
HTTP ``status`` and a safe ``user_message`` that does not leak internal
details about the translation provider.
"""


class TranslationServiceError(Exception):
    """Base class for all translation domain errors."""

    code: str = "translation_error"
    http_status: int = 500
    user_message: str = "The translation service encountered an unexpected error."


class SameLanguageError(TranslationServiceError):
    """Raised when source and target languages are identical."""

    code = "same_language"
    http_status = 400
    user_message = "Source and target languages must be different."


class ProviderError(TranslationServiceError):
    """Base class for third-party translation provider failures."""

    code = "provider_error"
    http_status = 502
    user_message = "The translation provider could not complete the request."


class ProviderAuthError(ProviderError):
    """Provider rejected the configured credentials."""

    code = "provider_authentication_error"
    http_status = 502
    user_message = (
        "The translation provider rejected the configured credentials. "
        "Check your service account / API key configuration."
    )


class ProviderRateLimitError(ProviderError):
    """Provider is throttling the client."""

    code = "provider_rate_limit"
    http_status = 429
    user_message = "The translation provider rate limit was exceeded. Please retry shortly."


class ProviderTimeoutError(ProviderError):
    """Provider did not respond within the timeout window."""

    code = "provider_timeout"
    http_status = 504
    user_message = "The translation provider timed out. Please retry."


class ProviderUnavailableError(ProviderError):
    """Provider is temporarily unavailable."""

    code = "provider_unavailable"
    http_status = 503
    user_message = "The translation provider is temporarily unavailable. Please retry later."


class InvalidProviderResponseError(ProviderError):
    """Provider returned data that does not match the expected shape."""

    code = "invalid_provider_response"
    http_status = 502
    user_message = "The translation provider returned an invalid response. Please try again later."


# Most-specific first so FastAPI's exception middleware resolves subclasses
# before their base class.
TRANSLATION_ERRORS_BY_ROLE: tuple[type[TranslationServiceError], ...] = (
    SameLanguageError,
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    InvalidProviderResponseError,
    ProviderError,
)