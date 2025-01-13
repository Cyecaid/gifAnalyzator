import logging
import os
import struct

from gif_frame import Frame, GraphicControlExtension, ApplicationExtension, CommentExtension, PlainTextExtension
from file_description import FileDescription
from lzw_decoder import LZWDecoder
from gif_custom_errors import GifFormatError


class GifParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.screen_descriptor = None
        self.global_color_table = None
        self.frames = []

    def parse(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл {self.file_path} не найден.")

        with open(self.file_path, 'rb') as file:
            header = file.read(6)
            screen_descriptor_data = file.read(7)
            try:
                self.screen_descriptor = self._parse_screen_descriptor(header, screen_descriptor_data)
            except GifFormatError as e:
                raise GifFormatError(f"Ошибка при разборе заголовков GIF файла: {str(e)}")

            color_table_data = file.read(self.screen_descriptor.global_color_table_size * 3)
            try:
                self.global_color_table = self._parse_global_color_table(self.screen_descriptor, color_table_data)
            except GifFormatError as e:
                raise GifFormatError(f"Ошибка при разборе глобальной таблицы цветов: {str(e)}")

            self._parse_blocks(file)

    def _parse_blocks(self, file):
        graphic_control_extension = plain_text_extension = application_extension = comment_extension = None
        while True:
            byte = file.read(1)
            if len(byte) == 0:
                break
            block_id = byte[0]
            if block_id == 0x3B:
                break
            elif block_id == 0x21:
                graphic_control_extension, plain_text_extension, application_extension, comment_extension = self._parse_extension(file)
            elif block_id == 0x2C:
                try:
                    left, top, width, height, packed = self._parse_image_descriptor(file)
                except GifFormatError as e:
                    raise GifFormatError(f"Ошибка при разборе дескриптора изображения: {str(e)}")

                local_color_table = self._parse_local_color_table(file, packed)
                pixel_indices = self._parse_pixel_indices(file)

                frame = Frame(
                    local_color_table, graphic_control_extension,
                    plain_text_extension, application_extension, comment_extension,
                    pixel_indices, left, top, width, height, packed
                )
                self.frames.append(frame)
                graphic_control_extension = plain_text_extension = application_extension = comment_extension = None
            else:
                self._skip_sub_blocks(file)

    @staticmethod
    def _parse_screen_descriptor(header, descriptor_data):
        if len(header) != 6:
            raise GifFormatError("Неверная длина заголовка.")

        if len(descriptor_data) != 7:
            raise GifFormatError("Неверная длина логического дескриптора экрана.")

        signature, version = struct.unpack("3s3s", header)
        signature = signature.decode('ascii', errors='replace')
        version = version.decode('ascii', errors='replace')

        if signature != 'GIF':
            raise GifFormatError("Файл не является GIF-форматом.")

        width, height, packed, bg_color_index, aspect_ratio = struct.unpack("<HHBBB", descriptor_data)
        return FileDescription(signature, version, width, height, packed, bg_color_index, aspect_ratio)

    @staticmethod
    def _parse_global_color_table(screen_descriptor, data):
        if screen_descriptor.global_color_table_flag:
            if len(data) != screen_descriptor.global_color_table_size * 3:
                raise GifFormatError("Некорректные данные глобальной таблицы цветов.")
            colors = [(data[i], data[i + 1], data[i + 2]) for i in range(0, len(data), 3)]
            return colors
        return None

    @staticmethod
    def _parse_extension(file):
        graphic_control_extension = plain_text_extension = application_extension = comment_extension = None

        extension_label = file.read(1)[0]
        if extension_label == 0xF9:
            file.read(1)
            extension_data = file.read(4)
            file.read(1)
            graphic_control_extension = GifParser._parse_graphic_control_extension(extension_data)
        elif extension_label == 0x01:
            file.read(1)
            text_extension_data = file.read(12)
            text_sub_blocks = GifParser._read_sub_blocks(file)
            plain_text_extension = GifParser._parse_plain_text_extension(text_extension_data, text_sub_blocks)
        elif extension_label == 0xFF:
            file.read(1)
            app_extension_data = file.read(11)
            app_sub_blocks = GifParser._read_sub_blocks(file)
            application_extension = GifParser._parse_application_extension(app_extension_data, app_sub_blocks)
        elif extension_label == 0xFE:
            comment_sub_blocks = GifParser._read_sub_blocks(file)
            comment_extension = GifParser._parse_comment_extension(comment_sub_blocks)
        else:
            GifParser._skip_sub_blocks(file)

        return graphic_control_extension, plain_text_extension, application_extension, comment_extension

    @staticmethod
    def _parse_image_descriptor(file):
        descriptor_data = file.read(9)
        if len(descriptor_data) != 9:
            raise GifFormatError("Неверная длина дескриптора изображения.")

        left, top, width, height, packed = struct.unpack("<HHHHB", descriptor_data)
        return left, top, width, height, packed

    @staticmethod
    def _parse_local_color_table(file, packed):
        local_color_table = None
        local_table_flag = (packed & 0x80) >> 7
        if local_table_flag:
            size_flag = packed & 0x07
            table_size = 2 ** (size_flag + 1)
            color_table_data = file.read(table_size * 3)
            if len(color_table_data) != table_size * 3:
                raise GifFormatError("Некорректная длина локальной таблицы цветов.")
            local_color_table = [(color_table_data[i], color_table_data[i + 1], color_table_data[i + 2]) for i in range(0, len(color_table_data), 3)]
        return local_color_table

    @staticmethod
    def _parse_pixel_indices(file):
        lzw_minimum_code_size = file.read(1)[0]
        image_data_blocks = GifParser._read_sub_blocks(file)
        decoder = LZWDecoder(lzw_minimum_code_size, image_data_blocks)
        return decoder.decode()

    @staticmethod
    def _parse_graphic_control_extension(data):
        if len(data) != 4:
            raise GifFormatError("Неверная длина расширения графики.")
        packed, delay_low, delay_high, transparent_color_index = struct.unpack('<BBBB', data)

        disposal_method = (packed & 0x1C) >> 2
        user_input_flag = (packed & 0x02) >> 1
        transparency_flag = (packed & 0x01)

        delay_time = delay_low + (delay_high << 8)

        return GraphicControlExtension(disposal_method, user_input_flag, transparency_flag, delay_time, transparent_color_index)

    @staticmethod
    def _parse_plain_text_extension(header_data, text_data):
        if len(header_data) != 12:
            raise GifFormatError("Неверная длина расширения простого текста.")

        left, top, width, height, cell_width, cell_height, fg_color_index, bg_color_index = struct.unpack("<HHHHBBBB", header_data)
        text_content = text_data.decode('ascii', errors='replace')
        return PlainTextExtension(left, top, width, height, cell_width, cell_height, fg_color_index, bg_color_index, text_content)

    @staticmethod
    def _parse_application_extension(header_data, sub_blocks):
        application_identifier = header_data[:8].decode('ascii', errors='replace').strip()
        authentication_code = header_data[8:].decode('ascii', errors='replace')
        return ApplicationExtension(application_identifier, authentication_code, sub_blocks)

    @staticmethod
    def _parse_comment_extension(comment_data):
        comment_content = comment_data.decode('ascii', errors='replace')
        return CommentExtension(comment_content)

    @staticmethod
    def _skip_sub_blocks(file):
        while True:
            block_size_data = file.read(1)
            if not block_size_data:
                break
            block_size = block_size_data[0]
            if block_size == 0:
                break
            file.read(block_size)

    @staticmethod
    def _read_sub_blocks(file):
        sub_blocks = bytearray()
        while True:
            block_size_data = file.read(1)
            if not block_size_data:
                break
            block_size = block_size_data[0]
            if block_size == 0:
                break
            sub_blocks.extend(file.read(block_size))
        return bytes(sub_blocks)
