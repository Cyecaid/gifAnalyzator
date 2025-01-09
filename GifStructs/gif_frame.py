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
                f"{'Есть локальная таблица цветов' if self.local_color_table else 'Нет локальной таблицы цветов'}\n")

