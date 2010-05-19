# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This simple plugin shows you the hardest cards in the defined time (default
# last 30 minutes).
#

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ankiqt import mw
import time

# last 30 minutes
MINUTES = 30
# limit to maximum of 10 cards
MAXCARDS = 10

def onHardest():
    data = mw.deck.s.all("""
select question, cnt from (
select cardId, count() as cnt from reviewHistory where time > :t
and ease = 1 group by cardId), cards where cardId = id order by cnt desc limit :d""",
                         t=time.time() - 60*MINUTES, d=MAXCARDS)

    s = "<h1>Hardest Cards</h1><table>"
    for (q, cnt) in data:
        s += "<tr><td>%s</td><td>failed %d times</td></tr>" % (q, cnt)
    # show dialog
    diag = QDialog(mw.app.activeWindow())
    diag.setWindowTitle("Anki")
    layout = QVBoxLayout(diag)
    diag.setLayout(layout)
    text = QTextEdit()
    text.setReadOnly(True)
    text.setHtml(s)
    layout.addWidget(text)
    box = QDialogButtonBox(QDialogButtonBox.Close)
    layout.addWidget(box)
    mw.connect(box, SIGNAL("rejected()"), diag, SLOT("reject()"))
    diag.setMinimumHeight(400)
    diag.setMinimumWidth(500)
    diag.exec_()

a = QAction(mw)
a.setText("Show Hardest Cards")
mw.mainWin.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), onHardest)
