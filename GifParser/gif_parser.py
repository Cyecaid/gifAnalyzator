import logging
import os

from GifStructs.GifExtensions.application_extension import GifApplicationExtension
from GifStructs.GifExtensions.comment_extension import GifCommentExtension
from GifStructs.GifExtensions.graphic_control_extension import GifGraphicControlExtension
from GifStructs.GifExtensions.plain_text_extension import GifPlainTextExtension
from GifStructs.gif_frame import GifFrame
from GifStructs.image_descriptor import GifImageDescriptor
from GifStructs.logical_screen_descriptor import GifLogicalScreenDescriptor
from GifStructs.global_color_table import GifGlobalColorTable
from GifStructs.gif_header import GifHeader
from GifStructs.local_color_table import GifLocalColorTable
from GifParser.lzw_decompressor import LZWDecompressor


class GifParser:
    def __init__(self, filename):
        self.filename = filename
        self.header = None
        self.logical_screen_descriptor = None
        self.global_color_table = None
        self.frames = []

    def parse(self):
        """
        Парсинг GIF файла.
        """
        if not os.path.exists(self.filename):
            logging.error(f"Файл {self.filename} не найден.")
            return

        with open(self.filename, 'rb') as f:
            header_data = f.read(6)
            self.header = self.parse_header(header_data)
            log_desc_data = f.read(7)
            self.logical_screen_descriptor = self.parse_logical_screen_descriptor(log_desc_data)
            data = f.read(self.logical_screen_descriptor.global_color_table_size * 3)
            self.global_color_table = self.parse_global_color_table(self.logical_screen_descriptor, data)
            self.parse_blocks(f)

    @staticmethod
    def parse_header(header_data):
        """
        Парсинг заголовка GIF файла.
        :param header_data: Заголовок файла в байтовом формате.
        :return: Заголовок GIF файла.
        """
        signature = header_data[0:3].decode('ascii', errors='replace')
        version = header_data[3:6].decode('ascii', errors='replace')

        if signature != 'GIF':
            logging.error(f"Неверный формат файла!")
            return None

        return GifHeader(signature, version)

    @staticmethod
    def parse_logical_screen_descriptor(log_desc_data):
        """
        Парсинг дескриптора экрана.
        :param log_desc_data: Данные дескриптора экрана в байтовом формате.
        :return: Логический дескриптор экрана.
        """
        width = log_desc_data[0] + 256 * log_desc_data[1]
        height = log_desc_data[2] + 256 * log_desc_data[3]
        packed, bg_color_index, aspect = log_desc_data[4], log_desc_data[5], log_desc_data[6]
        return GifLogicalScreenDescriptor(width, height, packed, bg_color_index, aspect)

    @staticmethod
    def parse_global_color_table(logical_screen_descriptor, data):
        """
        Парсинг глобальной таблицы цветов.
        :param logical_screen_descriptor: Логический дескриптор экрана.
        :param data: Данные таблицы цветов в байтовом формате.
        :return: Глобальная таблица цветов, если есть, иначе None.
        """
        if logical_screen_descriptor.global_color_table_flag:
            colors = [(data[i], data[i + 1], data[i + 2]) for i in range(0, len(data), 3)]
            return GifGlobalColorTable(colors)
        return None

    def parse_blocks(self, f):
        graphic_control_ext = plain_text_ext = application_ext = comment_ext = None
        while True:
            b = f.read(1)
            if len(b) == 0:
                break
            block_id = b[0]
            if block_id == 0x3B:
                break
            elif block_id == 0x21:
                graphic_control_ext, plain_text_ext, application_ext, comment_ext = GifParser.parse_extension(f)
            elif block_id == 0x2C:
                image_descriptor = GifParser.parse_image_descriptor(f)
                local_ct = GifParser.parse_local_color_table(f, image_descriptor)
                indices = GifParser.parse_indices(f)

                frame = GifFrame(image_descriptor, local_ct, graphic_control_ext,
                                 plain_text_ext, application_ext, comment_ext, indices)
                self.frames.append(frame)
                graphic_control_ext = plain_text_ext = application_ext = comment_ext = None
            else:
                GifParser.skip_sub_blocks(f)

    @staticmethod
    def parse_extension(f):
        """
        Парсинг расширения.
        :param f: Открытый GIF файл.
        :return: Расширения, если есть, иначе None.
        """
        graphic_control_ext = plain_text_ext = application_ext = comment_ext = None

        ext_label = f.read(1)[0]
        if ext_label == 0xF9:
            f.read(1)
            gce_data = f.read(4)
            f.read(1)
            graphic_control_ext = GifParser.parse_graphic_control_extension(gce_data)
        elif ext_label == 0x1:
            f.read(1)
            pte_data = f.read(12)
            text_data = GifParser.read_sub_blocks(f)
            plain_text_ext = GifParser.parse_plain_text_extension(pte_data, text_data)
        elif ext_label == 0xFF:
            f.read(1)
            app_data = f.read(11)
            app_sub_blocks = GifParser.read_sub_blocks(f)
            application_ext = GifParser.parse_application_extension(app_data, app_sub_blocks)
        elif ext_label == 0xFE:
            comment_data = GifParser.read_sub_blocks(f)
            comment_ext = GifParser.parse_comment_extension(comment_data)
        else:
            GifParser.skip_sub_blocks(f)

        return graphic_control_ext, plain_text_ext, application_ext, comment_ext

    @staticmethod
    def parse_image_descriptor(f):
        """
        Парсинг дескриптора изображения.
        :param f: Открытый GIF файл.
        :return: Дескриптор изображения.
        """
        img_desc_data = f.read(9)
        left = img_desc_data[0] + 256 * img_desc_data[1]
        top = img_desc_data[2] + 256 * img_desc_data[3]
        width = img_desc_data[4] + 256 * img_desc_data[5]
        height = img_desc_data[6] + 256 * img_desc_data[7]
        packed = img_desc_data[8]
        return GifImageDescriptor(left, top, width, height, packed)

    @staticmethod
    def parse_local_color_table(f, image_descriptor):
        """
        Парсинг локальной таблицы цветов.
        :param f: Открытый GIF файл.
        :param image_descriptor: Дескриптор изображения.
        :return: Локальная таблица цветов, если есть, иначе None.
        """
        local_ct = None
        if image_descriptor.local_color_table_flag:
            size = image_descriptor.local_color_table_size
            data = f.read(size * 3)
            local_ct_colors = [(data[i], data[i + 1], data[i + 2]) for i in range(0, len(data), 3)]
            local_ct = GifLocalColorTable(local_ct_colors)
        return local_ct

    @staticmethod
    def parse_indices(f):
        """
        Парсинг индексов изображения.
        :param f: Открытый GIF файл.
        :return: Индексы изображения.
        """
        lzw_min_code_size = f.read(1)[0]
        img_data_blocks = GifParser.read_sub_blocks(f)
        decompressor = LZWDecompressor(lzw_min_code_size, img_data_blocks)
        return decompressor.decode()

    @staticmethod
    def parse_graphic_control_extension(gce_data):
        """
        Парсинг расширения управления графикой.
        :param gce_data: Данные расширения управления графикой в байтовом формате.
        :return: Расширение управления графикой.
        """
        packed = gce_data[0]
        disposal_method = (packed & 0x1C) >> 2
        user_input_flag = (packed & 0x02) >> 1
        transparency_flag = (packed & 0x01)
        delay_time = gce_data[1] + 256 * gce_data[2]
        transparent_color_index = gce_data[3]
        return GifGraphicControlExtension(disposal_method, user_input_flag, transparency_flag,
                                          delay_time, transparent_color_index)

    @staticmethod
    def parse_plain_text_extension(pte_data, text_data):
        """
        Парсинг расширения простого текста.
        :param pte_data: Данные расширения простого текста в байтовом формате.
        :param text_data: Данные о тексте в байтовом формате.
        :return: Расширение простого текста.
        """
        left = pte_data[0] + (pte_data[1] << 8)
        top = pte_data[2] + (pte_data[3] << 8)
        width = pte_data[4] + (pte_data[5] << 8)
        height = pte_data[6] + (pte_data[7] << 8)
        cell_width = pte_data[8]
        cell_height = pte_data[9]
        fg_color_index = pte_data[10]
        bg_color_index = pte_data[11]
        text_str = text_data.decode('ascii', errors='replace')
        return GifPlainTextExtension(left, top, width, height, cell_width, cell_height,
                                      fg_color_index, bg_color_index, text_str)

    @staticmethod
    def parse_application_extension(app_data, app_sub_blocks):
        """
        Парсинг расширения приложения.
        :param app_data: Идентификатор и код авторизации расширения приложения в байтовом формате.
        :param app_sub_blocks: Данные расширения приложения в байтовом формате.
        :return: Расширение приложения.
        """
        app_identifier = app_data[:8].decode('ascii', errors='replace').strip()
        app_auth_code = app_data[8:].decode('ascii', errors='replace')
        return GifApplicationExtension(app_identifier, app_auth_code, app_sub_blocks)

    @staticmethod
    def parse_comment_extension(comment_data):
        """
        Парсинг расширения комментария.
        :param comment_data: Данные расширения комментария в байтовом формате.
        :return: Расширение комментария.
        """
        comment_str = comment_data.decode('ascii', errors='replace')
        return GifCommentExtension(comment_str)

    @staticmethod
    def skip_sub_blocks(f):
        while True:
            block_size_data = f.read(1)
            if not block_size_data:
                break
            size = block_size_data[0]
            if size == 0:
                break
            f.read(size)

    @staticmethod
    def read_sub_blocks(f):
        """
        Чтение блока данных.
        :param f: Открытый GIF файл.
        :return: Блок данных о составляющей GIF файла.
        """
        result = bytearray()
        while True:
            block_size_data = f.read(1)
            if not block_size_data:
                break
            size = block_size_data[0]
            if size == 0:
                break
            chunk = f.read(size)
            result.extend(chunk)
        return bytes(result)
