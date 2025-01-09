import pytest
from unittest.mock import MagicMock, mock_open, patch
from gif_parser import GifParser
from gif_frame import ApplicationExtension, CommentExtension, PlainTextExtension, GraphicControlExtension


MOCK_GIF_DATA = (
    b'GIF89a'
    b'\x10\x00\x10\x00'
    b'\xF7' 
    b'\x00'
    b'\x00' +
    b'\xFF\xFF\xFF' * 256 +
    b'\x00\x00\x00'
    b'\x21\xF9' 
    b'\x04\x00\x00\x00\x00' 
    b'\x00' 
    b'\x2C'
    b'\x00\x00\x00\x00\x10\x00\x10\x00\x00'
    b'\x08'
    b'\x03'
    b'\x01\x02\x03'
    b'\x00'
    b'\x3B'
)


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_GIF_DATA)
def test_parse(mock_open, mock_exists):
    parser = GifParser("mock_path.gif")
    parser.parse()

    mock_exists.assert_called_once_with("mock_path.gif")
    mock_open.assert_called_once_with("mock_path.gif", "rb")

    assert parser.screen_descriptor.width == 16
    assert parser.screen_descriptor.height == 16
    assert parser.screen_descriptor.global_color_table_flag == 1

    assert parser.global_color_table == [(255, 255, 255)] * 256


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_GIF_DATA)
def test_skip_sub_blocks(mock_open, mock_exists):
    parser = GifParser("mock_path.gif")

    with patch("gif_parser.GifParser._skip_sub_blocks", wraps=parser._skip_sub_blocks) as mock_skip:
        parser.parse()

    mock_skip.assert_called()


def test_parse_graphic_control_extension():
    mock_data = b'\x09\x00\x10\x00'
    result = GifParser._parse_graphic_control_extension(mock_data)

    assert isinstance(result, GraphicControlExtension)
    assert result.disposal_method == 2
    assert result.user_input_flag == 0
    assert result.transparency_flag == 1
    assert result.delay_time == 4096
    assert result.transparent_color_index == 0


def test_parse_plain_text_extension():
    header_data = b'\x00\x00\x00\x00\x10\x00\x10\x00\x01\x01\x02\x03'
    text_data = b'Test Plain Text'
    result = GifParser._parse_plain_text_extension(header_data, text_data)

    assert isinstance(result, PlainTextExtension)
    assert result.left_pos == 0
    assert result.top_pos == 0
    assert result.width == 16
    assert result.height == 16
    assert result.cell_width == 1
    assert result.cell_height == 1
    assert result.foreground_color_index == 2
    assert result.background_color_index == 3
    assert result.text_data == 'Test Plain Text'


def test_parse_application_extension():
    header_data = b'NETSCAPE\x03'
    sub_blocks = b'\x01\x00\x01'
    result = GifParser._parse_application_extension(header_data, sub_blocks)

    assert isinstance(result, ApplicationExtension)
    assert result.application_id == 'NETSCAPE'
    assert result.authentication_code == '\x03'
    assert result.data == sub_blocks


def test_parse_comment_extension():
    comment_data = b'This is a comment'
    result = GifParser._parse_comment_extension(comment_data)

    assert isinstance(result, CommentExtension)
    assert result.comment == 'This is a comment'


def test_parse_extension():
    mock_file = MagicMock()
    mock_file.read.side_effect = [
        b'\xF9',
        b'\x04',
        b'\x09\x00\x10\x00',
        b'\x00',
    ]

    result = GifParser._parse_extension(mock_file)

    graphic_control_extension, plain_text_extension, application_extension, comment_extension = result
    assert graphic_control_extension is not None
    assert plain_text_extension is None
    assert application_extension is None
    assert comment_extension is None


def test_parse_image_descriptor():
    mock_file = MagicMock()
    mock_file.read.return_value = b'\x01\x00\x02\x00\x10\x00\x10\x00\xF0'

    result = GifParser._parse_image_descriptor(mock_file)

    assert result == (1, 2, 16, 16, 0xF0)


