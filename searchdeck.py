# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatically prepend 'deck:current' when searching. To search the whole
# collection, include deck:* in search.
#

from aqt import mw
from aqt.browser import Browser
from anki.hooks import wrap

def onSearch(self, reset=True):
    txt = unicode(self.form.searchEdit.lineEdit().text()).strip()
    if "deck:" in txt:
        return
    if _("<type here to search; hit enter to show current deck>") in txt:
        return
    if "is:current" in txt:
        return
    if not txt.strip():
        return
    self.form.searchEdit.lineEdit().setText("deck:current " + txt)

Browser.onSearch = wrap(Browser.onSearch, onSearch, "before")
