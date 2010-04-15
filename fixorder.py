# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Fix the ordering of cards so that different templates are shown one after
# another if the minimum spacing is 0. You only need this if a previous bug in
# Anki (now fixed) didn't set the order right.
#

from ankiqt import mw
from ankiqt import ui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def onFix():
    mw.deck.s.execute("""
update cards set created = (select created from facts
where cards.factId = facts.id) + cards.ordinal * 0.000001""")
    mw.deck.s.execute("""
update cards set due = created, combinedDue =
max(created,spaceUntil) where type = 2""")
    ui.utils.showInfo("Ordering fixed.")

act = QAction(mw)
act.setText("Fix Ordering")
mw.connect(act, SIGNAL("triggered()"), onFix)

mw.mainWin.menuTools.addAction(act)
