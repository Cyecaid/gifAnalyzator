from lzw_decoder import LZWDecoder


def test_empty_data():
    expected = []
    decompressor = LZWDecoder(2, [])
    result = decompressor.decode()
    assert result == expected


def test_only_clear_and_end_codes():
    expected = [0]
    data = b'D\x01'
    decompressor = LZWDecoder(2, data)
    result = decompressor.decode()
    assert result == expected


def test_big_data():
    expected = [0]
    data = b'D\x01' * 1000
    decompressor = LZWDecoder(2, data)
    result = decompressor.decode()
    assert result == expected
