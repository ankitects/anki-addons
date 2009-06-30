# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw
from ankiqt.ui import facteditor

def setColour(widget, colour):
    w = widget.focusedEdit()
    cursor = w.textCursor()
    new = QColor(colour)
    w.setTextColor(new)
    cursor.clearSelection()
    w.setTextCursor(cursor)

def turnBlue(self):
    setColour(self, "#0000FF")

def newFields(self):
    oldFields(self)
    b1 = QPushButton()
    b1.connect(b1, SIGNAL("clicked()"), lambda self=self: turnBlue(self))
    b1.setShortcut("F1")
    self.iconsBox.addWidget(b1)
    print "foo"

oldFields = facteditor.FactEditor.setupFields
facteditor.FactEditor.setupFields = newFields
