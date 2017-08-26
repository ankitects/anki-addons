# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Edit this to customize colours and shortcuts. By default, F8 will set the
# selection to red, and F9 to blue. You can use either simple colour names or
# HTML colour codes.

colours = [
    ("red", "F8"),
    ("#00f", "F9"),
]

from aqt import mw
from aqt.qt import *
from anki.hooks import addHook

def updateColour(editor, colour):
    editor.web.eval("saveSel();")
    editor.fcolour = colour
    editor.onColourChanged()
    editor._wrapWithColour(editor.fcolour)

def onSetupButtons(editor):
    # add colours
    for code, key in colours:
        s = QShortcut(QKeySequence(key), editor.parentWindow)
        s.connect(s, SIGNAL("activated()"),
                  lambda c=code: updateColour(editor, c))
    # remove the default f8 shortcut
    editor._buttons['change_colour'].setShortcut(QKeySequence())

addHook("setupEditorButtons", onSetupButtons)
