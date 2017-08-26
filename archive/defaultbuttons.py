# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Allows you to change the default buttons. Replace '2' and '3' with what you
# like.
#

from ankiqt import ui

def defaultEaseButton(self):
    if self.currentCard.successive:
        # card was answered correctly previously
        return 3
    if self.currentCard.reps:
        # card has been answered before, but not successfully
        return 2
    # card hasn't been seen before
    return 2

ui.main.AnkiQt.defaultEaseButton = defaultEaseButton
