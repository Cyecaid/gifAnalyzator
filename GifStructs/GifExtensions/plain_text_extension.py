class GifPlainTextExtension:
    def __init__(self, left_pos, top_pos, height, width, cell_width, cell_height,
                 foreground_color_index, background_color_index, text_data):
        self.left_pos = left_pos
        self.top_pos = top_pos
        self.height = height
        self.width = width
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.foreground_color_index = foreground_color_index
        self.background_color_index = background_color_index
        self.text_data = text_data

    def __str__(self):
        return (f"Расширение простого текста:\n"
                f"  Левый верхний угол экрана: ({self.left_pos}, {self.top_pos})\n"
                f"  Ширина: {self.width} px\n"
                f"  Высота: {self.height} px\n"
                f"  Ширина ячейки: {self.cell_width}\n"
                f"  Высота ячейки: {self.cell_height}\n"
                f"  Индекс цвета переднего плана: {self.foreground_color_index}\n"
                f"  Индекс цвета заднего плана: {self.background_color_index}\n"
                f"  Текст: {self.text_data}")

    def __eq__(self, other):
        return (self.left_pos == other.left_pos and
                self.top_pos == other.top_pos and
                self.height == other.height and
                self.width == other.width and
                self.cell_width == other.cell_width and
                self.cell_height == other.cell_height and
                self.foreground_color_index == other.foreground_color_index and
                self.background_color_index == other.background_color_index and
                self.text_data == other.text_data)
