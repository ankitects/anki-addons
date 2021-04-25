from aqt import mw, gui_hooks
import json
from pathlib import Path

file = Path(__file__)

with open(file.with_name("addon.js")) as f:
    script = f.read()

def on_mount(dialog):
    dialog.web.eval(script)

gui_hooks.deck_options_did_load.append(on_mount)
