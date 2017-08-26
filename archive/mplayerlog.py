import subprocess, os
from aqt import mw
import anki.sound as s

file = None
s.mplayerCmd.remove("-really-quiet")

def sp(self):
    global file
    if not file:
        file = open(os.path.join(mw.pm.addonFolder(), "mplayerlog.txt"), "w")
    cmd = s.mplayerCmd + ["-slave", "-idle"]
    self.mplayer = subprocess.Popen(
        cmd, startupinfo=s.si, stdin=subprocess.PIPE,
        stdout=file, stderr=file)

s.MplayerMonitor.startProcess = sp
