#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from subprocess import Popen, run

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QMessageBox, QPushButton,
    QTextBrowser, QTextEdit, QVBoxLayout,
)
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QColor, QDesktopServices, QFontDatabase, QPalette, QIcon, QPixmap

_APP_ICON = QIcon('/usr/share/icons/hicolor/scalable/apps/updater-mx.svg')

BUILD_VERSION='@VERSION@'

try:
    MX_UPDATER_PATH = os.environ["MX_UPDATER_PATH"]
except KeyError:
    print("MX_UPDATER_PATH missing from environment, exiting")
    sys.exit(1)

sys.path.insert(0, MX_UPDATER_PATH)

from updater_translator import Translator

try:
    from version.version import Version
except ImportError:
    class Version:
        version = BUILD_VERSION  # Fallback version


# localization
import gettext
LOCALE_DOMAIN = 'mx-updater'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(LOCALE_DOMAIN, LOCALE_DIR)
gettext.textdomain(LOCALE_DOMAIN)
_ = gettext.gettext

translator = Translator(textdomain=LOCALE_DOMAIN)


class UpdaterAbout():

    def __init__(self):
        os.environ["QT_LOGGING_RULES"] = "qt.qpa.xcb.warning=false"
        self.version = Version.version
        print(f"[About] Version: {self.version}")



    def About(self, aboutBox):
        self.aboutBox = aboutBox


        updater_name         = _("MX Updater")
        about_updater        =  _("Tray applet to notify of system and application updates")
        about_updater_title  = _("About MX Updater")
        about_copyright      = 'Copyright (c) MX Linux'
        about_window_icon    = '/usr/share/icons/hicolor/scalable/apps/updater-mx.svg'

        about_box_icon       = '/usr/share/icons/hicolor/96x96/apps/mx-updater.png'
        about_box_url        = 'https://mxlinux.org'
        about_copyright      = 'Copyright (c) MX Linux'
        about_window_icon    = '/usr/share/icons/hicolor/scalable/apps/updater-mx.svg'
        changelog_file       = '/usr/share/doc/mx-updater/changelog.gz'
        license_file         = '/usr/share/doc/mx-updater/license.html'
        
        Close                = _("Close")
        License              = _("License")
        Changelog            = _("Changelog")
    
        license_title =  updater_name + ' - ' + License
        changelog_title = updater_name + ' - ' + Changelog
        license_title        = updater_name + ' - ' + License

        Help             = _("Help")
        help_file        = '/usr/share/doc/mx-updater/help.html'
        help_title       = updater_name + ' - ' + Help

        Changelog_Button = Changelog
        Close_Button     = Close
        License_Button   = License
        Help_Button      = Help

        cmd = "dpkg-query -f ${Version} -W mx-updater".split()
        pkg_version = run(cmd, capture_output=True, text=True).stdout.strip()
        updater_version = pkg_version if pkg_version else BUILD_VERSION
        updater_version = self.version

        # link colors for dark:
        # link_color = "#58a6ff"  # soft blue
        # link_color = "#4CAF50"  # muted green-blue
        # link_color = "#64B5F6"  # light blue

        # link colors for dark:
        # link_color = "#58a6ff"  # soft blue
        # link_color = "#4CAF50"  # muted green-blue
        # link_color = "#64B5F6"  # light blue

        
        theme_link_colors = {
            #'light': '#1E88E5',  # deep blue for light theme
            'light': '#0d47a1',   # deeper navy blue for light theme
            'dark': '#58a6ff',    # soft blue for dark theme
            #'dark': '#4CAF50',    # muted green-blue
        }
    
        link_color = theme_link_colors['dark'] if self.is_dark_theme() else theme_link_colors['light']

        if self.is_dark_theme():
            link_style = f' style="color: {link_color};"'
            #print(f"Link color for dark theme is {link_color}")
        else:
            link_style = "" # use system defaults
            #print(f"Link color for light theme is {link_color}")
            
        
        aboutText = f"""
        <p align=center><b><h2>{updater_name}</h2></b></p>
        <p align=center>Version: {updater_version}</p>
        <p align=center><h3>{about_updater}</h3></p>
        <p align=center><a href="{about_box_url}" {link_style}>{about_box_url}</a>
        <br></p><p align=center>{about_copyright}<br /><br/></p>
        """
        #print(f"aboutText:'{aboutText}'")

        icon_pixmap = QtGui.QPixmap(about_box_icon)
        aboutBox.setIconPixmap(icon_pixmap)

        aboutBox.setWindowTitle(about_updater_title)
        aboutBox.setWindowIcon(QtGui.QIcon(about_window_icon))
        aboutBox.setText(aboutText)
        """
        class ButtonRole(enum.Enum)
        
         |  AcceptRole = <ButtonRole.AcceptRole: 0>
         |  
         |  ActionRole = <ButtonRole.ActionRole: 3>
         |  
         |  ApplyRole = <ButtonRole.ApplyRole: 8>
         |  
         |  DestructiveRole = <ButtonRole.DestructiveRole: 2>
         |  
         |  HelpRole = <ButtonRole.HelpRole: 4>
         |  
         |  InvalidRole = <ButtonRole.InvalidRole: -1>
         |  
         |  NoRole = <ButtonRole.NoRole: 6>
         |  
         |  RejectRole = <ButtonRole.RejectRole: 1>
         |  
         |  ResetRole = <ButtonRole.ResetRole: 7>
         |  
         |  YesRole = <ButtonRole.YesRole: 5>
        
        """
        changelogButton = aboutBox.addButton( (Changelog_Button), QMessageBox.ButtonRole.ActionRole)
        licenseButton   = aboutBox.addButton( (License_Button)  , QMessageBox.ButtonRole.ActionRole)
        helpButton      = aboutBox.addButton( (Help_Button)     , QMessageBox.ButtonRole.HelpRole)
        closeButton     = aboutBox.addButton( (Close_Button)    , QMessageBox.ButtonRole.RejectRole)
        aboutBox.setDefaultButton(closeButton)
        aboutBox.setEscapeButton(closeButton)

        while True:
            reply = aboutBox.exec()
            if aboutBox.clickedButton() == closeButton:
                sys.exit(reply)

            if aboutBox.clickedButton() == licenseButton:
                _show_html_doc(license_title, license_file)

            if aboutBox.clickedButton() == helpButton:
                Popen(['/usr/libexec/mx-updater/updater_action_run', 'updater_help'])

            if aboutBox.clickedButton() == changelogButton:
                cmd = ['/usr/bin/python3', '/usr/libexec/mx-updater/updater-changelog.py']
                r = run(cmd, capture_output=True, text=True)
                #Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                #aboutBox.done()
                #sys.exit(0)

    def displayAbout(self):
        app = QApplication(sys.argv)
        app.setApplicationName("updater-mx")

        if is_dark_theme():
            IS_DARK_THEME = True
            #print(f"dark theme")
        else:
            IS_DARK_THEME = False
            #print(f"light theme")
        
        aboutBox = QMessageBox()
        about = UpdaterAbout()
        about.About(aboutBox)
        aboutBox.show()
        sys.exit(app.exec())

    def is_dark_theme(self):
        return QApplication.palette().color(QtGui.QPalette.ColorRole.Window).lightness() < 128


