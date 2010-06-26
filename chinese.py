# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin adds Mandarin and Cantonese models, and implements basic reading
# generation via unihan.db. It will be obsoleted by the Mandarin and Cantonese
# toolkit in the future.
#

import sys, os, re
from anki.utils import findTag, stripHTML
from anki.hooks import addHook
from anki.db import *

cantoneseTag = "Cantonese"
mandarinTag = "Mandarin"
srcFields = ('Expression') # works with n pairs
dstFields = ('Reading')

# Models
##########################################################################

from anki.models import Model, CardModel, FieldModel
import anki.stdmodels

def MandarinModel():
   m = Model(_("Mandarin"))
   f = FieldModel(u'Expression')
   f.quizFontSize = 72
   m.addFieldModel(f)
   m.addFieldModel(FieldModel(u'Meaning', False, False))
   m.addFieldModel(FieldModel(u'Reading', False, False))
   m.addCardModel(CardModel(u"Recognition",
                            u"%(Expression)s",
                            u"%(Reading)s<br>%(Meaning)s"))
   m.addCardModel(CardModel(u"Recall",
                            u"%(Meaning)s",
                            u"%(Expression)s<br>%(Reading)s",
                            active=False))
   m.tags = u"Mandarin"
   return m

anki.stdmodels.models['Mandarin'] = MandarinModel

def CantoneseModel():
    m = Model(_("Cantonese"))
    f = FieldModel(u'Expression')
    f.quizFontSize = 72
    m.addFieldModel(f)
    m.addFieldModel(FieldModel(u'Meaning', False, False))
    m.addFieldModel(FieldModel(u'Reading', False, False))
    m.addCardModel(CardModel(u"Recognition",
                             u"%(Expression)s",
                             u"%(Reading)s<br>%(Meaning)s"))
    m.addCardModel(CardModel(u"Recall",
                             u"%(Meaning)s",
                             u"%(Expression)s<br>%(Reading)s",
                             active=False))
    m.tags = u"Cantonese"
    return m

anki.stdmodels.models['Cantonese'] = CantoneseModel

# Controller
##########################################################################

class UnihanController(object):

    def __init__(self, target):
        if sys.platform.startswith("win32"):
           base = unicode(os.path.dirname(os.path.abspath(__file__)),
                          "mbcs")
        else:
           base = os.path.dirname(os.path.abspath(__file__))
        self.engine = create_engine(u"sqlite:///" + os.path.abspath(
            os.path.join(base, "unihan.db")),
                                    echo=False, strategy='threadlocal')
        self.session = sessionmaker(bind=self.engine,
                                    autoflush=False,
                                    autocommit=True)
        self.type = target

    def reading(self, text):
        text = stripHTML(text)
        result = []
        s = SessionHelper(self.session())
        for c in text:
            n = ord(c)
            ret = s.scalar("select %s from unihan where id = :id"
                           % self.type, id=n)
            if ret:
                result.append(self.formatMatch(ret))
        return u" ".join(result)

    def formatMatch(self, match):
        m = match.split(" ")
        if len(m) == 1:
            return m[0]
        return "{%s}" % (",".join(m))

# Double click to remove handler
##########################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt.ui.facteditor import FactEdit

# this shouldn't be necessary if/when we move away from kakasi
def mouseDoubleClickEvent(self, evt):
    t = self.parent.fact.model.tags.lower()
    if (not "japanese" in t and
        not "mandarin" in t and
        not "cantonese" in t):
        return QTextEdit.mouseDoubleClickEvent(self,evt)
    r = QRegExp("\\{(.*[|,].*)\\}")
    r.setMinimal(True)

    mouseposition = self.textCursor().position()

    blockoffset = 0
    result = r.indexIn(self.toPlainText(), 0)

    found = ""

    while result != -1:
        if mouseposition > result and mouseposition < result + r.matchedLength():
            mouseposition -= result + 1
            frompos = 0
            topos = 0

            string = r.cap(1)
            offset = 0
            bits = re.split("[|,]", unicode(string))
            for index in range(0, len(bits)):
                offset += len(bits[index]) + 1
                if mouseposition < offset:
                    found = bits[index]
                    break
            break

        blockoffset= result + r.matchedLength()
        result = r.indexIn(self.toPlainText(), blockoffset)

    if found == "":
        return QTextEdit.mouseDoubleClickEvent(self,evt)
    self.setPlainText(self.toPlainText().replace(result, r.matchedLength(), found))

FactEdit.mouseDoubleClickEvent = mouseDoubleClickEvent

# Hooks
##########################################################################

class ChineseGenerator(object):

    def __init__(self):
        self.unihan = None

    def toReading(self, type, val):
        try:
            if not self.unihan:
                self.unihan = UnihanController(type)
            else:
                self.unihan.type = type
            return self.unihan.reading(val)
        except:
            return u""

unihan = ChineseGenerator()

def onFocusLost(fact, field):
    if field.name not in srcFields:
        return
    if findTag(cantoneseTag, fact.model.tags):
        type = "cantonese"
    elif findTag(mandarinTag, fact.model.tags):
        type = "mandarin"
    else:
        return

    idx = srcFields.index(field.name)
    dstField = dstFields[idx]

    try:
        if fact[dstField]:
            return
    except:
        return
    fact[dstField] = unihan.toReading(type, field.value)

addHook('fact.focusLost', onFocusLost)

from ankiqt import mw
mw.registerPlugin("Basic Chinese Support", 171)
