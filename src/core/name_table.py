from pathlib import Path

import pandas as pd


def load_name_table(file_path: Path) -> list[tuple[str, str]]:
    """Read an Excel/CSV file into (old_name, new_username) pairs.

    Column 1 is the original name (index or filename), column 2 the new
    username. Headers are tolerated: a first row whose second cell is
    non-numeric is treated as a header and skipped.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        frame = pd.read_csv(file_path, header=None, dtype=str, keep_default_na=False)
    else:
        frame = pd.read_excel(
            file_path, header=None, dtype=str, keep_default_na=False
        )

    if frame.empty or frame.shape[1] < 2:
        return []

    rows: list[tuple[str, str]] = []

    for _, row in frame.iloc[:, :2].iterrows():
        old = str(row.iloc[0]).strip()
        new = str(row.iloc[1]).strip()

        if old and new:
            rows.append((old, new))

    return _drop_header(rows)


def _drop_header(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    if not rows:
        return rows

    first_old, first_new = rows[0]

    if first_old.lower() in {
        "index",
        "no",
        "no.",
        "num",
        "number",
        "old",
        "old name",
        "original",
        "filename",
        "file",
        "id",
    }:
        return rows[1:]

    if not first_new.replace(".", "", 1).isdigit() and _looks_like_header(first_new):
        return rows[1:]

    return rows


def _looks_like_header(value: str) -> bool:
    return value.lower() in {
        "name",
        "username",
        "user",
        "new name",
        "new",
        "new username",
        "nickname",
        "nick",
        "display name",
    }
