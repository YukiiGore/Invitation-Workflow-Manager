from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot


class ImageBrowser(QObject):
    """Holds the loaded image list and the active index, independent of the UI."""

    selection_changed = Signal(int, int)
    folder_changed = Signal(list)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._images: list[Path] = []
        self._index: int = 0

    @property
    def images(self) -> list[Path]:
        return self._images

    @property
    def index(self) -> int:
        return self._index

    @property
    def count(self) -> int:
        return len(self._images)

    @property
    def is_empty(self) -> bool:
        return not self._images

    @property
    def current_image(self) -> Path | None:
        if self.is_empty:
            return None

        return self._images[self._index]

    @property
    def current_username(self) -> str:
        image = self.current_image

        return "" if image is None else image.stem

    def set_images(self, images: list[Path]) -> None:
        self._images = list(images)
        self._index = 0

        self.folder_changed.emit(self._images)
        self.selection_changed.emit(self._index, self.count)

    def next_image(self) -> None:
        self.move_by(1)

    def previous_image(self) -> None:
        self.move_by(-1)

    @Slot(int)
    def move_by(self, offset: int) -> None:
        if self.is_empty:
            return

        count = self.count
        self._index = (self._index + offset) % count

        self.selection_changed.emit(self._index, count)

    @Slot(int)
    def select(self, index: int) -> None:
        if self.is_empty:
            return

        self._index = max(0, min(index, self.count - 1))

        self.selection_changed.emit(self._index, self.count)
