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

    def __eq__(self, other):
        return (self.disposal_method == other.disposal_method and
                self.user_input_flag == other.user_input_flag and
                self.transparency_flag == other.transparency_flag and
                self.delay_time == other.delay_time and
                self.transparent_color_index == other.transparent_color_index)
