from pathlib import Path


class TemplateEngine:
    def __init__(self, template_path: Path):
        self.template_path = template_path

    def load_template(self) -> str:
        return self.template_path.read_text(encoding="utf-8")

    def render_template(self, username: str) -> str:
        return self.render(self.load_template(), username)

    @staticmethod
    def render(template: str, username: str) -> str:
        return template.replace("{username}", username)