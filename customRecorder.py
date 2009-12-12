# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Lets you customize the settings used for the recorder

from anki import sound as s
import pyaudio

s.PYAU_FORMAT = pyaudio.paInt16
s.PYAU_CHANNELS = 1
s.PYAU_RATE = 44100
# change the input index to a different number to match your device
# try 1, 2, etc.
s.PYAU_INPUT_INDEX = 0

# if you can't guess the number, uncomment the following lines, and then
# restart Anki. An error will pop up, listing each of your devices. Then
# update the number above and comment the lines below again.

# import sys
# p = pyaudio.PyAudio()
# for x in range(p.get_device_count()):
#     sys.stderr.write("%d %s\n" % (x, p.get_device_info_by_index(x)))
