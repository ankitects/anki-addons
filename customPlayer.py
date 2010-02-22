# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin allows you to customize the default media player to use a
# program of your choice. It will be used for any files with [sound:..] tags -
# this includes movies you specify with that tag.
#
# If you're on OSX, you'll probably need to specify a full path, like
# "/Applications/MyProgram.app/Contents/MacOS/myprogram". You can find out the
# path by going to your applications folder, right clicking on the app, and
# choosing to show the contents of the package.
#

##########################################################################

# change 'customPlayer' to the player you want
#externalPlayer = ["mplayer", "-really-quiet"]
externalPlayer = ["customPlayer"]

##########################################################################

externalManager = None
queue = []

import threading, subprocess, sys, time
import anki.sound as s

class QueueMonitor(threading.Thread):

    def run(self):
        while 1:
            if queue:
                path = queue.pop(0)
                try:
                    s.retryWait(subprocess.Popen(
                        externalPlayer + [path], startupinfo=s.si))
                except OSError:
                    raise Exception("Audio player not found")
            else:
                return
            time.sleep(0.1)

def queueExternal(path):
    global externalManager
    path = path.encode(sys.getfilesystemencoding())
    queue.append(path)
    if not externalManager or not externalManager.isAlive():
        externalManager = QueueMonitor()
        externalManager.start()

def clearExternalQueue():
    global queue
    queue = []

s._player = queueExternal
s._queueEraser = clearExternalQueue
