# -*- coding: utf-8 -*-
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt.qt import *
from aqt.webview import AnkiWebView


def _runJavaScriptSync(page, js, timeout=500):
    result = None
    eventLoop = QEventLoop()
    called = False

    def callback(val):
        nonlocal result, called
        result = val
        called = True
        eventLoop.quit()

    page.runJavaScript(js, callback)

    if not called:
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(eventLoop.quit)
        timer.start(timeout)
        eventLoop.exec_()

    if not called:
        print("runJavaScriptSync() timed out")
    return result


def event(self, evt):
    if evt.type() == QEvent.ShortcutOverride:
        # alt-gr bug workaround
        exceptChars = (str(num) for num in range(1, 10))
        if evt.text() not in exceptChars:
            js = """
var e=document.activeElement;
(e.tagName === "DIV" && e.contentEditable) ||
["INPUT", "TEXTAREA"].indexOf(document.activeElement.tagName) !== -1"""
            if _runJavaScriptSync(self.page(), js, timeout=100):
                evt.accept()
                return True
    return QWebEngineView.event(self, evt)


AnkiWebView.event = event  # type: ignore
