# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Set focus to middle area when answer shown, so space does not trigger the
# answer buttons.
#

from aqt import mw
from anki.hooks import addHook

def noAnswer():
    mw.reviewer.web.setFocus()

addHook("showAnswer", noAnswer)
