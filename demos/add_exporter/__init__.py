"""
An example of adding an exporter to export page.
"""

from pathlib import Path

from aqt import gui_hooks
from aqt.webview import AnkiWebView


def setup(webview: AnkiWebView) -> None:
    webview.eval(Path(__file__).with_name("init.js").read_text(encoding="utf8"))


gui_hooks.webview_did_inject_style_into_page.append(setup)
