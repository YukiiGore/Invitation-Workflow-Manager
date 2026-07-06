from pathlib import Path

from core.image_loader import ImageLoader
from core.template_engine import TemplateEngine


def main():
    loader = ImageLoader(Path("examples/images"))
    template = TemplateEngine(Path("templates/template.txt"))

    images = loader.load_images()

    print(f"Found {len(images)} image(s).\n")

    for image in images:
        username = image.stem

        print("=" * 40)
        print(template.render_template(username))
        print()


if __name__ == "__main__":
    main()