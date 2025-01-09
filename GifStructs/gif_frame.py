class GifFrame:
    def __init__(self, local_color_table, graphic_control_ext, plain_text_ext,
                 application_ext, comment_ext, image_data, left, top, width, height, packed):
        self.local_color_table = local_color_table
        self.graphic_control_extension = graphic_control_ext
        self.plain_text_ext = plain_text_ext
        self.application_ext = application_ext
        self.comment_ext = comment_ext
        self.image_data = image_data

        self.width = width
        self.height = height
        self.top = top
        self.left = left
        self.packed = packed

    @property
    def local_color_table_flag(self):
        return (self.packed & 0x80) >> 7

    @property
    def interlace_flag(self):
        return (self.packed & 0x40) >> 6

    @property
    def sort_flag(self):
        return (self.packed & 0x20) >> 5

    @property
    def local_color_table_size(self):
        n = self.packed & 0x07
        return 2 ** (n + 1) if self.local_color_table_flag else 0

    def __str__(self):
        result = (f"Позиция изображения: ({self.left}, {self.top})\n"
                  f"Разрешение: {self.width}x{self.height}\n"
                  f"Использование чересстрочной развертки: {self.interlace_flag}\n")
        result += f"{'Есть локальная таблица цветов' if self.local_color_table else 'Нет локальной таблицы цветов'}\n"
        if self.local_color_table_flag:
            result += (f"Использование сортировки локальной таблицы цветов: {self.sort_flag}\n"
                       f"Размер локальной таблицы цветов: {self.local_color_table_size}\n")
        return result

