class Frame:
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
        result = (f"  —  Позиция изображения: ({self.left}, {self.top})\n"
                  f"  —  Разрешение: {self.width}x{self.height}\n"
                  f"  —  Использование чересстрочной развертки: {bool(self.interlace_flag)}\n")
        if self.local_color_table_flag:
            result += f"  —  Локальная таблица цветов - Есть\n"
        else:
            result += f"  —  Локальная таблица цветов - Отсутствует'\n"
        if self.local_color_table_flag:
            result += (f"  —  Количество цветов в локальной таблице: {self.local_color_table_size}\n"
                       f"  —  Использование сортировки локальной таблицы цветов: {bool(self.sort_flag)}\n")
        return result


class ApplicationExtension:
    def __init__(self, application_id, authentication_code, data):
        self.application_id = application_id
        self.authentication_code = authentication_code
        self.data = data

    def __str__(self):
        return (f"** Расширение программы:\n"
                f"  —  ID приложения: {self.application_id}\n"
                f"  —  Код аутентификации: {self.authentication_code}\n"
                f"  —  Данные: {self.data}")


class CommentExtension:
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return (f"** Расширение комментария:\n"
                f"  —  Комментарий: {self.comment}")


class GraphicControlExtension:
    def __init__(self, disposal_method, user_input_flag, transparency_flag, delay_time, transparent_color_index):
        self.disposal_method = disposal_method
        self.user_input_flag = user_input_flag
        self.transparency_flag = transparency_flag
        self.delay_time = delay_time
        self.transparent_color_index = transparent_color_index

    def __str__(self):
        disp_methods = {
            0: "Без применения обработки",
            1: "Картинка без изменений",
            2: "Затирание картинки фоном",
            3: "Восстановление изображения под картинкой"
        }
        return (f"** Расширение управления графикой:\n"
                f"  —  Метод обработки: {self.disposal_method} ({disp_methods.get(self.disposal_method, 'Не определён')})\n"
                f"  —  Использование ввода пользователя: {bool(self.user_input_flag)}\n"
                f"  —  Использование цвета прозрачности: {bool(self.transparency_flag)}\n"
                f"  —  Время задержки: {self.delay_time * 10} мс\n"
                f"  —  Цвет прозрачности (индекс): {self.transparent_color_index}")


class PlainTextExtension:
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
        return (f"** Расширение текста:\n"
                f"  —  Позиция изображения: ({self.left_pos}, {self.top_pos})\n"
                f"  —  Разрешение: {self.width}x{self.height}\n"
                f"  —  Размер ячейки: {self.cell_width}x{self.cell_height}\n"
                f"  —  Цвет переднего плана (индекс): {self.foreground_color_index}\n"
                f"  —  Цвета заднего плана (индекс): {self.background_color_index}\n"
                f"  —  Текст: {self.text_data}")