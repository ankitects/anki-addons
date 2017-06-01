# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatic reading generation with kakasi and mecab.
# See http://ichi2.net/anki/wiki/JapaneseSupport
#

import sys, os, platform, re, subprocess, aqt.utils
from anki.utils import stripHTML, entsToTxt, isWin, isMac
from anki.hooks import addHook
from .notetypes import isJapaneseNoteType

srcFields = ['Expression']
dstFields = ['Reading']
furiganaFieldSuffix = u" (furigana)"

kakasiArgs = ["-isjis", "-osjis", "-u", "-JH", "-KH"]
mecabArgs = ['--node-format=%m[%f[7]] ', '--eos-format=\n',
            '--unk-format=%m[] ']

def mergeHTMLFurigana(HTML_string, furigana_string):
	format_position = 0
	furigana_position = 0
	combined_string = ''
	HTML_string = entsToTxt(HTML_string)
	HTML_string = HTML_string.replace(u'\uff5e', "~")
	while furigana_position < len(furigana_string) and format_position < len(HTML_string):
		if HTML_string[format_position] == furigana_string[furigana_position]:
			character_lookahead_pos = 1
			while furigana_position + character_lookahead_pos < len(furigana_string) and format_position + character_lookahead_pos < len(HTML_string) and HTML_string[format_position + character_lookahead_pos] == furigana_string[furigana_position + character_lookahead_pos]:
				character_lookahead_pos += 1
			combined_string +=HTML_string[format_position:format_position + character_lookahead_pos]
			furigana_position += character_lookahead_pos
			format_position += character_lookahead_pos
		elif furigana_string[furigana_position] == '[':
			character_lookahead_pos = furigana_position + 1
			while not furigana_string[character_lookahead_pos] == ']':
				character_lookahead_pos += 1
			combined_string += furigana_string[furigana_position:character_lookahead_pos+1]
			furigana_position = character_lookahead_pos + 1
		elif furigana_string[furigana_position] == ' ':
			combined_string +=' '
			furigana_position+= 1
		elif HTML_string[format_position] == ' ':
			combined_string += ' '
			format_position += 1
		elif not HTML_string[format_position] == furigana_string[furigana_position]:
			character_lookahead_pos = format_position + 1
			while not HTML_string[character_lookahead_pos] == furigana_string[furigana_position]:
				character_lookahead_pos += 1
			combined_string += HTML_string[format_position:character_lookahead_pos]
			format_position = character_lookahead_pos
		else:
			break
	if furigana_position < len(furigana_string):
		combined_string += furigana_string[furigana_position:]
	return combined_string

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

def mungeForPlatform(popen):
    if isWin:
        popen = [os.path.normpath(x) for x in popen]
        popen[0] += ".exe"
    elif not isMac:
        popen[0] += ".lin"
    return popen

class MecabController(object):

    def __init__(self):
        self.mecab = None

    def setup(self):
        base = "../../addons/japanese/support/"
        self.mecabCmd = mungeForPlatform(
            [base + "mecab"] + mecabArgs + [
                '-d', base, '-r', base + "mecabrc"])
        os.environ['DYLD_LIBRARY_PATH'] = base
        os.environ['LD_LIBRARY_PATH'] = base
        if not isWin:
            os.chmod(self.mecabCmd[0], 0o755)

    def ensureOpen(self):
        if not self.mecab:
            self.setup()
            try:
                self.mecab = subprocess.Popen(
                    self.mecabCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=si)
            except OSError:
                raise Exception("Please ensure your Linux system has 64 bit binary support.")

    def reading(self, expr):
        self.ensureOpen()
        original_expression = expr
        expr = escapeText(expr)
        self.mecab.stdin.write(expr.encode("euc-jp", "ignore") + b'\n')
        self.mecab.stdin.flush()
        expr = self.mecab.stdout.readline().rstrip(b'\r\n').decode('euc-jp')
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
        return mergeHTMLFurigana(original_expression, fin.strip().replace("< br>", "<br>"))

# Kakasi
##########################################################################

class KakasiController(object):

    def __init__(self):
        self.kakasi = None

    def setup(self):
        base = "../../addons/japanese/support/"
        self.kakasiCmd = mungeForPlatform(
            [base + "kakasi"] + kakasiArgs)
        os.environ['ITAIJIDICT'] = base + "itaijidict"
        os.environ['KANWADICT'] = base + "kanwadict"
        if not isWin:
            os.chmod(self.kakasiCmd[0], 0o755)

    def ensureOpen(self):
        if not self.kakasi:
            self.setup()
            try:
                self.kakasi = subprocess.Popen(
                    self.kakasiCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=si)
            except OSError:
                raise Exception("Please install kakasi")

    def reading(self, expr):
        self.ensureOpen()
        expr = escapeText(expr)
        self.kakasi.stdin.write(expr.encode("sjis", "ignore") + b'\n')
        self.kakasi.stdin.flush()
        res = self.kakasi.stdout.readline().rstrip(b'\r\n').decode("sjis")
        return res

# Focus lost hook
##########################################################################

def onFocusLost(flag, n, fidx):
    global mecab
    from aqt import mw
    if not mecab:
        return flag
    src = None
    dst = None
    # japanese model?
    if not isJapaneseNoteType(n.model()['name']):
        return flag
    # have src and dst fields?
    fields = mw.col.models.fieldNames(n.model())
    src = fields[fidx]
    # Retro compatibility
    if src in srcFields:
        srcIdx = srcFields.index(src)
        dst = dstFields[srcIdx]
    else:
        dst = src + furiganaFieldSuffix
    if not src or not dst:
        return flag
    # dst field exists?
    if dst not in n:
        return flag
    # dst field already filled?
    if n[dst]:
        return flag
    # grab source text
    srcTxt = mw.col.media.strip(n[src])
    if not srcTxt:
        return flag
    # update field
    try:
        n[dst] = mecab.reading(srcTxt)
    except Exception as e:
        mecab = None
        raise
    return True

# Init
##########################################################################

kakasi = KakasiController()
mecab = MecabController()

addHook('editFocusLost', onFocusLost)

# Tests
##########################################################################

if __name__ == "__main__":
    expr = u"カリン、自分でまいた種は自分で刈り取れ"
    print(mecab.reading(expr).encode("utf-8"))
    expr = u"昨日、林檎を2個買った。"
    print(mecab.reading(expr).encode("utf-8"))
    expr = u"真莉、大好きだよん＾＾"
    print(mecab.reading(expr).encode("utf-8"))
    expr = u"彼２０００万も使った。"
    print(mecab.reading(expr).encode("utf-8"))
    expr = u"彼二千三百六十円も使った。"
    print(mecab.reading(expr).encode("utf-8"))
    expr = u"千葉"
    print(mecab.reading(expr).encode("utf-8"))
