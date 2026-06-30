#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QPushButton,
    QTextBrowser, QTextEdit, QVBoxLayout,
)
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QColor, QDesktopServices, QFontDatabase, QIcon, QPalette

_APP_ICON = QIcon('/usr/share/icons/hicolor/scalable/apps/updater-mx.svg')

_MX_UPDATER_PATH = "/usr/libexec/mx-updater"
if _MX_UPDATER_PATH not in sys.path:
    sys.path.insert(0, _MX_UPDATER_PATH)

from updater_translator import Translator

import gettext
LOCALE_DOMAIN = 'mx-updater'
LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(LOCALE_DOMAIN, LOCALE_DIR)
gettext.textdomain(LOCALE_DOMAIN)
_ = gettext.gettext

translator = Translator(textdomain=LOCALE_DOMAIN)


def is_dark_theme():
    return QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128


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


def _apply_html_theme(browser, dark, html_path=None, img_prefix='img/'):
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
            if img_prefix != 'img/':
                html = html.replace('src="img/', f'src="{img_prefix}')
            if dark:
                base_dir = os.path.dirname(os.path.abspath(html_path))
                def _swap_dark(m):
                    src, ext = m.group(1), m.group(2)
                    if os.path.exists(os.path.join(base_dir, f'{src}-dark.{ext}')):
                        return m.group(0).replace(f'{src}.{ext}"', f'{src}-dark.{ext}"')
                    return m.group(0)
                html = re.sub(
                    r'class="screenshot"[^>]*?src="([^"]+?)\.(png|jpg)"',
                    _swap_dark, html
                )
            browser.document().setBaseUrl(QUrl.fromLocalFile(html_path))
            browser.setHtml(html)
        except OSError:
            pass
    elif browser.source().isValid():
        browser.reload()


def show_help():
    lang = QtCore.QLocale.system().name().split('_')[0]
    lang_help = f'/usr/share/doc/mx-updater/help_{lang}.html'
    if os.path.exists(lang_help):
        help_path = lang_help
        img_prefix = 'img/'
    else:
        help_path = '/usr/share/doc/mx-updater/help.html'
        lang_img_dir = f'/usr/share/doc/mx-updater/img/{lang}'
        img_prefix = f'img/{lang}/' if os.path.isdir(lang_img_dir) else 'img/'

    title = _("MX Updater Help")

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

    if os.path.exists(help_path):
        _apply_html_theme(browser, viewer_dark[0], html_path=help_path, img_prefix=img_prefix)
    else:
        browser.setText(_("Could not load %s") % help_path)

    btn_toggle = QPushButton("\u2600" if viewer_dark[0] else "\u263e")
    btn_close  = QPushButton(_get_close_text())
    btn_close.clicked.connect(dialog.close)

    def toggle_theme():
        viewer_dark[0] = not viewer_dark[0]
        _apply_html_theme(browser, viewer_dark[0], html_path=help_path, img_prefix=img_prefix)
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
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.xcb.warning=false"
    show_help()
    sys.exit(0)


if __name__ == '__main__':
    main()
