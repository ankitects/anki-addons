# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Bulk update of readings.
#

from aqt.qt import *
from anki.hooks import addHook
from .reading import mecab, srcFields, dstFields
from .notetypes import isJapaneseNoteType
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
        if not isJapaneseNoteType(_noteName):
            continue
        for (srcField, dstField) in zip(srcFields, dstFields):
            if srcField in note and dstField in note and not note[dstField]:
              srcTxt = mw.col.media.strip(note[srcField])
              if not srcTxt.strip():
                  continue
              try:
                  mecabReading = mecab.reading(srcTxt)
                  note[dstField] = mecabReading
              except Exception as e:
                  mecab = None
                  raise
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
