import re
import urllib.parse
from anki.notes import Note, NoteId
from anki.httpclient import HttpClient
from aqt import mw
from .constants import COLLECTION_LOCK, PAUSE_EVENT, EXCLUDED_DOMAINS
from .media_handler import retrieve_url

def process_note(nid: NoteId, stats, client: HttpClient) -> None:
    try:
        PAUSE_EVENT.wait()
        with COLLECTION_LOCK:
            note = mw.col.get_note(nid)
        
        if _localize_note_content(nid, note, client, stats):
            stats.log_success(nid)
    except Exception as e:
        stats.log_error(nid, f"Failed note {nid}: {str(e)}")

def is_excluded(url: str) -> bool:
    """Checks if the URL domain is in the EXCLUDED_DOMAINS list."""
    try:
        domain = urllib.parse.urlparse(url).netloc.lower()
        # Remove 'www.' for consistent checking if needed, or match exactly
        return any(domain == d or domain.endswith("." + d) for d in EXCLUDED_DOMAINS)
    except Exception:
        return False

def _localize_note_content(nid: NoteId, note: Note, client: HttpClient, stats) -> bool:
    changed = False
    all_resolved = True
    
    for fld in note.keys():
        val = note[fld]
        orig_val = val
        
        # 1. Normalize audio tags
        val = re.sub(
            r'<audio[^>]*>\s*<source[^>]*src="([^"]+)"[^>]*>\s*</audio>',
            r'[sound:\1]', val, flags=re.IGNORECASE
        )

        # 2. Identify remote files
        with COLLECTION_LOCK:
            files = mw.col.media.files_in_str(note.note_type()["id"], val, include_remote=True)
            
        for fname in files:
            if fname.startswith(("http://", "https://")):
                # FIX: Check if domain is excluded (e.g. YouTube)
                if is_excluded(fname):
                    continue
                    
                new_name = retrieve_url(nid, fname, client, stats)
                if new_name:
                    # Safe replacement using regex escape to avoid partial matches
                    val = re.sub(re.escape(fname), new_name, val)
                else:
                    all_resolved = False

        if val != orig_val:
            note[fld] = val
            changed = True

    if changed:
        with COLLECTION_LOCK:
            mw.col.update_note(note)
    return all_resolved
