import argparse
import logging
import tkinter as tk

from gif_viewer import GifViewer
from gif_parser import GifParser
from info_output import get_descriptor, print_all_frames_headers


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
