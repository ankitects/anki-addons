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
s.PYAU_INPUT_INDEX = 0
