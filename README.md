# Invitation Workflow Suite

Desktop application for batch-renaming invitation assets and generating
personalized captions. Built with PySide6.

## Features

### 1. Batch Rename (Excel)

- 📁 Folder picker for raw PNGs (`1.png`, `2.png`, …)
- 📊 Excel / CSV picker — column 1 is the old name, column 2 the new username
- 📋 Live mapping preview: `[Original Filename] -> [New Filename]`
- 🛡️ Pre-flight validation for missing, duplicate, colliding, and invalid names
- ▶️ One-click batch rename with confirmation
- 📝 Notepad converter: paste newline-separated names, or load them from a `.txt`

### 2. Caption & Dialogue Generator

- 🖼 PNG preview with the username detected from the filename
- 🖱 Drag the preview straight into Discord, Slack, or Explorer
- 📋 Copy caption to the clipboard
- 📂 Reveal the active file in Explorer
- ◀ Previous / ▶ Next navigation with position indicator
- ✏️ Interactive template editor using the `{username}` placeholder
- 💾 Save / load templates to `templates/config.json`

## Install

```
pip install -r requirements.txt
```

## Run

```
python src/main.py
```

The GUI opens on a two-tab layout. Add `--cli` to print captions to the
console instead of launching the window.

## Build a standalone executable

```
pip install -r requirements.txt
python build_exe.py
```

Produces `dist/InvitationWorkflowSuite.exe`, a single console-free binary.
Run `python build_exe.py --clean` to delete `build/` and `dist/`.

The build bundles `templates/template.txt` and the app icons, and embeds
`assets/icon.ico` as the file icon. `build/`, `dist/`, and generated `*.spec`
files are git-ignored, so `build_exe.py` is the source of truth for the
bundling flags.

### Frozen behaviour

A PyInstaller build unpacks itself to a temporary folder on launch, so
`src/core/paths.py` switches behaviour when frozen:

| Purpose | Source checkout | Frozen executable |
|---|---|---|
| `examples/images`, `templates/config.json` | project root | folder containing the `.exe` |
| `templates/template.txt` | project root | folder containing the `.exe`, else the bundled copy |
| `assets/icon.*` | project root | folder containing the `.exe`, else the bundled copy |

Keeping writable data beside the `.exe` means your images and saved config
survive, instead of being written into a temp directory that is deleted on
exit. If that folder is read-only (for example under `Program Files`), the
app falls back to `%LOCALAPPDATA%\InvitationWorkflowSuite`.

Regenerate the icon with `python tools/make_icon.py`, which writes
`assets/icon.ico` at 7 resolutions from 16px to 256px.

## Template

Placeholders in the template are replaced when a caption is rendered:

- `{username}` — the username detected from the PNG filename

## Layout

```
.
├── build_exe.py            PyInstaller build script
├── assets/
│   ├── icon.ico            app + window icon (7 resolutions)
│   └── icon.png            256px preview
├── tools/
│   └── make_icon.py        regenerates assets/icon.ico
├── templates/
│   ├── template.txt        default dialogue template
│   └── config.json         saved config (created at runtime, git-ignored)
├── examples/images/        your PNGs (git-ignored)
└── src/
    ├── main.py             entry point (GUI by default, --cli for console)
    ├── core/               no Qt imports
    │   ├── batch_rename.py rename planning, validation, execution
    │   ├── config_store.py JSON config read/write
    │   ├── image_loader.py PNG discovery
    │   ├── name_table.py   Excel/CSV parsing via pandas
    │   ├── notepad_names.py pasted name lists
    │   ├── paths.py        path resolution, frozen-mode aware
    │   ├── sorting.py      natural (human) sort for numbered filenames
    │   ├── system_utils.py clipboard + file manager
    │   └── template_engine.py {username} substitution
    └── gui/
        ├── app.py          QApplication, dark palette, window icon
        ├── main_window.py  two-tab shell
        ├── tab_rename.py   batch rename tab
        ├── tab_caption.py  caption tab
        ├── template_editor.py template editing + config buttons
        ├── notepad_dialog.py notepad converter modal
        ├── image_browser.py selection state
        ├── preview_panel.py image preview + drag source
        ├── caption_panel.py caption + actions
        └── theme.py        dark QSS stylesheet
```

Paths resolve against the project root, so the app runs from any working
directory. `examples/images` is created on first launch.

## File ordering

Filenames are sorted naturally, so `1.png` is followed by `2.png` up to
`10.png` rather than the lexicographic `1.png, 10.png, 11.png, 2.png`.
Since name lists are paired positionally against the folder's files, this
keeps row 2 of a Notepad or Excel list aligned with `2.png`.

## Drag and drop

The preview in Tab 2 is a drag source. Press and drag the image to drop the
original file into Discord, Slack, or File Explorer. The drag carries a file
URL rather than inline image data, so the receiving app gets the
full-resolution original rather than the scaled on-screen preview. The drag
thumbnail shown under the cursor is capped at 256px, and a movement
threshold stops ordinary clicks from being mistaken for a drag.

## No Discord API

Invitation Workflow Suite does **not** automate Discord or use user tokens.

It assists manual workflows by organizing invitation assets and generating
personalized captions.
