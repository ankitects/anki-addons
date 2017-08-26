# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Alter fonts and position of text randomly

fontFaces = [u"Arial", u"Times New Roman", u"Courier"]
fontColours = ["#000", "#00f", "#0f0", "#f00"]
# start at maximum of 70% to the right
maxRight = 70
maxTop = 0
maxBottom = 30

import random
import re
from anki.hooks import addHook
from ankiqt import mw
from ankiqt import ui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

saved = {}

def alter(css, card):
    if mw.state == "showQuestion":
        saved['face'] = random.choice(fontFaces)
        saved['col'] = random.choice(fontColours)
        saved['hoz'] = random.uniform(0, maxRight)
        saved['vert'] = random.uniform(maxTop, maxBottom)
    # else:
    #     saved['vert'] = 0
    css = re.sub('font-family:"(.+?)"', 'font-family:"%s"' % saved['face'], css)
    css = re.sub('color:(.+?);', 'color:%s;' % saved['col'], css)
    css = re.sub('text-align:.+?;', """
text-align: left; margin-left: %d%%; margin-top: %d%%""" %
                     (saved['hoz'], saved['vert']), css)
    return css

addHook("addStyles", alter)
