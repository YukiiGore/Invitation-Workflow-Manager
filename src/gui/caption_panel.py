from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

WORKFLOW_HINT = "1. Copy Caption, then paste with Ctrl+V  →  2. Drag image to Discord"


class CaptionPanel(QGroupBox):
    """Shows the rendered caption and exposes copy / reveal actions."""

    copy_requested = Signal()
    reveal_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Caption", parent)

        self._caption = QPlainTextEdit()
        self._caption.setReadOnly(True)
        self._caption.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self._caption.setMinimumHeight(180)
        self._caption.setPlaceholderText("Select a folder to get started.")

        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignRight)
        self._status.setObjectName("Muted")

        self._copy_button = QPushButton("Copy Caption")
        self._copy_button.setEnabled(False)
        self._copy_button.clicked.connect(self.copy_requested)

        self._reveal_button = QPushButton("Reveal in Explorer")
        self._reveal_button.setEnabled(False)
        self._reveal_button.clicked.connect(self.reveal_requested)

        buttons = QHBoxLayout()
        buttons.addWidget(self._copy_button)
        buttons.addWidget(self._reveal_button)
        buttons.addStretch(1)
        buttons.addWidget(self._status)

        self._hint = QLabel(WORKFLOW_HINT)
        self._hint.setObjectName("Muted")
        self._hint.setWordWrap(True)
        self._hint.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self._caption)
        layout.addLayout(buttons)
        layout.addWidget(self._hint)

    def set_caption(self, text: str) -> None:
        self._caption.setPlainText(text)

        has_caption = bool(text.strip())
        self._copy_button.setEnabled(has_caption)
        self._reveal_button.setEnabled(has_caption)
        self._hint.setVisible(has_caption)

        if not has_caption:
            self._status.clear()

    def set_status(self, message: str) -> None:
        self._status.setText(message)

    def clear(self, message: str = "") -> None:
        self._caption.setPlainText(message)
        self._copy_button.setEnabled(False)
        self._reveal_button.setEnabled(False)
        self._hint.setVisible(False)
        self._status.clear()
