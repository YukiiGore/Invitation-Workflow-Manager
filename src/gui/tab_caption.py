from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.config_store import DEFAULT_TEMPLATE, load_config, save_config
from core.paths import ensure_folder
from core.system_utils import copy_to_clipboard, reveal_in_file_manager
from core.sorting import sort_naturally
from gui.caption_panel import CaptionPanel
from gui.image_browser import ImageBrowser
from gui.preview_panel import PreviewPanel
from gui.template_editor import TemplateEditor


class CaptionTab(QWidget):
    """Preview renamed PNGs, edit the caption template, and save it as JSON."""

    directory_changed = Signal(str)

    def __init__(self, default_folder: Path, parent=None):
        super().__init__(parent)

        config = load_config()

        self._folder = default_folder
        self._browser = ImageBrowser(self)

        self._build_ui()

        self._template_editor.set_text(config.get("template", DEFAULT_TEMPLATE))
        self._template_editor.template_changed.connect(self._on_template_changed)

        self._connect_signals()
        self.load_folder(default_folder)

    def _build_ui(self) -> None:
        heading = QLabel("Caption & Dialogue Generator")
        heading.setObjectName("Heading")

        subtitle = QLabel(
            "Preview each renamed PNG, edit the dialogue template, "
            "and copy the result."
        )
        subtitle.setObjectName("Subheading")
        subtitle.setWordWrap(True)

        self._folder_edit = QLineEdit(str(self._folder))
        self._folder_edit.setReadOnly(True)

        folder_button = QPushButton("Choose Folder…")
        folder_button.clicked.connect(self._choose_folder)

        reload_button = QPushButton("Refresh")
        reload_button.clicked.connect(lambda: self.load_folder(self._folder))

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Active folder:"))
        folder_row.addWidget(self._folder_edit, stretch=1)
        folder_row.addWidget(folder_button)
        folder_row.addWidget(reload_button)

        self._template_editor = TemplateEditor()

        self._preview = PreviewPanel()
        self._caption = CaptionPanel()

        self._position = QLabel("0 / 0")
        self._position.setAlignment(Qt.AlignCenter)

        self._previous_button = QPushButton("◀ Previous")
        self._next_button = QPushButton("Next ▶")

        nav_row = QHBoxLayout()
        nav_row.addStretch(1)
        nav_row.addWidget(self._previous_button)
        nav_row.addWidget(self._position)
        nav_row.addWidget(self._next_button)
        nav_row.addStretch(1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self._preview)
        left_layout.addLayout(nav_row)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self._caption, stretch=1)
        right_layout.addWidget(self._template_editor, stretch=1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([560, 420])

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addLayout(folder_row)
        layout.addWidget(splitter, stretch=1)

    def _connect_signals(self) -> None:
        self._browser.selection_changed.connect(self._on_selection_changed)
        self._caption.copy_requested.connect(self._copy_caption)
        self._caption.reveal_requested.connect(self._reveal_image)
        self._previous_button.clicked.connect(self._browser.previous_image)
        self._next_button.clicked.connect(self._browser.next_image)

    @property
    def browser(self) -> ImageBrowser:
        return self._browser

    @property
    def folder(self) -> Path:
        return self._folder

    @property
    def template_editor(self) -> TemplateEditor:
        return self._template_editor

    def _choose_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self, "Select PNG folder", str(self._folder)
        )

        if selected:
            self.load_folder(Path(selected))

    def load_folder(self, folder: Path) -> None:
        self._folder = ensure_folder(folder)
        self._folder_edit.setText(str(self._folder))

        self._browser.set_images(sort_naturally(self._folder.glob("*.png")))

        if self._browser.is_empty:
            self._position.setText("0 / 0")
            self._previous_button.setEnabled(False)
            self._next_button.setEnabled(False)
            self._preview.clear("No PNGs in this folder")
            self._caption.clear("Run a batch rename first, or pick another folder.")
        else:
            self._previous_button.setEnabled(True)
            self._next_button.setEnabled(True)

        self.directory_changed.emit(str(self._folder))

    def _on_selection_changed(self, index: int, count: int) -> None:
        self._position.setText(f"{index + 1} / {count}")

        image = self._browser.current_image

        if image is None:
            return

        username = self._browser.current_username

        self._preview.show_image(image, username)
        self._caption.set_caption(self._render_caption(username))

    def _on_template_changed(self) -> None:
        self._refresh_caption()

    def _refresh_caption(self) -> None:
        if self._browser.is_empty:
            return

        self._caption.set_caption(
            self._render_caption(self._browser.current_username)
        )

    def _render_caption(self, username: str) -> str:
        return self._template_editor.render(username)

    def save_config(self) -> None:
        config = load_config()
        config["template"] = self._template_editor.text()

        try:
            path = save_config(config)
        except OSError as error:
            QMessageBox.critical(self, "Could not save config", str(error))
            return

        self._caption.set_status(f"Saved to {path.name}")

    def load_config_into_editor(self) -> bool:
        try:
            config = load_config()
        except OSError as error:
            QMessageBox.critical(self, "Could not load config", str(error))
            return False

        self._template_editor.set_text(config.get("template", DEFAULT_TEMPLATE))

        return True

    def _copy_caption(self) -> None:
        if self._browser.current_image is None:
            return

        caption = self._render_caption(self._browser.current_username)

        try:
            copy_to_clipboard(caption)
        except RuntimeError as error:
            QMessageBox.warning(self, "Clipboard", str(error))
            return

        self._caption.set_status("Copied ✓")

    def _reveal_image(self) -> None:
        image = self._browser.current_image

        if image is None:
            return

        reveal_in_file_manager(image)
