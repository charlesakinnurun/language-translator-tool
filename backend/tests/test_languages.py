"""Tests for the supported language catalogue."""

import re

from app.services.languages import SUPPORTED_LANGUAGES, is_supported

_ISO_CODE = re.compile(r"^[a-z]{2,3}$")


def test_language_codes_are_sorted():
    assert list(SUPPORTED_LANGUAGES) == sorted(SUPPORTED_LANGUAGES)


def test_language_codes_match_iso_pattern():
    for code in SUPPORTED_LANGUAGES:
        assert _ISO_CODE.match(code), f"invalid language code: {code}"


def test_language_names_are_non_empty():
    for name in SUPPORTED_LANGUAGES.values():
        assert name.strip()


def test_catalogue_has_multiple_languages():
    assert len(SUPPORTED_LANGUAGES) >= 20


def test_is_supported():
    assert is_supported("en")
    assert is_supported("zh")
    assert not is_supported("xx")
    assert not is_supported("")