# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
#            Glutanimate <github.com/glutanimate>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin keeps Anki on top of other windows.

from anki.hooks import wrap

from aqt import dialogs
from aqt import mw, addcards, editcurrent, browser
from aqt.qt import *

def alwaysOnTop():
    mw._onTop = not mw._onTop
    windows = [mw]
    for dclass, instance in dialogs._dialogs.values():
        if instance:
            windows.append(instance)
    for window in windows:
        windowFlags = window.windowFlags()
        windowFlags ^= Qt.WindowStaysOnTopHint
        window.setWindowFlags(windowFlags)
        window.show()

def onWindowInit(self, *args, **kwargs):
    if mw._onTop:
        windowFlags = self.windowFlags() | Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        self.show()
    
mw._onTop = False
action = QAction("Always on top", mw)
action.setCheckable(True)
mw.connect(action, SIGNAL("triggered()"), alwaysOnTop)
mw.form.menuTools.addAction(action)

addcards.AddCards.__init__ = wrap(addcards.AddCards.__init__, onWindowInit, "after")
editcurrent.EditCurrent.__init__ = wrap(editcurrent.EditCurrent.__init__, onWindowInit, "after")
browser.Browser.__init__ = wrap(browser.Browser.__init__, onWindowInit, "after")
