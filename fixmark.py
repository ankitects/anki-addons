# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Fix the mark command while reviewing in beta5. Please remove for future
# betas.
#

from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap
def fixMark(self):
    self.card.note().flush()
Reviewer.onMark = wrap(Reviewer.onMark, fixMark)