def test_parse_local_color_table():
    mock_file = MagicMock()
    mock_file.read.return_value = b'\x00\x00\xFF\xFF\x00\x00\x00\x00\x00'

    packed = 0x87
    result = GifParser._parse_local_color_table(mock_file, packed)

    assert result == [(0, 0, 255), (255, 0, 0), (0, 0, 0)]


def test_read_sub_blocks():
    mock_file = MagicMock()
    mock_file.read.side_effect = [
        b'\x03',
        b'ABC',
        b'\x02',
        b'DE',
        b'\x00',
    ]

    result = GifParser._read_sub_blocks(mock_file)

    assert result == b'ABCDE'

    assert mock_file.read.call_count == 5


def test_parse_pixel_indices():
    mock_file = MagicMock()
    mock_file.read.side_effect = [
        b'\x02',
    ]

    with patch('gif_parser.GifParser._read_sub_blocks', return_value=b'\x08\xFF\x00') as mock_read_sub_blocks:
        with patch('gif_parser.LZWDecoder') as MockLZWDecoder:
            mock_decoder_instance = MockLZWDecoder.return_value
            mock_decoder_instance.decode.return_value = [42, 42, 42]

            result = GifParser._parse_pixel_indices(mock_file)

            assert result == [42, 42, 42]

            MockLZWDecoder.assert_called_once_with(2, b'\x08\xFF\x00')

            mock_read_sub_blocks.assert_called_once()

            mock_file.read.assert_called_once()


from unittest.mock import patch


@patch('logging.error')
def test_parse_screen_descriptor_invalid_header(mock_logging_error):
    header = b'XYZ123'
    descriptor_data = b'\x10\x00\x10\x00\xF7\x00\x00'

    try:
        result = GifParser._parse_screen_descriptor(header, descriptor_data)
        assert False
    except ValueError as e:
        assert True
        mock_logging_error.assert_called_once_with("Неверный формат файла")


@patch('logging.error')
def test_parse_screen_descriptor_invalid_header_length(mock_logging_error):
    header = b'GIF'
    descriptor_data = b'\x10\x00\x10\x00\xF7\x00\x00'

    result = GifParser._parse_screen_descriptor(header, descriptor_data)

    assert result is None
    mock_logging_error.assert_called_once_with("Неверная длина заголовка")


@patch('logging.error')
def test_parse_screen_descriptor_invalid_descriptor_length(mock_logging_error):
    header = b'GIF89a'
    descriptor_data = b'\x10\x00'

    result = GifParser._parse_screen_descriptor(header, descriptor_data)

    assert result is None
    mock_logging_error.assert_called_once_with("Неверна длина логического дескриптора экрана")


@patch('logging.error')
def test_parse_image_descriptor_fail(mock_logging_error):
    mock_file = MagicMock()
    mock_file.read.return_value = b'\x01\x00\x02\x00\x10\x00\x10\x00'

    result = GifParser._parse_image_descriptor(mock_file)

    assert result is None
    mock_logging_error.assert_called_once_with("Неверная длина дескриптора изображения")


@patch('logging.error')
def test_parse_graphic_control_extension_fail(mock_logging_error):
    mock_data = b'\x09\x00\x10'
    result = GifParser._parse_graphic_control_extension(mock_data)

    assert result is None
    mock_logging_error.assert_called_once_with("Неверная длина расширения графики")

@patch('logging.error')
def test_parse_plain_text_extension_fail(mock_logging_error):
    header_data = b'\x00\x00\x00\x00\x10\x00\x10\x00\x01\x01\x02'
    text_data = b'Test Plain Text'
    result = GifParser._parse_plain_text_extension(header_data, text_data)

    assert result is None
    mock_logging_error.assert_called_once_with("Неверная длина расширения простого текста")