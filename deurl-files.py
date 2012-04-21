# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Convert percent escapes in files and sound: references
#

import re, os, urllib
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, askUser
from anki.utils import ids2str

def fix():
    if not askUser("Have you backed up your collection and media folder?"):
        return
    mw.progress.start(immediate=True)
    # media folder
    for file in os.listdir(mw.col.media.dir()):
        ok = False
        if "%" not in file:
            continue
        for type in "mp3", "wav", "ogg":
            if file.endswith(type):
                ok = True
                break
        if not ok:
            continue
        os.rename(file, file.replace("%", ""))
    # sound fields
    nids = mw.col.db.list(
        "select distinct(nid) from cards where id in "+
        ids2str(mw.col.findCards("[sound: \%")))
    def repl(match):
        old = match.group(2)
        if "%" not in old:
            return match.group(0)
        return "[sound:%s]" % old.replace("%", "")
    for nid in nids:
        n = mw.col.getNote(nid)
        dirty = False
        for (name, value) in n.items():
            new = re.sub(mw.col.media.regexps[0], repl, value)
            if new != value:
                n[name] = new
                dirty = True
        if dirty:
            n.flush()
    mw.progress.finish()
    showInfo("Success.")

a = QAction(mw)
a.setText("Fix Encoded Media")
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), fix)
