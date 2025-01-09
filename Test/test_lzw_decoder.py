import unittest

from lzw_decoder import LZWDecoder


class TestLZWDecompressor(unittest.TestCase):
    def test_empty_data(self):
        expected = []
        decompressor = LZWDecoder(2, [])
        result = decompressor.decode()
        self.assertEqual(expected, result)

    def test_only_clear_and_end_codes(self):
        expected = [0]
        data = b'D\x01'
        decompressor = LZWDecoder(2, data)
        result = decompressor.decode()
        self.assertEqual(expected, result)

    def test_big_data(self):
        expected = [0]
        data = b'D\x01' * 1000
        decompressor = LZWDecoder(2, data)
        result = decompressor.decode()
        self.assertEqual(expected, result)

