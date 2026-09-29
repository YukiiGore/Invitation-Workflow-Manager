import json
from pathlib import Path

from core.paths import config_path

DEFAULT_TEMPLATE = (
    "Hello {username}!\n\n"
    "I'm inviting you to my redebut!\n\n"
    "Hope to see you there 💜\n"
)


def load_config(path: Path | None = None) -> dict:
    target = path or config_path()

    if not target.exists():
        return {"template": DEFAULT_TEMPLATE}

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"template": DEFAULT_TEMPLATE}

    if not isinstance(data, dict):
        return {"template": DEFAULT_TEMPLATE}

    data.setdefault("template", DEFAULT_TEMPLATE)

    return data


def save_config(config: dict, path: Path | None = None) -> Path:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    target.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return target
