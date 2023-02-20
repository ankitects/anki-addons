# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Register a dummy TTS player to prevent a pop-up being shown when none is available.
"""

from dataclasses import dataclass
from typing import List

from anki.lang import compatMap
from anki.sound import AVTag
from aqt import mw
from aqt.sound import av_player
from aqt.tts import TTSProcessPlayer, TTSVoice

# this is the language map that gtts.lang.tts_langs() outputs
orig_langs = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en-au": "English (Australia)",
    "en-ca": "English (Canada)",
    "en-gb": "English (UK)",
    "en-gh": "English (Ghana)",
    "en-ie": "English (Ireland)",
    "en-in": "English (India)",
    "en-ng": "English (Nigeria)",
    "en-nz": "English (New Zealand)",
    "en-ph": "English (Philippines)",
    "en-tz": "English (Tanzania)",
    "en-uk": "English (UK)",
    "en-us": "English (US)",
    "en-za": "English (South Africa)",
    "eo": "Esperanto",
    "es-es": "Spanish (Spain)",
    "es-us": "Spanish (United States)",
    "et": "Estonian",
    "fi": "Finnish",
    "fr-ca": "French (Canada)",
    "fr-fr": "French (France)",
    "gu": "Gujarati",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "jw": "Javanese",
    "km": "Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "la": "Latin",
    "lv": "Latvian",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "my": "Myanmar (Burmese)",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt-br": "Portuguese (Brazil)",
    "pt-pt": "Portuguese (Portugal)",
    "ro": "Romanian",
    "ru": "Russian",
    "si": "Sinhala",
    "sk": "Slovak",
    "sq": "Albanian",
    "sr": "Serbian",
    "su": "Sundanese",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Filipino",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh-cn": "Chinese (Mandarin/China)",
    "zh-tw": "Chinese (Mandarin/Taiwan)",
}


# we subclass the default voice object to store the gtts language code
@dataclass
class DummyVoice(TTSVoice):
    pass

class DummyPlayer(TTSProcessPlayer):
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

            voices.append(DummyVoice(name="dummy", lang=std_code))
        return voices  # type: ignore

    def _play(self, tag: AVTag) -> None:
        return

# register our handler
av_player.players.append(DummyPlayer(mw.taskman))
