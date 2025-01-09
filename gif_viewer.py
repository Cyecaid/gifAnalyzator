import tkinter as tk
import customtkinter as ctk

from info_output import print_all_frames_headers, get_descriptor


class GifViewer:
    def __init__(self, root, gif_parser):
        self.root = root
        self.gif_parser = gif_parser
        self.current_frame_idx = 0
        self.is_playing = False

        self.width = gif_parser.logical_screen_descriptor.width
        self.height = gif_parser.logical_screen_descriptor.height

        self.checkerboard = self._create_checkerboard(self.width, self.height)
        self._configure_root_window(root)
        self._create_ui_components()
        self.base_image = [row.copy() for row in self.checkerboard]
        self.previous_images_stack = []

    @staticmethod
    def _configure_root_window(root):
        default_width, default_height = 800, 600
        root.geometry(f"{default_width}x{default_height}")

    def _create_ui_components(self):
        top_controls_frame = ctk.CTkFrame(self.root)
        top_controls_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        self.prev_frame_btn = ctk.CTkButton(top_controls_frame, text="Предыдущий кадр", command=self._previous_frame, state=tk.DISABLED)
        self.prev_frame_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.play_pause_btn = ctk.CTkButton(top_controls_frame, text="Старт", command=self._toggle_play_pause)
        self.play_pause_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_frame_btn = ctk.CTkButton(top_controls_frame, text="Следующий кадр", command=self._next_frame, state=tk.NORMAL if len(self.gif_parser.frames) > 1 else tk.DISABLED)
        self.next_frame_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.current_frame_label = ctk.CTkLabel(top_controls_frame, text=f"Кадр: {self.current_frame_idx + 1}/{len(self.gif_parser.frames)}")
        self.current_frame_label.pack(side=tk.LEFT, padx=5, pady=5)

        frame = ctk.CTkFrame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self._add_scrollbars(frame)

        self.photo = tk.PhotoImage(width=self.width, height=self.height)
        self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=(0, 0, self.width, self.height))

        self.info_textbox = ctk.CTkTextbox(self.root, height=200)
        self.info_textbox.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        self._populate_info()

    def _add_scrollbars(self, frame):
        v_scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scroll.set)

        h_scroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=h_scroll.set)

    def animate_gif(self):
        if not self.is_playing:
            return

        frame = self.gif_parser.frames[self.current_frame_idx]
        delay = (frame.graphic_control_extension.delay_time * 10) if frame.graphic_control_extension else 100

        self._frame_processing()
        self._set_frame_into_image(frame)
        self._update_canvas()

        self.current_frame_label.configure(text=f"Кадр: {self.current_frame_idx + 1}/{len(self.gif_parser.frames)}")

        if len(self.gif_parser.frames) > 1:
            if self.current_frame_idx == len(self.gif_parser.frames) - 1:
                self._clear_canvas(frame)
            self.current_frame_idx = (self.current_frame_idx + 1) % len(self.gif_parser.frames)
            self.root.after(delay, self.animate_gif)

    def _toggle_play_pause(self):
        self.is_playing = not self.is_playing
        self.play_pause_btn.configure(text="Пауза" if self.is_playing else "Старт")

        self.prev_frame_btn.configure(state=tk.DISABLED if self.is_playing else (tk.NORMAL if self.current_frame_idx > 0 else tk.DISABLED))
        self.next_frame_btn.configure(state=tk.DISABLED if self.is_playing else (tk.NORMAL if self.current_frame_idx < len(self.gif_parser.frames) - 1 else tk.DISABLED))

        self.current_frame_label.configure(text=f"Кадр: {self.current_frame_idx + 1}/{len(self.gif_parser.frames)}")

        if self.is_playing:
            self.animate_gif()

    def _previous_frame(self):
        if self.current_frame_idx > 0:
            self.current_frame_idx -= 1
            self._update_frame()

        self.prev_frame_btn.configure(state=tk.DISABLED if self.current_frame_idx == 0 else tk.NORMAL)
        self.next_frame_btn.configure(state=tk.NORMAL)

    def _next_frame(self):
        if self.current_frame_idx < len(self.gif_parser.frames) - 1:
            self.current_frame_idx += 1
            self._update_frame()

        self.next_frame_btn.configure(state=tk.DISABLED if self.current_frame_idx == len(self.gif_parser.frames) - 1 else tk.NORMAL)
        self.prev_frame_btn.configure(state=tk.NORMAL)

    def _update_frame(self):
        frame = self.gif_parser.frames[self.current_frame_idx]
        self._frame_processing()
        self._set_frame_into_image(frame)
        self._update_canvas()

        self.current_frame_label.configure(text=f"Кадр: {self.current_frame_idx + 1}/{len(self.gif_parser.frames)}")

    def _populate_info(self):
        info = get_descriptor(self.gif_parser) + print_all_frames_headers(self.gif_parser)
        self.info_textbox.insert("1.0", info)

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

    def _clear_canvas(self, frame):
        left, top, width, height = frame.left, frame.top, frame.width, frame.height
        for y in range(top, top + height):
            for x in range(left, left + width):
                tile_x, tile_y = x // 10, y // 10
                color = "#C8C8C8" if (tile_x + tile_y) % 2 == 0 else "#646464"
                self.base_image[y][x] = color

    def _set_frame_into_image(self, frame):
        left, top, width, height = frame.left, frame.top, frame.width, frame.height

        color_table = (
            frame.local_color_table
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

    def _update_canvas(self):
        rows_str = ["{" + " ".join(row) + "}" for row in self.base_image]
        self.photo.put("\n".join(rows_str))
