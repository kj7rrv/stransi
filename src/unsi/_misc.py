"""Private miscellaneous utilities."""

from __future__ import annotations

import re
from typing import Iterable, Pattern, Text


def _isplit(
    text: Text, pattern: Pattern[Text] | Text, include_separators: bool = False
) -> Iterable[Text]:
    r"""
    Split text into parts separated by the given pattern.

    This yields the text before the first match, then the match, then the text
    after the match and so on. In any case, empty strings are *never* yielded.

    If `include_separators` is False (the default), separators are not
    included in the result.

    Examples
    --------
    >>> list(_isplit('a b  c', ' '))
    ['a', 'b', 'c']
    >>> list(_isplit('a b  c', ' ', include_separators=True))
    ['a', ' ', 'b', ' ', ' ', 'c']
    >>> list(_isplit('a b  c', r'\s+'))
    ['a', 'b', 'c']
    >>> list(_isplit('a b  c', r'\s+', include_separators=True))
    ['a', ' ', 'b', '  ', 'c']
    """
    if isinstance(pattern, Text):
        pattern = re.compile(pattern)

    prev_end = 0
    for separator in pattern.finditer(text):
        # Yield the text before separator.
        if piece := text[prev_end : separator.start()]:
            yield piece

        # Yield separator.
        if include_separators and (piece := separator.group(0)):
            yield piece

        # Update the start position.
        prev_end = separator.end()

    # Yield the text after the last separator.
    if piece := text[prev_end:]:
        yield piece