class GifFrame:
    def __init__(self, image_descriptor, local_color_table, graphic_control_ext, plain_text_ext,
                 application_ext, comment_ext, image_data):
        self.image_descriptor = image_descriptor
        self.local_color_table = local_color_table
        self.graphic_control_extension = graphic_control_ext
        self.plain_text_ext = plain_text_ext
        self.application_ext = application_ext
        self.comment_ext = comment_ext
        self.image_data = image_data

    def __str__(self):
        return (f"{self.image_descriptor}\n"
                f"{'Есть локальная таблица цветов' if self.local_color_table else 'Нет локальной таблицы цветов'}\n"
                f"{'Есть расширение управления графикой' if self.graphic_control_extension else 'Нет расширения управления графикой'}\n"
                f"{'Есть расширение простого текста' if self.plain_text_ext else 'Нет расширения простого текста'}\n"
                f"{'Есть расширение приложения' if self.application_ext else 'Нет расширения приложения'}\n"
                f"{'Есть расширение комментария' if self.comment_ext else 'Нет расширения комментария'}\n")

    def __eq__(self, other):
        return (self.image_descriptor == other.image_descriptor and
                self.local_color_table == other.local_color_table and
                self.graphic_control_extension == other.graphic_control_extension and
                self.plain_text_ext == other.plain_text_ext and
                self.application_ext == other.application_ext and
                self.comment_ext == other.comment_ext and
                self.image_data == other.image_data)
