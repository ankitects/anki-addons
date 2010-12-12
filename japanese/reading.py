# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatic reading generation with kakasi and mecab.
# See http://ichi2.net/anki/wiki/JapaneseSupport
#

import sys, os, platform, re, subprocess
from anki.utils import findTag, stripHTML
from anki.hooks import addHook

# disable to use kakasi only
USE_MECAB=True
# look for mecab&kakasi in the folder anki is being run from
WIN32_READING_DIR=os.path.dirname(os.path.abspath(sys.argv[0]))

modelTag = "Japanese"
srcFields = ['Expression']
dstFields = ['Reading']

if USE_MECAB:
    kakasiCmd = ["kakasi", "-isjis", "-osjis", "-u", "-JH", "-KH"]
else:
    kakasiCmd = ["kakasi", "-isjis", "-osjis", "-u", "-JH", "-p"]
mecabCmd = ["mecab", '--node-format=%m[%f[7]] ', '--eos-format=\n',
            '--unk-format=%m[] ']

def escapeText(text):
    # strip characters that trip up kakasi/mecab
    text = text.replace("\n", " ")
    text = text.replace(u'\uff5e', "~")
    text = re.sub("<br( /)?>", "---newline---", text)
    text = stripHTML(text)
    text = text.replace("---newline---", "<br>")
    return text

if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    try:
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    except:
        si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
else:
    si = None

# Mecab
##########################################################################

class MecabController(object):

    def __init__(self):
        self.mecab = None

    def setup(self):
        if sys.platform == "win32":
            dir = WIN32_READING_DIR
            os.environ['PATH'] += (";%s\\mecab\\bin" % dir)
            os.environ['MECABRC'] = ("%s\\mecab\\etc\\mecabrc" % dir)
        elif sys.platform.startswith("darwin"):
            dir = os.path.dirname(os.path.abspath(__file__))
            os.environ['PATH'] += ":" + dir + "/osx/mecab/bin"
            os.environ['MECABRC'] = dir + "/osx/mecab/etc/mecabrc"
            os.environ['DYLD_LIBRARY_PATH'] = dir + "/osx/mecab/bin"
            os.chmod(dir + "/osx/mecab/bin/mecab", 0755)

    def ensureOpen(self):
        if not self.mecab:
            self.setup()
            try:
                self.mecab = subprocess.Popen(
                    mecabCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=si)
            except OSError:
                raise Exception(_("Please install mecab"))

    def reading(self, expr):
        self.ensureOpen()
        expr = escapeText(expr)
        self.mecab.stdin.write(expr.encode("euc-jp", "ignore")+'\n')
        self.mecab.stdin.flush()
        expr = unicode(self.mecab.stdout.readline().rstrip('\r\n'), "euc-jp")
        out = []
        for node in expr.split(" "):
            if not node:
                break
            (kanji, reading) = re.match("(.+)\[(.*)\]", node).groups()
            # hiragana, punctuation, not japanese, or lacking a reading
            if kanji == reading or not reading:
                out.append(kanji)
                continue
            # katakana
            if kanji == kakasi.reading(reading):
                out.append(kanji)
                continue
            # convert to hiragana
            reading = kakasi.reading(reading)
            # ended up the same
            if reading == kanji:
                out.append(kanji)
                continue
            # don't add readings of numbers
            if kanji in u"一二三四五六七八九十０１２３４５６７８９":
                out.append(kanji)
                continue
            # strip matching characters and beginning and end of reading and kanji
            # reading should always be at least as long as the kanji
            placeL = 0
            placeR = 0
            for i in range(1,len(kanji)):
                if kanji[-i] != reading[-i]:
                    break
                placeR = i
            for i in range(0,len(kanji)-1):
                if kanji[i] != reading[i]:
                    break
                placeL = i+1
            if placeL == 0:
                if placeR == 0:
                    out.append(" %s[%s]" % (kanji, reading))
                else:
                    out.append(" %s[%s]%s" % (
                        kanji[:-placeR], reading[:-placeR], reading[-placeR:]))
            else:
                if placeR == 0:
                    out.append("%s %s[%s]" % (
                        reading[:placeL], kanji[placeL:], reading[placeL:]))
                else:
                    out.append("%s %s[%s]%s" % (
                        reading[:placeL], kanji[placeL:-placeR],
                        reading[placeL:-placeR], reading[-placeR:]))
        fin = u""
        for c, s in enumerate(out):
            if c < len(out) - 1 and re.match("^[A-Za-z0-9]+$", out[c+1]):
                s += " "
            fin += s
        return fin.strip()

# Kakasi
##########################################################################

