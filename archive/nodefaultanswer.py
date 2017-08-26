# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Set focus to middle area when answer shown, so space does not trigger the
# answer buttons.
#

from aqt.qt import *
from aqt import mw
import aqt.reviewer
from anki.hooks import addHook, wrap

def noAnswer():
    mw.reviewer.web.setFocus()

addHook("showAnswer", noAnswer)

def keyHandler(self, evt, _old):
    key = unicode(evt.text())
    if (key == " " or evt.key() in (Qt.Key_Return, Qt.Key_Enter)):
        if self.state == "answer":
            return
    _old(self, evt)

aqt.reviewer.Reviewer._keyHandler = wrap(
    aqt.reviewer.Reviewer._keyHandler, keyHandler, "around")
