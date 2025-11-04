#!/usr/bin/python3

import sys
import os

BUILD_VERSION='%%VERSION%%'
MX_UPDATER_PATH = "/usr/libexec/mx-updater"

# remove directory of the current script
if '' in sys.path:
    sys.path.remove('')

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

if MX_UPDATER_PATH not in sys.path:
    sys.path.insert(0, MX_UPDATER_PATH)


from updater_translator import Translator

from PyQt6.QtWidgets import (
    QApplication, QDialog, QTextEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialogButtonBox, QMessageBox, QStyle,
    QLineEdit
)
from PyQt6.QtGui import QIcon, QFont, QGuiApplication, QShortcut, QKeySequence, QTextCursor
from PyQt6.QtCore import Qt, QRect, QTranslator, QLocale, QLibraryInfo
from PyQt6.QtCore import QSettings, QPoint, QSize
from PyQt6.QtGui import QTextDocument, QPalette
from PyQt6.QtCore import QRegularExpressionMatch, QRegularExpression


from PyQt6.QtGui import QColor, QTextDocument
from PyQt6.QtCore import Qt

# localization
LOCALE_DOMAIN = 'mx-updater'
LOCALE_DIR = '/usr/share/locale'

translator = Translator(textdomain=LOCALE_DOMAIN)
_ = translator.translate  # Use the translator function

# use _t() to reuse existing tranlations
_t = _

'''
import gettext
LOCALE_DOMAIN = 'mx-updater'
LOCALE_DIR = '/usr/share/locale'
# bind the domain
gettext.bindtextdomain(LOCALE_DOMAIN, LOCALE_DIR)
gettext.textdomain(LOCALE_DOMAIN)
_ = gettext.gettext

'''

