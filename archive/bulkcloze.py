# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatically generate cloze deletions for all the cards in a deck. By
# default it generates a cloze from fields 1->2 and 3->4. To change this,
# adjust the FIELDS below
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw
from ankiqt import ui
from anki.hooks import addHook
import re

# generate 1->2 and 3->4
FIELDS = (1,3)
# example: generate 2->3
#FIELDS = (2,)

def onCloze(browser):
    browser.onFirstCard()
    browser.onFact()
    l = len(browser.model.cards) - 1
    c = 0
    cont = True
    while True:
        mw.app.processEvents()
        for f in FIELDS:
            w = browser.editor.fieldsGrid.itemAtPosition(f-1, 1).widget()
            w2 = browser.editor.fieldsGrid.itemAtPosition(f, 1).widget()
            if w2.toPlainText():
                continue
            w.setFocus()
            if not browser.editor.onCloze():
                cont = False
                break
        if c == l or not cont:
            break
        c += 1
        browser.onNextCard()

# hacked to return status info
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
    # check if there's anything to change
    if not re.search("\[.+?\]", unicode(src.toPlainText())):
        ui.utils.showInfo(
            _("You didn't specify anything to occlude."),
            help="ClozeDeletion",
            parent=self.parent)
        return
    # create
    s = unicode(src.toHtml())
    def repl(match):
        exp = ""
        if match.group(2):
            exp = match.group(2)
        return '<font color="%s"><b>[...%s]</b></font>' % (
            ui.facteditor.clozeColour, exp)
    new = re.sub(re1, repl, s)
    old = re.sub(re2, '<font color="%s"><b>\\1</b></font>'
                 % ui.facteditor.clozeColour, s)
    src.setHtml(new)
    dst.setHtml(old)
    self.lastCloze = (oldSrc, unicode(src.toHtml()),
                      unicode(dst.toHtml()))
    self.saveFields()
    return True

def onMenuSetup(browser):
    act = QAction(mw)
    act.setText("Generate Clozes")
    browser.dialog.menuActions.addSeparator()
    browser.dialog.menuActions.addAction(act)
    browser.connect(act, SIGNAL("triggered()"), lambda b=browser: onCloze(b))

addHook("editor.setupMenus", onMenuSetup)
ui.facteditor.FactEditor.onCloze = onClozeRepl
