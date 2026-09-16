"""Translation provider abstraction.

Adding a new provider (Azure, DeepL, ...) means implementing
:class:`TranslationProvider` and registering it in the app factory, leaving
the rest of the stack untouched.
"""

import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class TranslatedText:
    """Normalised payload returned by any translation provider."""

    text: str
    detected_language: str | None = None


class TranslationProvider(abc.ABC):
    """Interface every translation backend must implement."""

    name: str = "base"

    @abc.abstractmethod
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        timeout: float,
    ) -> TranslatedText:
        """Translate ``text`` and return a normalised result.

        Implementations must raise the domain exceptions from
        :mod:`app.core.exceptions` instead of leaking provider-specific
        errors to callers.
        """