class LogViewer(QDialog):
    def __init__(self, file_path=None, view_cmd=None, icon_path=None,
                 window_class=None, window_title="Log Viewer",
                 default_width=960, default_height=600):
        """
        Initialize the LogViewer dialog with smart screen sizing.
        """
        super().__init__()

        # Initialize settings
        self.qsettings  = QSettings('MX-Linux', 'mx-updater')
        if "dpkg_log" in os.path.basename(os.path.abspath(__file__)):
            self.qsettings_section = "Geometry_AutoUpdate_Dpkg_LogViewer"
        else:
            self.qsettings_section = "Geometry_AutoUpdate_LogViewer"

        self.default_width  = default_width
        self.default_height = default_height

        self.cursor = None
        self.highlight_all = False
        self.extra_selections = []

        self.setWindowTitle(window_title)

        if window_class:
            self.setProperty('class', window_class)

        if icon_path:
            if os.path.isfile(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # try icon from theme
                self.setWindowIcon(QIcon.fromTheme(icon_path))

        # VBox layout
        layout = QVBoxLayout()

        #--------------------------------------------------------------
        # Text area
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        #self.text_area.setFont(QFont('monospace', 10))
        #self.text_area.setFont(QFont('Liberation Mono Regular', 11))
        self.text_area.setFont(QFont('Liberation Sans Regular', 11))
        #self.text_area.setFont(QFont('Courier New', 11))

        layout.addWidget(self.text_area)

        # Search layout
        search_layout = QHBoxLayout()

        # Search field
        self.search_field = QLineEdit()
        #--------------------------------------------------------------

        #--------------------------------------------------------------
        palette = QApplication.palette()

        # Dynamically adjust colors based on current theme
        is_dark_theme = palette.color(QPalette.ColorRole.Window).lightness() < 128

        # Enhanced color selection for light theme
        base_color = (
            palette.color(QPalette.ColorRole.Base) if is_dark_theme
            else palette.color(QPalette.ColorRole.Base).lighter(110)
        )

        placeholder_color = (
            palette.color(QPalette.ColorRole.Light) if is_dark_theme
            else palette.color(QPalette.ColorRole.Dark).darker(150)
        )

        # Specific clear button color for light theme
        clear_button_color = (
            palette.color(QPalette.ColorRole.Mid) if is_dark_theme
            else QColor("#707070")  # Darker grey for light theme
        )

        self.search_field.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
                border-radius: 4px;
                background-color: {base_color.name()};
                color: {palette.color(QPalette.ColorRole.Text).name()};
                padding: 4px;
            }}

            QLineEdit::placeholder {{
                color: {placeholder_color.name()};
                font-weight: bold;
            }}

            QLineEdit QToolButton {{
                background-color: {clear_button_color.name()};
                color: {palette.color(QPalette.ColorRole.Text).name()};
                border: none;
                border-radius: 2px;
            }}

            QLineEdit QToolButton:hover {{
                background-color: {palette.color(QPalette.ColorRole.Highlight).name()};
            }}
        """)

        #--------------------------------------------------------------

        # TRANSLATORS: This is the first line of the tooltip of the
        # button with an arrorw down symbol to jump to the next found "search string"
        next_label = _("Find Next")
        # TRANSLATORS: This is the first line of the tooltip of the
        # button with an arrorw up symbol to jump to the previous found "search string"
        prev_label = _("Find Previous")
        # TRANSLATORS: This is the first line of the tooltip of the
        # button with a symbol "[Aa]" to toggle on/off case sensitive search.
        case_label = _("Match Case")
        # TRANSLATORS: This is the first line of the tooltip of the
        # button with an ellipsis symbol "[...]" to toggle "whole word" search.
        word_label = _("Whole Word")
        # TRANSLATORS: This is the first line of the tooltip of the
        # button with an "star" symbol "[*]" to toggle highlight of all searches found.
        mark_label = _("Mark All")
        # TRANSLATORS: This is the string used to label the "Ctrl" key on the keyboard.
        ctrl_label = _("Ctrl")
        # TRANSLATORS: This is the string used to label the "Shift" key on the keyboard.
        shift_label = _("Shift")
        # TRANSLATORS: This is the placeholder string shown within in the search field.
        # The string is also shown as the first line within the tooltip.
        find_label = _("Search...")

        #--------------------------------------------------------------
        search_placeholdertext = f"{find_label}"
        search_tooltip = f"{search_placeholdertext}\n{ctrl_label}+F"
        #--------------------------------------------------------------
        self.search_field.setPlaceholderText(search_placeholdertext)
        self.search_field.setToolTip(search_tooltip)
        self.search_field.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_field)

        """
        BLACK DOWN-POINTING TRIANGLE ▼  U+25bc
        BLACK UP-POINTING TRIANGLE   ▲  U+25b2
        """
        # Create search buttons
        self.next_button = QPushButton("▼")
        self.prev_button = QPushButton("▲")
        self.case_button = QPushButton("[Aa]")
        self.word_button = QPushButton("[...]")
        self.mark_button = QPushButton("[ * ]")

        search_buttons = [
            self.next_button, self.prev_button, self.case_button,
            self.word_button, self.mark_button
        ]

        # Fixed width
        fixed_width = 48
        for button in search_buttons:
            button.setFixedWidth(fixed_width)
            search_layout.addWidget(button)

        fixed_width = 64
        self.next_button.setFixedWidth(fixed_width)
        self.prev_button.setFixedWidth(fixed_width)

        self.next_button.setToolTip(f"{next_label}\n{ctrl_label}+G\n{ctrl_label}+N")
        self.prev_button.setToolTip(f"{prev_label}\n{shift_label}+{ctrl_label}+G\n{ctrl_label}+P")
        self.case_button.setToolTip(f"{case_label}\n{ctrl_label}+I")
        self.word_button.setToolTip(f"{word_label}\n{ctrl_label}+W")
        self.mark_button.setToolTip(f"{mark_label}\n{ctrl_label}+M")

        self.case_button.setCheckable(True)
        self.word_button.setCheckable(True)
        self.mark_button.setCheckable(True)

        #--------------------------------------------------------------
        # standard button box with Close
        #button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        #button_box.rejected.connect(self.reject)  # Close and Esc

        # widgets to layout
        # layout.addWidget(button_box)

        #--------------------------------------------------------------
        # horizontal layout for buttons and search field

        # Button layout (Close button on the right)
        button_layout = QHBoxLayout()
        button_layout.addLayout(search_layout)
        button_layout.addStretch()

        # Close button
        close_text = get_standard_button_text(QMessageBox.StandardButton.Close)
        self.close_button = QPushButton(close_text, self)
        self.close_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))

        # translate close label
        locale = QLocale.system().name()  # system locale
        if not locale.startswith('en'):
            if close_text == "&Close":
                close_text = _t("_Close")
                self.close_button.setText(close_text.replace('_','&'))
        # Set connection
        self.close_button.clicked.connect(self.close_and_exit)
        # Add close button to button layout
        button_layout.addWidget(self.close_button)

        # Add button layout to main layout
        layout.addLayout(button_layout)

        # Set the layout
        self.setLayout(layout)

        # Setup search functionality
        self.setup_search_functionality()

        # Load file if it exists
        if file_path and view_cmd:
            self.load_file(file_path=file_path, view_cmd=view_cmd)
        elif  not file_path and view_cmd:
            self.load_file(view_cmd=view_cmd)
        else:
            # If no file is provided, show a default message
            self.text_area.setPlainText("No file specified. Please provide a file path.")

        # Set initial size and center with scaling
        # self.resize_and_center(default_width, default_height)
        # Restore dialog geometry
        self.restore_dialog_geometry()

    def setup_search_functionality(self):
        # Ctrl+F shortcut to focus search field
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.focus_search_field)

        # Connect buttons
        self.next_button.clicked.connect(self.find_next)
        self.prev_button.clicked.connect(self.find_previous)
        self.case_button.clicked.connect(self.highlight_matches)
        self.word_button.clicked.connect(self.highlight_matches)
        self.mark_button.clicked.connect(self.mark_matches)


        self.search_field.textChanged.connect(self.highlight_matches)
        self.ctrl_g_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        self.ctrl_n_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)

        self.shift_ctrl_g_shortcut = QShortcut(QKeySequence("Shift+Ctrl+G"), self)
        self.ctrl_p_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)

        self.ctrl_i_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        self.ctrl_w_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.ctrl_m_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)

        # shortcut connections
        self.ctrl_g_shortcut.activated.connect(self.find_next)
        self.ctrl_n_shortcut.activated.connect(self.find_next)

        self.shift_ctrl_g_shortcut.activated.connect(self.find_previous)
        self.ctrl_p_shortcut.activated.connect(self.find_previous)

        self.ctrl_i_shortcut.activated.connect(self.toggle_ignore_case)
        self.ctrl_w_shortcut.activated.connect(self.toggle_whole_word)
        self.ctrl_m_shortcut.activated.connect(self.toggle_mark_matches)

    def focus_search_field(self):
        """Set focus to the search field."""
        self.search_field.setFocus()
        self.search_field.selectAll()

    def toggle_mark_matches(self):
        """Toggle all highlighted matches in the text."""
        self.mark_button.setChecked(not self.mark_button.isChecked())
        self.mark_matches()

    def mark_matches(self):
        """Toggle all highlighted matches in the text."""
        self.highlight_all = not self.highlight_all
        if self.highlight_all:
            self.text_area.setExtraSelections(self.extra_selections)
        else:
            self.text_area.setExtraSelections([])

    def highlight_matches(self):
        """Highlight all matches in the text."""
        search_text = self.search_field.text()

        # Clear all highlights and reset cursor if no valid matches
        if not search_text:
            self.extra_selections = []
            self.text_area.setExtraSelections([])

            # Reset cursor to avoid keeping any previous highlight
            cursor = self.text_area.textCursor()
            cursor.clearSelection()
            self.text_area.setTextCursor(cursor)
            return

        # Prepare search flags
        flags = QTextDocument.FindFlag(0)
        if self.case_button.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        if self.word_button.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords

        # Adjust highlight colors based on current theme
        is_dark_theme = QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128

        #highlight_color = "#707070" if is_dark_theme else "#FFFF00"

        highlight_color = "#5C5C0A" if is_dark_theme else "#FFFF00"

        # Get the visible area's first and last positions
        first_visible_pos = self.text_area.viewport().rect().topLeft()
        last_visible_pos = self.text_area.viewport().rect().bottomRight()
        first_visible_cursor = self.text_area.cursorForPosition(first_visible_pos)

        # Find all matches
        self.extra_selections = []
        first_match = None
        cursor = self.text_area.document().find(search_text, 0, flags)

        while not cursor.isNull():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(highlight_color))
            selection.cursor = cursor
            self.extra_selections.append(selection)

            # Store the first match separately
            if first_match is None:
                first_match = QTextCursor(cursor)

            cursor = self.text_area.document().find(search_text, cursor, flags)

        # Set highlights
        if self.highlight_all:
            self.text_area.setExtraSelections(self.extra_selections)

        # If no matches found, ensure no lingering highlights or cursor selection
        if not self.extra_selections:
            cursor = self.text_area.textCursor()
            cursor.clearSelection()
            self.text_area.setTextCursor(cursor)
            return

        # Set cursor to first match, preferring matches in visible area
        if first_match:
            # Try to find first match in visible area
            visible_match = None
            for selection in self.extra_selections:
                if (first_visible_cursor.position() <= selection.cursor.position() <=
                    self.text_area.cursorForPosition(last_visible_pos).position()):
                    visible_match = selection.cursor
                    break

            # Use visible match if found, otherwise use first overall match
            cursor_to_set = visible_match or first_match
            self.text_area.setTextCursor(cursor_to_set)
            self.text_area.ensureCursorVisible()


    def find_next(self):
        """Find and select the next match with improved search behavior."""
        search_text = self.search_field.text()
        if not search_text:
            return

        # Prepare search flags
        flags = QTextDocument.FindFlag(0)
        if self.case_button.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        if self.word_button.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords

        # Current cursor and visible area
        current_cursor = self.text_area.textCursor()
        current_position = current_cursor.position()

        first_visible_pos = self.text_area.viewport().rect().topLeft()
        last_visible_pos = self.text_area.viewport().rect().bottomRight()

        first_visible_cursor = self.text_area.cursorForPosition(first_visible_pos)
        last_visible_cursor = self.text_area.cursorForPosition(last_visible_pos)

        first_visible_cursor = self.text_area.cursorForPosition(first_visible_pos)
        last_visible_cursor = self.text_area.cursorForPosition(last_visible_pos)

        # First, try to find next match in the visible area
        if first_visible_cursor.position() <= current_position <= last_visible_cursor.position():
            search_start_cursor = current_cursor
        else:
            search_start_cursor = first_visible_cursor

        # First, try to find next match in the visible area
        next_in_view = self.text_area.document().find(
            search_text,
            search_start_cursor,
            flags
        )

        # If no match from current cursor, search from the beginning
        if next_in_view.isNull():
            next_in_view = self.text_area.document().find(
                search_text,
                0,
                flags
            )

        # If still no match is found
        if next_in_view.isNull():
            no_match_popup = QMessageBox()
            no_match_popup.setIcon(QMessageBox.Icon.Information)

            # TRANSLATORS: This is the title of the popup window indicating that the
            # search string was not found.
            not_found_title = _('Not Found')

            # TRANSLATORS: This is the text shown within the Not-found  popup window.
            # The token '%(s)s' will be replaced with the search text at runtime.
            not_found_msg = _('"%(s)s" was not found.')
            if not "%(s)s" in not_found_msg:
                not_found_msg = '"%(s)s" was not found.'
            try:
                not_found_msg = not_found_msg % { "s": search_text}
            except:
                not_found_msg = f'"{search_text}" was not found.'

            no_match_popup.setText(not_found_msg)
            no_match_popup.setWindowTitle(not_found_title)
            no_match_popup.setStandardButtons(QMessageBox.StandardButton.Ok)
            no_match_popup.exec()
            return

        # Set the cursor to the found match and ensure it's visible
        self.text_area.setTextCursor(next_in_view)
        self.text_area.ensureCursorVisible()


    def find_previous(self):
        """Find and select the previous match with improved search behavior."""
        search_text = self.search_field.text()
        if not search_text:
            return

        # Prepare search flags backwards
        flags = QTextDocument.FindFlag.FindBackward
        if self.case_button.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        if self.word_button.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords

        # Current cursor and visible area
        current_cursor = self.text_area.textCursor()
        current_position = current_cursor.position()

        first_visible_pos = self.text_area.viewport().rect().topLeft()
        last_visible_pos = self.text_area.viewport().rect().bottomRight()

        first_visible_cursor = self.text_area.cursorForPosition(first_visible_pos)
        last_visible_cursor = self.text_area.cursorForPosition(last_visible_pos)

        first_visible_cursor = self.text_area.cursorForPosition(first_visible_pos)
        last_visible_cursor = self.text_area.cursorForPosition(last_visible_pos)

        # First, try to find previous match in the visible area
        if first_visible_cursor.position() <= current_position <= last_visible_cursor.position():
            search_start_cursor = current_cursor
        else:
            search_start_cursor = last_visible_cursor


        # First, try to find previous match in the visible area
        prev_in_view = self.text_area.document().find(
            search_text,
            search_start_cursor,
            flags
        )

        # If no match from current cursor, search from the end
        if prev_in_view.isNull():
            prev_in_view = self.text_area.document().find(
                search_text,
                self.text_area.document().characterCount(),
                flags
            )

        # If no match is found anywhere
        if prev_in_view.isNull():
            no_match_popup = QMessageBox()
            no_match_popup.setIcon(QMessageBox.Icon.Information)

            # TRANSLATORS: This is the title of the popup window indicating that the
            # search string was not found.
            not_found_title = _('Not Found')

            # TRANSLATORS: This is the text shown within the Not-found  popup window.
            # The token '%(s)s' will be replaced with the search text at runtime.
            not_found_msg = _('"%(s)s" was not found.')
            if not "%(s)s" in not_found_msg:
                not_found_msg = '"%(s)s" was not found.'
            try:
                not_found_msg = not_found_msg % { "s": search_text}
            except:
                not_found_msg = f'"{search_text}" was not found.'

            no_match_popup.setText(not_found_msg)
            no_match_popup.setWindowTitle(not_found_title)
            no_match_popup.setStandardButtons(QMessageBox.StandardButton.Ok)
            no_match_popup.exec()
            return

        # Set the cursor to the found match and ensure it's visible
        self.text_area.setTextCursor(prev_in_view)
        self.text_area.ensureCursorVisible()

    def toggle_ignore_case(self):
        """Toggle match case button and update highlights."""
        self.case_button.setChecked(not self.case_button.isChecked())
        self.highlight_matches()

    def toggle_whole_word(self):
        """Toggle whole word button and update highlights."""
        print(f"Clicked toggle_whole_word")
        self.word_button.setChecked(not self.word_button.isChecked())
        self.highlight_matches()

    def close_and_exit(self):
        self.accept()  # Close the dialog

    def load_file(self, file_path=None, view_cmd=None):
        """
        Load file content into the text area.

        :param file_path: Path to the file to be viewed
        :param view_cmd: Command to view the file (optional)
        """
        content = None
        try:
            # check file exists
            if file_path and not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # with view_cmd given, read the file
            if file_path and view_cmd:
                import subprocess
                content = subprocess.check_output([view_cmd, file_path],
                                                  universal_newlines=True)
            elif not file_path and view_cmd:
                import subprocess
                #content = subprocess.check_output([view_cmd],
                content = subprocess.check_output(view_cmd,
                                                  universal_newlines=True)
            elif file_path and not view_cmd:
                # try to read the file directly
                with open(file_path, 'r') as f:
                    content = f.read()

            # Ensure some content
            if not content:
                content = _("No logs found.")

            self.text_area.setPlainText(content)
        except Exception as e:
            # show error in text area
            error_msg = f"Error loading file: {str(e)}"
            self.text_area.setPlainText(error_msg)
            # message box for the error - not used
            #QMessageBox.warning(self, "File Load Error", error_msg)

    #def resize_and_center(self, default_width, default_height):
    def resize_and_center(self):
        """
        Resize and center the window with scaling.

        :param default_width: Desired window width
        :param default_height: Desired window height
        """

        default_width  = self.default_width
        default_height = self.default_height

        #print(f"Original size: {default_width}x{default_height}")

        # Get the primary screen
        screen = QGuiApplication.primaryScreen()

        # Get available screen geometry (accounting for panels)
        available_geometry = screen.availableGeometry()
        #print(f"Screen available: {available_geometry.width()}x{available_geometry.height()}")

        # Calculate maximum allowed size while preserving aspect ratio
        max_width = int(available_geometry.width() * 0.9)  # 90% of available width
        max_height = int(available_geometry.height() * 0.9)  # 90% of available height
        #print(f"max_width x max_height: {max_width} x {max_height}")

        # Calculate scaling factors
        width_scale = max_width / default_width
        height_scale = max_height / default_height

        # Use the smaller scale to maintain aspect ratio, but not scale up
        scale = min(1.0, min(width_scale, height_scale))

        # Calculate final dimensions
        final_width = int(default_width * scale)
        final_height = int(default_height * scale)

        # Resize the window to exact calculated dimensions
        self.resize(final_width, final_height)

        # Calculate center position
        center_point = available_geometry.center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)

        # Ensure the window is within available screen space
        adjusted_pos = frame_geometry.topLeft()
        adjusted_pos.setX(max(available_geometry.left(),
                               min(adjusted_pos.x(),
                                   available_geometry.right() - frame_geometry.width())))
        adjusted_pos.setY(max(available_geometry.top(),
                               min(adjusted_pos.y(),
                                   available_geometry.bottom() - frame_geometry.height())))

        # Move the window
        self.move(adjusted_pos)

        #print(f"Final size: {final_width}x{final_height}")

    def keyPressEventXXX(self, event):
        """
        Override key press event to close window when Esc is pressed.

        :param event: Key press event
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)


    def done(self, result):
        # Save geometry when dialog is closed
        self.save_dialog_geometry()
        super().done(result)

    def save_dialog_geometry(self):
        """
        Save dialog position and size to QSettings
        """
        section = self.qsettings_section
        self.qsettings.setValue(f'{section}/position', self.pos())
        self.qsettings.setValue(f'{section}/size', self.size())

    def restore_dialog_geometry(self):
        """
        Restore dialog position and size, with fallback to resize_and_center
        """
        # Get the primary screen's available geometry
        screen = QGuiApplication.primaryScreen()
        available_geometry = screen.availableGeometry()

        # Check if valid geometry exists in settings
        section = self.qsettings_section
        saved_pos = self.qsettings .value(f'{section}/position', None)
        saved_size = self.qsettings .value(f'{section}/size', None)

        # Validate saved geometry
        if (saved_pos is not None and saved_size is not None and
            isinstance(saved_pos, QPoint) and isinstance(saved_size, QSize)):

            # Adjust size to fit within available geometry
            adjusted_size = self.adjust_size_to_screen(saved_size, available_geometry)

            # Adjust position to ensure dialog is within screen bounds
            adjusted_pos = self.adjust_position_to_screen(saved_pos, adjusted_size, available_geometry)

            # Set the dialog geometry
            self.resize(adjusted_size)
            self.move(adjusted_pos)

        else:
            # No valid saved geometry - use resize_and_center method
            self.resize_and_center()

    def adjust_size_to_screen(self, size, available_geometry):
        """
        Ensure dialog size does not exceed available screen geometry
        """
        max_width = min(size.width(), available_geometry.width())
        max_height = min(size.height(), available_geometry.height())

        return QSize(
            max(max_width, self.minimumWidth()),
            max(max_height, self.minimumHeight())
        )

    def adjust_position_to_screen(self, pos, size, available_geometry):
        """
        Ensure dialog position is within available screen geometry
        """
        # Adjust x-coordinate
        x = max(
            available_geometry.left(),
            min(pos.x(), available_geometry.right() - size.width())
        )

        # Adjust y-coordinate
        y = max(
            available_geometry.top(),
            min(pos.y(), available_geometry.bottom() - size.height())
        )

        return QPoint(x, y)

    def resize_and_centerXXX(self):
        """
        Resize and center the dialog
        """
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.sizeHint()
        self.resize(size)

        # Center the dialog
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

