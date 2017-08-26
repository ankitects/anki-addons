# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Adds an item to the tools menu to build .png files for any LaTeX in fields.
# This is normally done when you review a card; use this to do them all in
# bulk for distributing to users without LaTeX.
#

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

def build():
    mw.progress.start()
    for cid in mw.col.db.list("select id from cards"):
        mw.col.getCard(cid).q()
    mw.progress.finish()
    showInfo("LaTeX generated.")

a = QAction(mw)
a.setText("Build LaTeX")
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), build)
