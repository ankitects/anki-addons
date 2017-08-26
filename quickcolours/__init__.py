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

from anki.hooks import addHook

def updateColour(editor, colour):
    editor.fcolour = colour
    editor.onColourChanged()
    editor._wrapWithColour(editor.fcolour)

def onSetupShortcuts(cuts, editor):
    # remove the default f8 shortcut
    idx = None
    for n, (key, fn) in enumerate(cuts):
        if key == "F8":
            idx = n
            break
    if idx is not None:
        del cuts[idx]

    # add colours
    for code, key in colours:
        cuts.append((key, lambda c=code: updateColour(editor, c)))

addHook("setupEditorShortcuts", onSetupShortcuts)
