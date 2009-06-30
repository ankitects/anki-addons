# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin lets you record audio for a number of cards at once - very
# useful for teachers or students who have a native-speaking friend.
#
# Screenshots: http://ichi2.net/anki/plugins/bulkrecord
#
# Only Linux and Windows are currently supported - to use this plugin on
# Windows or OSX, you'll need to modify the getAudio() function
#
# On Linux, you need three programs:
# 1. mplayer (for playback)
# 2. ecasound (for recording)
# 3. sox (for noise reduction)
#
# On Windows, you need two to install two programs:
# 1. Download http://prdownloads.sourceforge.net/sox/sox-14.1.0-cygwin.zip?download
# 2. Download http://www.rarewares.org/dancer/dancer.php?f=226
# 3. Unzip each file and copy the .exe and .dll files to your windows
# directory (usually c:\windows)
# - To run the commands below, choose Start -> Run, type cmd, choose OK, then
# type the commands below without the $.
#
# version 1: initial release
# version 2: add windows support, change instructions, noise amplification
#
###############################################################################
# Build a noise profile
###############################################################################
#
# First you need to create a noise profile so that background noise will be
# cancelled.
#
# On the command line, run the following, and hit Ctrl+c after you've recorded
# 10 seconds of silence
#
# $ rec silence.wav
#
# Next, record yourself speaking and hit Ctrl+c when done. Try to include some words
# like 'put' - some sounds are naturally louder than others, and we want a
# good sample for the next section. Speak at the same volume and distance from
# the mic as you plan to when recording material later. Again, hit Ctrl+c to
# stop recording.
#
# $ rec speaking.wav
#
# Now build the noise profile
#
# $ sox silence.wav -t null /dev/null noiseprof noiseprofile
#
# Determine the optimum level of noise cancelation by putting on some
# earphones and running the following command, changing 0.1 to a value between
# 0.1 and 1.0. Higher numbers will cancel more noise, but will also probably
# cancel your voice too:
#
# $ play speaking.wav noisered noiseprofile 0.1
#
# When you've determined the optimum number, write it down for later, then run
# the following command for the next step:
#
# $ sox speaking.wav speaking2.wav noisered noiseprofile 0.1
#
# If you're on windows, you may want to move the noise profile to an easier to
# access location:
#
# $ mv noiseprofile c:\
#
###############################################################################
# Determine optimum amplification & bass
###############################################################################
#
# Next you need to find the optimum amplification level and bass boost.
#
# Run the following command. Look for the 'clip' section at the bottom right
# of the program output. Make sure that no samples are clipped (which means
# it's too loud and the audio is being distorted). When you're happy with the
# numbers, adjust them below. The bass boost compensates for the lack of bass
# response on cheap microphones. Adjust to suit.
#
# $ play speaking2.wav norm -3 bass +5
#
###############################################################################
# Win32 notes
###############################################################################
#
# If you have problems, there are two likely culprits:
#
# 1. Make sure c:\tmp exists, it's needed to store a temporary file when
# normalizing
#
# 2. Make sure you've specified the correct path to your noise profile.
#
# To stop recording, hit ctrl+c
#
###############################################################################
# Recording in Anki
###############################################################################
#
# To use the plugin, add a field called 'Audio' to your facts (or change
# AUDIO_FIELD_NAME below). Add %(Audio)s to the answer format of your cards.
# Then select some cards in the editor, click the Facts button, and choose
# "Bulk Record". You'll be prompted to record each card that has an empty
# field.
#
###############################################################################
# User variables
###############################################################################
# Adjust this section to customize amplification, path to your noise profile,
# etc.

import os

# the field in your card model
AUDIO_FIELD_NAME = "Audio"

NOISE_PROFILE_LOCATION = "/home/resolve/Lib/misc/noiseprofile"
# on win32, use something like the following (assuming you've put the
# noiseprofile file in c:\
#NOISE_PROFILE_LOCATION = "c:\\noiseprofile"

# the amount of noise to cancel
NOISE_AMOUNT = "0.1"
# the amount of amplification
NORM_AMOUNT = "-3"
# the amount of bass
BASS_AMOUNT = "+5"

###############################################################################

import subprocess, signal, re, stat, socket, sys, tempfile, traceback
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw
from ankiqt.ui import cardlist
from ankiqt.ui.utils import showInfo
from anki.facts import Fact
from anki.media import copyToMedia

try:
    import hashlib
    md5 = hashlib.md5
except ImportError:
    import md5
    md5 = md5.new

audioPlayCommand = ["mplayer", "-really-quiet"]
# ecasound for recording, since sox cuts off the end
audioRecordCommand = ["ecasound", "-x", "-f:16,1,44100", "-i",
                      "alsahw,1,0", "-o", "tmp.wav"]
# sox for postprocessing
audioProcessCommand = ["sox", "tmp.wav", "tmp2.wav",
                       # noise reduction
                       "noisered", NOISE_PROFILE_LOCATION, NOISE_AMOUNT]
audioProcessCommand2 = ["sox", "tmp2.wav", "tmp3.wav",
                       "norm", NORM_AMOUNT, "bass", BASS_AMOUNT, "fade", "0.2", "0"]
audioProcessCommand3 = ["lame", "tmp3.wav", "tmp.mp3", "--noreplaygain"]

