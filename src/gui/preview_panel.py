from pathlib import Path

from PySide6.QtCore import QMimeData, QPoint, Qt, QUrl
from PySide6.QtGui import QDrag, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.theme import BORDER, SURFACE_ALT, TEXT_MUTED

DRAG_HINT = "Drag the image into Discord, Slack, or Explorer"


class ImagePreview(QFrame):
    """Scales the active PNG to fit, and drags the original file to other apps.

    The widget paints its own pixmap instead of hosting a child QLabel so that
    press and move events reach this frame and can start a QDrag. The drag
    carries the file URL, not the scaled pixmap, so the recipient receives the
    full-resolution original.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._path: Path | None = None
        self._source: QPixmap | None = None
        self._placeholder = "No image selected"
        self._press_pos: QPoint | None = None

        self.setMinimumSize(320, 240)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            f"ImagePreview {{"
            f"  background: {SURFACE_ALT};"
            f"  border: 1px solid {BORDER};"
            f"  border-radius: 4px;"
            f"}}"
        )

    @property
    def image_path(self) -> Path | None:
        return self._path

    @property
    def has_image(self) -> bool:
        return self._path is not None and self._source is not None

    def clear(self, message: str = "No image selected") -> None:
        self._path = None
        self._source = None
        self._placeholder = message
        self._set_drag_affordance(False)

        self.update()

    def show_image(self, path: Path) -> bool:
        pixmap = QPixmap(str(path))

        if pixmap.isNull():
            self.clear(f"Could not read\n{path.name}")
            return False

        self._path = path
        self._source = pixmap
        self._placeholder = ""
        self._set_drag_affordance(True)

        self.update()

        return True

    def _set_drag_affordance(self, draggable: bool) -> None:
        self.setToolTip(DRAG_HINT if draggable else "")
        self.setCursor(Qt.OpenHandCursor if draggable else Qt.ArrowCursor)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        if self._source is not None and not self._source.isNull():
            pixmap = self._scaled()
            origin = QPoint(
                (self.width() - pixmap.width()) // 2,
                (self.height() - pixmap.height()) // 2,
            )
            painter.drawPixmap(origin, pixmap)
            return

        painter.setPen(TEXT_MUTED)
        painter.drawText(
            self.rect(),
            Qt.AlignCenter | Qt.TextWordWrap,
            self._placeholder,
        )

    def _scaled(self) -> QPixmap:
        return self._source.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._press_pos = event.position().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not (event.buttons() & Qt.LeftButton) or self._press_pos is None:
            return

        if not self.has_image:
            return

        moved = event.position().toPoint() - self._press_pos

        if (
            moved.manhattanLength()
            < QApplication.startDragDistance()
        ):
            return

        self._press_pos = None
        self.start_file_drag()

    def start_file_drag(self) -> bool:
        if self._path is None:
            return False

        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(self._path.resolve()))])

        drag = QDrag(self)
        drag.setMimeData(mime)

        if self._source is not None:
            drag.setPixmap(self._drag_thumbnail())

        drag.exec(Qt.CopyAction)

        return True

    def _drag_thumbnail(self) -> QPixmap:
        thumbnail = self._source.scaled(
            256,
            256,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        return thumbnail


class PreviewPanel(QGroupBox):
    """Image preview plus the username detected from the filename."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Preview", parent)

        self._username = QLabel("—")
        self._username.setAlignment(Qt.AlignCenter)
        self._username.setStyleSheet("font-size: 16px; font-weight: 600;")

        self._username_caption = QLabel("Detected username")
        self._username_caption.setAlignment(Qt.AlignCenter)
        self._username_caption.setObjectName("Muted")

        self._drag_hint = QLabel(DRAG_HINT)
        self._drag_hint.setAlignment(Qt.AlignCenter)
        self._drag_hint.setObjectName("Muted")
        self._drag_hint.setVisible(False)

        self._preview = ImagePreview()

        layout = QVBoxLayout(self)
        layout.addWidget(self._preview, stretch=1)
        layout.addSpacing(8)
        layout.addWidget(self._username_caption)
        layout.addWidget(self._username)
        layout.addWidget(self._drag_hint)

    def show_image(self, path: Path, username: str) -> bool:
        self._username.setText(username or "—")
        loaded = self._preview.show_image(path)
        self._drag_hint.setVisible(loaded)

        return loaded

    def clear(self, message: str = "No image selected") -> None:
        self._username.setText("—")
        self._preview.clear(message)
        self._drag_hint.setVisible(False)
