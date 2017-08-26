# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from ankiqt import mw

def fixedDropboxFolder():
    folder = orig()
    # Dropbox changed the folder name from "My Dropbox" to "Dropbox".
    folder = folder.replace("My Dropbox", "Dropbox")
    # If you want to use a custom location, uncomment the following line
    # and edit it to match the actual path. Note that you need to use two
    # backslash characters instead of one.
    #return "c:\\users\\bob\\documents\\dropbox"
    return folder

orig = mw.dropboxFolder
mw.dropboxFolder = fixedDropboxFolder

