"""Google Cloud Translation v3 provider.

Authentication uses Application Default Credentials (ADC). Configure the
path to a service-account key file via ``GOOGLE_APPLICATION_CREDENTIALS``
in ``backend/.env``, or authenticate once with:
    ``gcloud auth application-default login``

Provider modules import the Google SDK lazily so the rest of the app (and
the test suite) runs fine without the SDK installed.
"""

import logging

from app.core.exceptions import (
    InvalidProviderResponseError,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.services.providers.base import TranslatedText, TranslationProvider

logger = logging.getLogger(__name__)


class GoogleTranslationProvider(TranslationProvider):
    """Production provider backed by the Google Cloud Translation v3 API."""

    name = "google"

    def __init__(self, project_id: str, location: str = "global") -> None:
        if not project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT must be set when TRANSLATION_PROVIDER=google"
            )
        self._project_id = project_id
        self._location = location
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google.cloud import translate_v3

            self._client = translate_v3.TranslationServiceClient()
        return self._client

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        timeout: float,
    ) -> TranslatedText:
        from google.api_core import exceptions as core_exceptions
        from google.cloud import translate_v3

        parent = f"projects/{self._project_id}/locations/{self._location}"
        logger.info(
            "calling_google_translate",
            extra={
                "target_language": target_language,
                "source_language": source_language,
                "text_length": len(text),
            },
        )

        try:
            request = translate_v3.TranslateTextRequest(
                parent=parent,
                contents=[text],
                mime_type="text/plain",
                source_language_code=source_language,
                target_language_code=target_language,
            )
            response = self._get_client().translate_text(
                request=request, timeout=timeout
            )
        except core_exceptions.DeadlineExceeded as exc:
            raise ProviderTimeoutError("Google Translation API timed out") from exc
        except core_exceptions.ResourceExhausted as exc:
            raise ProviderRateLimitError(
                "Google Translation API rate limit exceeded"
            ) from exc
        except (
            core_exceptions.PermissionDenied,
            core_exceptions.Unauthenticated,
        ) as exc:
            raise ProviderAuthError(
                "Google Translation API authentication failed"
            ) from exc
        except core_exceptions.ServiceUnavailable as exc:
            raise ProviderUnavailableError(
                "Google Translation API is unavailable"
            ) from exc
        except core_exceptions.GoogleAPICallError as exc:
            raise ProviderError("Google Translation API request failed") from exc

        if not response.translations or not response.translations[0].translated_text:
            raise InvalidProviderResponseError(
                "Google Translation API returned an empty response"
            )

        translation = response.translations[0]
        return TranslatedText(
            text=translation.translated_text,
            detected_language=translation.detected_language_code,
        )