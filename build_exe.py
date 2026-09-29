"""Build a standalone InvitationWorkflowSuite.exe with PyInstaller.

Run from the project root:

    python build_exe.py

Produces dist/InvitationWorkflowSuite.exe as a single, console-free binary.
The generated .spec file is a build artifact and is git-ignored, so the flags
below are the source of truth for how the executable is produced.
"""

import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "InvitationWorkflowSuite"
ENTRY_POINT = "src/main.py"
ICON = "assets/icon.ico"

# Files that must exist at runtime inside the bundle.
DATA = (
    "templates/template.txt",
    "assets/icon.ico",
    "assets/icon.png",
)


def project_root() -> Path:
    return Path(__file__).resolve().parent


def build_command(root: Path) -> list[str]:
    separator = ";" if sys.platform == "win32" else ":"

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--noconsole",
        "--name",
        APP_NAME,
        "--paths",
        "src",
        "--distpath",
        str(root / "dist"),
        "--workpath",
        str(root / "build"),
        "--specpath",
        str(root / "build"),
    ]

    # absolute: PyInstaller resolves spec-relative paths against the spec's own
    # directory (build/), not the project root
    if (root / ICON).exists():
        command.append(f"--icon={root / ICON}")
    else:
        print(f"icon missing at '{ICON}'; building without one.", file=sys.stderr)

    for item in DATA:
        # keep the relative layout inside the bundle
        destination = item.split("/")[0]
        command.append(f"--add-data={root / item}{separator}{destination}")

    command.append(str(root / ENTRY_POINT))

    return command


def preflight(root: Path) -> list[str]:
    problems = []

    for required in (ENTRY_POINT, "templates/template.txt", "requirements.txt"):
        if not (root / required).exists():
            problems.append(f"missing required file: {required}")

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        problems.append(
            "PyInstaller is not installed. Run: pip install -r requirements.txt"
        )

    return problems


def main() -> int:
    root = project_root()

    problems = preflight(root)

    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)

        return 1

    spec = root / "build" / f"{APP_NAME}.spec"

    if spec.exists():
        spec.unlink()

    print("running:")
    print("  " + " ".join(build_command(root)))

    result = subprocess.run(build_command(root), cwd=root)

    if result.returncode != 0:
        print("\nbuild failed", file=sys.stderr)
        return result.returncode

    exe = root / "dist" / f"{APP_NAME}.exe"
    bundled = root / "dist" / APP_NAME

    binary = exe if exe.exists() else bundled

    if not binary.exists():
        print("\nbuild reported success but no binary was produced", file=sys.stderr)
        return 1

    size_mb = binary.stat().st_size / (1024 * 1024)

    print(f"\nbinary: {binary}")
    print(f"size:   {size_mb:.1f} MB")

    return 0


def clean() -> int:
    for folder in ("build", "dist"):
        target = project_root() / folder

        if target.exists():
            shutil.rmtree(target)
            print(f"removed {target}")

    return 0


if __name__ == "__main__":
    if "--clean" in sys.argv[1:]:
        sys.exit(clean())

    sys.exit(main())
