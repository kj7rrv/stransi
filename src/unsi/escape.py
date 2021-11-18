"""A dedicated class for representing ANSI escape sequences."""

from __future__ import annotations

import re
from typing import Iterable, Iterator, Text

import ochre

from ._misc import _CustomText, _isplit
from .attribute import Attribute, SetAttribute
from .color import ColorRole, SetColor
from .instruction import Instruction
from .token import Token
from .unsupported import Unsupported


def isescape(text: Text) -> bool:
    """Return True if text is an ANSI escape sequence."""
    return text.startswith("\N{ESC}[")


class Escape(_CustomText):
    """A single ANSI escape sequence."""

    SEPARATOR = re.compile(r";")
    SUPPORTED_ATTRIBUTE_CODES: set[int] = set(a.value for a in Attribute)

    def tokens(self) -> Iterator[Token]:
        """Yield individual tokens from the escape sequence."""
        assert isescape(self), f"{self!r} is not an escape sequence"
        kind = self[-1]
        if params := self[2:-1]:
            for param in _isplit(params, self.SEPARATOR):
                yield Token(kind=kind, data=int(param))
            return
        yield Token(kind=kind, data=0)

    def instructions(self) -> Iterable[Instruction]:
        r"""
        Decode a string of tokens into escapable objects.

        Examples
        --------
        >>> list(Escape("\x1b[1m").instructions())
        [SetAttribute(attribute=<Attribute.BOLD: 1>)]
        >>> list(Escape("\x1b[5;44m")
        ...      .instructions())  # doctest: +NORMALIZE_WHITESPACE
        [SetAttribute(attribute=<Attribute.BLINK: 5>),
         SetColor(role=<ColorRole.BACKGROUND: 40>, color=Ansi256(4))]
        """
        tokens = self.tokens()
        while token := next(tokens, None):
            if not token.issgr():
                # We only support SGR (Select Graphic Rendition)
                yield Unsupported(token)
                continue

            if token.data in self.SUPPORTED_ATTRIBUTE_CODES:
                yield SetAttribute(Attribute(token.data))
                continue

            if 30 < token.data < 38:
                # Foreground colors
                yield SetColor(
                    role=ColorRole.FOREGROUND,
                    color=ochre.Ansi256(token.data - ColorRole.FOREGROUND.value),
                )
                continue

            if 40 < token.data < 48:
                # Foreground colors
                yield SetColor(
                    role=ColorRole.BACKGROUND,
                    color=ochre.Ansi256(token.data - ColorRole.BACKGROUND.value),
                )
                continue

            # TODO: support 38/48;2/5

            # Unsupported SGR code
            yield Unsupported(token)
