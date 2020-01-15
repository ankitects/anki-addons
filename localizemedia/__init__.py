# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Changes remote image links in selected cards to local ones.
#

import re
import time

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo


def onLocalize(browser):
    nids = browser.selectedNotes()
    if not nids:
        showInfo("Please select some notes.")
        return

    mw.progress.start(immediate=True)
    success = False
    try:
        success = _localizeNids(browser, nids)
    finally:
        mw.progress.finish()

    browser.model.reset()
    mw.requireReset()

    if success:
        showInfo("Checked %d notes" % len(nids), parent=browser)


def _localizeNids(browser, nids):
    for c, nid in enumerate(nids):
        note = mw.col.getNote(nid)
        if not _localizeNote(browser, note):
            mw.progress.finish()
            showInfo(
                "Aborted after processing %d notes. Any media already downloaded has been saved."
                % (c)
            )
            return

        mw.progress.update(
            label="Successfully processed %d/%d notes" % (c + 1, len(nids))
        )
    return True


# true on success
def _localizeNote(browser, note):
    for fld, val in note.items():
        # any remote links?
        files = mw.col.media.filesInStr(note.model()["id"], val, includeRemote=True)
        found = False
        for file in files:
            if file.startswith("http://") or file.startswith("https://"):
                found = True
                break
            elif file.startswith("data:image"):
                found = True
                break

        if not found:
            continue

        # gather and rewrite
        for regex in mw.col.media.regexps:
            for match in re.finditer(regex, val):
                fname = match.group("fname")
                remote = re.match("(https?)://", fname.lower())
                if remote:
                    newName = browser.editor._retrieveURL(fname)
                    if not newName:
                        return
                    val = val.replace(fname, newName)

                    # don't overburden the server(s)
                    time.sleep(1)
                elif fname.startswith("data:image"):
                    val = val.replace(
                        fname, browser.editor.inlinedImageToFilename(fname)
                    )

        note[fld] = val
        note.flush()
    return True


def onMenuSetup(browser):
    act = QAction(browser)
    act.setText("Localize Media")
    mn = browser.form.menu_Notes
    mn.addSeparator()
    mn.addAction(act)
    act.triggered.connect(lambda b=browser: onLocalize(browser))


addHook("browser.setupMenus", onMenuSetup)
