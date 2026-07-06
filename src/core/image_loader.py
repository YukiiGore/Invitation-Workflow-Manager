from pathlib import Path


class ImageLoader:
    def __init__(self, folder_path: Path):
        self.folder_path = folder_path

    def load_images(self) -> list[Path]:
        if not self.folder_path.exists():
            raise FileNotFoundError(
                f"Folder '{self.folder_path}' does not exist."
            )

        if not self.folder_path.is_dir():
            raise NotADirectoryError(
                f"'{self.folder_path}' is not a folder."
            )

        images = sorted(self.folder_path.glob("*.png"))

        return images