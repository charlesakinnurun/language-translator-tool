"""Logging configuration.

The key security property here is that the API never logs user text content
or API credentials - only routing metadata, status codes and durations.
"""

import logging

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

_configured = False


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging exactly once per process."""
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_FORMAT))
    root = logging.getLogger()
    root.setLevel(level.upper())
    root.addHandler(handler)

    # Keep FastAPI/uvicorn access logs at a quieter level.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    _configured = True