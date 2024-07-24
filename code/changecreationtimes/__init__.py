# Copyright: Matthew Duggan, mostly copied from bulk reading generator plugin
#            by Damien Elmes.
#
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Reset creation times of a block of cards.
#
# For information about how to use, how to report a problem, see this addon's
# download page: https://ankiweb.net/shared/info/1348853407
#
# History:
# 2010/12/17 - New.
#   In Anki 1, creation time was at the card level, and kept in its own column.
# 2013/03/19 - Updated for Anki 2.0.8 (by someguy)
#   In Anki 2, creation time is at the "note" level, inhereted by all the cards
#   created from a note, regardless of when those cards were created. Also,
#   creation time is no longer in its own column. It is the note's "id".
#   Changing the creation time is a bit trickier now because we have to execute
#   SQL to change the note table in a way Anki didn't intend. And, because
#   cards are foreign-keyed to the note's ID, we have to execute SQL to change
#   the card table too.

from __future__ import annotations

import random
import time
from collections.abc import Sequence

from anki.cards import CardId
from anki.lang import ngettext
from anki.notes import NoteId
from aqt import mw
from aqt.browser.browser import Browser
from aqt.qt import *
from aqt.utils import getText, showWarning, tooltip

# debug
# from aqt.utils import showInfo

# Bulk updates
##########################################################################


def resetCreationTimes(note_ids: Sequence[NoteId], desttime: int) -> None:
    mw.progress.start(label="Reset Creation Times: updating...", max=len(note_ids))

    # debug
    # showInfo(("Called reset with %s notes") % len(note_ids))

    for note_cnt, note_id in enumerate(note_ids):
        # debug
        # showInfo(("Loop: Processing note id %s") % note_id)

        mw.progress.update(
            label=("Resetting Creation Times: updating note %s") % note_id,
            value=note_cnt,
        )

        # Ensure timestamp doesn't already exist. (Copied from anki/utils.py
        # timestampID function).
        while mw.col.db.scalar("select id from notes where id = ?", desttime):
            desttime += 1

        # Update the note row
        mw.col.db.execute(
            """update notes
            set id=?
            where id = ?""",
            desttime,
            note_id,
        )

        # Update the cards row(s)
        mw.col.db.execute(
            """update cards
               set nid=?
               where nid = ?""",
            desttime,
            note_id,
        )

        desttime += 10

    mw.progress.finish()

    return


# The browser displays cards. But, the creation date is on the note, and the
# note can have multiple cards associated to it. This creates a challenge to
# access the notes in the order of the displayed cards. To keep the processing
# simple, this addon preprocesses the cards, gathering the unique note IDs,
# and ensuring there are no surprises (such as the same note referenced by
# cards in different sort locations in the browser).
def identifyNotes(card_ids: Sequence[CardId]) -> tuple[int, list[NoteId]]:
    mw.progress.start(
        label="Reset Creation Times: collecting notes...", max=len(card_ids)
    )
    last_nid: NoteId | None = None
    nids_ordered = []
    nids_lookup = {}

    # debug
    # showInfo(("Called identifyNotes with %s cards") % len(card_ids))

    # Loop through the selected cards, detecting unique notes and saving the
    # note IDs for driving the DB update.
    card_cnt = 0
    for card_cnt, card_id in enumerate(card_ids):
        # debug
        # showInfo(("Loop: Processing card id %s") % card_id)

        mw.progress.update(
            label=("Reset Creation Times: collecting note for card %s") % card_id,
            value=card_cnt,
        )

        # Retrieve the selected card to get the note ID.
        card = mw.col.get_card(card_id)

        # debug
        # showInfo(("retrieved card_id %s with note_id %s") % (card_id, card.nid))

        # We expect sibling cards (of a note) to be grouped together. When a new
        # note is encountered, save it for later processing.
        if card.nid != last_nid:
            # I don't think this could ever happen:
            # This is a precaution that a note's sibling cards are grouped
            # together. If it were possible for them to be sorted in the browser
            # in a way that they wouldn't be contiguous, this would cause the
            # underlying note (creation time) to be processed twice in a way the
            # user didn't intend. Anki's data model makes this logically
            # possible, but the browser may prevent it. This test is a way to be
            # absolutely certain.
            if card.nid in nids_lookup:
                showWarning(
                    "A note found out of order. Your cards appear to be sorted in a way that siblings are not contiguous. It is not possible to reset the create time this way. Please report this to the addon discussion forum."
                )

            # Add the nid to the end of an array which will be used to drive the
            # DB update. This maintains note ids in the same order which the
            # cards appear in the browser.
            nids_ordered.append(card.nid)

            # Add the nid to a dictionary so we can easily reference it (to see
            # if a nid was previously encountered. I.e., whether sibling cards
            # weren't grouped together in the browser.).
            nids_lookup.update({card.nid: 1})

            # Save the new nid value so we can skip sibling cards and detect
            # when a card belonging to a different note is encountered.
            last_nid = card.nid

    mw.progress.finish()

    return card_cnt + 1, nids_ordered


def setupMenu(browser: Browser) -> None:
    a = QAction("Reset Creation Times", browser)
    a.triggered.connect(lambda _, e=browser: onResetTimes(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def onResetTimes(browser: Browser) -> None:
    # Make sure user selected something.
    if not browser.form.tableView.selectionModel().hasSelection():
        showWarning(
            "Please select at least one card to reset creation date.", parent=browser
        )
        return

    # Preprocess cards, collecting note IDs.
    (card_cnt, nids) = identifyNotes(browser.selected_cards())

    # debug
    # showInfo(("Processed %s cards leading to %s notes") % (card_cnt, len(nids)))

    # Prompt for date.
    todaystr = time.strftime("%Y/%m/%d", time.localtime())
    (s, ret) = getText(
        "Enter a date as YYYY/MM/DD to set as the creation time, or 'today' for current date (%s):"
        % todaystr,
        parent=browser,
    )

    if (not s) or (not ret):
        return

    # Generate a random MM:HH:SS. This will help prevent the same timestamp from
    # being used if this addon is executed multiple times with the same date.
    random_time = ("%s:%s:%s") % (
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59),
    )

    # Don't want random? Uncomment the following line and specify any time you
    # want in the format HH:MM:SS where HH is 00-24:
    # random_time = "15:01:01"

    if s == "today":
        desttime = time.mktime(
            time.strptime(("%s %s") % (todaystr, random_time), "%Y/%m/%d %H:%M:%S")
        )
    else:
        try:
            desttime = time.mktime(
                time.strptime(("%s %s") % (s, random_time), "%Y/%m/%d %H:%M:%S")
            )
        except ValueError:
            showWarning(
                "Sorry, I didn't understand that date.  Please enter 'today' or a date in YYYY/MM/DD format",
                parent=browser,
            )
            return

    # This mimics anki/utils.py timestampID function (which calls int_time for
    # seconds since epoch and multiplies those seconds by 1000).
    desttime = desttime * 1000

    # debug
    # showInfo(("desttime %s") % desttime)

    # Force a full sync if collection isn't already marked for one. This is
    # apparently because we are changing the key column of the table.
    # (Per Damien on 2013/01/07: http://groups.google.com/group/anki-users/msg/3c8910e10f6fd0ac?hl=en )
    mw.col.mod_schema(check=True)

    # Do it.
    resetCreationTimes(nids, int(desttime))

    # Done.
    mw.reset()
    tooltip(
        ngettext(
            "Creation time reset for %d note.",
            "Creation time reset for %d notes.",
            len(nids),
        )
        % len(nids)
    )


from aqt import gui_hooks

gui_hooks.browser_will_show.append(setupMenu)
