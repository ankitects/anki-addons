# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

def init():
    import japanese.model
    import japanese.furigana
    import japanese.reading
    import japanese.lookup
    import japanese.stats
    import japanese.bulkreading

from ankiqt import mw
mw.registerPlugin("Japanese Support", 172)

from anki.hooks import addHook
addHook('init', init)
