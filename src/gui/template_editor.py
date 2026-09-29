from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.paths import template_path
from core.template_engine import TemplateEngine


class TemplateEditor(QGroupBox):
    """Editable dialogue template with a {username} placeholder."""

    template_changed = Signal()
    save_requested = Signal()
    load_requested = Signal()
    reset_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Dialogue Template", parent)

        self._engine = TemplateEngine(template_path())
        self._updating = False

        hint = QLabel(
            "Use {username} anywhere in the text to insert the detected username."
        )
        hint.setObjectName("Muted")
        hint.setWordWrap(True)

        self._editor = QPlainTextEdit()
        self._editor.setPlaceholderText("Hello {username}!")
        self._editor.setMinimumHeight(130)
        self._editor.textChanged.connect(self._on_text_changed)

        self._save_button = QPushButton("Save Config")
        self._save_button.setObjectName("Primary")
        self._save_button.clicked.connect(self.save_requested)

        load_button = QPushButton("Load Config")
        load_button.clicked.connect(self.load_requested)

        reset_button = QPushButton("Reset to File")
        reset_button.clicked.connect(self._reset_to_file)

        buttons = QHBoxLayout()
        buttons.addWidget(self._save_button)
        buttons.addWidget(load_button)
        buttons.addWidget(reset_button)
        buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(hint)
        layout.addWidget(self._editor, stretch=1)
        layout.addLayout(buttons)

    def text(self) -> str:
        return self._editor.toPlainText()

    def set_text(self, text: str) -> None:
        self._updating = True
        self._editor.setPlainText(text)
        self._updating = False
        self.template_changed.emit()

    def render(self, username: str) -> str:
        return self._engine.render(self.text(), username)

    def _on_text_changed(self) -> None:
        if not self._updating:
            self.template_changed.emit()

    def _reset_to_file(self) -> None:
        try:
            self.set_text(self._engine.load_template())
        except OSError:
            self.set_text("")
