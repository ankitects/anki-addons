# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw, ui
import os,re

def onEdit():
    diag = QDialog(mw.app.activeWindow())
    diag.setWindowTitle("Edit Fonts")
    layout = QVBoxLayout(diag)
    diag.setLayout(layout)

    label = QLabel("""\
See <a href="http://ichi2.net/anki/wiki/EmbeddingFonts">the documentation</a>.
<p>
Paste your font CSS below.
""")
    label.setTextInteractionFlags = Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse

    layout.addWidget(label)

    text = QTextEdit()
    text.setPlainText(mw.deck.getVar("fontCSS") or "")
    layout.addWidget(text)

    box = QDialogButtonBox(QDialogButtonBox.Close)
    layout.addWidget(box)
    box.connect(box, SIGNAL("rejected()"), diag, SLOT("reject()"))

    def onClose():
        mw.deck.setVar("fontCSS", unicode(text.toPlainText()))
        ui.utils.showInfo("""\
Settings saved. Please see the documentation for the next step.""")

    diag.connect(diag, SIGNAL("rejected()"), onClose)

    diag.setMinimumHeight(400)
    diag.setMinimumWidth(500)
    diag.exec_()

# Setup menu entries
menu1 = QAction(mw)
menu1.setText("Embedded Fonts...")
mw.connect(menu1, SIGNAL("triggered()"),onEdit)
mw.mainWin.menuTools.addSeparator()
mw.mainWin.menuTools.addAction(menu1)