# override for different computer with different microphone & noise settings
if socket.gethostname() == "mobile":
    audioRecordCommand = ["ecasound", "-x", "-f:16,1,44100", "-i",
                          "alsahw,0,0", "-o", "tmp.wav"]
    audioProcessCommand = ["sox", "tmp.wav", "tmp2.wav",
                           # noise reduction
                           "noisered", "/home/resolve/Lib/misc/noiseprofile-mobile", NOISE_AMOUNT]

##########################################################################
# win32 compat

if sys.platform.startswith("win32"):
    # override for windows
    audioPlayCommand = [
        "c:\\program files\\windows media player\\wmplayer.exe"]
    audioRecordCommand = ["rec", "tmp.wav"]
    startupInfo = subprocess.STARTUPINFO()
    startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    startupInfo = None

##########################################################################

bulkRecordAction = None
editorObj = None


(tempfd, tempname) = tempfile.mkstemp()
tmpfile = os.fdopen(tempfd, "w+")

def getAudio(string, parent):
    "Record and return filename"
    # record first
    process = subprocess.Popen(audioRecordCommand)
    if not sys.platform.startswith("win32"):
        mb2 = QMessageBox(parent)
        but = QPushButton("Stop")
        mb2.addButton(but, QMessageBox.RejectRole)
        mb2.setText(string + "<br><br>Recording..")
        mb2.exec_()
        os.kill(process.pid, signal.SIGINT)
    process.wait()
    # postprocess
    try:
        subprocess.check_call(audioProcessCommand, stdout=tmpfile, stderr=tmpfile)
        subprocess.check_call(audioProcessCommand2, stdout=tmpfile, stderr=tmpfile)
        subprocess.check_call(audioProcessCommand3, stdout=tmpfile, stderr=tmpfile)
    except:
        tmpfile.flush()
        showInfo("Error occurred:\n%s\n%s" % (
            traceback.format_exc(),
            open(tempname).read()))
    return "tmp.mp3"

def bulkRecord(parent):
    modelIds = mw.deck.s.column0("""
select distinct modelId from fieldModels
where name = :name""", name=AUDIO_FIELD_NAME)
    factIds = parent.selectedFacts()
    needed = []
    for mid in modelIds:
        ordinal = mw.deck.s.scalar(
"""select ordinal from fieldModels
where modelId = :mid and name = :name""",
name=AUDIO_FIELD_NAME, mid=mid)
        for fact in mw.deck.s.query(Fact).filter_by(modelId=mid):
            if fact.id not in factIds:
                continue
            if not fact.fields[ordinal].value:
                needed.append((fact, ordinal))
    total = len(needed)
    count = 1
    for (fact, ordinal) in needed:
        if not recordFact(parent, fact, ordinal, count, total):
            break
        count += 1

def recordFact(parent, fact, ordinal, count, total):
    recorded = False
    while 1:
        mb = QMessageBox(parent)
        mb.setWindowTitle("%d of %d" % (count, total))
        mb.setTextFormat(Qt.RichText)
        # display string
        str = ""
        for field in fact.fields:
            str += "%s: %s<br>" % (field.name, field.value)
        mb.setText(str)
        # save
        bSave = QPushButton("Save and continue")
        mb.addButton(bSave, QMessageBox.RejectRole)
        if not recorded:
            bSave.setEnabled(False)
        # replay
        bReplay = QPushButton("Replay")
        mb.addButton(bReplay, QMessageBox.RejectRole)
        if not recorded:
            bReplay.setEnabled(False)
        # record (again)
        if recorded:
            bRecord = QPushButton("Record again")
        else:
            bRecord = QPushButton("Record")
        mb.addButton(bRecord, QMessageBox.RejectRole)
        # skip
        bSkip = QPushButton("Skip this fact")
        mb.addButton(bSkip, QMessageBox.RejectRole)
        # stop
        bStop = QPushButton("Stop bulk update")
        mb.addButton(bStop, QMessageBox.RejectRole)
        mb.exec_()
        if mb.clickedButton() == bRecord:
            recorded = getAudio(str, parent)
            continue
        elif mb.clickedButton() == bReplay:
            subprocess.Popen(audioPlayCommand + [os.path.abspath("tmp.mp3")])
            continue
        elif mb.clickedButton() == bSave:
            new = copyToMedia(mw.deck, recorded)
            os.unlink("tmp.mp3")
            os.unlink("tmp.wav")
            os.unlink("tmp2.wav")
            os.unlink("tmp3.wav")
            fact.fields[ordinal].value = u"[sound:%s]" % new
            fact.setModified(textChanged=True)
            mw.deck.flushMod()
            mw.deck.save()
            editorObj.updateAfterCardChange()
            return True
        elif mb.clickedButton() == bSkip:
            return True
        elif mb.clickedButton() == bStop:
            return False

def setupMenus(parent):
    global bulkRecordAction, editorObj
    editorObj = parent
    bulkRecordAction = QAction(parent)
    bulkRecordAction.setText("Bulk record")
    parent.connect(bulkRecordAction, SIGNAL("triggered()"),
                   lambda parent=parent: bulkRecord(parent))
    parent.dialog.menuActions.addSeparator()
    parent.dialog.menuActions.addAction(bulkRecordAction)

mw.addHook("editor.setupMenus", setupMenus)
