# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Furigana support.
#

import re
from anki.utils import hexifyID
from anki.hooks import addHook

MODELTAG = "Japanese"
READING = "Reading"
EXPRESSION = "Expression"

# If set to true, the plugin will look for any furigana on the card, instead
# of just looking in the reading field.
FURI_OUTSIDE_READING = True

# The following setting changes the behaviour of %(Reading)s in the question.
# If set to 1, hide the kanji and show only the reading
# If set to 2, show both the kanji and reading
# If set to 3, show the kanji and show the reading in a tooltip
READING_IN_QUESTION = 1

def getReading(card):
    if not "[" in card.fact.get(READING, ""):
        return
    # get the reading field
    read = [x.id for x in card.fact.model.fieldModels
            if x.name == READING]
    if not read:
        return
    return '<span class="fm%s">' % hexifyID(read[0])

def filterQuestion(txt, card, transform='question'):
    if READING_IN_QUESTION == 1 and transform == 'question':
        fn = removeKanji
    else:
        fn = lambda x: rubify(x, transform)
    if not MODELTAG in card.fact.model.tags:
        return txt
    if not FURI_OUTSIDE_READING:
        reading = getReading(card)
        if not reading:
            return txt
    # replace
    def repl(match):
        return reading + fn(match.group(1)) + "</span>"
    if FURI_OUTSIDE_READING:
        txt = fn(txt)
    else:
        txt = re.sub("%s(.*?)</span>" % reading, repl, txt)
    return txt

def filterAnswer(txt, card):
    return filterQuestion(txt, card, transform="answer")

def replNoSound(new):
    def repl(m):
        return match.group(int(m.group(1)))
    def fn(match):
        if match.group(2).startswith("sound:"):
            return match.group(0)
        return new.replace("\\1", match.group(1)).replace("\\2", match.group(2))
    return fn

def removeKanji(txt):
    def repl(match):
        txt = match.group(2)
        if txt.startswith("sound:"):
            return match.group(0)
        return txt.replace(" ", "")
    txt = re.sub(" ?([^ >]+?)\[(.+?)\]", repl, txt)
    return txt

def rubify(txt, type):
    if type == "question" and READING_IN_QUESTION == 3:
        txt = re.sub(" ?([^ >]+?)\[(.+?)\]",
                     replNoSound('<span class=tip>\\1<span>\\2</span></span>'),
                     txt)
    else:
        txt = re.sub(" ?([^ >]+?)\[(.+?)\]",
                     replNoSound('<span class="ezRuby" title="\\2">\\1</span>'),
                     txt)
    return txt

def addCss(styles, card):
    # based on http://welkin.s60.xrea.com/css_labo/Ruby-CSS_DEMO3.html
    styles += """
/* Ruby Base */
html>/* */body .ezRuby {
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  margin: 0;
  padding: 0;
  border: none;
  display: inline-block;
}

/* Ruby Text */
html>/* */body .ezRuby:before {
  font-size: 0.64em;
  font-weight: normal;
  line-height: 1.2;
  text-decoration: none;
  display: block;
  content: attr(title);
}

/* Adapt to your site's CSS */
html>/* */body .ezRuby:hover{
  color: #000000;
  background-color: #FFFFCC;
}

html>/* */body .ezRuby:hover:before{
  background-color: #FFCC66;
}


.tip {
	position: relative;
}

.tip:hover {
	background: #77f;
	color: #fff;
}

.tip span {
	display: none;
	position: absolute;
	top: 40px;
	left: -20px;
	padding: 5px;
	z-index: 100;
	background: #000;
	color: #fff;
        font-size: 1em;
        width: 200px;
}

span:hover.tip span {
	display: block;
}
"""
    return styles

addHook('drawQuestion', filterQuestion)
addHook('drawAnswer', filterAnswer)
addHook('addStyles', addCss)
