class GifImageDescriptor:
    def __init__(self, left, top, width, height, packed):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
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
        result = (f"Блок изображения:\n"
                  f"  Позиция изображения: ({self.left}, {self.top})\n"
                  f"  Разрешение: {self.width}x{self.height}\n"
                  f"  Использование локальной таблицы цветов: {self.local_color_table_flag}\n"
                  f"  Использование чересстрочной развертки: {self.interlace_flag}\n")
        if self.local_color_table_flag:
            result += (f"  Использование сортировки локальной таблицы цветов: {self.sort_flag}\n"
                       f"  Размер локальной таблицы цветов: {self.local_color_table_size}\n")
        return result

