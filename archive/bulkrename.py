# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# this plugin lets you apply transformations to your media files. one use for
# this is when you convert all your wav files to mp3 files, and so on. it
# will try to rename the files if they exist - if they have already been
# renamed, it will continue without problems.
#
# no checking is done to see if files already exist or your pattern is safe,
# so be sure to back your deck and media directory up first.
#
# the default replacement string takes a file in a subdirectory and moves it
# to the top level media directory - eg a path like this:
#
#   foo/bar/baz.mp3
#
# becomes
#
#   foo-bar-baz.mp3
#

# version 1: initial release

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw, ui
from anki.media import mediaRefs, _modifyFields
import os, re

fromStr = "/"
toStr = "-"

def bulkrename():
    # rename files
    deck = mw.deck
    mediaDir = deck.mediaDir()
    dirs = [mediaDir]
    renamedFiles = 0
    while 1:
        if not dirs:
            break
        dir = dirs.pop()
        for fname in os.listdir(unicode(dir)):
            path = os.path.join(dir, fname)
            if os.path.isdir(path):
                dirs.append(path)
                continue
            else:
                relpath = path[len(mediaDir)+1:]
                newrel = re.sub(fromStr, toStr, relpath)
                if relpath != newrel:
                    os.rename(os.path.join(mediaDir, relpath),
                              os.path.join(mediaDir, newrel))
                    renamedFiles += 1
    # rename fields
    modifiedFacts = {}
    updateFields = []
    for (id, fid, val) in deck.s.all(
        "select id, factId, value from fields"):
        oldval = val
        for (full, fname, repl) in mediaRefs(val):
            tmp = re.sub(fromStr, toStr, fname)
            if tmp != fname:
                val = re.sub(re.escape(full), repl % tmp, val)
        if oldval != val:
            updateFields.append({'id': id, 'val': val})
            modifiedFacts[fid] = 1
    if modifiedFacts:
        _modifyFields(deck, updateFields, modifiedFacts, True)
    ui.utils.showInfo("%d files renamed.\n%d facts modified." %
                      (renamedFiles, len(modifiedFacts)))

def init():
    q = QAction(mw)
    q.setText("Bulk Rename")
    mw.mainWin.menuAdvanced.addSeparator()
    mw.mainWin.menuAdvanced.addAction(q)
    mw.connect(q, SIGNAL("triggered()"), bulkrename)

mw.addHook("init", init)
