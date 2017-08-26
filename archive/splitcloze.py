# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Moves non-cloze cards in cloze models to a new model. Assumes the first
# field is the cloze field.
#

import re, copy
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki.utils import ids2str, splitFields

def splitClozes():
    mw.col.modSchema()
    mw.progress.start(immediate=True)
    try:
        _splitClozes()
    finally:
        mw.progress.finish()
    showInfo("Success. Please remove this addon and upgrade.")

def _splitClozes():
    data = []
    for m in mw.col.models.all():
        # cloze model?
        if '{{cloze:' not in m['tmpls'][0]['qfmt']:
            continue
        tmpls = []
        tmap = {}
        for t in m['tmpls']:
            if '{{cloze:' not in t['qfmt']:
                tmpls.append(t)
                tmap[t['ord']] = len(tmpls) - 1
                t['afmt'] = t['afmt'].replace("{{cloze:1:", "{{")
        # any non-clozes found?
        if not tmpls:
            continue
        # create a new model
        m2 = mw.col.models.copy(m)
        # add the non-cloze templates
        m2['tmpls'] = copy.deepcopy(tmpls)
        mw.col.models._updateTemplOrds(m2)
        mw.col.models.save(m2)
        mw.col.models.setCurrent(m2)
        # copy old note data
        snids = ids2str(mw.col.models.nids(m))
        for id, flds in mw.col.db.all(
            "select id, flds from notes where id in " + snids):
            n = mw.col.newNote()
            sflds = splitFields(flds)
            for name, (ord, field) in mw.col.models.fieldMap(m2).items():
                if ord == 0:
                    sflds[0] = re.sub("{{c\d::(.+?)}}", r"\1", sflds[0])
                n[name] = sflds[ord]
            mw.col.addNote(n)
            # delete the generated cards and move the old cards over
            mw.col.db.execute(
                "delete from cards where nid = ?", n.id)
            for old, new in tmap.items():
                mw.col.db.execute("""
update cards set ord = ?, nid = ? where ord = ? and nid = ?""",
                                  new, n.id, old, id)
        # delete the templates from the old model
        for t in tmpls:
            mw.col.models.remTemplate(m, t)

a = QAction(mw)
a.setText("Split Clozes")
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), splitClozes)
