# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin adds your LaTeX files to the media database when you run
# Tools>Advanced>Cache LaTeX. After doing this, you can use them in the iPhone
# app.

import time
from anki.utils import genID
from anki import latex as latexOrig
from anki.utils import canonifyTags

def imgLink(deck, latex, build=True):
    "Parse LATEX and return a HTML image representing the output."
    latex = latexOrig.mungeLatex(latex)
    (ok, img) = latexOrig.imageForLatex(deck, latex, build)
    deck.s.statement("""
insert or replace into media values
(:id, :fn, 0, :t, '', 'latex')""",
                     id=genID(),
                     fn=img,
                     t=time.time())
    if ok:
        return '<img src="%s">' % img
    else:
        return img

latexOrig.imgLink = imgLink
