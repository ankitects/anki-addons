# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Exports the cards in the current deck to a HTML file, so they can be
# printed. Card styling is not included. Cards are printed in sort field
# order.

import re, urllib
from aqt.qt import *
from anki.utils import isWin
from anki.hooks import runHook, addHook
from aqt.utils import getBase, openLink
from aqt import mw
from anki.utils import ids2str

CARDS_PER_ROW = 3

def sortFieldOrderCids(did):
    dids = [did]
    for name, id in mw.col.decks.children(did):
        dids.append(id)
    return mw.col.db.list("""
select c.id from cards c, notes n where did in %s
and c.nid = n.id order by n.sfld""" % ids2str(dids))

def onPrint():
    path = os.path.join(mw.pm.profileFolder(), "print.html")
    ids = sortFieldOrderCids(mw.col.decks.selected())
    def esc(s):
        # strip off the repeated question in answer if exists
        #s = re.sub("(?si)^.*<hr id=answer>\n*", "", s)
        # remove type answer
        s = re.sub("\[\[type:[^]]+\]\]", "", s)
        return s
    def upath(path):
        if isWin:
            prefix = u"file:///"
        else:
            prefix = u"file://"
        return prefix + unicode(
            urllib.quote(path.encode("utf-8")), "utf-8")
    buf = open(path, "w")
    buf.write("<html><head>" +
              '<meta charset="utf-8">'
              + getBase(mw.col).encode("utf8") + "</head><body>")
    buf.write("""<style>
img { max-width: 100%; }
tr { page-break-after:auto; }
td { page-break-after:auto; }
td { border: 1px solid #ccc; padding: 1em; }
</style><table cellspacing=10 width=100%>""")
    first = True

    mw.progress.start(immediate=True)
    for j, cid in enumerate(ids):
        if j % CARDS_PER_ROW == 0:
            if not first:
                buf.write("</tr>")
            else:
                first = False
            buf.write("<tr>")
        c = mw.col.getCard(cid)
        cont = u"<td><center>%s</center></td>" % esc(c._getQA(True, False)['a'])
        buf.write(cont.encode("utf8"))
        if j % 50 == 0:
            mw.progress.update("Cards exported: %d" % (j+1))
    buf.write("</tr>")
    buf.write("</table></body></html>")
    mw.progress.finish()
    buf.close()
    openLink(upath(path))

q = QAction(mw)
q.setText("Print")
q.setShortcut(QKeySequence("Ctrl+P"))
mw.form.menuTools.addAction(q)
mw.connect(q, SIGNAL("triggered()"), onPrint)
