# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Standard Japanese model.
#

import anki.stdmodels

def addJapaneseModel(col):
    mm = col.models
    m = mm.new(_("Japanese (recognition)"))
    fm = mm.newField(_("Expression"))
    mm.addField(m, fm)
    fm = mm.newField(_("Meaning"))
    mm.addField(m, fm)
    fm = mm.newField(_("Reading"))
    mm.addField(m, fm)
    t = mm.newTemplate(_("Recognition"))
    # css
    m['css'] += u"""\
.jp { font-size: 30px }
.win .jp { font-family: "MS Mincho", "ＭＳ 明朝"; }
.mac .jp { font-family: "Hiragino Mincho Pro", "ヒラギノ明朝 Pro"; }
.linux .jp { font-family: "Kochi Mincho", "東風明朝"; }
.mobile .jp { font-family: "Hiragino Mincho ProN"; }"""
    # recognition card
    t['qfmt'] = "<div class=jp> {{Expression}} </div>"
    t['afmt'] = """{{FrontSide}}\n\n<hr id=answer>\n\n\
<div class=jp> {{furigana:Reading}} </div><br>\n\
{{Meaning}}"""
    mm.addTemplate(m, t)
    mm.add(m)
    return m

def addDoubleJapaneseModel(col):
    mm = col.models
    m = addJapaneseModel(col)
    m['name'] = "Japanese (recognition&recall)"
    rev = mm.newTemplate(_("Recall"))
    rev['qfmt'] = "{{Meaning}}"
    rev['afmt'] = """{{FrontSide}}

<hr id=answer>

<div class=jp> {{Expression}} </div>
<div class=jp> {{furigana:Reading}} </div>"""
    mm.addTemplate(m, rev)
    return m

def addOptionalJapaneseModel(col):
    mm = col.models
    m = addDoubleJapaneseModel(col)
    m['name'] = "Japanese (optional recall)"
    rev = m['tmpls'][1]
    rev['qfmt'] = "{{#Add Recall}}\n"+rev['qfmt']+"\n{{/Add Recall}}"
    fm = mm.newField("Add Recall")
    mm.addField(m, fm)
    return m

anki.stdmodels.models.append((_("Japanese (recognition)"), addJapaneseModel))
anki.stdmodels.models.append((_("Japanese (recognition&recall)"), addDoubleJapaneseModel))
anki.stdmodels.models.append((_("Japanese (optional recall)"), addOptionalJapaneseModel))
