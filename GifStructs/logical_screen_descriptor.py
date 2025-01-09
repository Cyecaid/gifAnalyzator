class GifLogicalScreenDescriptor:
    def __init__(self, signature, version, width, height, packed, bg_color_index, pixel_aspect_ratio):
        self.signature = signature
        self.version = version
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
        return (f"Тип файла: {self.signature}{self.version}\n"
                f"Логический дескриптор экрана:\n"
                f"  Разрешение: {self.width}x{self.height}\n"
                f"  Использования глобальной таблицы цветов: {self.global_color_table_flag}\n"
                f"  Использование сортировки: {self.sort_flag}\n"
                f"  Размер общей таблицы цветов: {self.global_color_table_size}\n"
                f"  Индекс цвета фона: {self.bg_color_index}\n"
                f"  Соотношение сторон: {self.pixel_aspect_ratio}")
