"""
An example of extending the deck options screen with raw HTML/JS.
"""

from aqt import mw, gui_hooks
import json
from pathlib import Path

file = Path(__file__)

with open(file.with_name("raw.html")) as f:
    html = f.read()
with open(file.with_name("raw.js")) as f:
    script = f.read()

def on_mount(dialog):
    dialog.web.eval(
        script.replace("HTML_CONTENT", json.dumps(html)))

gui_hooks.deck_options_did_load.append(on_mount)
