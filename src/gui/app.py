import sys

from PySide6.QtGui import QIcon, QPalette
from PySide6.QtWidgets import QApplication

from core.paths import IMAGES_FOLDER, ensure_folder, icon_path, template_path
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


def _apply_icon(app: QApplication, window: MainWindow) -> bool:
    """Set the app and window icon. Returns False when no icon was found."""
    path = icon_path()

    if path is None:
        return False

    icon = QIcon(str(path))

    if icon.isNull():
        return False

    app.setWindowIcon(icon)
    window.setWindowIcon(icon)

    return True


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setApplicationDisplayName(APP_TITLE)

    if not template_path().exists():
        print(f"Template not found at '{template_path()}'.", file=sys.stderr)
        return 1

    _apply_dark_palette(app)

    window = MainWindow(default_folder=ensure_folder(IMAGES_FOLDER))
    window.show()

    if not _apply_icon(app, window):
        print("App icon not found; continuing without one.", file=sys.stderr)

    return app.exec()
