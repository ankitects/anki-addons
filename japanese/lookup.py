# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Dictionary lookup support.
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import urllib, re
from anki.hooks import addHook
from ankiqt import mw
from ankiqt import ui

class Lookup(object):

    def __init__(self, main):
        self.main = main

    def selection(self, function):
        "Get the selected text and look it up with FUNCTION."
        text = unicode(self.main.mainWin.mainText.selectedText())
        text = text.strip()
        if "\n" in text:
            ui.utils.showInfo(_("Can't look up a selection with a newline."))
            return
        text = text.strip()
        if not text:
            ui.utils.showInfo(_("Empty selection."))
            return
        function(text)

    def edictKanji(self, text):
        self.edict(text, True)

    def edict(self, text, kanji=False):
        "Look up TEXT with edict."
        if kanji:
            x="M"
        else:
            x="U"
        baseUrl="http://www.csse.monash.edu.au/~jwb/cgi-bin/wwwjdic.cgi?1M" + x
        if self.isJapaneseText(text):
            baseUrl += "J"
        else:
            baseUrl += "E"
        url = baseUrl + urllib.quote(text.encode("utf-8"))
        qurl = QUrl()
        qurl.setEncodedUrl(url)
        QDesktopServices.openUrl(qurl)

    def alc(self, text):
        "Look up TEXT with ALC."
        newText = urllib.quote(text.encode("utf-8"))
        url = (
            "http://eow.alc.co.jp/" +
            newText +
            "/UTF-8/?ref=sa")
        qurl = QUrl()
        qurl.setEncodedUrl(url)
        QDesktopServices.openUrl(qurl)

    def isJapaneseText(self, text):
        "True if 70% of text is a Japanese character."
        total = len(text)
        if total == 0:
            return True
        jp = 0
        en = 0
        for c in text:
            if ord(c) >= 0x2E00 and ord(c) <= 0x9FFF:
                jp += 1
            if re.match("[A-Za-z]", c):
                en += 1
        if not jp:
            return False
        return ((jp + 1) / float(en + 1)) >= 1.0

def initLookup():
    if not getattr(mw, "lookup", None):
        mw.lookup = Lookup(mw)

def onLookupExpression():
    initLookup()
    try:
        mw.lookup.alc(mw.currentCard.fact['Expression'])
    except KeyError:
        ui.utils.showInfo(_("No expression in current card."))

def onLookupMeaning():
    initLookup()
    try:
        mw.lookup.alc(mw.currentCard.fact['Meaning'])
    except KeyError:
        ui.utils.showInfo(_("No meaning in current card."))

def onLookupEdictSelection():
    initLookup()
    mw.lookup.selection(mw.lookup.edict)

def onLookupEdictKanjiSelection():
    initLookup()
    mw.lookup.selection(mw.lookup.edictKanji)

def onLookupAlcSelection():
    initLookup()
    mw.lookup.selection(mw.lookup.alc)

def createMenu():
    ml = QMenu(mw.mainWin.menubar)
    ml.setTitle("Lookup")
    mw.mainWin.menuTools.addAction(ml.menuAction())
    mw.mainWin.menuLookup = ml
    # add actions
    a = QAction(mw)
    a.setText("...expression on alc")
    a.setShortcut("Ctrl+1")
    ml.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), onLookupExpression)
    a = QAction(mw)
    a.setText("...meaning on alc")
    a.setShortcut("Ctrl+2")
    ml.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), onLookupMeaning)
    a = QAction(mw)
    a.setText("...selection on alc")
    a.setShortcut("Ctrl+3")
    ml.addAction(a)
    ml.addSeparator()
    mw.connect(a, SIGNAL("triggered()"), onLookupAlcSelection)
    a = QAction(mw)
    a.setText("...word selection on edict")
    a.setShortcut("Ctrl+4")
    ml.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), onLookupEdictSelection)
    a = QAction(mw)
    a.setText("...kanji selection on edict")
    a.setShortcut("Ctrl+5")
    ml.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), onLookupEdictKanjiSelection)

def disableMenu():
    mw.mainWin.menuLookup.setEnabled(False)

def enableMenu():
    mw.mainWin.menuLookup.setEnabled(True)

addHook('disableCardMenuItems', disableMenu)
addHook('enableCardMenuItems', enableMenu)

createMenu()
