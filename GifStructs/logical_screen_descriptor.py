class GifLogicalScreenDescriptor:
    def __init__(self, width, height, packed, bg_color_index, pixel_aspect_ratio):
        self.width = width
        self.height = height
        self.packed = packed
        self.bg_color_index = bg_color_index
        self.pixel_aspect_ratio = pixel_aspect_ratio

    @property
    def global_color_table_flag(self):
        return (self.packed & 0x80) >> 7

    @property
    def sort_flag(self):
        return (self.packed & 0x08) >> 3

    @property
    def global_color_table_size(self):
        n = self.packed & 0x07
        return 2 ** (n + 1)

    def __str__(self):
        return (f"Логический дескриптор экрана:\n"
                f"  Ширина: {self.width} px\n"
                f"  Высота: {self.height} px\n"
                f"  Флаг использования глобальной таблицы цветов: {self.global_color_table_flag}\n"
                f"  Флаг сортировки: {self.sort_flag}\n"
                f"  Размер общей таблицы цветов: {self.global_color_table_size}\n"
                f"  Индекс цвета фона: {self.bg_color_index}\n"
                f"  Соотношение сторон: {self.pixel_aspect_ratio}")
