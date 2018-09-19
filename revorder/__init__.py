# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Force review cards to be displayed in a particular order, at a roughly 10x
# decrease in performance.
#
# ivl desc: sort from largest interval first
# ivl asc: sort from smallest interval first
#
# This only changes the behaviour of the regular scheduler in Anki 2.1.
# If you are using the experimental scheduler, a better option is to use
# a filtered deck to change the review order, as this is faster and works
# on mobile as well.

order = "ivl desc"

from anki.sched import Scheduler

import random
import anki
from anki.utils import ids2str
from anki.schedv2 import Scheduler

def _fillRev(self):
    if self._revQueue:
        return True
    if not self.revCount:
        return False
    while self._revDids:
        did = self._revDids[0]
        lim = min(self.queueLimit, self._deckRevLimit(did))
        if lim:
            sql = """
select id from cards where
did = ? and queue = 2 and due <= ?"""
            sql2 = " limit ?"
# limit ?"""
            if self.col.decks.get(did)['dyn']:
                self._revQueue = self.col.db.list(
                    sql+sql2, did, self.today, lim)
                self._revQueue.reverse()
            else:
                self._revQueue = self.col.db.list(
                    sql+" order by "+order+sql2, did, self.today, lim)
                self._revQueue.reverse()
            if self._revQueue:
                # is the current did empty?
                if len(self._revQueue) < lim:
                    self._revDids.pop(0)
                return True
        # nothing left in the deck; move to next
        self._revDids.pop(0)

anki.sched.Scheduler._fillRev = _fillRev

def _v2_fillRev(self):
    if self._revQueue:
        return True
    if not self.revCount:
        return False

    lim = min(self.queueLimit, self._currentRevLimit())
    if lim:
        self._revQueue = self.col.db.list("""
select id from cards where
did in %s and queue = 2 and due <= ?
order by due
limit ?""" % (ids2str(self.col.decks.active())),
                self.today, lim)

        if self._revQueue:
            if self.col.decks.get(self.col.decks.selected(), default=False)['dyn']:
                # dynamic decks need due order preserved
                self._revQueue.reverse()
            else:
                # fixme: as soon as a card is answered, this is no longer consistent
                r = random.Random()
                r.seed(self.today)
                r.shuffle(self._revQueue)
            return True

    if self.revCount:
        # if we didn't get a card but the count is non-zero,
        # we need to check again for any cards that were
        # removed from the queue but not buried
        self._resetRev()
        return self._fillRev()

anki.schedv2.Scheduler._fillRev = _v2_fillRev
