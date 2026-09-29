from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from core.notepad_names import parse_lines


class NotepadConverterDialog(QDialog):
    """Paste newline-separated names, or load them from a plain text file."""

    SAMPLE = "alice\nbob\ncarol"

    def __init__(self, folder, existing_files, parent=None):
        super().__init__(parent)

        self._folder = folder
        self._existing = list(existing_files)

        self.setWindowTitle("Notepad Name Converter")
        self.setMinimumSize(560, 520)

        self._build_ui()
        self._update_summary()

    def _build_ui(self) -> None:
        header = QLabel("Paste one username per line, in the order they should be applied.")
        header.setObjectName("Subheading")

        self._editor = QPlainTextEdit()
        self._editor.setPlaceholderText(self.SAMPLE)
        self._editor.textChanged.connect(self._update_summary)

        self._summary = QLabel("")
        self._summary.setObjectName("Muted")
        self._summary.setWordWrap(True)

        load_file = QPushButton("Load from .txt…")
        load_file.clicked.connect(self._load_file)

        clear = QPushButton("Clear")
        clear.clicked.connect(self._editor.clear)

        editor_row = QHBoxLayout()
        editor_row.addWidget(load_file)
        editor_row.addWidget(clear)
        editor_row.addStretch(1)

        self._preview_label = QLabel("Loading preview…")
        self._preview_label.setWordWrap(True)
        self._preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._preview_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self._preview = QGroupBox("Resulting mapping")
        self._preview.setMinimumHeight(190)
        preview_layout = QVBoxLayout(self._preview)
        preview_layout.addWidget(self._preview_label)

        buttons = QDialogButtonBox()
        apply_button = buttons.addButton(
            "Use These Names", QDialogButtonBox.AcceptRole
        )
        apply_button.setObjectName("Primary")
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(self._editor, stretch=1)
        layout.addLayout(editor_row)
        layout.addWidget(self._summary)
        layout.addWidget(self._preview, stretch=1)
        layout.addWidget(buttons)

    def _load_file(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Load names from file",
            str(self._folder),
            "Text files (*.txt);;All files (*)",
        )

        if not selected:
            return

        try:
            with open(selected, "r", encoding="utf-8", errors="replace") as handle:
                self._editor.setPlainText(handle.read())
        except OSError as error:
            QMessageBox.warning(self, "Could not read file", str(error))

    def _update_summary(self) -> None:
        names = self.parsed_names()

        if not names:
            self._summary.setText("No names entered yet.")
            self._preview_label.setText("Nothing to preview.")
            return

        self._summary.setText(
            f"{len(names)} name(s) entered, "
            f"{len(self._existing)} PNG file(s) found in the selected folder."
        )

        lines = []
        for index, name in enumerate(names):
            old = self._existing[index] if index < len(self._existing) else "—"

            lines.append(f"{index + 1}.  {old}  →  {name}.png")

        if len(names) > len(self._existing):
            lines.append(
                f"\n{len(names) - len(self._existing)} extra name(s) have no matching file."
            )

        self._preview_label.setText("\n".join(lines))

    def parsed_names(self) -> list[str]:
        return parse_lines(self._editor.toPlainText())

    def mapping_order(self) -> list[str]:
        return self._existing

    def accept(self) -> None:
        if not self.parsed_names():
            QMessageBox.information(
                self, "Nothing to convert", "Enter at least one username first."
            )
            return

        super().accept()
