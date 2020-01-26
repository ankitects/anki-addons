# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
An example of how other TTS services can be added to Anki.

This add-on registers all voices with the name 'gTTS', meaning if the user
wishes to use it in preference to any other TTS drivers that are registered,
they can use the following in their template, changing en_US to another language
as necessary:

{{tts en_US voices=gTTS:Field}}
"""

import os
import sys
from concurrent.futures import Future
from dataclasses import dataclass
from typing import List, cast

from anki.lang import compatMap
from anki.sound import AVTag, TTSTag
from aqt import mw
from aqt.sound import OnDoneCallback, PlayerInterrupted, av_player
from aqt.tts import TTSProcessPlayer, TTSVoice

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

from gtts import gTTS  # isort:skip pylint: disable=import-error

# this is the language map that gtts.lang.tts_langs() outputs
orig_langs = {
    "af": "Afrikaans",
    "sq": "Albanian",
    "ar": "Arabic",
    "hy": "Armenian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    "et": "Estonian",
    "tl": "Filipino",
    "fi": "Finnish",
    "fr": "French",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "hi": "Hindi",
    "hu": "Hungarian",
    "is": "Icelandic",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "jw": "Javanese",
    "kn": "Kannada",
    "km": "Khmer",
    "ko": "Korean",
    "la": "Latin",
    "lv": "Latvian",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "my": "Myanmar (Burmese)",
    "ne": "Nepali",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sr": "Serbian",
    "si": "Sinhala",
    "sk": "Slovak",
    "es": "Spanish",
    "su": "Sundanese",
    "sw": "Swahili",
    "sv": "Swedish",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "cy": "Welsh",
    "zh-cn": "Chinese (Mandarin/China)",
    "zh-tw": "Chinese (Mandarin/Taiwan)",
    "en-us": "English (US)",
    "en-ca": "English (Canada)",
    "en-uk": "English (UK)",
    "en-gb": "English (UK)",
    "en-au": "English (Australia)",
    "en-gh": "English (Ghana)",
    "en-in": "English (India)",
    "en-ie": "English (Ireland)",
    "en-nz": "English (New Zealand)",
    "en-ng": "English (Nigeria)",
    "en-ph": "English (Philippines)",
    "en-za": "English (South Africa)",
    "en-tz": "English (Tanzania)",
    "fr-ca": "French (Canada)",
    "fr-fr": "French (France)",
    "pt-br": "Portuguese (Brazil)",
    "pt-pt": "Portuguese (Portugal)",
    "es-es": "Spanish (Spain)",
    "es-us": "Spanish (United States)",
}


# we subclass the default voice object to store the gtts language code
@dataclass
class GTTSVoice(TTSVoice):
    gtts_lang: str


class GTTSPlayer(TTSProcessPlayer):
    # this is called the first time Anki tries to play a TTS file
    def get_available_voices(self) -> List[TTSVoice]:
        voices = []
        for code, name in orig_langs.items():
            if "-" in code:
                # get a standard code like en_US from the gtts code en-us
                head, tail = code.split("-")
                std_code = f"{head}_{tail.upper()}"
            else:
                # get a standard code like cs_CZ from gtts code cs
                std_code = compatMap.get(code)
                # skip languages we don't understand
                if not std_code:
                    continue

            # add the voice using the name "gtts"
            voices.append(GTTSVoice(name="gTTS", lang=std_code, gtts_lang=code))
        return voices  # type: ignore

    # this is called on a background thread, and will not block the UI
    def _play(self, tag: AVTag) -> None:
        # get the avtag
        assert isinstance(tag, TTSTag)
        match = self.voice_for_tag(tag)
        assert match
        voice = cast(GTTSVoice, match.voice)

        # is the field blank?
        if not tag.field_text.strip():
            return

        # get filename, and skip if already generated
        self._tmpfile = self.temp_file_for_tag_and_voice(tag, match.voice) + ".mp3"
        if os.path.exists(self._tmpfile):
            return

        # call gtts to save an mp3 file to the path
        tts = gTTS(text=tag.field_text, lang=voice.gtts_lang, lang_check=False)
        tts.save(self._tmpfile)

    # this is called on the main thread, after _play finishes
    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        try:
            ret.result()
        except PlayerInterrupted:
            # don't fire done callback when interrupted
            return

        # inject file into the top of the audio queue
        av_player.insert_file(self._tmpfile)

        # then tell player to advance, which will cause the file to be played
        cb()

    # we don't support stopping while the file is being downloaded
    # (but the user can interrupt playing after it has been downloaded)
    def stop(self):
        pass


# register our handler
av_player.players.append(GTTSPlayer(mw.taskman))
