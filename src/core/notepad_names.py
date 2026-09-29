"""Parse pasted Notepad name lists into (old_name, new_username) pairs."""

from pathlib import Path

from core.name_table import load_name_table
from core.sorting import sort_naturally


def parse_lines(text: str) -> list[str]:
    names: list[str] = []

    for raw in text.splitlines():
        line = raw.strip()

        if not line:
            continue

        if line.lower().endswith(".png"):
            line = line[:-4]

        names.append(line)

    return names


def build_pairs(
    folder: Path,
    names: list[str],
    order: list[str] | None = None,
) -> list[tuple[str, str]]:
    """Pair pasted names against the folder's existing PNGs.

    `order` lets the caller supply a specific pairing (used by the notepad
    dialog to pair row N with the Nth file in the folder).
    """
    if order is not None:
        return [
            (old, new) for old, new in zip(order, names) if new
        ]

    existing = sort_naturally(p.stem for p in folder.glob("*.png"))

    return [(old, new) for old, new in zip(existing, names) if new]


def pairs_from_notepad(
    text: str,
    folder: Path,
    order: list[str] | None = None,
) -> list[tuple[str, str]]:
    return build_pairs(folder, parse_lines(text), order)


def pairs_from_file(file_path: Path) -> list[tuple[str, str]]:
    if file_path.suffix.lower() == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="replace")
        names = parse_lines(text)

        return [(name, name) for name in names]

    return load_name_table(file_path)
