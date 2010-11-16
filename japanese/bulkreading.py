# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Bulk update of readings.
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
from japanese.reading import mecab, USE_MECAB
from anki.facts import Fact
from ankiqt import mw

srcFields = ('Expression',) # works with n pairs
dstFields = ('Reading',)

# Bulk updates
##########################################################################

def regenerateReadings(factIds):
    mw.deck.startProgress(max=len(factIds))
    for c, id in enumerate(factIds):
        mw.deck.updateProgress(label="Generating readings...",
                            value=c)
        fact = mw.deck.s.query(Fact).get(id)
        try:
            for i in range(len(srcFields)):
                fact[dstFields[i]] = mecab.reading(fact[srcFields[i]])
        except:
            pass
    try:
        mw.deck.refreshSession()
    except:
        # old style
        mw.deck.refresh()
    mw.deck.updateCardQACacheFromIds(factIds, type="facts")
    mw.deck.finishProgress()

def setupMenu(editor):
    a = QAction("Regenerate Readings", editor)
    editor.connect(a, SIGNAL("triggered()"), lambda e=editor: onRegenerate(e))
    editor.dialog.menuActions.addSeparator()
    editor.dialog.menuActions.addAction(a)

def onRegenerate(editor):
    n = "Regenerate Readings"
    editor.parent.setProgressParent(editor)
    editor.deck.setUndoStart(n)
    regenerateReadings(editor.selectedFacts())
    editor.deck.setUndoEnd(n)
    editor.parent.setProgressParent(None)
    editor.updateSearch()

if USE_MECAB:
    addHook("editor.setupMenus", setupMenu)
