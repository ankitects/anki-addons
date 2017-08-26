# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Marks the previous answer button like '*Again*'
# Sponsored by Alan Clontz.
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw, ui
from anki.hooks import wrap
import os,re

def showLast():
    lastEase = mw.deck.s.scalar("""
select ease from reviewHistory where cardId = :id
order by time desc limit 1""", id=mw.currentCard.id)
    # make sure ease1 is reset
    mw.mainWin.easeButton1.setText(_("Again"))
    if lastEase:
        but = getattr(mw.mainWin, "easeButton%d" % lastEase)
        but.setText("*%s*" % but.text())

mw.showEaseButtons = wrap(mw.showEaseButtons, showLast)
