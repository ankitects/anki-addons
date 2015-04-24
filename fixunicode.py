# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

import re
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

# regex from http://stackoverflow.com/questions/18673213/detect-remove-unpaired-surrogate-character-in-python-2-gtk
lone = re.compile(
    ur'''(?x)            # verbose expression (allows comments)
    (                    # begin group
    [\ud800-\udbff]      #   match leading surrogate
    (?![\udc00-\udfff])  #   but only if not followed by trailing surrogate
    )                    # end group
    |                    #  OR
    (                    # begin group
    (?<![\ud800-\udbff]) #   if not preceded by leading surrogate
    [\udc00-\udfff]      #   match trailing surrogate
    )                    # end group
    ''')

def fix():
    mw.col.modSchema(check=True)
    mw.progress.start()
    toFix = []
    for nid, flds in mw.col.db.execute("select id, flds from notes"):
        rep = lone.sub("", flds)
        if rep != flds:
            toFix.append((rep, nid))
    mw.col.db.executemany("update notes set flds=? where id=?", toFix)
    mw.progress.finish()
    showInfo("Found & fixed %d notes. Please upload your collection and download it to other devices." % len(toFix))

a = QAction(mw)
a.setText("Fix Invalid Characters")
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), fix)
