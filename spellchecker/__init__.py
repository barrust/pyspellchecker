""" SpellChecker Module """
from .spellchecker import SpellChecker, WordFrequency
from .info import (
    __author__,
    __maintainer__,
    __email__,
    __license__,  # noqa: F401
    __version__,
    __credits__,
    __url__,
    __bugtrack_url__,
)  # noqa: F401


__all__ = ["SpellChecker", "WordFrequency"]
