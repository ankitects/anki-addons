# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Emulate some Anki 1.2 shortcuts.

from aqt import mw
from aqt.qt import *

mw.otherDeck = QShortcut(QKeySequence("Ctrl+w"), mw)
mw.otherAdd = QShortcut(QKeySequence("Ctrl+d"), mw)
mw.otherBrowse = QShortcut(QKeySequence("Ctrl+f"), mw)

mw.connect(
    mw.otherDeck, SIGNAL("activated()"), lambda: mw.moveToState("deckBrowser"))
mw.connect(
    mw.otherAdd, SIGNAL("activated()"), lambda: mw.onAddCard())
mw.connect(
    mw.otherBrowse, SIGNAL("activated()"), lambda: mw.onBrowse())
