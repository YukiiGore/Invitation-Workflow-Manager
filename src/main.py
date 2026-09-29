import sys

from core.config_store import load_config
from core.image_loader import ImageLoader
from core.paths import IMAGES_FOLDER, ensure_folder, resolve_from_root
from core.template_engine import TemplateEngine

TEMPLATE_FILE = "templates/template.txt"


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def run_cli() -> int:
    images_folder = ensure_folder(IMAGES_FOLDER)

    if not any(images_folder.iterdir()):
        print(f"No files in '{images_folder}' yet. Add PNGs and run again.\n")

    template = TemplateEngine(resolve_from_root(TEMPLATE_FILE))
    template_text = load_config().get("template") or template.load_template()

    images = ImageLoader(images_folder).load_images()

    print(f"Found {len(images)} image(s).\n")

    for image in images:
        print("=" * 40)
        print(TemplateEngine.render(template_text, image.stem))
        print()

    return 0


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()

    argv = sys.argv[1:] if argv is None else argv

    if "--cli" in argv:
        return run_cli()

    try:
        from gui.app import run as run_gui
    except ImportError as error:
        print(f"PySide6 is not available ({error}).", file=sys.stderr)
        print(
            "Install dependencies with: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
