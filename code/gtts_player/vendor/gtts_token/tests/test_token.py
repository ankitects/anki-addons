# coding=UTF-8

import unittest
import requests

from gtts_token import gtts_token


class TestToken(unittest.TestCase):
    """Test gToken"""

    def setUp(self):
        self.tokenizer = gtts_token.Token()

    def test_token(self):
        text = 'test'
        self.assertEqual('278125.134055', self.tokenizer.calculate_token(text, seed="406986.2817744745"))

    def test_real(self):
        text = "Hello"
        token = self.tokenizer.calculate_token(text)
        payload = {
            'q' : text,
            'tl' : "en",
            'client' : 't',
            'tk' : token
        }

        r = requests.get('https://translate.google.com/translate_tts', params=payload)
        self.assertEqual(200, r.status_code)


if __name__ == '__main__':
    unittest.main()