class KakasiController(object):

    def __init__(self):
        self.kakasi = None

    def setup(self):
        if sys.platform == "win32":
            dir = WIN32_READING_DIR
            os.environ['PATH'] += (";%s\\kakasi\\bin" % dir)
            os.environ['ITAIJIDICT'] = ("%s\\kakasi\dic\\itaijidict" %
                                        dir)
            os.environ['KANWADICT'] = ("%s\\kakasi\\dic\\kanwadict" % dir)
        elif sys.platform.startswith("darwin"):
            dir = os.path.dirname(os.path.abspath(__file__))
            os.environ['PATH'] += ":" + dir + "/osx/kakasi"
            os.environ['ITAIJIDICT'] = dir + "/osx/kakasi/itaijidict"
            os.environ['KANWADICT'] = dir + "/osx/kakasi/kanwadict"
            os.chmod(dir + "/osx/kakasi/kakasi", 0755)

    def ensureOpen(self):
        if not self.kakasi:
            self.setup()
            try:
                self.kakasi = subprocess.Popen(
                    kakasiCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=si)
            except OSError:
                raise Exception(_("Please install kakasi"))

    def reading(self, expr):
        self.ensureOpen()
        expr = escapeText(expr)
        self.kakasi.stdin.write(expr.encode("sjis", "ignore")+'\n')
        self.kakasi.stdin.flush()
        res = unicode(self.kakasi.stdout.readline().rstrip('\r\n'), "sjis")
        return res

# Fact hook
##########################################################################

def onFocusLost(fact, field):
    if not kakasi:
        return
    if field.name not in srcFields:
        return
    if not findTag(modelTag, fact.model.tags):
        return

    idx = srcFields.index(field.name)
    dstField = dstFields[idx]

    try:
        if fact[dstField]:
            return
    except:
        return
    origText = re.sub("\[sound:.+?\]", "", field.value)
    if USE_MECAB:
        tmp = mecab.reading(origText)
        fact[dstField] = tmp
    else:
        tmp = kakasi.reading(origText)
        if tmp != origText:
            fact[dstField] = tmp

canLoad = True
if sys.platform.startswith("darwin"):
    while 1:
        try:
            proc = platform.processor()
        except IOError:
            proc = None
        if proc:
            canLoad = proc != "powerpc"
            break

kakasi = None
mecab = None
tool = None
if canLoad:
    try:
        kakasi = KakasiController()
        mecab = MecabController()
        if USE_MECAB:
            mecab.ensureOpen()
            tool = mecab
        else:
            tool = kakasi
        addHook('fact.focusLost', onFocusLost)
    except Exception:
        if sys.platform.startswith("win32"):
            from PyQt4.QtGui import QDesktopServices
            from PyQt4.QtCore import QUrl
            from ankiqt.ui.utils import showInfo
            showInfo("Please install anki-reading.exe")
            QDesktopServices.openUrl(QUrl(
                "http://ichi2.net/anki/wiki/JapaneseSupport"))
        raise

# Ctrl+g shortcut, based on Samson's regenerate reading field plugin
##########################################################################

def genReading(self):
    # make sure current text is saved
    self.saveFieldsNow()
    # find the first src field available
    reading = None
    for f in srcFields:
        try:
            reading = tool.reading(self.fact[f])
            break
        except:
            continue
    if not reading:
        return
    # save it in the first dst field available
    for f in dstFields:
        try:
            self.fact[f] = reading
            self.fact.setModified(textChanged=True, deck=self.deck)
            self.deck.setModified()
            self.loadFields()
            break
        except:
            continue

def newSetupFields(self):
    s = QShortcut(QKeySequence(_("Ctrl+g")), self.parent)
    s.connect(s, SIGNAL("activated()"), lambda self=self: genReading(self))

from ankiqt.ui import facteditor as fe
from ankiqt import mw
from anki.hooks import wrap
from PyQt4.QtCore import *
from PyQt4.QtGui import *

fe.FactEditor.setupFields = wrap(fe.FactEditor.setupFields, newSetupFields,
        "after")
s = QShortcut(QKeySequence(_("Ctrl+g")), mw.editor.parent)
s.connect(s, SIGNAL("activated()"), lambda self=mw.editor: genReading(self))

# Tests
##########################################################################

if __name__ == "__main__":
    expr = u"カリン、自分でまいた種は自分で刈り取れ"
    print mecab.reading(expr).encode("utf-8")
    expr = u"昨日、林檎を2個買った。"
    print mecab.reading(expr).encode("utf-8")
    expr = u"真莉、大好きだよん＾＾"
    print mecab.reading(expr).encode("utf-8")
    expr = u"彼２０００万も使った。"
    print mecab.reading(expr).encode("utf-8")
    expr = u"彼二千三百六十円も使った。"
    print mecab.reading(expr).encode("utf-8")
    expr = u"千葉"
    print mecab.reading(expr).encode("utf-8")
