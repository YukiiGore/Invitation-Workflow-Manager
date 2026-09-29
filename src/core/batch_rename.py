"""Batch rename planning and execution for PNG assets.

A rename plan is built and validated before anything touches disk, so
collisions and duplicates are reported up front instead of half-applying.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class RenameStatus(str, Enum):
    OK = "ok"
    MISSING = "missing"
    COLLISION = "collision"
    DUPLICATE = "duplicate"
    INVALID = "invalid"
    UNCHANGED = "unchanged"


@dataclass
class RenameEntry:
    old_name: str
    new_username: str
    status: RenameStatus = RenameStatus.OK
    detail: str = ""
    source: Path | None = None
    target: Path | None = None

    @property
    def old_filename(self) -> str:
        return _with_extension(self.old_name)

    @property
    def new_filename(self) -> str:
        return _with_extension(self.new_username)

    @property
    def is_runnable(self) -> bool:
        return self.status is RenameStatus.OK


@dataclass
class RenameReport:
    renamed: list[RenameEntry] = field(default_factory=list)
    skipped: list[RenameEntry] = field(default_factory=list)
    failed: list[RenameEntry] = field(default_factory=list)

    @property
    def total_renamed(self) -> int:
        return len(self.renamed)

    def summary(self) -> str:
        return (
            f"Renamed {len(self.renamed)} file(s), "
            f"skipped {len(self.skipped)}, failed {len(self.failed)}."
        )


def sanitize_username(name: str) -> str:
    cleaned = INVALID_CHARS.sub("", name).strip().rstrip(".")
    return cleaned


def is_valid_username(name: str) -> bool:
    if not name:
        return False

    if sanitize_username(name) != name:
        return False

    stem = name.split(".")[0].upper()

    return stem not in RESERVED_NAMES


def build_plan(folder: Path, pairs: list[tuple[str, str]]) -> list[RenameEntry]:
    entries = [
        RenameEntry(old_name=old, new_username=new)
        for old, new in pairs
    ]

    planned: dict[str, list[RenameEntry]] = {}

    for entry in entries:
        planned.setdefault(entry.new_filename.lower(), []).append(entry)

    for entry in entries:
        entry.source = folder / entry.old_filename
        entry.target = folder / entry.new_filename

        if not is_valid_username(entry.new_username):
            entry.status = RenameStatus.INVALID
            entry.detail = "Usernames cannot contain < > : \" / \\ | ? *"
            continue

        if len(planned[entry.new_filename.lower()]) > 1:
            entry.status = RenameStatus.DUPLICATE
            entry.detail = "Another row targets the same filename"
            continue

        if entry.old_filename == entry.new_filename:
            entry.status = RenameStatus.UNCHANGED
            entry.detail = "Already named this"
            continue

        if not entry.source.exists():
            entry.status = RenameStatus.MISSING
            entry.detail = "Source file not found"
            continue

        if entry.target.exists():
            entry.status = RenameStatus.COLLISION
            entry.detail = "Target file already exists"
            continue

    return entries


def run_plan(folder: Path, entries: list[RenameEntry]) -> RenameReport:
    report = RenameReport()

    staged: list[tuple[Path, Path]] = []

    try:
        for entry in entries:
            if not entry.is_runnable:
                report.skipped.append(entry)
                continue

            entry.source.rename(entry.target)
            staged.append((entry.source, entry.target))
            report.renamed.append(entry)

    except OSError as error:
        for source, target in reversed(staged):
            try:
                target.rename(source)
            except OSError:
                pass

        failed = next(
            (e for e in entries if e.is_runnable and e not in report.renamed),
            None,
        )

        if failed is not None:
            failed.status = RenameStatus.INVALID
            failed.detail = str(error)
            report.failed.append(failed)

    return report


def _with_extension(name: str) -> str:
    return name if Path(name).suffix else f"{name}.png"
