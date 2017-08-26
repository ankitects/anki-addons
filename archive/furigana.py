# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin is a hack that overrides the default question/answer format for
# Japanese models to show furigana above the kanji. It will only work on
# Japanese which has been added after Anki 0.9.9.8.
#
# Version 2: use CSS. Much more robust, and a candidate for inclusion in Anki
# in the future.

import re
from ankiqt import mw
from anki.hooks import addHook
from anki.utils import hexifyID

def filterAnswer(txt):
    if (not "Japanese" in mw.currentCard.fact.model.tags and
        not "Mandarin" in mw.currentCard.fact.model.tags and
        not "Cantonese" in mw.currentCard.fact.model.tags):
        return txt
    if not "[" in mw.currentCard.fact.get('Reading', ""):
        return txt
    # get the reading field
    read = [x.id for x in mw.currentCard.fact.model.fieldModels
            if x.name == "Reading"]
    if not read:
        return txt
    read = '<span class="fm%s">' % hexifyID(read[0])
    # replace
    def repl(match):
        return read + rubify(match.group(1)) + "</span>"
    txt = re.sub("%s(.*?)</span>" % read, repl, txt)
    return txt

def rubify(txt):
    expr = '<span class="fm%s">' % hexifyID(
        [x.id for x in mw.currentCard.fact.model.fieldModels
         if x.name == "Expression"][0])
    read = '<span class="fm%s">' % hexifyID(
        [x.id for x in mw.currentCard.fact.model.fieldModels
         if x.name == "Reading"][0])
    txt = re.sub("([^ >]+?)\[(.+?)\]", """\
<span class="ezRuby" title="\\2">\\1</span>""", txt)
    txt = re.sub("> +", ">", txt)
    txt = re.sub(" +<", "<", txt)
    return txt

def addCss():
    # based on http://welkin.s60.xrea.com/css_labo/Ruby-CSS_DEMO3.html
    mw.bodyView.buffer += """
<style>
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
</style>"""

addHook('drawAnswer', filterAnswer)
addHook('preFlushHook', addCss)
