# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Exports the cards in the current deck to a HTML file, so they can be
# printed. Card styling is not included. Cards are printed in sort field
# order.

from __future__ import annotations

import re

from anki.cards import CardId
from anki.decks import DeckId
from anki.utils import ids2str
from aqt import mw
from aqt.qt import *
from aqt.utils import mungeQA, openLink

config = mw.addonManager.getConfig(__name__)


def sortFieldOrderCids(did: DeckId) -> list[CardId]:
    dids = [did]
    for name, id in mw.col.decks.children(did):
        dids.append(id)
    return mw.col.db.list(
        """
select c.id from cards c, notes n where did in %s
and c.nid = n.id order by n.sfld"""
        % ids2str(dids)
    )


def onPrint() -> None:
    path = os.path.join(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DesktopLocation
        ),
        "print.html",
    )
    ids = sortFieldOrderCids(mw.col.decks.selected())

    def esc(s: str) -> str:
        # strip off the repeated question in answer if exists
        # s = re.sub("(?si)^.*<hr id=answer>\n*", "", s)
        # remove type answer
        s = re.sub(r"\[\[type:[^]]+\]\]", "", s)
        return s

    buf = open(path, "w", encoding="utf8")
    buf.write(
        "<html><head>" + '<meta charset="utf-8">' + mw.baseHTML() + "</head><body>"
    )
    buf.write(
        """<style>
img { max-width: 100%; }
tr { page-break-inside:avoid; page-break-after:auto }
td { page-break-after:auto; }
td { border: 1px solid #ccc; padding: 1em; }
.playImage { display: none; }
</style><table cellspacing=10 width=100%>"""
    )
    first = True

    mw.progress.start(immediate=True)
    for j, cid in enumerate(ids):
        if j % config["cardsPerRow"] == 0:
            if not first:
                buf.write("</tr>")
            else:
                first = False
            buf.write("<tr>")
        c = mw.col.get_card(cid)
        qatxt = c.render_output(True, False).answer_text
        qatxt = mw.prepare_card_text_for_display(qatxt)
        cont = '<td width="{1}%"><center>{0}</center></td>'.format(
            esc(qatxt), 100 / config["cardsPerRow"]
        )
        buf.write(cont)
        if j % 50 == 0:
            mw.progress.update("Cards exported: %d" % (j + 1))
    buf.write("</tr>")
    buf.write("</table></body></html>")
    mw.progress.finish()
    buf.close()
    openLink(QUrl.fromLocalFile(path))


q = QAction(mw)
q.setText("Print")
q.setShortcut(QKeySequence("Shift+P"))
mw.form.menuTools.addAction(q)
q.triggered.connect(onPrint)  # type: ignore
