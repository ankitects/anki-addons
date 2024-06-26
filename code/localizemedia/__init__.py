# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Changes remote image links in selected cards to local ones.
#

from __future__ import annotations

import os
import re
import time
import urllib.parse
from typing import Sequence

from anki.httpclient import HttpClient
from anki.notes import Note, NoteId
from aqt import mw
from aqt.browser.browser import Browser
from aqt.operations import CollectionOp, OpChanges
from aqt.qt import *
from aqt.utils import showInfo, showWarning, tr


def onLocalize(browser: Browser) -> None:
    nids = browser.selected_notes()
    if not nids:
        showInfo("Please select some notes.")
        return

    def on_failure(exc: Exception) -> None:
        showInfo(
            f"An error occurred. Any media already downloaded has been saved. Error: {exc}"
        )

    CollectionOp(parent=browser, op=lambda _col: _localizeNids(browser, nids)).success(
        lambda _: showInfo("Success")
    ).failure(on_failure).run_in_background()


def _localizeNids(browser: Browser, nids: Sequence[NoteId]) -> OpChanges:
    undo_start = mw.col.add_custom_undo_entry("Localize Media")
    with HttpClient() as client:
        client.timeout = 30
        for c, nid in enumerate(nids):
            note = mw.col.get_note(nid)
            if not _localizeNote(browser, note, undo_start, client):
                raise Exception("aborted")
            mw.taskman.run_on_main(
                lambda c=c: mw.progress.update(f"Processed {c+1}/{len(nids)}...")  # type: ignore
            )
    return mw.col.merge_undo_entries(undo_start)


def _retrieveURL(url: str, client: HttpClient) -> str:
    content_type = None
    url = urllib.parse.unquote(url)
    with client.get(url) as response:
        if response.status_code != 200:
            raise Exception(
                f"got http code {response.status_code} while fetching {url}"
            )
        filecontents = response.content
        content_type = response.headers.get("content-type")
    # strip off any query string
    url = re.sub(r"\?.*?$", "", url)
    fname = os.path.basename(urllib.parse.unquote(url))
    if not fname.strip():
        fname = "paste"
    if content_type:
        fname = mw.col.media.add_extension_based_on_mime(fname, content_type)

    return mw.col.media.write_data(fname, filecontents)


def _localizeNote(
    browser: Browser, note: Note, undo_start: int, client: HttpClient
) -> bool:
    for fld, val in note.items():
        # any remote links?
        files = mw.col.media.files_in_str(
            note.note_type()["id"], val, include_remote=True
        )
        found = False
        for file in files:
            if file.startswith("http://") or file.startswith("https://"):
                found = True
                break
            elif file.startswith("data:image"):
                found = True
                break

        if not found:
            continue

        # gather and rewrite
        for regex in mw.col.media.regexps:
            for match in re.finditer(regex, val):
                fname = match.group("fname")
                remote = re.match("(https?)://", fname.lower())
                if remote:
                    newName = _retrieveURL(fname, client)
                    val = val.replace(fname, newName)

                    # don't overburden the server(s)
                    time.sleep(1)
                elif fname.startswith("data:image"):
                    val = val.replace(
                        fname, browser.editor.inlinedImageToFilename(fname)
                    )

        note[fld] = val
        mw.col.update_note(note)
    mw.col.merge_undo_entries(undo_start)
    return True


def onMenuSetup(browser: Browser) -> None:
    act = QAction(browser)
    act.setText("Localize Media")
    mn = browser.form.menu_Notes
    mn.addSeparator()
    mn.addAction(act)
    act.triggered.connect(lambda b=browser: onLocalize(browser))


from aqt import gui_hooks

gui_hooks.browser_will_show.append(onMenuSetup)
