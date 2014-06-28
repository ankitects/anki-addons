# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Bulk update of readings.
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
from japanese.reading import mecab, srcFields, dstFields
from notetypes import isActiveNoteType
from aqt import mw

# Bulk updates
##########################################################################

def regenerateReadings(nids):
    global mecab
    mw.checkpoint("Bulk-add Readings")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)
        # Amend notetypes.py to add your note types
        _noteName = note.model()['name'].lower()
        if not isActiveNoteType(_noteName):
            continue

        src = None
        for field in srcFields:
            if field in note:
                src = field
                break
        if not src:
            # no src field
            continue
        # dst is the destination field for the Readings
        dst = None
        for field in dstFields:
            if field in note:
                dst = field
                break
        if not dst:
            # no dst field
            continue
        if note[dst]:
            # already contains data, skip
            continue
        srcTxt = mw.col.media.strip(note[src])
        if not srcTxt.strip():
            continue
        try:
            note[dst] = mecab.reading(srcTxt)
        except Exception, e:
            mecab = None
            raise
        note.flush()
    mw.progress.finish()
    mw.reset()

def setupMenu(browser):
    a = QAction("Bulk-add Readings", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onRegenerate(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

def onRegenerate(browser):
    regenerateReadings(browser.selectedNotes())

addHook("browser.setupMenus", setupMenu)
