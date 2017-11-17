# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Changes remote image links in selected cards to local ones.
# For use with Anki 2.1.0beta25+
#

import re
import time

from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
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
            showInfo("Aborted after processing %d notes. Any images already downloaded have been saved." % (c))
            return

        mw.progress.update(label="Successfully processed %d/%d notes" % (c+1, len(nids)))
    return True

# true on success
def _localizeNote(browser, note):
    for fld, val in note.items():
        # any remote links?
        files = mw.col.media.filesInStr(note.model()['id'], val, includeRemote=True)
        found = False
        for file in files:
            if file.startswith("http://") or file.startswith("https://"):
                found = True
                break
        if not found:
            continue

        # gather and rewrite
        for regex in mw.col.media.imgRegexps:
            for match in re.finditer(regex, val):
                fname = match.group("fname")
                remote = re.match("(https?)://", fname.lower())
                if not remote:
                    continue

                newName = browser.editor._retrieveURL(fname)
                if not newName:
                    return
                val = val.replace(fname, newName)

                # don't overburden the server(s)
                time.sleep(1)

        note[fld] = val
        note.flush()
        return True

def onMenuSetup(browser):
    act = QAction(browser)
    act.setText("Localize Images")
    mn = browser.form.menu_Notes
    mn.addSeparator()
    mn.addAction(act)
    mn.triggered.connect(lambda b=browser: onLocalize(browser))

addHook("browser.setupMenus", onMenuSetup)
