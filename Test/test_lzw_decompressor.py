import unittest

from lzw_decompressor import LZWDecompressor


class TestLZWDecompressor(unittest.TestCase):
    def test_empty_data(self):
        expected = []
        decompressor = LZWDecompressor(2, [])
        result = decompressor.decode()
        self.assertEqual(expected, result)

    def test_only_clear_and_end_codes(self):
        expected = [0]
        data = b'D\x01'
        decompressor = LZWDecompressor(2, data)
        result = decompressor.decode()
        self.assertEqual(expected, result)

    def test_big_data(self):
        expected = [0]
        data = b'D\x01' * 1000
        decompressor = LZWDecompressor(2, data)
        result = decompressor.decode()
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
