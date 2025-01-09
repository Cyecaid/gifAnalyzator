import logging
import tkinter as tk
import click

from gif_viewer import GifViewer
from gif_parser import GifParser
from info_output import get_descriptor, print_all_frames_headers


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--description", "-d", is_flag=True, help="Информация по файлу")
@click.option("--frames", "-f", is_flag=True, help="Информация о каждом слайде")
@click.option("--animate", "-a", is_flag=True, help="Показать изображение/анимацию и информацию")
def main(input, description, frames, animate):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:\n%(message)s")

    gif_parser = GifParser(input)
    gif_parser.parse()

    if description:
        logging.info(get_descriptor(gif_parser))

    if frames:
        logging.info(print_all_frames_headers(gif_parser))

    if animate and gif_parser.frames:
        root = tk.Tk()
        viewer = GifViewer(root, gif_parser)
        viewer.animate_gif()
        root.mainloop()


if __name__ == "__main__":
    main()
