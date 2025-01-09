from GifParser.gif_parser import GifParser
from GifStructs.gif_frame import GifFrame
import tkinter as tk


class GifViewer:
    def __init__(self, root, gif_parser: GifParser):
        self.root = root
        self.gif_parser = gif_parser
        self.current_frame_idx = 0

        self.width = gif_parser.logical_screen_descriptor.width
        self.height = gif_parser.logical_screen_descriptor.height

        self.checkerboard = self._create_checkerboard(self.width, self.height)
        self._configure_root_window(root)
        self._create_ui_components()
        self.base_image = [row.copy() for row in self.checkerboard]
        self.previous_images_stack = []

    def _configure_root_window(self, root):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width, window_height = self._calculate_window_size(screen_width, screen_height)
        root.geometry(f"{window_width}x{window_height}")

    def _create_ui_components(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self._add_scrollbars(frame)

        self.photo = tk.PhotoImage(width=self.width, height=self.height)
        self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=(0, 0, self.width, self.height))

    def _add_scrollbars(self, frame):
        v_scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scroll.set)

        h_scroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=h_scroll.set)

    def animate_gif(self):
        frame = self.gif_parser.frames[self.current_frame_idx]
        delay = frame.graphic_control_extension.delay_time if frame.graphic_control_extension else 100

        self._frame_processing()
        self._set_frame_into_image(frame)
        self._update_canvas()

        if len(self.gif_parser.frames) > 1:
            if self.current_frame_idx == len(self.gif_parser.frames) - 1:
                self._clear_canvas(frame)
            self.current_frame_idx = (self.current_frame_idx + 1) % len(self.gif_parser.frames)
            self.root.after(delay, self.animate_gif)

    def _calculate_window_size(self, screen_width, screen_height):
        scrollbar_width = 21
        scrollbar_height = 21
        window_width = min(self.width + scrollbar_width, screen_width)
        window_height = min(self.height + scrollbar_height, screen_height)
        return window_width, window_height

    @staticmethod
    def _create_checkerboard(width, height):
        color1, color2 = "#C8C8C8", "#646464"
        return [
            [color1 if (x // 10 + y // 10) % 2 == 0 else color2 for x in range(width)]
            for y in range(height)
        ]

    def _frame_processing(self):
        frame = self.gif_parser.frames[self.current_frame_idx]
        disposal = frame.graphic_control_extension.disposal_method if frame.graphic_control_extension else 0

        if self.current_frame_idx > 0:
            prev_frame = self.gif_parser.frames[self.current_frame_idx - 1]
            prev_disposal = (
                prev_frame.graphic_control_extension.disposal_method
                if prev_frame.graphic_control_extension else 0
            )

            if prev_disposal == 2:
                self._clear_canvas(prev_frame)
            elif prev_disposal == 3 and self.previous_images_stack:
                self.base_image = self.previous_images_stack.pop()

        if disposal == 3:
            self.previous_images_stack.append([row.copy() for row in self.base_image])

    def _clear_canvas(self, frame: GifFrame) -> None:
        left, top, width, height = frame.left, frame.top, frame.width, frame.height
        for y in range(top, top + height):
            for x in range(left, left + width):
                tile_x, tile_y = x // 10, y // 10
                color = "#C8C8C8" if (tile_x + tile_y) % 2 == 0 else "#646464"
                self.base_image[y][x] = color

    def _set_frame_into_image(self, frame: GifFrame) -> None:
        left, top, width, height = frame.left, frame.top, frame.width, frame.height

        color_table = (
            frame.local_color_table.colors
            if frame.local_color_table else self.gif_parser.global_color_table
        )

        transparent_idx = (
            frame.graphic_control_extension.transparent_color_index
            if frame.graphic_control_extension and frame.graphic_control_extension.transparency_flag
            else None
        )

        for y in range(height):
            for x in range(width):
                idx = y * width + x
                color_idx = frame.image_data[idx]
                if transparent_idx is not None and color_idx == transparent_idx:
                    continue
                rgb = color_table[color_idx]
                color = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
                self.base_image[top + y][left + x] = color

    def _update_canvas(self) -> None:
        rows_str = ["{" + " ".join(row) + "}" for row in self.base_image]
        self.photo.put("\n".join(rows_str))
