#!/usr/bin/python
# Copyright Andreas Klauer 2013
#-*- coding: utf-8 -*-

import aqt
from aqt.utils import askUser
from anki.hooks import addHook
from anki.utils import intTime, ids2str

def profileLoaded():
    col = aqt.mw.col
    dm = col.decks

    leafdecks = []

    for deck in dm.all():
        if 'terms' in deck:
            # ignore dynamic decks
            continue
        if not dm.parents(deck['id']):
            # ignore decks without parents
            continue
        if dm.children(deck['id']):
            # ignore decks with children
            continue

        leafdecks.append(deck)

    if not askUser("Merge decks?"):
        return

    for deck in leafdecks:
        # deck.parent()?
        parent="::".join(deck['name'].split("::")[:-1])
        parent = dm.get(dm.id(parent))

        print "merging", deck['name'], "into", parent['name']

        cids = dm.cids(deck['id'])

        # inspired from aqt.browser.setDeck
        mod = intTime()
        usn = col.usn()
        scids = ids2str(cids)
        col.sched.remFromDyn(cids)
        col.db.execute("""
update cards set usn=?, mod=?, did=? where id in """ + scids,
                            usn, mod, parent['id'])

        # delete the deck
        dm.rem(deck['id'])

        # add original deck name to deckmerge field (if present and empty)
        nids = list(set([col.getCard(i).nid for i in cids]))
        col.findReplace(nids, "^$", deck['name'], regex=True, field='deckmerge')


addHook("profileLoaded", profileLoaded)
