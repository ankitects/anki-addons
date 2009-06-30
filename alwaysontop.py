# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin keeps Anki on top of other windows.

from ankiqt import mw
from PyQt4.QtCore import *
from PyQt4.QtGui import *

mw.setWindowFlags(Qt.WindowStaysOnTopHint)
mw.show()

mw.registerPlugin("Always On Top", 9)
