"""
-*- coding: utf-8 -*-
Author: RawToast
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Configure settings for the note types and source fields for the Japanese Support plugin here
"""

# If sets to True the plugin will work for ALL note types.
EFFECT_ALL_NOTES = False

# The note type(s) that the plugin will act upon. This is case insensitive. Add your own note types here, for
# example: NOTE_TYPES = ["japanese", "subs"]
# If EFFECT_ALL_NOTES is True, this has no effect
NOTE_TYPES = ["japanese"]

# Looks for Kanji in these fields. Replaces source fields in stats.py line 15
SOURCE_FIELDS = ["Expression", "Kanji"]


def isActiveNoteType(noteName):
    """
    Should bulk readings be added to the note type chosen?
    :param note: The selected card's note type
    :return: True if we should add readings to the notes
    """
    _result = False
    if not EFFECT_ALL_NOTES:
        for _note in NOTE_TYPES:
            if noteName in _note:
                _result = True
    else:
        _result = True

    return _result


