import logging
import os
from tkinter import filedialog
from PIL import Image


class GifFrameSaver:
    def __init__(self, gif_parser):
        self.gif_parser = gif_parser
        self.full_image = Image.new("RGBA", (gif_parser.screen_descriptor.width, gif_parser.screen_descriptor.height),
                                    (0, 0, 0, 0))

    def save_frames(self, save_path=None, frame_indices=None):
        if save_path is None:
            save_path = filedialog.askdirectory(title="Выберите папку для сохранения кадров")
            if not save_path:
                return

        if frame_indices is None:
            frame_indices = range(len(self.gif_parser.frames))
        else:
            frame_indices = self._parse_frame_indices(frame_indices)

        self.full_image = Image.new("RGBA",
                                    (self.gif_parser.screen_descriptor.width, self.gif_parser.screen_descriptor.height),
                                    (0, 0, 0, 0))

        max_index = len(self.gif_parser.frames) - 1

        for idx in range(len(self.gif_parser.frames)):
            try:
                frame = self.gif_parser.frames[idx]
                self._update_full_image(frame)

                if idx in frame_indices:
                    self._save_frame_as_png(idx, save_path)

                invalid_indices = [idx + 1 for idx in frame_indices if idx > max_index or idx < 0]
                if invalid_indices:
                    logging.warning(f"Часть кадров не были сохранены, так как номер кадра был больше, чем их количество: {invalid_indices}")
            except IndexError:
                logging.error("Во время скачивания произошла ошибка из-за неверного кадра - файл битый")
                return

    @staticmethod
    def _parse_frame_indices(indices):
        parsed_indices = set()
        try:
            for part in indices.split(", "):
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    parsed_indices.update(range(start - 1, end))
                else:
                    parsed_indices.add(int(part) - 1)
        except ValueError:
            logging.error("Кажется вы ввели неверный формат, необходимые кадры можно указывать или одиночно, или диапазоном")
            return []

        return sorted(parsed_indices)

    def _update_full_image(self, frame):
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

        disposal = frame.graphic_control_extension.disposal_method if frame.graphic_control_extension else 0

        if disposal == 2:
            draw = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            self.full_image.paste(draw, (left, top))
        elif disposal == 3 and hasattr(self, "previous_image"):
            self.full_image = self.previous_image.copy()

        if disposal == 3:
            self.previous_image = self.full_image.copy()

        frame_image = Image.new("RGBA", (width, height))
        pixels = frame_image.load()
        try:
            for y in range(height):
                for x in range(width):
                    idx = y * width + x
                    color_idx = frame.image_data[idx]
                    if transparent_idx is not None and color_idx == transparent_idx:
                        continue

                    rgb = color_table[color_idx]
                    pixels[x, y] = (rgb[0], rgb[1], rgb[2], 255)

            self.full_image.paste(frame_image, (left, top), frame_image)
        except IndexError:
            raise

    def _save_frame_as_png(self, frame_idx, save_path):
        filename = os.path.join(save_path, f"frame_{frame_idx + 1:03d}.png")
        self.full_image.save(filename, "PNG")
        logging.info(f"Кадр {frame_idx + 1} сохранён")
