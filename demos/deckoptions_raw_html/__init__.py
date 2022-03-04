"""
An example of extending the deck options screen with raw HTML/JS.
"""

import json
from pathlib import Path

from aqt import gui_hooks, mw

file = Path(__file__)

with open(file.with_name("raw.html"), encoding="utf8") as f:
    html = f.read()
with open(file.with_name("raw.js"), encoding="utf8") as f:
    script = f.read()


def on_mount(dialog):
    dialog.web.eval(script.replace("HTML_CONTENT", json.dumps(html)))


gui_hooks.deck_options_did_load.append(on_mount)
