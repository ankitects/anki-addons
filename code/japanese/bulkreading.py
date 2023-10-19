# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Bulk update of readings.
#

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *

from .notetypes import isJapaneseNoteType
from .reading import regenerateReading

# Bulk updates
##########################################################################


def regenerateReadings(nids):
    mw.progress.start()
    for nid in nids:
        note = mw.col.get_note(nid)
        if not isJapaneseNoteType(note.note_type()["name"]):
            continue
        fields = mw.col.models.field_names(note.note_type())
        for src in fields:
            regenerateReading(note, src)
        mw.col.update_note(note)
    mw.progress.finish()
    mw.reset()


def setupMenu(browser):
    a = QAction("Bulk-add Readings", browser)
    a.triggered.connect(lambda: onRegenerate(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def onRegenerate(browser):
    regenerateReadings(browser.selected_notes())


addHook("browser.setupMenus", setupMenu)
