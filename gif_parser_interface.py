import argparse
import logging
import tkinter as tk

from GifParser.gif_viewer import GifViewer
from GifParser.gif_parser import GifParser


def get_descriptor(parser):
    result = f"{parser.logical_screen_descriptor}\n"
    return result


def print_all_frames_headers(parser):
    result = f"{get_descriptor(parser)}\n"
    for i, frame in enumerate(parser.frames, start=1):
        result += f"Кадр {i}:\n"
        result += f"{frame}\n"
        if frame.graphic_control_extension:
            result += f"{frame.graphic_control_extension}\n"
        if frame.plain_text_ext:
            result += f"{frame.plain_text_ext}\n"
        if frame.application_ext:
            result += f"{frame.application_ext}\n"
        if frame.comment_ext:
            result += f"{frame.comment_ext}\n"
        result += "\n"
    return result


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:\n%(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Путь к GIF-файлу")
    parser.add_argument("--descriptor", "-d", action="store_true", help="Показать дескриптор экрана")
    parser.add_argument("--headers", "-H", action="store_true", help="Показать заголовки для каждого кадра")
    parser.add_argument("--animate", "-a", action="store_true", help="Показать изображение/анимацию")
    args = parser.parse_args()
    filepath = args.input

    gif_parser = GifParser(filepath)
    gif_parser.parse()

    if args.descriptor:
        logging.info(get_descriptor(gif_parser))

    if args.headers:
        logging.info(print_all_frames_headers(gif_parser))

    if args.animate and gif_parser.frames:
        root = tk.Tk()
        viewer = GifViewer(root, gif_parser)
        viewer.animate_gif()
        root.mainloop()


if __name__ == "__main__":
    main()
