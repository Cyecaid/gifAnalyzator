from PIL import Image

import pytest
from unittest.mock import MagicMock, patch
from gif_analyzer import GifAnalyzer


@pytest.fixture
def mock_gif_parser(monkeypatch):
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
    monkeypatch.setattr('gif_parser.GifParser', mock_parser)
    return mock_parser


def test_open_file(monkeypatch):
    mock_file = "/path/to/test.gif"

    monkeypatch.setattr('tkinter.filedialog.askopenfilename', lambda **kwargs: mock_file)

    app = GifAnalyzer()
    app.load_gif = MagicMock()

    app.open_file()
    app.load_gif.assert_called_with(mock_file)

def test_load_gif(mock_gif_parser):
    app = GifAnalyzer()

    # Mock tkinter canvas
    app.canvas = MagicMock()

    # Create a real Pillow image to use as a mock frame
    mock_image = Image.new("RGBA", (16, 16), (255, 0, 0, 255))  # A red 16x16 image
    mock_sequence = [mock_image]

    # Mock ImageTk.PhotoImage to prevent TclError
    with patch('PIL.Image.open', return_value=mock_image), \
         patch('PIL.ImageSequence.Iterator', return_value=mock_sequence), \
         patch('PIL.ImageTk.PhotoImage', return_value=MagicMock()):

        app.load_gif("/path/to/test.gif")

    # Assertions
    assert len(app.frames) == 1
    assert app.total_frames == 1
    assert app.current_frame_index == 0

    # Verify that the frame was drawn
    app.canvas.create_image.assert_called()
    app.update_current_frame()
    app.canvas.create_image.assert_called_with(
        app.canvas.winfo_width() // 2,
        app.canvas.winfo_height() // 2,
        image=app.checkerboard_image,
        anchor="center",
        tags="gif"
    )
    assert app.frame_label.cget("text") == "Frame: 1/1"



def test_toggle_animation():
    app = GifAnalyzer()
    app.frames = [MagicMock()]
    app.stop_animation = MagicMock()
    app.start_animation = MagicMock()

    # Test start animation
    app.toggle_animation()
    assert app.animation_running is False


def test_zoom_in(monkeypatch):
    app = GifAnalyzer()
    app.frames = [MagicMock()]
    app.reload_frames = MagicMock()

    app.zoom_factor = 1
    app.max_zoom = 8

    app.zoom_in()
    assert app.zoom_factor == 2
    app.reload_frames.assert_called_once()
