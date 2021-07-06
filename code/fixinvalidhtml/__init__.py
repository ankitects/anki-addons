# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Feed field HTML through BeautifulSoup to fix things like unbalanced div tags.
#

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from bs4 import BeautifulSoup


def onFixHTML(browser):
    nids = browser.selected_notes()
    if not nids:
        showInfo("Please select some notes.")
        return

    mw.checkpoint("Fix Invalid HTML")

    mw.progress.start(immediate=True)
    try:
        changed = _onFixHTML(browser, nids)
    finally:
        mw.progress.finish()

    browser.note_type.reset()
    mw.requireReset()

    showInfo("Updated %d/%d notes." % (changed, len(nids)), parent=browser)


def _onFixHTML(browser, nids):
    changed = 0
    for c, nid in enumerate(nids):
        note = mw.col.getNote(nid)
        if _fixNoteHTML(note):
            changed += 1
        mw.progress.update(label="Processed %d/%d notes" % (c + 1, len(nids)))
    return changed


# true on change
def _fixNoteHTML(note):
    changed = False
    for fld, val in note.items():
        parsed = str(BeautifulSoup(val, "html.parser"))
        if parsed != val:
            note[fld] = parsed
            changed = True

    if changed:
        note.flush()

    return changed


def onMenuSetup(browser):
    act = QAction(browser)
    act.setText("Fix Invalid HTML")
    mn = browser.form.menu_Notes
    mn.addSeparator()
    mn.addAction(act)
    act.triggered.connect(lambda b=browser: onFixHTML(browser))


addHook("browser.setupMenus", onMenuSetup)