def is_dark_theme():
    return QApplication.palette().color(QtGui.QPalette.ColorRole.Window).lightness() < 128


def debugging():
    """
    simple debugging helper
    """
    import os
    global debug_apt_notifier
    try:
        debug_apt_notifier
    except:
        try:
            debug_apt_notifier = os.getenv('MX_UPDATER_DEBUG')
        except:
            debug_apt_notifier = False

    return debug_apt_notifier

def debug_p(text=''):
    """
    simple debug print helper -  msg get printed to stderr
    """
    if debugging():
        print("Debug: " + text, file = sys.stderr)

def _get_close_text():
    return translator.translate("&Close")


def _show_plain_text_doc(title, path):
    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(QtCore.Qt.WindowType.Window)
    dialog.setWindowIcon(_APP_ICON)
    screen = QApplication.primaryScreen().availableGeometry()
    dialog.resize(int(screen.width() * 0.6), int(screen.height() * 0.65))

    text_edit = QTextEdit(dialog)
    text_edit.setReadOnly(True)
    text_edit.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            text_edit.setPlainText(f.read())
    except OSError:
        text_edit.setPlainText(_("Could not load %s") % path)

    btn_close = QPushButton(_get_close_text())
    btn_close.clicked.connect(dialog.close)

    btn_row = QHBoxLayout()
    btn_row.addStretch()
    btn_row.addWidget(btn_close)

    layout = QVBoxLayout(dialog)
    layout.addWidget(text_edit)
    layout.addLayout(btn_row)
    dialog.exec()


