# -*- coding: utf-8 -*-
# ------------------
# Media Custom Directory
# Written by Marcus Andrén (wildclaw@gmail.com)
# ------------------
# Allows for storing of media directories separate from the anki deck
# Usage: Set the location where the media directories are stored via the Set Directory menu entry on the tools menu.


from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt.ui.utils import getText
from anki.hooks import wrap,addHook
from anki.deck import Deck
from ankiqt import mw
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
        elif not os.path.exists(dir) and create:
            try:
                os.mkdir(dir)
                # change to the current dir
                os.chdir(dir)
            except OSError:
                # permission denied
                return None
        return dir
    
def configureDirectory():
    if CONFIG_CUSTOM_MEDIA_DIR in mw.config:
        currentDir = mw.config[CONFIG_CUSTOM_MEDIA_DIR]
    else:
        currentDir = ""
    (text, r) = getText('Please enter the location where the Deck.media directories are stored or leave empty to disable.<br>\
Don''t forget to copy the media directories to the new location first!<br>Current Location: %s )' % currentDir)
    if r:
        if len(text.strip()) == 0: #Empty
            if CONFIG_CUSTOM_MEDIA_DIR in mw.config:
                del mw.config[CONFIG_CUSTOM_MEDIA_DIR]
        else:
            mw.config[CONFIG_CUSTOM_MEDIA_DIR] = text.strip()
            QMessageBox.information(mw,"New Directory", "Makes sure that the media files are placed in %s\\xxxxx.media\\ where xxxxx is the name of the deck"% os.path.abspath(text.strip()))
    else:
        return


Deck.mediaDir = wrap(Deck.mediaDir,newMediaDir,"")


# Setup menu entries
menu1 = QAction(mw)
menu1.setText("Media Custom Directory - Set Directory")
mw.connect(menu1, SIGNAL("triggered()"),configureDirectory)
mw.mainWin.menuTools.addSeparator()
mw.mainWin.menuTools.addAction(menu1)
