# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

from typing import Callable

from aqt import gui_hooks, mw
from aqt.editor import Editor

config = mw.addonManager.getConfig(__name__)


def updateColour(editor: Editor, colour: str) -> None:
    editor.fcolour = colour
    editor.onColourChanged()
    editor._wrapWithColour(editor.fcolour)


def onSetupShortcuts(cuts: list[tuple], editor: Editor) -> None:
    # add colours
    for code, key in config["keys"]:
        cuts.append((key, lambda c=code: updateColour(editor, c)))


gui_hooks.editor_did_init_shortcuts.append(onSetupShortcuts)
