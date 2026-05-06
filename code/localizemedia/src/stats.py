import threading
from typing import Sequence, List, Set
from anki.notes import NoteId
from aqt.operations import OpChanges

class LocalizeStats:
    def __init__(self, nids: Sequence[NoteId]):
        self.success_count = 0
        self.fail_count = 0
        self.aborted = False
        self.errors: List[str] = []
        self.pending_nids = list(nids)
        self.failed_nids: Set[NoteId] = set()
        self.lock = threading.Lock()
        self.changes = OpChanges()

    def log_success(self, nid: NoteId):
        with self.lock:
            self.success_count += 1
            if nid in self.pending_nids:
                self.pending_nids.remove(nid)
            self.changes.note_text = True

    def log_error(self, nid: NoteId, message: str):
        with self.lock:
            self.fail_count += 1
            self.errors.append(message)
            self.failed_nids.add(nid)
            if nid in self.pending_nids:
                self.pending_nids.remove(nid)