"""
-*- coding: utf-8 -*-
Author: RawToast
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Configure settings for the note types and source fields for the Japanese
Support plugin here

"""

from . import cfg; config = cfg.load()

def isJapaneseNoteType(noteName):
    noteName = noteName.lower()
    for allowedString in config["noteTypes"]:
        if allowedString in noteName:
            return True

    return False
