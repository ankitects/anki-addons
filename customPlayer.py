# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin allows you to customize the default media player to use a
# program of your choice. It will be used for any files with [sound:..] tags -
# this includes movies you specify with that tag.

PLAYER = ["mplayer"]

import anki.sound as s

s.externalPlayer = PLAYER
s.play = s.playExternal
s.clearAudioQueue = s.clearQueueExternal
