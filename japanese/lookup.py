# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Dictionary lookup support.
#

import urllib, re
from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

class Lookup(object):

    def __init__(self):
        pass

    def selection(self, function):
        "Get the selected text and look it up with FUNCTION."
        # lazily acquire selection by copying it into clipboard
        mw.web.triggerPageAction(QWebPage.Copy)
        text = mw.app.clipboard().mimeData().text()
        text = text.strip()
        if not text:
            showInfo(_("Empty selection."))
            return
        if "\n" in text:
            showInfo(_("Can't look up a selection with a newline."))
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
        mw.lookup = Lookup()

def _field(name):
    try:
        return mw.reviewer.card.note()[name]
    except:
        return

def onLookupExpression(name="Expression"):
    initLookup()
    txt = _field(name)
    if not txt:
        return showInfo("No %s in current note." % name)
    mw.lookup.alc(txt)

def onLookupMeaning():
    onLookupExpression("Meaning")

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
    ml = QMenu()
    ml.setTitle("Lookup")
    mw.form.menuTools.addAction(ml.menuAction())
    # make it easier for other plugins to add to the menu
    mw.form.menuLookup = ml
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

# def disableMenu():
#     mw.mainWin.menuLookup.setEnabled(False)

# def enableMenu():
#     mw.mainWin.menuLookup.setEnabled(True)

# addHook('disableCardMenuItems', disableMenu)
# addHook('enableCardMenuItems', enableMenu)

createMenu()
