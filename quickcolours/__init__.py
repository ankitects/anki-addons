# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

from aqt import mw

config = mw.addonManager.getConfig(__name__)

from anki.hooks import addHook

def updateColour(editor, colour):
    editor.fcolour = colour
    editor.onColourChanged()
    editor._wrapWithColour(editor.fcolour)

def onSetupShortcuts(cuts, editor):
    # add colours
    for code, key in config['keys']:
        cuts.append((key, lambda c=code: updateColour(editor, c)))

addHook("setupEditorShortcuts", onSetupShortcuts)
