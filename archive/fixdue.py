# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Fix floast in the DB which have been mistakenly turned into strings due to
# string concatenation.
#

from ankiqt import mw
from ankiqt import ui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def onFix():
    for col in ("created", "due", "combinedDue", "spaceUntil"):
        mw.deck.s.execute(
            "update cards set %s = cast (%s as float)" % (
            col, col))
    mw.deck.setModified()
    ui.utils.showInfo("Fixed.")

act = QAction(mw)
act.setText("Fix Floats")
mw.connect(act, SIGNAL("triggered()"), onFix)

mw.mainWin.menuTools.addAction(act)
