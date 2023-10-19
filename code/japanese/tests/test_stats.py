from unittest import TestCase

from japanese.stats import KanjiStats
from mock import MagicMock


class TestKanjiStats(TestCase):
    def setUp(self) -> None:
        self.col = MagicMock()
        self.kanji_stats = KanjiStats(self.col, wholeCollection=True)

    def test_kanjiCountStr(self) -> None:
        self.assertEqual(
            self.kanji_stats.kanjiCountStr("Grade-X", 200), "200 Grade-X kanji."
        )

    def test_kanjiCountStr_with_total(self) -> None:
        self.assertEqual(
            self.kanji_stats.kanjiCountStr("Grade-Y", 200, 1000),
            "Grade-Y: 200 of 1000 (20.0%).",
        )
