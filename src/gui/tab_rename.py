from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.batch_rename import (
    RenameEntry,
    RenameReport,
    RenameStatus,
    build_plan,
    run_plan,
)
from core.name_table import load_name_table
from core.paths import ensure_folder
from core.sorting import sort_naturally
from gui.notepad_dialog import NotepadConverterDialog
from gui.theme import DANGER, SUCCESS, WARNING

COLUMN_SOURCE = 0
COLUMN_TARGET = 1
COLUMN_STATUS = 2

STATUS_COLORS = {
    RenameStatus.OK: SUCCESS,
    RenameStatus.UNCHANGED: WARNING,
    RenameStatus.MISSING: WARNING,
    RenameStatus.COLLISION: DANGER,
    RenameStatus.DUPLICATE: DANGER,
    RenameStatus.INVALID: DANGER,
}


class BatchRenameTab(QWidget):
    """Maps numbered PNGs onto real usernames using an Excel/CSV or notepad list."""

    directory_changed = Signal(str)
    rename_finished = Signal(int)

    def __init__(self, default_folder: Path, parent=None):
        super().__init__(parent)

        self._folder = default_folder
        self._data_file: Path | None = None
        self._entries: list[RenameEntry] = []

        self._build_ui()
        self.refresh_folder()

    def _build_ui(self) -> None:
        heading = QLabel("Batch Rename")
        heading.setObjectName("Heading")

        subtitle = QLabel(
            "Map raw filenames like 1.png onto real usernames from a spreadsheet "
            "or a pasted Notepad list."
        )
        subtitle.setObjectName("Subheading")
        subtitle.setWordWrap(True)

        self._folder_edit = QLineEdit(str(self._folder))
        self._folder_edit.setReadOnly(True)

        folder_button = QPushButton("Choose PNG Folder…")
        folder_button.clicked.connect(self._choose_folder)

        reload_button = QPushButton("Refresh")
        reload_button.clicked.connect(self.refresh_folder)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("PNG folder:"))
        folder_row.addWidget(self._folder_edit, stretch=1)
        folder_row.addWidget(folder_button)
        folder_row.addWidget(reload_button)

        self._data_edit = QLineEdit("No file selected")
        self._data_edit.setReadOnly(True)

        data_button = QPushButton("Choose Excel / CSV…")
        data_button.clicked.connect(self._choose_data_file)

        notepad_button = QPushButton("Notepad Converter…")
        notepad_button.clicked.connect(self._open_notepad)

        clear_button = QPushButton("Clear Mapping")
        clear_button.clicked.connect(self._clear_mapping)

        data_row = QHBoxLayout()
        data_row.addWidget(QLabel("Name source:"))
        data_row.addWidget(self._data_edit, stretch=1)
        data_row.addWidget(data_button)
        data_row.addWidget(notepad_button)
        data_row.addWidget(clear_button)

        sources = QGroupBox("Sources")
        sources_layout = QVBoxLayout(sources)
        sources_layout.addLayout(folder_row)
        sources_layout.addSpacing(6)
        sources_layout.addLayout(data_row)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(
            ["Original Filename", "New Filename", "Status"]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setShowGrid(False)
        self._table.setSortingEnabled(False)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(COLUMN_SOURCE, QHeaderView.Stretch)
        header.setSectionResizeMode(COLUMN_TARGET, QHeaderView.Stretch)
        header.setSectionResizeMode(COLUMN_STATUS, QHeaderView.ResizeToContents)

        self._summary = QLabel("No mapping loaded.")
        self._summary.setObjectName("Muted")

        mapping = QGroupBox("Mapping Preview")
        mapping_layout = QVBoxLayout(mapping)
        mapping_layout.addWidget(self._table, stretch=1)

        self._run_button = QPushButton("Run Batch Rename")
        self._run_button.setObjectName("Primary")
        self._run_button.setEnabled(False)
        self._run_button.clicked.connect(self._run_rename)

        self._reset_button = QPushButton("Reset Mapping")
        self._reset_button.setEnabled(False)
        self._reset_button.clicked.connect(self._clear_mapping)

        actions = QHBoxLayout()
        actions.addWidget(self._summary)
        actions.addStretch(1)
        actions.addWidget(self._reset_button)
        actions.addWidget(self._run_button)

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addWidget(sources)
        layout.addWidget(mapping, stretch=1)
        layout.addLayout(actions)

    @property
    def folder(self) -> Path:
        return self._folder

    @property
    def entries(self) -> list[RenameEntry]:
        return self._entries

    def _choose_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self, "Select PNG folder", str(self._folder)
        )

        if selected:
            self.set_folder(Path(selected))

    def _choose_data_file(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Select spreadsheet",
            str(self._folder),
            "Spreadsheets (*.xlsx *.xls *.csv);;All files (*)",
        )

        if not selected:
            return

        self._data_file = Path(selected)
        self._data_edit.setText(self._data_file.name)

        try:
            pairs = load_name_table(self._data_file)
        except Exception as error:
            QMessageBox.critical(self, "Could not read file", str(error))
            self._data_file = None
            self._data_edit.setText("No file selected")
            return

        if not pairs:
            QMessageBox.warning(
                self,
                "Nothing to rename",
                "The first two columns of that file were empty.\n\n"
                "Column 1 should hold the old name (e.g. 1), "
                "column 2 the new username.",
            )
            return

        self._apply_pairs(pairs)

    def _open_notepad(self) -> None:
        existing = sort_naturally(path.stem for path in self._folder.glob("*.png"))

        if not existing:
            QMessageBox.information(
                self,
                "No PNGs found",
                f"No PNG files were found in:\n{self._folder}",
            )
            return

        dialog = NotepadConverterDialog(self._folder, existing, self)
        dialog.exec()

        names = dialog.parsed_names()

        if not names:
            return

        self._data_file = None
        self._data_edit.setText("Pasted from Notepad")
        self._apply_pairs(list(zip(existing, names)))

    def _apply_pairs(self, pairs: list[tuple[str, str]]) -> None:
        self._entries = build_plan(self._folder, pairs)
        self._refresh_table()

    def _clear_mapping(self) -> None:
        self._entries = []
        self._table.setRowCount(0)
        self._data_file = None
        self._data_edit.setText("No file selected")
        self._summary.setText("No mapping loaded.")
        self._run_button.setEnabled(False)
        self._reset_button.setEnabled(False)

    def set_folder(self, folder: Path) -> None:
        self._folder = ensure_folder(folder)
        self._folder_edit.setText(str(self._folder))
        self.directory_changed.emit(str(self._folder))
        self.refresh_folder()

    def refresh_folder(self) -> None:
        self._folder_edit.setText(str(self._folder))

        if self._data_file is not None:
            try:
                pairs = load_name_table(self._data_file)
            except Exception:
                pairs = []
                self._data_file = None
                self._data_edit.setText("No file selected")

            self._apply_pairs(pairs)
        else:
            self._refresh_table()

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)
        self._table.setRowCount(len(self._entries))

        for row, entry in enumerate(self._entries):
            self._table.setItem(
                row, COLUMN_SOURCE, QTableWidgetItem(entry.old_filename)
            )
            self._table.setItem(
                row, COLUMN_TARGET, QTableWidgetItem(entry.new_filename)
            )

            status = QTableWidgetItem(self._status_text(entry))
            status.setForeground(QColor(STATUS_COLORS.get(entry.status, WARNING)))
            self._table.setItem(row, COLUMN_STATUS, status)

            if entry.detail:
                status.setToolTip(entry.detail)

        runnable = [entry for entry in self._entries if entry.is_runnable]
        blocked = [entry for entry in self._entries if not entry.is_runnable]

        if not self._entries:
            self._summary.setText("No mapping loaded.")
        elif runnable:
            skipped = f", {len(blocked)} needing attention" if blocked else ""
            self._summary.setText(
                f"Ready to rename {len(runnable)} file(s){skipped}."
            )
        else:
            self._summary.setText(
                f"No files can be renamed — all {len(blocked)} row(s) need attention."
            )

        self._run_button.setEnabled(bool(runnable))
        self._reset_button.setEnabled(bool(self._entries))

    def _status_text(self, entry: RenameEntry) -> str:
        if entry.status is RenameStatus.OK:
            return "Ready"
        if entry.status is RenameStatus.UNCHANGED:
            return "No change"
        if entry.status is RenameStatus.MISSING:
            return "Missing"
        if entry.status is RenameStatus.COLLISION:
            return "Target exists"
        if entry.status is RenameStatus.DUPLICATE:
            return "Duplicate"
        return "Invalid"

    def _run_rename(self) -> None:
        runnable = [entry for entry in self._entries if entry.is_runnable]

        if not runnable:
            return

        confirmed = QMessageBox.question(
            self,
            "Confirm batch rename",
            f"Rename {len(runnable)} file(s) in:\n{self._folder}\n\n"
            "This changes files on disk. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirmed != QMessageBox.Yes:
            return

        report: RenameReport = run_plan(self._folder, runnable)

        self._entries = build_plan(
            self._folder,
            [
                (entry.old_filename, entry.new_filename)
                for entry in self._entries
            ],
        )
        self._refresh_table()

        details = report.summary()

        if report.failed:
            failures = "\n".join(
                f"{entry.old_filename}: {entry.detail}" for entry in report.failed
            )
            QMessageBox.critical(
                self, "Batch rename failed", f"{details}\n\n{failures}"
            )
        else:
            QMessageBox.information(self, "Batch rename complete", details)

        self.rename_finished.emit(report.total_renamed)
        self.directory_changed.emit(str(self._folder))
