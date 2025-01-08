import unittest
import tkinter as tk

from GifParser.gif_viewer import GifViewer
from GifParser.gif_parser import GifParser


class TestGifViewer(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_calculate_window_size(self):
        parser = GifParser("Images\small.gif")
        parser.parse()
        viewer = GifViewer(self.root, parser)

        screen_width = 1920
        screen_height = 1080
        expected_width = 22
        expected_height = 22
        width, height = viewer._calculate_window_size(screen_width, screen_height)
        self.assertEqual(expected_width, width)
        self.assertEqual(expected_height, height)

    def test_create_checkerboard(self):
        parser = GifParser("Images\small.gif")
        parser.parse()
        viewer = GifViewer(self.root, parser)

        expected_color1 = "#C8C8C8"
        expected_color2 = "#646464"
        checkerboard = viewer._create_checkerboard(20, 20)

        for y in range(20):
            for x in range(20):
                expected_color = expected_color1 if ((x // 10 + y // 10) % 2 == 0) else expected_color2
                self.assertEqual(expected_color, checkerboard[y][x])

    def test_process_disposal_method_2(self):
        parser = GifParser("Images\disp_method_2.gif")
        parser.parse()

        parser.frames[1].graphic_control_extension.disposal_method = 2

        viewer = GifViewer(self.root, parser)
        viewer.current_frame_idx = 1
        viewer._process_disposal()

        for y in range(0, 300):
            for x in range(0, 300):
                tile_x, tile_y = x // 10, y // 10
                expected_color = "#C8C8C8" if (tile_x + tile_y) % 2 == 0 else "#646464"
                self.assertEqual(expected_color, viewer.base_image[y][x])

    def test_process_disposal_method_3(self):
        parser = GifParser("Images\disp_method_3.gif")
        parser.parse()

        parser.frames[0].graphic_control_extension.disposal_method = 3
        parser.frames[1].graphic_control_extension.disposal_method = 3

        viewer = GifViewer(self.root, parser)
        viewer._process_disposal()
        viewer.current_frame_idx = 1
        viewer._process_disposal()

        self.assertEqual(1, len(viewer.previous_images_stack))
        self.assertEqual(viewer.base_image, viewer.previous_images_stack[0])

    def test_clear_image(self):
        parser = GifParser("Images\small.gif")
        parser.parse()
        viewer = GifViewer(self.root, parser)

        viewer._clear_image(parser.frames[0].image_descriptor)

        self.assertEqual(1, len(viewer.base_image))
        self.assertEqual(1, len(viewer.base_image[0]))
        self.assertEqual("#C8C8C8", viewer.base_image[0][0])

    def test_apply_frame(self):
        parser = GifParser("Images\small.gif")
        parser.parse()
        viewer = GifViewer(self.root, parser)

        viewer._apply_frame(parser.frames[0])

        self.assertEqual(1, len(viewer.base_image))
        self.assertEqual(1, len(viewer.base_image[0]))
        self.assertEqual("#B80000", viewer.base_image[0][0])

if __name__ == '__main__':
    unittest.main()
