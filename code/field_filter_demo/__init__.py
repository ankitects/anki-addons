# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
An example of how you can add content to a card's question and answer
dynamically in Anki 2.1.20.

One way to accomplish this would be to automatically insert a
"GeneratedField" field into the list of fields when a card is being
rendered. The user could then use {{GeneratedField}} on their card template
to show the extra information. But this is not a great solution, as when
the user switches to a mobile devices or a device without the add-on
installed, they'd get an error message that the field doesn't exist.
Another downside of that approach is that if you're creating hundreds
of fields, you may be doing extra work that does not end up getting used.

A better approach is to leverage Anki's field filter system. If the user
places {{myfilter:a_valid_field}} on their template, the field_filter hook
will be called, allowing your add-on to modify or add to the text contained
in a_valid_field.

While filters can be used to change the text of fields, in this case we are
only interested in adding new content, so we don't need to use the contents
of a_valid_field. While you could ask your user to create a blank field for
the benefit of your add-on so they don't get an invalid field message,
Anki provides a shortcut - if the field reference ends with a :, it will
not display the invalid field message, and will pass a blank string to the
filter. So users can just use {{myfilter:}} on the template instead.

On devices that are not running the add-on, unrecognized filters will be
silently ignored, so on a stock install {{myfilter:}} will not add anything to
the template.

We'll make an add-on that allows the user to add the following to their
template:

{{info-card-interval:}}   -- shows the card's interval
{{info-note-creation:}}   -- shows the date the note was created

We make use of the context argument to gain access to the card and note
that is being rendered. See template.py for the other options it provides.
"""

import time

from anki import hooks
from anki.template import TemplateRenderContext

# called each time a custom filter is encountered
def my_field_filter(
    field_text: str, field_name: str, filter_name: str, context: TemplateRenderContext,
) -> str:
    if not filter_name.startswith("info-"):
        # not our filter, return string unchanged
        return field_text

    # split the name into the 'info' prefix, and the rest
    try:
        (label, rest) = filter_name.split("-", maxsplit=1)
    except ValueError:
        return invalid_name(filter_name)

    # if in the adding screen, the card hasn't been saved to DB yet
    if rest.startswith("card-") and not context.card():
        return "(n/a)"

    # call the appropriate function
    if rest == "card-interval":
        return card_interval(context)
    elif rest == "note-creation":
        return note_creation(context)
    else:
        return invalid_name(filter_name)


def invalid_name(filter_name: str) -> str:
    return f"invalid filter name: {filter_name}"


def card_interval(ctx: TemplateRenderContext) -> str:
    return str(ctx.card().ivl)


def note_creation(ctx: TemplateRenderContext) -> str:
    # convert millisecond timestamp to seconds
    note_creation_unix_timestamp = ctx.note().id // 1000
    # convert timestamp to a human years-months-days
    return time.strftime("%Y-%m-%d", time.localtime(note_creation_unix_timestamp))

# register our function to be called when the hook fires
hooks.field_filter.append(my_field_filter)
