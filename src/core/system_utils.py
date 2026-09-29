import subprocess
import sys
from pathlib import Path


def copy_to_clipboard(text: str) -> None:
    try:
        import pyperclip

        pyperclip.copy(text)
    except Exception:
        _copy_fallback(text)


def reveal_in_file_manager(path: Path) -> None:
    if sys.platform == "win32":
        subprocess.Popen(["explorer", f"/select,{path}"])
        return

    if sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(path)])
        return

    target = path.parent if path.exists() else path
    subprocess.Popen(["xdg-open", str(target)])


def _copy_fallback(text: str) -> None:
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.user32.SetClipboardText(ctypes.c_wchar_p(text))
        return

    try:
        import tkinter

        root = tkinter.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.destroy()
    except Exception:
        raise RuntimeError("Could not access the system clipboard.")
