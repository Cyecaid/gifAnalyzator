import logging
import tkinter as tk
import click

from gif_gui import GifGUI
from gif_parser import GifParser
from info_output import print_file_description, print_frames_description
from gif_custom_errors import GifFormatError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:\n%(message)s")


@click.command()
@click.argument("input", type=click.Path())
@click.option("--description", "-d", is_flag=True, help="Информация по файлу")
@click.option("--frames", "-f", is_flag=True, help="Информация о каждом слайде")
@click.option("--animate", "-a", is_flag=True, help="Показать изображение/анимацию и информацию")
def main(input, description, frames, animate):
    try:
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
    except GifFormatError as e:
        logging.error(f"Во время разбора файла произошла следующая ошибка\n{str(e)}")
    except FileNotFoundError as e:
        logging.error(f"Такого файла не существует, убедитесь, что файл введён верно")


if __name__ == "__main__":
    main()