def _on_doc_link_clicked(url):
    if url.isLocalFile():
        _show_plain_text_doc(url.toLocalFile(), url.toLocalFile())
    else:
        QDesktopServices.openUrl(url)


def _apply_html_theme(browser, dark, html_path=None):
    if dark:
        bg, fg, link = '#1e1e1e', '#f0f0f0', '#58a6ff'
    else:
        bg, fg, link = '#ffffff', '#000000', '#0d47a1'
    p = browser.palette()
    p.setColor(QPalette.ColorRole.Base, QColor(bg))
    p.setColor(QPalette.ColorRole.Text, QColor(fg))
    browser.setPalette(p)
    browser.document().setDefaultStyleSheet(
        f"body {{ color: {fg}; background-color: {bg}; }}"
        f" a {{ color: {link}; }}"
    )
    if html_path:
        try:
            with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
                html = f.read()
            if dark:
                html = html.replace('-light.png"', '-dark.png"')
            browser.document().setBaseUrl(QUrl.fromLocalFile(html_path))
            browser.setHtml(html)
        except OSError:
            pass
    elif browser.source().isValid():
        browser.reload()


def _show_html_doc(title, html_path):
    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(QtCore.Qt.WindowType.Window)
    dialog.setWindowIcon(_APP_ICON)
    screen = QApplication.primaryScreen().availableGeometry()
    dialog.resize(int(screen.width() * 0.6), int(screen.height() * 0.65))

    browser = QTextBrowser(dialog)
    browser.setOpenLinks(False)
    browser.anchorClicked.connect(_on_doc_link_clicked)

    viewer_dark = [is_dark_theme()]
    _apply_html_theme(browser, viewer_dark[0])

    if os.path.exists(html_path):
        browser.setSource(QUrl.fromLocalFile(html_path))
    else:
        browser.setText(_("Could not load %s") % html_path)

    btn_toggle = QPushButton("\u2600" if viewer_dark[0] else "\u263e")
    btn_close  = QPushButton(_get_close_text())
    btn_close.clicked.connect(dialog.close)

    def toggle_theme():
        viewer_dark[0] = not viewer_dark[0]
        _apply_html_theme(browser, viewer_dark[0])
        btn_toggle.setText("\u2600" if viewer_dark[0] else "\u263e")

    btn_toggle.clicked.connect(toggle_theme)

    btn_row = QHBoxLayout()
    btn_row.addWidget(btn_toggle)
    btn_row.addStretch()
    btn_row.addWidget(btn_close)

    layout = QVBoxLayout(dialog)
    layout.addWidget(browser)
    layout.addLayout(btn_row)
    dialog.exec()


def main():

    app = QApplication(sys.argv)
    app.setApplicationName("updater-mx")
    about = UpdaterAbout()

    
    if about.is_dark_theme():
        IS_DARK_THEME = True
        #print(f"dark theme")
    else:
        IS_DARK_THEME = False
        #print(f"light theme")
        
    aboutBox = QMessageBox()
    about.About(aboutBox)
    aboutBox.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
