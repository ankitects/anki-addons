# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

def fix():
    mw.col.modSchema()
    mw.col.db.execute(
        "update cards set odue = 0 where (type = 1 or queue = 2) and not odid")
    showInfo("Fixed. If you get errors after running this, please let me know.")

a = QAction(mw)
a.setText("Fix Assertion Error")
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), fix)
