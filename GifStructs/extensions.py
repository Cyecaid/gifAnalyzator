class GifApplicationExtension:
    def __init__(self, application_id, authentication_code, data):
        self.application_id = application_id
        self.authentication_code = authentication_code
        self.data = data

    def __str__(self):
        return (f"Расширение программы:\n"
                f"  ID приложения: {self.application_id}\n"
                f"  Код аутентификации: {self.authentication_code}\n"
                f"  Данные: {self.data}")


class GifCommentExtension:
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return (f"Расширение комментария:\n"
                f"  Комментарий: {self.comment}")



class GifGraphicControlExtension:
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
        return (f"Расширение управления графикой:\n"
                f"  Метод обработки: {self.disposal_method} ({disp_methods.get(self.disposal_method, 'Не определён')})\n"
                f"  Флаг ввода пользователя: {self.user_input_flag}\n"
                f"  Флаг цвета прозрачности: {self.transparency_flag}\n"
                f"  Время задержки в анимации: {self.delay_time * 10} мс\n"
                f"  Индекс цвета прозрачности: {self.transparent_color_index}")


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
        return (f"Расширение текста:\n"
                f"  Левый верхний угол экрана: ({self.left_pos}, {self.top_pos})\n"
                f"  Ширина: {self.width} px\n"
                f"  Высота: {self.height} px\n"
                f"  Ширина ячейки: {self.cell_width}\n"
                f"  Высота ячейки: {self.cell_height}\n"
                f"  Индекс цвета переднего плана: {self.foreground_color_index}\n"
                f"  Индекс цвета заднего плана: {self.background_color_index}\n"
                f"  Текст: {self.text_data}")