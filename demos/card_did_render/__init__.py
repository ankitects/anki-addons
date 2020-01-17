# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
An example of how you can transform the rendered card content in Anki 2.1.20.
"""

from typing import Tuple

from anki import hooks
from anki.template import TemplateRenderContext


def on_card_did_render(
    text: Tuple[str, str], context: TemplateRenderContext
) -> Tuple[str, str]:
    front_text, back_text = text

    # let's uppercase the characters of the front text
    front_text = front_text.upper()

    # if the note is tagged "easy", show the answer in green
    # otherwise, in red
    if context.note().hasTag("easy"):
        colour = "green"
    else:
        colour = "red"

    back_text += f"<style>.card {{ color: {colour}; }}</style>"

    # we must return the text, even if we did not change it
    return front_text, back_text


# register our function to be called when the hook fires
hooks.card_did_render.append(on_card_did_render)
