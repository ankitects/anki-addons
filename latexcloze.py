# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Fixes cloze generation in LaTeX. This code is a hack. :-)
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import ui
from anki.utils import tidyHTML
import re

clozeColour = "#0000ff"

def onClozeRepl(self):
    src = self.focusedEdit()
    if not src:
        return
    re1 = "\[(?:<.+?>)?.+?(:(.+?))?\](?:</.+?>)?"
    re2 = "\[(?:<.+?>)?(.+?)(:.+?)?\](?:</.+?>)?"
    # add brackets because selected?
    cursor = src.textCursor()
    oldSrc = None
    if cursor.hasSelection():
        oldSrc = src.toHtml()
        s = cursor.selectionStart()
        e = cursor.selectionEnd()
        cursor.setPosition(e)
        cursor.insertText("]]")
        cursor.setPosition(s)
        cursor.insertText("[[")
        re1 = "\[" + re1 + "\]"
        re2 = "\[" + re2 + "\]"
    dst = None
    for field in self.fact.fields:
        w = self.fields[field.name][1]
        if w.hasFocus():
            dst = False
            continue
        if dst is False:
            dst = w
            break
    if not dst:
        dst = self.fields[self.fact.fields[0].name][1]
        if dst == w:
            return
    # check if there's alredy something there
    if not oldSrc:
        oldSrc = src.toHtml()
    oldDst = dst.toHtml()
    if unicode(dst.toPlainText()):
        if (self.lastCloze and
            self.lastCloze[1] == oldSrc and
            self.lastCloze[2] == oldDst):
            src.setHtml(self.lastCloze[0])
            dst.setHtml("")
            self.lastCloze = None
            self.saveFields()
            return
        else:
            ui.utils.showInfo(
                _("Next field must be blank."),
                help="ClozeDeletion",
                parent=self.parent)
            return
    # escape known
    oldtxt = unicode(src.toPlainText())
    html = unicode(src.toHtml())
    reg = "\[(/?(latex|\$|\$\$))\]"
    repl = "{\\1}"
    txt = re.sub(reg, repl, oldtxt)
    html = re.sub(reg, repl, html)
    haveLatex = txt != oldtxt
    # check if there's anything to change
    if not re.search("\[.+?\]", txt):
        ui.utils.showInfo(
            _("You didn't specify anything to occlude."),
            help="ClozeDeletion",
            parent=self.parent)
        return
    # create
    ses = tidyHTML(html).split("<br>")
    news = []
    olds = []
    for s in ses:
        haveLatex = ("latex" in s or "{$}" in s or "{$$}" in s)
        def repl(match):
            exp = ""
            if match.group(2):
                exp = match.group(2)
            if haveLatex:
                return "\\textbf{[...%s]}" % (exp)
            else:
                return '<font color="%s"><b>[...%s]</b></font>' % (
                    clozeColour, exp)
        new = re.sub(re1, repl, s)
        if haveLatex:
            old = re.sub(re2, "{\\\\bf{}\\1\\\\rm{}}", s)
        else:
            old = re.sub(re2, '<font color="%s"><b>\\1</b></font>'
                         % clozeColour, s)
        reg = "\{(/?(latex|\$|\$\$))\}"
        repl = "[\\1]"
        new = re.sub(reg, repl, new)
        old = re.sub(reg, repl, old)
        news.append(new)
        olds.append(old)
    src.setHtml("<br>".join(news))
    dst.setHtml("<br>".join(olds))
    self.lastCloze = (oldSrc, unicode(src.toHtml()),
                      unicode(dst.toHtml()))
    self.saveFields()

ui.facteditor.FactEditor.onCloze = onClozeRepl
