# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
An example of how you can transform the rendered card content in Anki 2.1.20.
"""

from typing import Tuple

from anki import hooks
from anki.template import TemplateRenderContext, TemplateRenderOutput


def on_card_did_render(
    output: TemplateRenderOutput, context: TemplateRenderContext
) -> None:
    # let's uppercase the characters of the front text
    output.question_text = output.question_text.upper()

    # if the note is tagged "easy", show the answer in green
    # otherwise, in red
    if context.note().has_tag("easy"):
        colour = "green"
    else:
        colour = "red"

    output.answer_text += f"<style>.card {{ color: {colour}; }}</style>"


# register our function to be called when the hook fires
hooks.card_did_render.append(on_card_did_render)
