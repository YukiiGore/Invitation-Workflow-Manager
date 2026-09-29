from pathlib import Path

from core.paths import ensure_folder
from core.sorting import sort_naturally


class ImageLoader:
    def __init__(self, folder_path: Path):
        self.folder_path = folder_path

    def load_images(self) -> list[Path]:
        if self.folder_path.exists() and not self.folder_path.is_dir():
            raise NotADirectoryError(
                f"'{self.folder_path}' is not a folder."
            )

        ensure_folder(self.folder_path)

        images = sort_naturally(self.folder_path.glob("*.png"))

        return images