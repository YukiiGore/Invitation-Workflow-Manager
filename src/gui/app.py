import sys

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from core.paths import IMAGES_FOLDER, ensure_folder, template_path
from gui.main_window import APP_TITLE, MainWindow
from gui.theme import (
    BACKGROUND,
    STYLESHEET,
    SURFACE,
    TEXT,
    TEXT_MUTED,
)


def _apply_dark_palette(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.Window, BACKGROUND)
    palette.setColor(QPalette.WindowText, TEXT)
    palette.setColor(QPalette.Base, SURFACE)
    palette.setColor(QPalette.AlternateBase, SURFACE)
    palette.setColor(QPalette.Text, TEXT)
    palette.setColor(QPalette.Button, SURFACE)
    palette.setColor(QPalette.ButtonText, TEXT)
    palette.setColor(QPalette.Highlight, "#7c5cff")
    palette.setColor(QPalette.HighlightedText, "#ffffff")
    palette.setColor(QPalette.ToolTipBase, SURFACE)
    palette.setColor(QPalette.ToolTipText, TEXT)
    palette.setColor(QPalette.PlaceholderText, TEXT_MUTED)

    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)

    if not template_path().exists():
        print(f"Template not found at '{template_path()}'.", file=sys.stderr)
        return 1

    _apply_dark_palette(app)

    window = MainWindow(default_folder=ensure_folder(IMAGES_FOLDER))
    window.show()

    return app.exec()
