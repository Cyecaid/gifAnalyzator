import logging
import tkinter as tk
import click

from gif_gui import GifGUI
from gif_parser import GifParser
from info_output import print_file_description, print_frames_description


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
        logging.info(print_file_description(gif_parser))

    if frames:
        logging.info(print_frames_description(gif_parser))

    if animate and gif_parser.frames:
        root = tk.Tk()
        viewer = GifGUI(root, gif_parser)
        viewer.animate_gif()
        root.mainloop()


if __name__ == "__main__":
    main()
