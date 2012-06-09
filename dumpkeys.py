# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from anki.hooks import wrap
import sys
from aqt.editor import EditorWebView
from aqt.qt import *

def repl(self, evt, _old):
    if evt.key() == Qt.Key_Delete:
        evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        QCoreApplication.postEvent(self, evt)
        return
    _old(self, evt)

EditorWebView.keyPressEvent = wrap(EditorWebView.keyPressEvent, repl, "around")
