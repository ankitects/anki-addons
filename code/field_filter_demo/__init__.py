# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
An example of how you can use the hooks in Anki 2.1.20 to modify the
way Anki renders cards.

When Anki encounters an unknown field in the template, it shows the message
"{unknown field <name>}". We want to avoid that message when the card is studied
on other platforms where the add-on is not installed. To accomplish this, we
can use an empty field name in the template replacement, eg instead of
{{myfilter:field}}, we'll use {{myfilter:}}, and the filter will be passed
a blank string. On platforms that don't have the filter, it will not add
anything to the template.

Because the filter code will only run when the filter is specified on the
template, the filter can potentially provide hundreds of options without
having to calculate them all up front and insert them into the list of fields.
Instead, it can just calculate the required information on demand.

We'll make an add-on that allows the user to add the following to their
template:

{{info-card-interval:}}   -- shows the card's interval
{{info-note-creation:}}   -- shows the date the note was created

The filter hook is not provided with a card or note ID, but there is
another hook we can use to get them. We could just store the IDs, and then
fetch the card or note from the database each time a filter is encountered.
But if the user adds tens or hundreds of these replacements to their card,
fetching the same card or note over and over again might be slow.

So instead, we store the current card and note at the start of the
rendering process, and each time a filter is processed on the card,
the objects can be reused.
"""

import time
from typing import Dict, Optional, Tuple

from anki import hooks
from anki.cards import Card
from anki.notes import Note
from anki.types import NoteType, QAData
from aqt import mw

# we will update these each time a new card is rendered
current_card: Optional[Card] = None
current_note: Optional[Note] = None

# called when a card is going to be rendered. we can update
# the current card and note here for the filter below to use.
def my_card_will_render_func(
    templates: Tuple[str, str], fields: Dict[str, str], notetype: NoteType, data: QAData
) -> Tuple[str, str]:
    # tell python we want to update the above global variables
    global current_card, current_note

    # update them using the IDs stored in the QAData object (see types.py)
    card_id = data[0]
    current_card = mw.col.getCard(card_id)

    note_id = data[1]
    current_note = mw.col.getNote(note_id)

    # this is a filter, so it must return its first argument.
    return templates


# called each time a custom filter is encountered
def my_field_filter(
    field_text: str, field_name: str, filter_name: str, fields: Dict[str, str],
) -> str:
    if not filter_name.startswith("info-"):
        # not our filter, return string unchanged
        return field_text

    # split the name into the 'info' prefix, and the rest
    try:
        (label, rest) = filter_name.split("-", maxsplit=1)
    except ValueError:
        return invalid_name(filter_name)

    # call the appropriate function
    if rest == "card-interval":
        return card_interval()
    elif rest == "note-creation":
        return note_creation()
    else:
        return invalid_name(filter_name)


def invalid_name(filter_name: str) -> str:
    return f"invalid filter name: {filter_name}"


def card_interval() -> str:
    return str(current_card.ivl)


def note_creation() -> str:
    # convert millisecond timestamp to seconds
    note_creation_unix_timestamp = current_note.id // 1000
    # convert timestamp to a human years-months-days
    return time.strftime("%Y-%m-%d", time.localtime(note_creation_unix_timestamp))


# register the hooks we want to use
hooks.card_will_render.append(my_card_will_render_func)
hooks.field_filter.append(my_field_filter)
