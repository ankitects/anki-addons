# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# this plugin will reschedule the cards in the revision queue over a period of
# days. it attempts to add the delay to the interval so cards answered later
# that are remembered will get a boost, but there's no guarantee it won't
# mess up your statistics or cause other problems

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from subprocess import Popen
from ankiqt import mw
import sys
from anki.cards import cardsTable
import time

def postpone():
    i = QInputDialog.getInteger(mw, _("Postpone"),
                                _("Number of days to spread repetitions over:"),
                                2, 1)
    if i[1] and i[0] > 1:
        mw.deck.s.flush()
        d = mw.deck
        q = d.s.all(
            d.cardLimit(
            "revActive", "revInactive", """
select c.id, interval, combinedDue from cards c where
type = 1 and combinedDue < :lim order by priority desc, combinedDue
"""), lim=d.dueCutoff)
        size = len(q) / i[0] + 1
        days = 0
        count = -1
        cards = []
        now = time.time()
        for item in q:
            count += 1
            if count == size:
                count = 0
                days += 1
            seconds = 86400 * days
            # determine the current delay
            delay = now - item.combinedDue
            cards.append({'id': item[0],
                          'interval': item[1] + days + (delay / 86400.0),
                          'due': now + seconds})
        # apply changes
        d.s.execute("""
update cards set
interval = :interval,
combinedDue = :due,
isDue = 0
where id = :id""", cards)
        # rebuild
        d.flushMod()
        mw.reset()

def init():
    q = QAction(mw)
    q.setText("Postpone")
    mw.mainWin.menuTools.addAction(q)
    mw.connect(q, SIGNAL("triggered()"), postpone)

mw.addHook("init", init)
mw.registerPlugin("Postpone Reviews", 6)
