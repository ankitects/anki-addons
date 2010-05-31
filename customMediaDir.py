# -*- coding: utf-8 -*-
# ------------------
# Media Custom Directory
# Written by Marcus Andrén (wildclaw@gmail.com)
# Modified by Damien Elmes (anki@ichi2.net) to make it easier to use
# ------------------
# Allows for storing of media directories separate from the anki deck

from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt.ui.utils import getText
from anki.hooks import wrap,addHook
from anki.deck import Deck
from ankiqt import mw, ui
import os,re

CONFIG_CUSTOM_MEDIA_DIR = "MediaCustomDirectory.Directory"

def newMediaDir(self,_old,create=False):
    if not self.path or not CONFIG_CUSTOM_MEDIA_DIR in mw.config:
        return _old(self,create) #Let the original method handle the temp dir case
    else:
        (originalDirectory,filename) = os.path.split(self.path)

        mediaDirName = re.sub("(?i)\.(anki)$", ".media", filename)

        dir = os.path.join(mw.config[CONFIG_CUSTOM_MEDIA_DIR],mediaDirName)

        if create == None:
            return dir
        elif not os.path.exists(dir):
            if create:
                try:
                    os.mkdir(dir)
                    # change to the current dir
                    os.chdir(dir)
                except OSError:
                    # permission denied
                    return None
            else:
                return None
        return dir

def configureDirectory():
    if mw.config.get(CONFIG_CUSTOM_MEDIA_DIR, ""):
        return
    dir = QFileDialog.getExistingDirectory(
        mw, _("Choose Media Directory"), mw.documentDir,
        QFileDialog.ShowDirsOnly)
    dir = unicode(dir)
    if not dir:
        return
    mw.config[CONFIG_CUSTOM_MEDIA_DIR] = dir
    mw.config.save()

def reconfigureDirectory():
    mw.config[CONFIG_CUSTOM_MEDIA_DIR] = ""
    configureDirectory()

Deck.mediaDir = wrap(Deck.mediaDir,newMediaDir,"")

# Setup menu entries
menu1 = QAction(mw)
menu1.setText("Change Media Directory")
mw.connect(menu1, SIGNAL("triggered()"),reconfigureDirectory)
mw.mainWin.menuAdvanced.addSeparator()
mw.mainWin.menuAdvanced.addAction(menu1)

addHook("init", configureDirectory)