def get_standard_button_text(button):
    # a temporary message box to access the button text
    msg_box = QMessageBox()
    msg_box.setStandardButtons(button)
    text = msg_box.button(button).text()
    return text


def main():

    window_class='mx-updater'

    app = QApplication(sys.argv)

    app.setApplicationName(window_class)

    # QTranslator instance
    qtranslator = QTranslator()
    locale = QLocale.system().name()  # system locale

    # get path to Qt's translations directory
    translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translation_file_path = f"{translations_path}/qt_{locale}.qm"

    # load translation file
    if qtranslator.load(translation_file_path):
        #print(f"Translation file for locale {locale} found: {translation_file_path}")
        app.installTranslator(qtranslator)
    else:
        # ignore if not found
        pass

    window_title_updater = _("MX Updater")
    if "dpkg_log" in os.path.basename(os.path.abspath(__file__)):

        default_width  = 800
        default_height = 500
        # original title was:
        # "MX Auto-update  --  unattended-upgrades dpkg log viewer"
        # so we keep translations, for now
        window_title = _("MX Auto-update  --  unattended-upgrades dpkg log viewer")

        log_view_title = _('Auto-update dpkg log(s)')
        window_title = f"[ {window_title_updater} ] -- {log_view_title}"

        view_cmd = [
            '/usr/bin/pkexec',
            '/usr/libexec/mx-updater/updater_auto_upgrades_dpkg_log_view'
            ]

    else:

        default_width  = 900
        default_height = 600
        # original title was:
        # "MX Auto-update  --  unattended-upgrades log viewer"
        window_title = _("MX Auto-update  --  unattended-upgrades log viewer")

        log_view_title = _('Auto-update log(s)')
        window_title = f"[ {window_title_updater} ] -- {log_view_title}"

        view_cmd = [
            '/usr/bin/pkexec',
            '/usr/libexec/mx-updater/updater_auto_upgrades_log_view'
            ]

    viewer = LogViewer(
        view_cmd=view_cmd,
        icon_path='/usr/share/icons/hicolor/scalable/mx-updater.svg',
        window_class=window_class,
        window_title=window_title,
        default_width=default_width,
        default_height=default_height
    )
    viewer.exec()



if __name__ == '__main__':
    main()




