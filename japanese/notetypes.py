"""
-*- coding: utf-8 -*-
Author: RawToast
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Configure settings for the note types and source fields for the Japanese
Support plugin here

WARNING: By default, this add-on operates on note types that contain the word
"Japanese" in their name. You can alter this by changing the settings below,
but please be aware that this will break things if you share your deck with
others. So please only consider changing these options if you're not planning
to share your deck.
"""

# If sets to True the plugin will work for ALL note types.
AFFECT_ALL_NOTES = False

# The note type(s) that the plugin will act upon. This is case insensitive. Add your own note types here, for
# example: NOTE_TYPES = ["japanese", "subs"]
# If EFFECT_ALL_NOTES is True, this has no effect
NOTE_TYPES = ["japanese"]

# Looks for Kanji in these fields. Replaces source fields in stats.py line 15
SOURCE_FIELDS = ["Expression", "Kanji"]

def isJapaneseNoteType(noteName):
    """
    Should bulk readings be added to the note type chosen?
    :param note: The selected card's note type
    :return: True if we should add readings to the notes
    """
    if AFFECT_ALL_NOTES:
        return True

    noteName = noteName.lower()
    for allowedString in NOTE_TYPES:
        if allowedString in noteName:
            return True

    return False
