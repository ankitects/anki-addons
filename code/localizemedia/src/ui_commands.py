import time
import anki.errors
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Sequence
from anki.notes import NoteId
from anki.httpclient import HttpClient
from aqt import mw, gui_hooks
from aqt.browser.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *
from aqt.utils import showInfo

from .constants import MAX_WORKERS, PAUSE_EVENT
from .stats import LocalizeStats
from .note_logic import process_note

def on_localize_triggered(browser: Browser) -> None:
    nids = browser.selected_notes()
    if not nids:
        showInfo("Please select some notes.")
        return
    execute_localization(browser, nids)

def execute_localization(browser: Browser, nids: Sequence[NoteId], existing_stats=None) -> None:
    stats = existing_stats or LocalizeStats(nids)
    PAUSE_EVENT.set()

    def background_op(col) -> LocalizeStats:
        if not stats.pending_nids:
            return stats

        # Mark the start for undo
        undo_start = mw.col.add_custom_undo_entry("Localize Media")
        client = HttpClient()
        time_window = deque(maxlen=20)
        last_time = time.time()

        try:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [executor.submit(process_note, nid, stats, client) for nid in stats.pending_nids]
                for i, future in enumerate(futures):
                    if mw.progress.want_cancel():
                        stats.aborted = True
                        executor.shutdown(wait=True, cancel_futures=True)
                        break
                    future.result()
                    
                    # Update progress
                    elapsed = time.time() - last_time
                    time_window.append(elapsed)
                    last_time = time.time()
                    avg = sum(time_window) / len(time_window)
                    eta = time.strftime('%H:%M:%S', time.gmtime(avg * (len(futures) - (i+1))))
                    mw.taskman.run_on_main(lambda m=f"Processing {i+1}/{len(futures)} (ETA: {eta})": mw.progress.update(m))
        finally:
            # FIX: Only merge if not aborted and suppress the "target undo op not found" error
            if not stats.aborted:
                try:
                    mw.col.merge_undo_entries(undo_start)
                except (anki.errors.InvalidInput, Exception):
                    # The undo stack was modified by something else or the ID is no longer valid.
                    # We ignore this as the primary note updates have already been committed.
                    pass
        
        return stats

    def on_finished(stats: LocalizeStats) -> None:
        if stats.aborted:
            msg = f"Localization paused/cancelled. {stats.success_count} notes processed."
        else:
            msg = f"Done. Success: {stats.success_count}, Fail: {stats.fail_count}"
        
        box = QMessageBox(browser)
        box.setWindowTitle("Localize Media")
        box.setText(msg)
        
        resume_btn = None
        if stats.pending_nids:
            resume_btn = box.addButton("Resume Remaining", QMessageBox.ButtonRole.AcceptRole)
        
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        
        if resume_btn and box.clickedButton() == resume_btn:
            execute_localization(browser, stats.pending_nids, stats)

    CollectionOp(parent=browser, op=background_op).success(on_finished).run_in_background()

def setup_menu(browser: Browser) -> None:
    act = QAction("Localize Media", browser)
    browser.form.menu_Notes.addAction(act)
    act.triggered.connect(lambda: on_localize_triggered(browser))

gui_hooks.browser_will_show.append(setup_menu)
