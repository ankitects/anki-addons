# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin replaces the standard 'delete card' option in the edit menu with
# one that marks the fact first. This is useful for finding facts missing
# certain cards later.
#
# If you have already deleted cards and want them to be included:
#
# 1. Open the editor, select all of your cards
# 2. Choose Actions>Generate Cards, and select the card type you deleted
# 3. Sort the deck by created date, and find all the newly added cards.
# 4. Select them, choose Actions>Add Tag, and add the tag "MarkDelete"
# 5. Remove the cards again.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw
from anki.utils import canonifyTags

def markAndDelete():
    undo = _("MarkDelete")
    mw.deck.setUndoStart(undo)
    mw.currentCard.fact.tags = canonifyTags(mw.currentCard.fact.tags +
                                            "," + "MarkDelete")
    mw.currentCard.fact.setModified()
    mw.deck.updateFactTags([mw.currentCard.fact.id])
    mw.deck.deleteCard(mw.currentCard.id)
    mw.reset()
    mw.deck.setUndoEnd(undo)

act = QAction(mw)
act.setText("Mark and &Delete")
icon = QIcon()
icon.addPixmap(QPixmap(":/icons/editdelete.png"))
act.setIcon(icon)
mw.connect(act, SIGNAL("triggered()"),
           markAndDelete)

old = mw.mainWin.actionDelete
act.setEnabled(old.isEnabled())

mw.mainWin.menuEdit.removeAction(mw.mainWin.actionDelete)
mw.mainWin.menuEdit.addAction(act)

# make sure it's enabled/disabled
mw.mainWin.actionDelete = act

mw.registerPlugin("Mark and Delete", 8)
