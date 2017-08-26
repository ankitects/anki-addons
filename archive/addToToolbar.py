# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# Add an icon to the toolbar. Adds a separator and 'suspend card' by default.

# version 1: initial release

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw

def init():
    mw.mainWin.toolBar.addSeparator()
    mw.mainWin.toolBar.addAction(mw.mainWin.actionSuspendCard)

mw.addHook("init", init)
mw.registerPlugin("Add to Toolbar", 13)
