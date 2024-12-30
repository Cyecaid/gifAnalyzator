import pytest
from unittest.mock import MagicMock
from pathlib import Path
import sys
import io

from cli import main


@pytest.fixture
def mock_gif_parser():
    mock_parser = MagicMock()
    mock_parser.return_value.parse_file.return_value = {
        'headers': {
            'Summary': {
                'Resolution': ('16x16', 'Image dimensions'),
                'Frame Count': (1, 'Total number of frames'),
                'File Size': ('1.0 KB', 'Size on disk'),
                'Duration': ('100ms', 'Total animation duration'),
            },
        },
        'frames': [
            {'Position': (0, 0), 'Size': '16x16', 'Local Color Table': False}
        ],
    }
    return mock_parser


def test_main_with_stdout(monkeypatch, capsys, mock_gif_parser):
    monkeypatch.setattr('gif_parser.GifParser', mock_gif_parser)

    test_args = ["script_name", "mock_gif.gif"]
    monkeypatch.setattr(sys, 'argv', test_args)

    mock_file_path = Path("mock_gif.gif")
    monkeypatch.setattr(Path, "exists", lambda x: True)

    mock_stat = MagicMock()
    mock_stat.st_size = 1024
    monkeypatch.setattr(Path, "stat", lambda x: mock_stat)

    mock_binary_data = io.BytesIO(
        b"GIF89a"
        b"\x10\x00\x10\x00"
        b"\xF7"
        b"\x00"
        b"\x00"
        b"".join([b"\x00\x00\x00" for _ in range(256)]) +
        b"\x21\xF9\x04\x00\x00\x00\x00\x00"
        b"\x2C\x00\x00\x00\x00\x10\x00\x10\x00\x00"
        b"\x02\x16\x8C\x0D\x5B\x04\x21\x7C\x80\x00\x00\x3B"
    )

    monkeypatch.setattr(Path, "open", lambda self, mode: mock_binary_data)

    main()

    captured = capsys.readouterr()
    assert "=== GIF Information ===" in captured.out
    assert "Frame 1:" in captured.out
    assert "Position: (0, 0)" in captured.out