import os
import re
import time
import random
import threading
import urllib.parse
from typing import Optional, Dict
from anki.httpclient import HttpClient
from aqt import mw
from .constants import DOMAIN_LOCKS, DOMAIN_REGISTRY_LOCK, COLLECTION_LOCK, PAUSE_EVENT

# Session cache to avoid re-downloading the same URL in one batch
DOWNLOAD_CACHE: Dict[str, str] = {}

def normalize_url(url: str) -> str:
    """Ensures URL is properly quoted, specifically handling the '&' issue."""
    try:
        parts = urllib.parse.urlsplit(url)
        # Re-quote the path and query to ensure special characters are escaped
        path = urllib.parse.quote(urllib.parse.unquote(parts.path))
        query = urllib.parse.quote(urllib.parse.unquote(parts.query), safe='=&')
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))
    except Exception:
        return url

def get_domain_lock(url: str) -> threading.Lock:
    try:
        domain = urllib.parse.urlparse(url).netloc
    except Exception:
        domain = "unknown"
    with DOMAIN_REGISTRY_LOCK:
        if domain not in DOMAIN_LOCKS:
            DOMAIN_LOCKS[domain] = threading.Lock()
        return DOMAIN_LOCKS[domain]

def retrieve_url(nid: int, url: str, client: HttpClient, stats) -> Optional[str]:
    if url in DOWNLOAD_CACHE:
        return DOWNLOAD_CACHE[url]

    norm_url = normalize_url(url)
    domain_lock = get_domain_lock(norm_url)
    filecontents = None
    content_type = None
    
    with domain_lock:
        for attempt in range(5):
            PAUSE_EVENT.wait()
            try:
                with client.get(norm_url) as response:
                    if response.status_code == 200:
                        filecontents = response.content
                        content_type = response.headers.get("content-type")
                        time.sleep(random.uniform(0.1, 0.3))
                        break
                    elif response.status_code == 404: 
                        return None
                    elif response.status_code in (429, 503):
                        time.sleep((2 ** attempt) + random.random())
            except Exception as e:
                if attempt == 4:
                    stats.log_error(nid, f"Network error: {url} ({str(e)})")
                    return None
                time.sleep(0.5)

    if not filecontents: 
        return None

    with COLLECTION_LOCK:
        clean_url = re.sub(r"\?.*?$", "", url)
        fname = os.path.basename(urllib.parse.unquote(clean_url)) or "download"
        if content_type:
            fname = mw.col.media.add_extension_based_on_mime(fname, content_type)
        new_name = mw.col.media.write_data(fname, filecontents)
        DOWNLOAD_CACHE[url] = new_name
        return new_name
