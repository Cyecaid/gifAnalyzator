import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from gif_parser import GifParser
from pathlib import Path


class GifAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GIF Analyzer with Pillow Checkerboard")
        self.geometry("800x600")
        self.resizable(False, False)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="x", padx=5, pady=5)

        self.select_button = ctk.CTkButton(
            self.top_frame,
            text="Select GIF File",
            command=self.open_file
        )
        self.select_button.pack(side="left", padx=5)

        self.zoom_frame = ctk.CTkFrame(self.top_frame)
        self.zoom_frame.pack(side="right", padx=5)

        self.zoom_out_btn = ctk.CTkButton(
            self.zoom_frame,
            text="-",
            width=30,
            command=self.zoom_out
        )
        self.zoom_out_btn.pack(side="left", padx=2)

        self.zoom_in_btn = ctk.CTkButton(
            self.zoom_frame,
            text="+",
            width=30,
            command=self.zoom_in
        )
        self.zoom_in_btn.pack(side="left", padx=2)

        self.reset_zoom_btn = ctk.CTkButton(
            self.zoom_frame,
            text="Reset",
            width=60,
            command=self.reset_zoom
        )
        self.reset_zoom_btn.pack(side="left", padx=2)

        self.playback_frame = ctk.CTkFrame(self.main_frame)
        self.playback_frame.pack(fill="x", padx=5, pady=5)

        self.controls_left = ctk.CTkFrame(self.playback_frame)
        self.controls_left.pack(side="left", padx=5)

        self.prev_frame_btn = ctk.CTkButton(
            self.controls_left,
            text="\u25C1",
            width=30,
            command=self.prev_frame
        )
        self.prev_frame_btn.pack(side="left", padx=2)

        self.play_pause_btn = ctk.CTkButton(
            self.controls_left,
            text="PLAY",
            width=50,
            command=self.toggle_animation
        )
        self.play_pause_btn.pack(side="left", padx=2)

        self.next_frame_btn = ctk.CTkButton(
            self.controls_left,
            text="\u25B7",
            width=30,
            command=self.next_frame
        )
        self.next_frame_btn.pack(side="left", padx=2)

        self.frame_label = ctk.CTkLabel(self.controls_left, text="Frame: 0/0")
        self.frame_label.pack(side="left", padx=5)

        self.controls_right = ctk.CTkFrame(self.playback_frame)
        self.controls_right.pack(side="right", padx=5)

        self.speed_label = ctk.CTkLabel(self.controls_right, text="Speed:")
        self.speed_label.pack(side="left", padx=2)

        self.speed_options = ["0.25x", "0.5x", "1x", "2x", "4x"]
        self.speed_var = tk.StringVar(value="1x")
        self.speed_menu = ctk.CTkOptionMenu(
            self.controls_right,
            values=self.speed_options,
            variable=self.speed_var,
            width=70,
            command=self.change_speed
        )
        self.speed_menu.pack(side="left", padx=2)

        self.canvas = tk.Canvas(self.main_frame, width=400, height=300, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10, fill="both", expand=True)

        self.info_text = ctk.CTkTextbox(self.main_frame, height=200)
        self.info_text.pack(fill="x", padx=5, pady=(5, 0))

        self.copy_frame = ctk.CTkFrame(self.main_frame)
        self.copy_frame.pack(fill="x", padx=5, pady=(2, 5))

        self.copy_button = ctk.CTkButton(
            self.copy_frame,
            text="Copy Result",
            width=100,
            command=self.copy_result
        )
        self.copy_button.pack(side="right", padx=5)

        self.save_button = ctk.CTkButton(
            self.copy_frame,
            text="Save As",
            width=100,
            command=self.save_result
        )
        self.save_button.pack(side="right", padx=5)

        self.frames = []
        self.photo_frames = []
        self.current_frame_index = 0
        self.total_frames = 0
        self.animation_speed = 100
        self.animation_running = False
        self.current_file = None

        self.zoom_factor = 1
        self.max_zoom = 8
        self.min_zoom = 1

        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, event):
        self.update_current_frame()

    def draw_checkerboard_with_pillow(self, frame_image, cell_size=20):
        frame_width, frame_height = frame_image.size

        checkerboard = Image.new("RGBA", (frame_width, frame_height), (255, 255, 255, 0))
        for x in range(0, frame_width, cell_size):
            for y in range(0, frame_height, cell_size):
                if (x // cell_size + y // cell_size) % 2 == 0:
                    for dx in range(cell_size):
                        for dy in range(cell_size):
                            if x + dx < frame_width and y + dy < frame_height:
                                checkerboard.putpixel((x + dx, y + dy), (192, 192, 192, 255))

        checkerboard.paste(frame_image, (0, 0), frame_image)
        return checkerboard

    def update_frame_counter(self):
        self.frame_label.configure(text=f"Frame: {self.current_frame_index + 1}/{self.total_frames}")

    def prev_frame(self):
        if not self.frames:
            return
        self.stop_animation()
        self.current_frame_index = (self.current_frame_index - 1) % self.total_frames
        self.update_current_frame()

    def next_frame(self):
        if not self.frames:
            return
        self.stop_animation()
        self.current_frame_index = (self.current_frame_index + 1) % self.total_frames
        self.update_current_frame()

    def toggle_animation(self):
        if not self.frames:
            return
        if self.animation_running:
            self.stop_animation()
            self.play_pause_btn.configure(text="PLAY")
        else:
            self.start_animation()
            self.play_pause_btn.configure(text="STOP")

    def stop_animation(self):
        self.animation_running = False

    def start_animation(self):
        self.animation_running = True
        self.play_pause_btn.configure(text="STOP")
        self.animate_gif()

    def animate_gif(self):
        if not self.animation_running or not self.frames:
            return
        self.current_frame_index = (self.current_frame_index + 1) % self.total_frames
        self.update_current_frame()
        self.after(self.animation_speed, self.animate_gif)

    def update_current_frame(self):
        if self.frames:
            self.canvas.delete("gif")

            frame_image = self.frames[self.current_frame_index]

            self.checkerboard_image = ImageTk.PhotoImage(frame_image)

            w = self.canvas.winfo_width() // 2
            h = self.canvas.winfo_height() // 2
            self.canvas.create_image(w, h, image=self.checkerboard_image, anchor="center", tags="gif")
            self.update_frame_counter()

    def change_speed(self, value):
        speed_multiplier = {
            "0.25x": 4.0,
            "0.5x": 2.0,
            "1x": 1.0,
            "2x": 0.5,
            "4x": 0.25
        }
        self.animation_speed = int(100 * speed_multiplier[value])

    def zoom_in(self):
        if self.zoom_factor < self.max_zoom:
            self.zoom_factor *= 2
            self.reload_frames()

    def zoom_out(self):
        if self.zoom_factor > self.min_zoom:
            self.zoom_factor //= 2
            self.reload_frames()

    def reset_zoom(self):
        if not self.frames:
            return
        self.zoom_factor = 1
        self.reload_frames()

    def reload_frames(self):
        if not self.current_file:
            return

        self.load_gif(self.current_file)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif")])
        if file_path:
            self.load_gif(file_path)

    def load_gif(self, file_path):
        self.stop_animation()
        self.play_pause_btn.configure(text="PLAY")
        self.frames = []
        self.photo_frames = []
        self.current_frame_index = 0
        self.animation_running = False
        self.current_file = file_path
        self.zoom_factor = 1

        base_image = None
        gif = Image.open(file_path)
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA")
            if base_image is None:
                base_image = Image.new("RGBA", gif.size)
            base_image.paste(frame, (0, 0), frame)
            checkerboard_frame = self.draw_checkerboard_with_pillow(base_image)
            self.frames.append(checkerboard_frame)

        self.total_frames = len(self.frames)
        self.update_frame_counter()
        if self.frames:
            self.update_current_frame()

        self.analyze_current_file()

    def analyze_current_file(self):
        if not hasattr(self, 'current_file') or not self.current_file:
            print("No file loaded to analyze")
            return

        try:
            parser = GifParser(Path(self.current_file))
            self.gif_info = parser.parse_file()

            self.info_text.configure(state="normal")
            self.info_text.delete("1.0", "end")

            self.info_text.insert("end", "=== GIF Information ===\n")
            self.info_text.insert("end", self.format_table(self.gif_info['headers']))

            self.info_text.insert("end", "\n\n=== Frame Information ===")
            for i, frame in enumerate(self.gif_info['frames']):
                self.info_text.insert("end", f"\nFrame {i + 1}:")
                for key, value in frame.items():
                    self.info_text.insert("end", f"\n{key}: {value}")

            self.info_text.configure(state="disabled")

        except Exception as e:
            print(f"Error analyzing GIF: {str(e)}")

    def get_formatted_result(self):
        if not hasattr(self, 'gif_info'):
            return ""

        text = []

        text.append("=== GIF Information ===")
        for section, items in self.gif_info['headers'].items():
            text.append(f"\n{section}:")
            for key, (value, description) in items.items():
                text.append(f"{key}: {value} ({description})")

        text.append("\n=== Frame Information ===")
        for i, frame in enumerate(self.gif_info['frames'], 1):
            text.append(f"\nFrame {i}:")
            for key, value in frame.items():
                text.append(f"{key}: {value}")

        return "\n".join(text)

    def format_table(self, data):
        result = []
        for section, items in data.items():
            result.append(f"{section}:")
            for key, (value, description) in items.items():
                result.append(f"{key}: {value} ({description})")
        return "\n".join(result)

    def copy_result(self):
        result = self.get_formatted_result()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)

    def save_result(self):
        result = self.get_formatted_result()
        if not result.strip():
            return

        default_name = "analysis.txt"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=default_name
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result)
            except Exception as e:
                print(f"Error saving file: {str(e)}")

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = GifAnalyzer()
    app.run()