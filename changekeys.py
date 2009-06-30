# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# this plugin allows you to redefine the keys used to answer cards. it defines
# 'x' as a failed answer and 'y' as a correct answer.

# version 1: initial release

from ankiqt import mw

def newEventHandler(evt):
    if mw.state == "showAnswer":
        key = unicode(evt.text())
        if key == "x":
            evt.accept()
            return mw.cardAnswered(1)
        if key == "y":
            evt.accept()
            return mw.cardAnswered(4)
    return oldEventHandler(evt)

oldEventHandler = mw.keyPressEvent
mw.keyPressEvent = newEventHandler

mw.registerPlugin("Change Keys", 7)
