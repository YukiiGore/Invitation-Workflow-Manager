from pathlib import Path

from core.template_engine import TemplateEngine


def main():
    template = TemplateEngine(Path("templates/template.txt"))

    result = template.render_template("YukiiGore")

    print(result)


if __name__ == "__main__":
    main()