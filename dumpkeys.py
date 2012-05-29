# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from anki.hooks import wrap
import sys
from aqt.editor import EditorWebView

def repl(self, evt):
    sys.stderr.write(str(evt.key()))

EditorWebView.keyPressEvent = wrap(EditorWebView.keyPressEvent, repl)
