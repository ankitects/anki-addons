# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Furigana support.
#

import re
from anki.utils import hexifyID
from anki.hooks import addHook

NO_KANJI_IN_QUESTION = True
MODELTAG = "Japanese"
READING = "Reading"
EXPRESSION = "Expression"

def getReading(card):
    if not MODELTAG in card.fact.model.tags:
        return
    if not "[" in card.fact.get(READING, ""):
        return
    # get the reading field
    read = [x.id for x in card.fact.model.fieldModels
            if x.name == READING]
    if not read:
        return
    return '<span class="fm%s">' % hexifyID(read[0])

def filterQuestion(txt, card, transform='question'):
    reading = getReading(card)
    if not reading:
        return txt
    if NO_KANJI_IN_QUESTION and transform == 'question':
        transform = removeKanji
    else:
        transform = rubify
    # replace
    def repl(match):
        return reading + transform(match.group(1)) + "</span>"
    txt = re.sub("%s(.*?)</span>" % reading, repl, txt)
    return txt

def filterAnswer(txt, card):
    return filterQuestion(txt, card, transform="answer")

def removeKanji(txt):
    txt = re.sub("([^ >]+?)\[(.+?)\]", "\\2", txt)
    txt = txt.replace(" ", "")
    return txt

def rubify(txt):
    txt = re.sub("([^ >]+?)\[(.+?)\]",
                 '<span class="ezRuby" title="\\2">\\1</span>',
                 txt)
    txt = re.sub("> +", ">", txt)
    txt = re.sub(" +<", "<", txt)
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
"""
    return styles

addHook('drawQuestion', filterQuestion)
addHook('drawAnswer', filterAnswer)
addHook('addStyles', addCss)
