import pytest
from unittest.mock import MagicMock, patch
from gif_gui import GifGUI


@pytest.fixture
def mock_gif_parser():
    # Create a mock gif_parser with necessary attributes
    mock_parser = MagicMock()
    mock_parser.screen_descriptor.width = 100
    mock_parser.screen_descriptor.height = 100
    mock_parser.frames = [
        MagicMock(
            left=0,
            top=0,
            width=50,
            height=50,
            local_color_table=None,
            graphic_control_extension=MagicMock(
                disposal_method=2,
                transparent_color_index=0,
                transparency_flag=True,
                delay_time=100,
            ),
            image_data=[0] * (50 * 50),
        ),
        MagicMock(
            left=10,
            top=10,
            width=30,
            height=30,
            local_color_table=None,
            graphic_control_extension=MagicMock(
                disposal_method=3,
                transparent_color_index=1,
                transparency_flag=True,
                delay_time=200,
            ),
            image_data=[1] * (30 * 30),
        ),
    ]
    mock_parser.global_color_table = [
        (200, 200, 200),  # Transparent color
        (100, 100, 100),  # Another color
    ]
    return mock_parser


@pytest.fixture
def gif_gui(mock_gif_parser):
    # Patch all the GUI components
    with patch("tkinter.Tk"), \
            patch("customtkinter.CTkFrame", MagicMock()), \
            patch("customtkinter.CTkButton", MagicMock()), \
            patch("customtkinter.CTkLabel", MagicMock()), \
            patch("customtkinter.CTkTextbox", MagicMock()), \
            patch("tkinter.Canvas", MagicMock()), \
            patch("tkinter.PhotoImage", MagicMock()):
        root = MagicMock()  # Mock the root window
        gui = GifGUI(root, mock_gif_parser)
        yield gui


def test_init(gif_gui, mock_gif_parser):
    # Test initialization
    assert gif_gui.width == mock_gif_parser.screen_descriptor.width
    assert gif_gui.height == mock_gif_parser.screen_descriptor.height
    assert gif_gui.current_frame_idx == 0
    assert gif_gui.is_playing is False


def test_toggle_play_pause(gif_gui):
    gif_gui._toggle_play_pause()
    assert gif_gui.is_playing is True

    gif_gui._toggle_play_pause()
    assert gif_gui.is_playing is False


def test_previous_frame(gif_gui):
    gif_gui.current_frame_idx = 1
    gif_gui._previous_frame()
    assert gif_gui.current_frame_idx == 0


def test_next_frame(gif_gui):
    gif_gui.current_frame_idx = 0
    gif_gui._next_frame()
    assert gif_gui.current_frame_idx == 1


def test_frame_processing(gif_gui, mock_gif_parser):
    gif_gui.current_frame_idx = 1
    gif_gui._frame_processing()
    assert len(gif_gui.previous_images_stack) == 1


def test_clear_canvas(gif_gui):
    mock_frame = MagicMock(left=0, top=0, width=10, height=10)
    gif_gui._clear_canvas(mock_frame)
    for y in range(mock_frame.top, mock_frame.top + mock_frame.height):
        for x in range(mock_frame.left, mock_frame.left + mock_frame.width):
            tile_x, tile_y = x // 10, y // 10
            expected_color = "#C8C8C8" if (tile_x + tile_y) % 2 == 0 else "#646464"
            assert gif_gui.base_image[y][x] == expected_color


def test_set_frame_into_image(gif_gui, mock_gif_parser):
    frame = mock_gif_parser.frames[1]
    gif_gui._set_frame_into_image(frame)
    for y in range(frame.height):
        for x in range(frame.width):
            idx = y * frame.width + x
            assert gif_gui.base_image[frame.top + y][frame.left + x] in ["#646464", '#C8C8C8']


def test_update_canvas(gif_gui):
    gif_gui._update_canvas()
    gif_gui.canvas.create_image.assert_called()
