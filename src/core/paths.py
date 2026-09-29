from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

IMAGES_FOLDER = "examples/images"
TEMPLATE_FILE = "templates/template.txt"
CONFIG_FILE = "templates/config.json"


def resolve_from_root(path: str | Path) -> Path:
    if (resolved := Path(path)).is_absolute():
        return resolved

    return PROJECT_ROOT / resolved


def ensure_folder(path: str | Path) -> Path:
    folder = resolve_from_root(path)
    folder.mkdir(parents=True, exist_ok=True)

    return folder


def config_path() -> Path:
    return resolve_from_root(CONFIG_FILE)


def template_path() -> Path:
    return resolve_from_root(TEMPLATE_FILE)
