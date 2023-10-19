# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Bulk update of readings.
#

from typing import Sequence

from anki.notes import NoteId
from aqt import mw
from aqt.browser.browser import Browser
from aqt.qt import *

from .notetypes import isJapaneseNoteType
from .reading import regenerateReading

# Bulk updates
##########################################################################


def regenerateReadings(nids: Sequence[NoteId]) -> None:
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


def setupMenu(browser: Browser) -> None:
    a = QAction("Bulk-add Readings", browser)
    a.triggered.connect(lambda: onRegenerate(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def onRegenerate(browser: Browser) -> None:
    regenerateReadings(browser.selected_notes())


from aqt import gui_hooks

gui_hooks.browser_will_show.append(setupMenu)
