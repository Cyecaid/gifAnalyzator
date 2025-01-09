import pytest
from unittest.mock import MagicMock
from info_output import print_file_description, print_frames_description


class TestGifParser:

    @pytest.fixture
    def mock_parser(self):
        mock = MagicMock()
        mock.screen_descriptor = "Screen Descriptor Mock"
        mock.frames = [
            MagicMock(
                __str__=lambda self: "Frame 1 Mock",
                graphic_control_extension="Graphic Control Extension Mock",
                plain_text_ext="Plain Text Extension Mock",
                application_ext="Application Extension Mock",
                comment_ext="Comment Extension Mock"
            ),
            MagicMock(
                __str__=lambda self: "Frame 2 Mock",
                graphic_control_extension=None,
                plain_text_ext=None,
                application_ext=None,
                comment_ext=None
            )
        ]
        return mock

    def test_print_file_description(self, mock_parser):
        assert print_file_description(mock_parser) == "Screen Descriptor Mock\n"

    def test_print_frames_description(self, mock_parser):
        expected_output = (
            "Screen Descriptor Mock\n\n"
            "* Кадр 1:\n"
            "Frame 1 Mock\n"
            "Graphic Control Extension Mock\n"
            "Plain Text Extension Mock\n"
            "Application Extension Mock\n"
            "Comment Extension Mock\n\n"
            "* Кадр 2:\n"
            "Frame 2 Mock\n\n"
        )
        assert print_frames_description(mock_parser) == expected_output