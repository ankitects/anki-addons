# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Feed field HTML through BeautifulSoup to fix things like unbalanced div tags.
#

import warnings

from anki.hooks import addHook
from aqt import mw
from aqt.browser.browser import Browser
from aqt.qt import *
from aqt.utils import showInfo
from bs4 import BeautifulSoup


def onFixHTML(browser: Browser):
    nids = browser.selected_notes()
    if not nids:
        showInfo("Please select some notes.")
        return

    mw.progress.start(immediate=True)
    try:
        changed = _onFixHTML(browser, nids)
    finally:
        mw.progress.finish()

    mw.reset()

    showInfo("Updated %d/%d notes." % (changed, len(nids)), parent=browser)


def _onFixHTML(browser, nids):
    changed = 0
    for c, nid in enumerate(nids):
        note = mw.col.get_note(nid)
        if _fixNoteHTML(note):
            changed += 1
        mw.progress.update(label="Processed %d/%d notes" % (c + 1, len(nids)))
    return changed


# true on change
def _fixNoteHTML(note):
    changed = False
    for fld, val in note.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = str(BeautifulSoup(val, "html.parser"))
        if parsed != val:
            note[fld] = parsed
            changed = True

    if changed:
        mw.col.update_note(note)

    return changed


def onMenuSetup(browser):
    act = QAction(browser)
    act.setText("Fix Invalid HTML")
    mn = browser.form.menu_Notes
    mn.addSeparator()
    mn.addAction(act)
    act.triggered.connect(lambda b=browser: onFixHTML(browser))


addHook("browser.setupMenus", onMenuSetup)
