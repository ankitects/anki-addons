# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# The count update timer can fire during long-running DB operations in 1.2.8,
# which causes bugs. This plugin disables updating.
#

import sys
from ankiqt import mw
mw.statusView.countTimer.stop()
