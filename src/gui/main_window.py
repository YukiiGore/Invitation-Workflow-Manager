from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gui.tab_caption import CaptionTab
from gui.tab_rename import BatchRenameTab

APP_TITLE = "Invitation Workflow Suite"


class MainWindow(QMainWindow):
    def __init__(self, default_folder: Path, parent=None):
        super().__init__(parent)

        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 760)

        self._rename_tab = BatchRenameTab(default_folder, self)
        self._caption_tab = CaptionTab(default_folder, self)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._rename_tab, "1. Batch Rename (Excel)")
        self._tabs.addTab(self._caption_tab, "2. Caption & Dialogue Generator")
        self._tabs.currentChanged.connect(self._on_tab_changed)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 16, 18, 12)
        layout.setSpacing(12)
        layout.addWidget(self._tabs, stretch=1)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())

        self._rename_tab.directory_changed.connect(self._on_rename_directory)
        self._rename_tab.rename_finished.connect(self._on_rename_finished)
        self._caption_tab.template_editor.save_requested.connect(
            self._caption_tab.save_config
        )
        self._caption_tab.template_editor.load_requested.connect(
            self._on_load_config
        )

        self._on_rename_directory(str(self._rename_tab.folder))

    @property
    def rename_tab(self) -> BatchRenameTab:
        return self._rename_tab

    @property
    def caption_tab(self) -> CaptionTab:
        return self._caption_tab

    def _on_rename_directory(self, folder: str) -> None:
        self._caption_tab.load_folder(Path(folder))
        self.statusBar().showMessage(f"Active folder: {folder}")

    def _on_rename_finished(self, count: int) -> None:
        if count:
            self.statusBar().showMessage(
                f"Renamed {count} file(s). Caption tab refreshed."
            )

    def _on_load_config(self) -> None:
        if self._caption_tab.load_config_into_editor():
            self.statusBar().showMessage("Template config loaded.")

    def _on_tab_changed(self, index: int) -> None:
        if index == 1:
            self._caption_tab.load_folder(self._caption_tab.folder)
