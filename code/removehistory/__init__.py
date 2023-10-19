# -*- coding: utf-8 -*-
# Copyright: Damien Elmes (http://help.ankiweb.net)
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from anki.hooks import addHook
from anki.utils import ids2str
from aqt import mw
from aqt.qt import *
from aqt.utils import askUser, showInfo


def onRemoveHistory(browser):
    cids = browser.selected_cards()
    if not cids:
        showInfo("No cards selected.")
        return
    if not askUser(
        "Are you sure you wish to remove the review history of the selected cards?"
    ):
        return

    mw.col.mod_schema(check=True)

    mw.progress.start(immediate=True)
    mw.col.db.execute("delete from revlog where cid in " + ids2str(cids))
    mw.progress.finish()

    mw.reset()

    showInfo("Removed history of %d cards" % len(cids))


def onMenuSetup(browser):
    act = QAction(browser)
    act.setText("Remove Card History")
    mn = browser.form.menu_Cards
    mn.addSeparator()
    mn.addAction(act)
    act.triggered.connect(lambda b=browser: onRemoveHistory(browser))


addHook("browser.setupMenus", onMenuSetup)
