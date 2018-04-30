# -*- coding: utf-8 -*-
# Copyright: Damien Elmes (http://help.ankiweb.net)
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import showInfo, askUser
from anki.utils import ids2str


def onRemoveHistory(browser):
    cids = browser.selectedCards()
    if not cids:
        showInfo("No cards selected.")
        return
    if not askUser("Are you sure you wish to remove the review history of the selected cards?"):
        return

    mw.col.modSchema(check=True)

    mw.progress.start(immediate=True)
    mw.col.db.execute("delete from revlog where cid in " + ids2str(cids))
    mw.col.setMod()
    mw.col.save()
    mw.progress.finish()

    browser.model.reset()
    mw.requireReset()

    showInfo("Removed history of %d cards" % len(cids))

def onMenuSetup(browser):
    act = QAction(browser)
    act.setText("Remove Card History")
    mn = browser.form.menu_Cards
    mn.addSeparator()
    mn.addAction(act)
    act.triggered.connect(lambda b=browser: onRemoveHistory(browser))

addHook("browser.setupMenus", onMenuSetup)
