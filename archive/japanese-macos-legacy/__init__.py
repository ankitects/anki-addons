# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt.utils import isMac
if not isMac:
    raise Exception("You have downloaded a Mac-only version of this add-on.")
from . import model, reading, lookup, stats, bulkreading
