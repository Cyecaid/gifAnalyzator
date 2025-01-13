import logging
import tkinter as tk
from tkinter import filedialog

import click

from gif_gui import GifGUI
from gif_parser import GifParser
from info_output import print_file_description, print_frames_description
from gif_frame_saver import GifFrameSaver
from gif_custom_errors import GifFormatError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:\n%(message)s")

@click.command()
@click.argument("input", type=click.Path())
@click.option("--description", "-d", is_flag=True, help="Информация по файлу")
@click.option("--frames", "-f", is_flag=True, help="Информация о каждом слайде")
@click.option("--animate", "-a", is_flag=True, help="Показать изображение/анимацию и информацию")
@click.option("--save", "-s", multiple=True, type=str, help="Сохранить кадры. Укажите 'all' для всех кадров или номера кадров через запятую.")
def main(input, description, frames, animate, save):
    try:
        gif_parser = GifParser(input)
        gif_parser.parse()

        if description:
            logging.info(print_file_description(gif_parser))

        if frames:
            logging.info(print_frames_description(gif_parser))

        if save:
            frame_saver = GifFrameSaver(gif_parser)
            logging.info("Выберите папку для сохранения")
            save_path = filedialog.askdirectory()
            if not save_path:
                logging.warning("Сохранение отменено пользователем.")
                return

            for save_flag in save:
                if save_flag == "all":
                    frame_saver.save_frames(save_path=save_path)
                else:
                    try:
                        frame_saver.save_frames(save_path=save_path, frame_indices=save_flag)
                    except ValueError:
                        logging.error("Некорректный формат списка кадров. Используйте числа, разделённые запятыми.")

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
