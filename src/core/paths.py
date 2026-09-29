import sys
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", "")) if FROZEN else None

# When frozen, the app is read-only inside the extraction directory, so the
# project root becomes the folder holding the executable. That is where
# examples/ and config.json can be written and where a user would expect to
# find them. In a source checkout it is the repository root.
PROJECT_ROOT = (
    Path(sys.executable).resolve().parent
    if FROZEN
    else Path(__file__).resolve().parent.parent.parent
)

IMAGES_FOLDER = "examples/images"
TEMPLATE_FILE = "templates/template.txt"
CONFIG_FILE = "templates/config.json"
ASSETS_FOLDER = "assets"


def resolve_from_root(path: str | Path) -> Path:
    if (resolved := Path(path)).is_absolute():
        return resolved

    return PROJECT_ROOT / resolved


def ensure_folder(path: str | Path) -> Path:
    folder = resolve_from_root(path)

    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError:
        fallback = _writable_fallback() / folder.name
        fallback.mkdir(parents=True, exist_ok=True)

        return fallback

    return folder


def config_path() -> Path:
    return resolve_from_root(CONFIG_FILE)


def _writable_fallback() -> Path:
    base = Path.home() / "AppData" / "Local"

    if not base.is_dir():
        base = Path.home()

    return base / "InvitationWorkflowSuite"


def _bundled(relative: str) -> Path | None:
    if BUNDLE_DIR is None:
        return None

    candidate = BUNDLE_DIR / relative

    return candidate if candidate.exists() else None


def template_path() -> Path:
    """Prefer a user-editable copy beside the app, else the bundled default."""
    local = resolve_from_root(TEMPLATE_FILE)

    if local.exists():
        return local

    return _bundled(TEMPLATE_FILE) or local


def icon_path() -> Path | None:
    """Best available app icon, or None when no icon is available."""
    names = ("icon.ico", "icon.png") if sys.platform == "win32" else (
        "icon.png",
        "icon.ico",
    )

    for name in names:
        relative = f"{ASSETS_FOLDER}/{name}"
        local = resolve_from_root(relative)

        if local.exists():
            return local

        bundled = _bundled(relative)

        if bundled is not None:
            return bundled

    return None
