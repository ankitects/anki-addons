# -*- coding: utf-8 -*-
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Some quick examples of audio handling in 2.1.20.
"""

from typing import Any, Callable, List, Optional, Tuple

from anki.sound import AVTag, SoundOrVideoTag
from aqt import gui_hooks, mw
from aqt.sound import (
    MpvManager,
    SimpleMplayerSlaveModePlayer,
    SimpleProcessPlayer,
    SoundOrVideoPlayer,
    av_player,
)

# Play files faster in mpv/mplayer
######################################


def set_speed(player: Any, speed: float) -> None:
    if isinstance(player, MpvManager):
        player.set_property("speed", speed)
    elif isinstance(player, SimpleMplayerSlaveModePlayer):
        player.command("speed_set", speed)


# automatically play fast


def did_begin_playing(player: Any, tag: AVTag) -> None:
    # mplayer seems to lose commands sent to it immediately after startup,
    # so we add a delay for it - an alternate approach would be to adjust
    # the command line arguments passed to it
    if isinstance(player, SimpleMplayerSlaveModePlayer):
        mw.progress.timer(500, lambda: set_speed(player, 1.25), False)
    else:
        set_speed(player, 1.25)


gui_hooks.av_player_did_begin_playing.append(did_begin_playing)

# shortcut key to make slower


def on_shortcuts_change(state: str, shortcuts: List[Tuple[str, Callable]]) -> None:
    if state == "review":
        shortcuts.append(("8", lambda: set_speed(av_player.current_player, 0.75)))


gui_hooks.state_shortcuts_will_change.append(on_shortcuts_change)

# Play .ogg files in the external program 'myplayer'
########################################################


class MyPlayer(SimpleProcessPlayer, SoundOrVideoPlayer):
    args = ["myplayer"]

    def rank_for_tag(self, tag: AVTag) -> Optional[int]:
        if isinstance(tag, SoundOrVideoTag) and tag.filename.endswith(".ogg"):
            return 100
        return None


av_player.players.append(MyPlayer(mw.taskman))
