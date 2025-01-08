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
        return (f"Блок изображения:\n"
                f"  Левый верхний угол экрана: ({self.left}, {self.top})\n"
                f"  Ширина: {self.width} px\n"
                f"  Высота: {self.height} px\n"
                f"  Флаг использования локальной таблицы цветов: {self.local_color_table_flag}\n"
                f"  Флаг чересстрочной развертки: {self.interlace_flag}\n"
                f"  Флаг сортировки локальной таблицы цветов: {self.sort_flag}\n"
                f"  Размер локальной таблицы цветов: {self.local_color_table_size}")

    def __eq__(self, other):
        return (self.left == other.left and self.top == other.top and
                self.width == other.width and self.height == other.height and
                self.packed == other.packed)
