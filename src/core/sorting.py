"""Natural (human) sorting for filenames that contain numbers.

Plain `sorted()` orders ``10.png`` before ``2.png`` because it compares
strings character by character. Since the batch renamer pairs a name list
positionally against the folder's files, that mismatch silently shifts every
row after the ninth. Splitting on digit runs keeps the positional pairing
aligned with the intended order.
"""

import re
from pathlib import Path
from typing import Iterable, TypeVar

T = TypeVar("T", str, Path)

_DIGIT_RUN = re.compile(r"(\d+)")


def natural_sort_key(value: str | Path) -> tuple[tuple[int, int, str], ...]:
    """Return a sort key that compares digit runs as integers.

    Text and numbers are tagged so a numeric segment never gets compared
    against a textual one, which would raise ``TypeError``.
    """
    text = value.name if isinstance(value, Path) else str(value)

    key: list[tuple[int, int, str]] = []

    for part in _DIGIT_RUN.split(text):
        if part.isdigit():
            key.append((1, int(part), ""))
        elif part:
            key.append((0, 0, part.casefold()))

    return tuple(key)


def sort_naturally(items: Iterable[T]) -> list[T]:
    return sorted(items, key=natural_sort_key)
