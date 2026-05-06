import threading
from typing import Dict, Set

MAX_WORKERS = 5
DOMAIN_LOCKS: Dict[str, threading.Lock] = {}
DOMAIN_REGISTRY_LOCK = threading.Lock()
COLLECTION_LOCK = threading.Lock()
PAUSE_EVENT = threading.Event()
PAUSE_EVENT.set()

# Domains that should be ignored by the localization process
EXCLUDED_DOMAINS: Set[str] = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "vimeo.com",
    "player.vimeo.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com"
}
