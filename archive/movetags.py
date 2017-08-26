# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# put in your plugins directory, open deck, run 'move tags' from the plugins
# menu. after that, you can remove the plugin again.
#
# since it will mark all facts modified, run it after syncing with the server

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw
from anki.facts import Fact
from anki.utils import canonifyTags

def moveTags():
    for fact in mw.deck.s.query(Fact).all():
        old = fact.tags
        fact.tags = canonifyTags(fact.tags + "," + ",".join(
                                 [c.tags for c in fact.cards]))
        fact.setModified()
    mw.deck.setModified()
    mw.reset()

def init():
    q = QAction(mw)
    q.setText("Move Tags")
    mw.mainWin.menuPlugins.addAction(q)
    mw.connect(q, SIGNAL("triggered()"), moveTags)

mw.addHook("init", init)
