"""Modern dark theme for the suite, expressed as Qt Style Sheets."""

BACKGROUND = "#1b1d23"
SURFACE = "#23262f"
SURFACE_ALT = "#2b2f3a"
BORDER = "#3a3f4d"
TEXT = "#e6e8ee"
TEXT_MUTED = "#9aa0ae"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#8f72ff"
ACCENT_PRESSED = "#6a4ce0"
SUCCESS = "#3ecf8e"
WARNING = "#f0b429"
DANGER = "#e5484d"

STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-size: 13px;
}}

QLabel {{
    background: transparent;
}}

QGroupBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {TEXT_MUTED};
    font-weight: 600;
}}

QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: {ACCENT};
    selection-color: #ffffff;
}}

QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}

QLineEdit:read-only {{
    color: {TEXT_MUTED};
}}

QLabel#Heading {{
    font-size: 17px;
    font-weight: 700;
    color: {TEXT};
}}

QLabel#Subheading, QLabel#Muted {{
    color: {TEXT_MUTED};
}}

QPushButton {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 14px;
    color: {TEXT};
}}

QPushButton:hover:enabled {{
    background-color: {BORDER};
    border-color: {ACCENT};
}}

QPushButton:pressed:enabled {{
    background-color: {SURFACE};
}}

QPushButton:disabled {{
    color: #5c6270;
    background-color: #212430;
    border-color: #2c303b;
}}

QPushButton#Primary {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
    color: #ffffff;
    font-weight: 600;
}}

QPushButton#Primary:hover:enabled {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}

QPushButton#Primary:pressed:enabled {{
    background-color: {ACCENT_PRESSED};
}}

QPushButton#Primary:disabled {{
    background-color: #3a3550;
    border-color: #3a3550;
    color: #6b6480;
}}

QPushButton#Danger {{
    background-color: {DANGER};
    border: 1px solid {DANGER};
    color: #ffffff;
    font-weight: 600;
}}

QPushButton#Danger:hover:enabled {{
    background-color: #ef5f63;
}}

QPushButton#Danger:disabled {{
    background-color: #4a2b2d;
    border-color: #4a2b2d;
    color: #8a6b6c;
}}

QTableWidget {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    alternate-background-color: {SURFACE};
    selection-background-color: {ACCENT};
    selection-color: #ffffff;
}}

QTableWidget::item {{
    padding: 4px 6px;
}}

QHeaderView::section {{
    background-color: {SURFACE};
    color: {TEXT_MUTED};
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    padding: 7px 8px;
    font-weight: 600;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    top: -1px;
    background-color: {BACKGROUND};
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    border: 1px solid transparent;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 9px 22px;
    margin-right: 4px;
}}

QTabBar::tab:selected {{
    background-color: {SURFACE};
    color: {TEXT};
    border-color: {BORDER};
    border-bottom-color: {SURFACE};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    color: {TEXT};
}}

QSplitter::handle {{
    background-color: {BORDER};
}}

QSplitter::handle:horizontal {{
    width: 4px;
    border-radius: 2px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 11px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 28px;
}}

QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 11px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 5px;
    min-width: 28px;
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
    width: 0px;
    border: none;
    background: transparent;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
}}

QProgressBar {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT};
    height: 18px;
}}

QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 5px;
}}

QCheckBox {{
    color: {TEXT};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background-color: {SURFACE_ALT};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}

QToolTip {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {ACCENT};
    padding: 4px;
}}

QMessageBox {{
    background-color: {SURFACE};
}}

QStatusBar {{
    background-color: {SURFACE};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER};
}}
"""
