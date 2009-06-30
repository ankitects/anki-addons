from PyQt4.QtCore import *
from PyQt4.QtGui import *
from subprocess import Popen
from ankiqt import mw
import sys

# add my own dictionary lookup tool
def epwingLookup(text):
    Popen(["lookup", text.encode("utf-8")])

def lookupQ():
    mw.initLookup()
    epwingLookup(mw.currentCard.fact['Expression'])

def lookupA():
    mw.initLookup()
    epwingLookup(mw.currentCard.fact['Meaning'])

def lookupS():
    mw.initLookup()
    mw.lookup.selection(epwingLookup)

# remove the standard lookup links
ml = mw.mainWin.menu_Lookup
for i in ("expr", "mean", "as", "es", "esk"):
    ml.removeAction(getattr(mw.mainWin,
                            "actionLookup_" + i))
# add custom links
q = QAction(mw)
q.setText("..question")
q.setShortcut(_("Ctrl+1"))
ml.addAction(q)
mw.connect(q, SIGNAL("triggered()"), lookupQ)
a = QAction(mw)
a.setText("..answer")
a.setShortcut(_("Ctrl+2"))
ml.addAction(a)
mw.connect(a, SIGNAL("triggered()"), lookupA)
s = QAction(mw)
s.setText("..selection")
s.setShortcut(_("Ctrl+3"))
ml.addAction(s)
mw.connect(s, SIGNAL("triggered()"), lookupS)

mw.registerPlugin("Custom Dictionary Lookup", 5)
