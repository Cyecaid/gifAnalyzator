import pytest
from unittest.mock import MagicMock, mock_open
from pathlib import Path
from gif_parser import GifParser


@pytest.fixture
def mock_file_path():
    return Path("mock_gif.gif")


@pytest.fixture
def gif_binary_data():
    return (
        b"GIF89a"
        b"\x10\x00\x10\x00" 
        b"\xf7"
        b"\x00"
        b"\x00" +
        b"".join([b"\x00\x00\x00" for _ in range(256)]) +
        b"\x21\xf9\x04\x00\x00\x00\x00\x00"  
        b"\x2c\x00\x00\x00\x00\x10\x00\x10\x00\x00"  
        b"\x02\x16\x8c\x0d\x5b\x04\x21\x7c\x80\x00\x00\x3b"
    )


def test_parse_file(mock_file_path, gif_binary_data, monkeypatch):
    mock_open_func = mock_open(read_data=gif_binary_data)
    monkeypatch.setattr("builtins.open", mock_open_func)
    monkeypatch.setattr(Path, "open", mock_open_func)

    monkeypatch.setattr(Path, "exists", lambda x: True)

    mock_stat = MagicMock()
    mock_stat.st_size = len(gif_binary_data)
    monkeypatch.setattr(Path, "stat", lambda x: mock_stat)

    parser = GifParser(mock_file_path)
    info = parser.parse_file()

    assert info["dimensions"] == (16, 16)
    assert info["frame_count"] == 1
    assert len(info["frames"]) == 1
    assert info["headers"]["Summary"]["Resolution"] == ("16x16", "Image dimensions")
    assert "Header" in info["headers"]
    assert "Logical Screen Descriptor" in info["headers"]
    assert "Canvas Size" in info["headers"]["Logical Screen Descriptor"]
    assert info["headers"]["Logical Screen Descriptor"]["Canvas Size"] == ("16x16", "Image dimensions")


def test_parse_header(mock_file_path, gif_binary_data, monkeypatch):
    mock_open_func = mock_open(read_data=gif_binary_data)
    monkeypatch.setattr("builtins.open", mock_open_func)
    monkeypatch.setattr(Path, "open", mock_open_func)

    monkeypatch.setattr(Path, "exists", lambda x: True)

    parser = GifParser(mock_file_path)

    with mock_open_func(mock_file_path.open("rb")) as f:
        parser._parse_header(f)

    headers = parser.headers_info["Header"]
    assert headers["Signature"] == ("GIF", "GIF signature")
    assert headers["Version"] == ("89a", "GIF version")


def test_logical_screen_descriptor(mock_file_path, gif_binary_data, monkeypatch):
    mock_open_func = mock_open(read_data=gif_binary_data)
    monkeypatch.setattr("builtins.open", mock_open_func)
    monkeypatch.setattr(Path, "open", mock_open_func)

    monkeypatch.setattr(Path, "exists", lambda x: True)

    parser = GifParser(mock_file_path)

    with mock_open_func(mock_file_path.open("rb")) as f:
        f.read(6)
        parser._parse_logical_screen_descriptor(f)

    descriptor = parser.headers_info["Logical Screen Descriptor"]
    assert descriptor["Canvas Size"] == ("16x16", "Image dimensions")
    assert descriptor["Global Color Table"] == (True, "Whether global color table exists")
    assert descriptor["Color Resolution"] == (8, "Bits per primary color")
    assert descriptor["Color Table Size"] == (256, "Number of entries in global color table")


def test_frame_parsing(mock_file_path, gif_binary_data, monkeypatch):
    mock_open_func = mock_open(read_data=gif_binary_data)
    monkeypatch.setattr("builtins.open", mock_open_func)
    monkeypatch.setattr(Path, "open", mock_open_func)

    monkeypatch.setattr(Path, "exists", lambda x: True)

    parser = GifParser(mock_file_path)

    with mock_open_func(mock_file_path.open("rb")) as f:
        f.read(6)
        f.read(7)
        f.read(3 * 256)
        parser._parse_frames(f)

    assert parser.frame_count == 1
    assert len(parser.frames_info) == 1
    assert "Position" in parser.frames_info[0]
    assert parser.frames_info[0]["Size"] == "16x16"

def test_parse_application_extension(mock_file_path, monkeypatch):
    app_extension_data = (
        b"GIF89a"  
        b"\x10\x00\x10\x00"  
        b"\xf7"  
        b"\x00"  
        b"\x00" +
        b"".join([b"\x00\x00\x00" for _ in range(256)]) +
        b"\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00"
    )

    mock_open_func = mock_open(read_data=app_extension_data)
    monkeypatch.setattr("builtins.open", mock_open_func)
    monkeypatch.setattr(Path, "open", mock_open_func)
    monkeypatch.setattr(Path, "exists", lambda x: True)

    parser = GifParser(mock_file_path)

    with mock_open_func(mock_file_path.open("rb")) as f:
        f.read(6)
        f.read(7)
        f.read(3 * 256)
        parser._parse_frames(f)

    metadata = parser.headers_info.get("Metadata", {})
    assert "Loop Count" in metadata
    assert metadata["Loop Count"] == (0, "Number of animation iterations (0 = infinite)")
