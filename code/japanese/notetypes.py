"""
-*- coding: utf-8 -*-
Author: RawToast
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Configure settings for the note types and source fields for the Japanese
Support plugin here

"""

from aqt import mw

config = mw.addonManager.getConfig(__name__)
noteTypes = [noteType.lower() for noteType in config["noteTypes"]]


def isJapaneseNoteType(noteName: str) -> bool:
    noteName = noteName.lower()
    for allowedString in noteTypes:
        if allowedString in noteName:
            return True

    return False
