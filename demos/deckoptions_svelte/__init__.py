import json
from pathlib import Path

from aqt import gui_hooks, mw

file = Path(__file__)

with open(file.with_name("addon.js")) as f:
    script = f.read()


def on_mount(dialog):
    dialog.web.eval(script)


gui_hooks.deck_options_did_load.append(on_mount)
