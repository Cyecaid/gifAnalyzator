import logging
import os
import struct

from GifStructs.extensions import (GifApplicationExtension, GifCommentExtension, GifGraphicControlExtension,
                                   GifPlainTextExtension)
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
        if len(header_data) != 6:
            logging.error("Invalid header size")
            return None

        signature, version = struct.unpack("3s3s", header_data)
        signature = signature.decode('ascii', errors='replace')
        version = version.decode('ascii', errors='replace')

        if signature != 'GIF':
            logging.error("Invalid file format")
            return None

        return GifHeader(signature, version)

    @staticmethod
    def parse_logical_screen_descriptor(log_desc_data):
        if len(log_desc_data) != 7:
            logging.error("Invalid logical screen descriptor size")
            return None

        width, height, packed, bg_color_index, aspect = struct.unpack("<HHBBB", log_desc_data)
        return GifLogicalScreenDescriptor(width, height, packed, bg_color_index, aspect)

    @staticmethod
    def parse_global_color_table(logical_screen_descriptor, data):
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
        img_desc_data = f.read(9)
        if len(img_desc_data) != 9:
            logging.error("Invalid image descriptor size")
            return None

        left, top, width, height, packed = struct.unpack("<HHHHB", img_desc_data)
        return GifImageDescriptor(left, top, width, height, packed)

    @staticmethod
    def parse_local_color_table(f, image_descriptor):
        local_ct = None
        if image_descriptor.local_color_table_flag:
            size = image_descriptor.local_color_table_size
            data = f.read(size * 3)
            local_ct_colors = [(data[i], data[i + 1], data[i + 2]) for i in range(0, len(data), 3)]
            local_ct = GifLocalColorTable(local_ct_colors)
        return local_ct

    @staticmethod
    def parse_indices(f):
        lzw_min_code_size = f.read(1)[0]
        img_data_blocks = GifParser.read_sub_blocks(f)
        decompressor = LZWDecompressor(lzw_min_code_size, img_data_blocks)
        return decompressor.decode()

    @staticmethod
    def parse_graphic_control_extension(gce_data):
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
        if len(pte_data) != 12:
            logging.error("Invalid plain text extension size")
            return None

        left, top, width, height, cell_width, cell_height, fg_color_index, bg_color_index = struct.unpack("<HHHHBBBB",
                                                                                                          pte_data)
        text_str = text_data.decode('ascii', errors='replace')
        return GifPlainTextExtension(left, top, width, height, cell_width, cell_height,
                                     fg_color_index, bg_color_index, text_str)

    @staticmethod
    def parse_application_extension(app_data, app_sub_blocks):
        app_identifier = app_data[:8].decode('ascii', errors='replace').strip()
        app_auth_code = app_data[8:].decode('ascii', errors='replace')
        return GifApplicationExtension(app_identifier, app_auth_code, app_sub_blocks)

    @staticmethod
    def parse_comment_extension(comment_data):
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
