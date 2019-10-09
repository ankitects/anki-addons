# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Bulk update of readings.
#

from aqt.qt import *
from anki.hooks import addHook
from .reading import regenerateReading
from .notetypes import isJapaneseNoteType
from aqt import mw

# Bulk updates
##########################################################################

def regenerateReadings(nids):
    mw.checkpoint("Bulk-add Readings")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)
        if not isJapaneseNoteType(note.model()['name']):
            continue
        fields = mw.col.models.fieldNames(note.model())
        for src in fields:
            regenerateReading(note, src)
        note.flush()
    mw.progress.finish()
    mw.reset()

def setupMenu(browser):
    a = QAction("Bulk-add Readings", browser)
    a.triggered.connect(lambda: onRegenerate(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

def onRegenerate(browser):
    regenerateReadings(browser.selectedNotes())

addHook("browser.setupMenus", setupMenu)
