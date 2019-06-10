from mock import MagicMock
from unittest import TestCase

from japanese.stats import KanjiStats


class TestKanjiStats(TestCase):
    def setUp(self):
        self.col = MagicMock()
        self.kanji_stats = KanjiStats(self.col, wholeCollection=True)

    def test_kanjiCountStr(self):
        self.assertEqual(
            self.kanji_stats.kanjiCountStr('Grade-X', 200),
            '200 Grade-X kanji.'
        )

    def test_kanjiCountStr_with_total(self):
        self.assertEqual(
            self.kanji_stats.kanjiCountStr('Grade-Y', 200, 1000),
            'Grade-Y: 200 of 1000 (20.0%).'
        )
