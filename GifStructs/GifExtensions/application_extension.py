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

    def __eq__(self, other):
        return (self.application_id == other.application_id and
                self.authentication_code == other.authentication_code and
                self.data == other.data)
