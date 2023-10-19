# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatic reading generation with kakasi and mecab.
#

from __future__ import annotations

import os
import re
import subprocess
import sys

from anki.notes import Note
from anki.utils import is_mac, is_win, strip_html
from aqt import gui_hooks, mw

from .notetypes import isJapaneseNoteType

config = mw.addonManager.getConfig(__name__)

srcFields = config["srcFields"]
dstFields = config["dstFields"]
furiganaFieldSuffix = config["furiganaSuffix"]

kakasiArgs = ["-isjis", "-osjis", "-u", "-JH", "-KH"]
mecabArgs = ["--node-format=%m[%f[7]] ", "--eos-format=\n", "--unk-format=%m[] "]

supportDir = os.path.join(os.path.dirname(__file__), "support")


def escapeText(text: str) -> str:
    # strip characters that trip up kakasi/mecab
    text = text.replace("\n", " ")
    text = text.replace("\uff5e", "~")
    text = re.sub("<br( /)?>", "---newline---", text)
    text = strip_html(text)
    text = text.replace("---newline---", "<br>")
    return text


if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    try:
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    except:
        # pylint: disable=no-member
        si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
else:
    si = None

# Mecab
##########################################################################


def mungeForPlatform(popen: list[str]) -> list[str]:
    if is_win:
        popen = [os.path.normpath(x) for x in popen]
        popen[0] += ".exe"
    elif not is_mac:
        popen[0] += ".lin"
    return popen


class MecabController(object):
    def __init__(self) -> None:
        self.mecab: subprocess.Popen | None = None

    def setup(self) -> None:
        self.mecabCmd = mungeForPlatform(
            [os.path.join(supportDir, "mecab")]
            + mecabArgs
            + [
                "-d",
                supportDir,
                "-r",
                os.path.join(supportDir, "mecabrc"),
                "-u",
                os.path.join(supportDir, "user_dic.dic"),
            ]
        )
        os.environ["DYLD_LIBRARY_PATH"] = supportDir
        os.environ["LD_LIBRARY_PATH"] = supportDir
        if not is_win:
            os.chmod(self.mecabCmd[0], 0o755)

    def ensureOpen(self) -> None:
        if not self.mecab:
            self.setup()
            try:
                self.mecab = subprocess.Popen(
                    self.mecabCmd,
                    bufsize=-1,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=si,
                )
            except OSError as exc:
                raise Exception(
                    "Please ensure your Linux system has 64 bit binary support."
                ) from exc

    def reading(self, expr: str) -> str:
        self.ensureOpen()
        expr = escapeText(expr)
        self.mecab.stdin.write(expr.encode("utf-8", "ignore") + b"\n")
        self.mecab.stdin.flush()
        assert self.mecab
        expr = self.mecab.stdout.readline().rstrip(b"\r\n").decode("utf-8", "replace")
        out = []
        for node in expr.split(" "):
            if not node:
                break
            m = re.match(r"(.+)\[(.*)\]", node)
            if not m:
                sys.stderr.write(
                    "Unexpected output from mecab. Perhaps your Windows username contains non-Latin text?: {}\n".format(
                        repr(expr)
                    )
                )
                return ""

            (kanji, reading) = m.groups()
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
            if kanji in "一二三四五六七八九十０１２３４５６７８９":
                out.append(kanji)
                continue
            # strip matching characters and beginning and end of reading and kanji
            # reading should always be at least as long as the kanji
            placeL = 0
            placeR = 0
            for i in range(1, len(kanji)):
                if kanji[-i] != reading[-i]:
                    break
                placeR = i
            for i in range(0, len(kanji) - 1):
                if kanji[i] != reading[i]:
                    break
                placeL = i + 1
            if placeL == 0:
                if placeR == 0:
                    out.append(" %s[%s]" % (kanji, reading))
                else:
                    out.append(
                        " %s[%s]%s"
                        % (kanji[:-placeR], reading[:-placeR], reading[-placeR:])
                    )
            else:
                if placeR == 0:
                    out.append(
                        "%s %s[%s]"
                        % (reading[:placeL], kanji[placeL:], reading[placeL:])
                    )
                else:
                    out.append(
                        "%s %s[%s]%s"
                        % (
                            reading[:placeL],
                            kanji[placeL:-placeR],
                            reading[placeL:-placeR],
                            reading[-placeR:],
                        )
                    )
        fin = ""
        for c, s in enumerate(out):
            if c < len(out) - 1 and re.match("^[A-Za-z0-9]+$", out[c + 1]):
                s += " "
            fin += s
        return fin.strip().replace("< br>", "<br>")


# Kakasi
##########################################################################


class KakasiController(object):
    def __init__(self) -> None:
        self.kakasi: subprocess.Popen | None = None

    def setup(self) -> None:
        self.kakasiCmd = mungeForPlatform(
            [os.path.join(supportDir, "kakasi")] + kakasiArgs
        )
        os.environ["ITAIJIDICT"] = os.path.join(supportDir, "itaijidict")
        os.environ["KANWADICT"] = os.path.join(supportDir, "kanwadict")
        if not is_win:
            os.chmod(self.kakasiCmd[0], 0o755)

    def ensureOpen(self) -> None:
        if not self.kakasi:
            self.setup()
            try:
                self.kakasi = subprocess.Popen(
                    self.kakasiCmd,
                    bufsize=-1,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=si,
                )
            except OSError as exc:
                raise Exception("Please install kakasi") from exc

    def reading(self, expr: str) -> str:
        self.ensureOpen()
        expr = escapeText(expr)
        self.kakasi.stdin.write(expr.encode("sjis", "ignore") + b"\n")
        self.kakasi.stdin.flush()
        res = self.kakasi.stdout.readline().rstrip(b"\r\n").decode("sjis", "replace")
        return res


# Focus lost hook
##########################################################################

mecab = None


def onFocusLost(changed: bool, note: Note, current_field_index: int) -> bool:
    # japanese model?
    if not isJapaneseNoteType(note.note_type()["name"]):
        return changed
    fields = mw.col.models.field_names(note.note_type())
    src = fields[current_field_index]
    if not regenerateReading(note, src):
        return changed
    return True


def regenerateReading(n: Note, src: str) -> bool:
    global mecab
    if not mecab:
        return False
    dst = None
    # Retro compatibility
    if src in srcFields:
        srcIdx = srcFields.index(src)
        dst = dstFields[srcIdx]
    if dst not in n:
        dst = src + furiganaFieldSuffix
    if not src or not dst:
        return False
    # dst field exists?
    if dst not in n:
        return False
    # dst field already filled?
    if n[dst]:
        return False
    # grab source text
    srcTxt = mw.col.media.strip(n[src])
    if not srcTxt:
        return False
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

gui_hooks.editor_did_unfocus_field.append(onFocusLost)

# Tests
##########################################################################

if __name__ == "__main__":
    expr = "カリン、自分でまいた種は自分で刈り取れ"
    print(mecab.reading(expr).encode("utf-8"))
    expr = "昨日、林檎を2個買った。"
    print(mecab.reading(expr).encode("utf-8"))
    expr = "真莉、大好きだよん＾＾"
    print(mecab.reading(expr).encode("utf-8"))
    expr = "彼２０００万も使った。"
    print(mecab.reading(expr).encode("utf-8"))
    expr = "彼二千三百六十円も使った。"
    print(mecab.reading(expr).encode("utf-8"))
    expr = "千葉"
    print(mecab.reading(expr).encode("utf-8"))
