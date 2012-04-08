# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Standard Japanese model.
#

import anki.stdmodels

def addJapaneseModel(col):
    mm = col.models
    m = mm.new(_("Japanese"))
    fm = mm.newField(_("Expression"))
    mm.addField(m, fm)
    fm = mm.newField(_("Meaning"))
    mm.addField(m, fm)
    fm = mm.newField(_("Reading"))
    mm.addField(m, fm)
    t = mm.newTemplate(_("Recognition"))
    # css
    t['css'] += u"""\
.jp { font-size: 30px }
.win .jp { font-family: "MS Mincho", "ＭＳ 明朝"; }
.mac .jp { font-family: "Hiragino Mincho Pro", "ヒラギノ明朝 Pro"; }
.linux .jp { font-family: "Kochi Mincho", "東風明朝"; }
.mobile .jp { font-family: "Hiragino Mincho ProN"; }"""
    # recognition card
    t['qfmt'] = "<span class=jp> {{Expression}} </span>"
    t['afmt'] = t['qfmt'] + """\n\n<hr id=answer>\n\n\
<span class=jp> {{furigana:Reading}} </span><br>\n\
{{Meaning}}"""
    mm.addTemplate(m, t)
    mm.add(m)
    return m

anki.stdmodels.models.append((_("Japanese"), addJapaneseModel))
