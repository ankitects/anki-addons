# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# An example of how to override review shortcuts. Changes:
# - when '5' is pressed with the question shown, show the answer
# - when '6' is pressed with the answer shown, answer with the default button
# - when '7' is pressed, undo the last review
# - when '8' is pressed, mark the card
# You can edit the code below to customize it.

from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap

def keyHandler(self, evt, _old):
    key = unicode(evt.text())
    if key == "5" and self.state == "question":
        self._showAnswerHack()
    elif key == "6" and self.state == "answer":
        self._answerCard(self._defaultEase())
    elif key == "7":
        self.mw.onUndo()
    elif key == "8":
        self.onMark()
    else:
        return _old(self, evt)

Reviewer._keyHandler = wrap(Reviewer._keyHandler, keyHandler, "around")

