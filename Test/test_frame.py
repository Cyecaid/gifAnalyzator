import pytest
from gif_frame import Frame, ApplicationExtension, CommentExtension, GraphicControlExtension, PlainTextExtension


class TestFrame:
    @pytest.fixture
    def frame(self):
        return Frame(
            local_color_table=None,
            graphic_control_ext=None,
            plain_text_ext=None,
            application_ext=None,
            comment_ext=None,
            image_data=None,
            left=10,
            top=20,
            width=100,
            height=200,
            packed=0b11100101
        )

    def test_local_color_table_flag(self, frame):
        assert frame.local_color_table_flag == 1

    def test_interlace_flag(self, frame):
        assert frame.interlace_flag == 1

    def test_sort_flag(self, frame):
        assert frame.sort_flag == 1

    def test_local_color_table_size(self, frame):
        assert frame.local_color_table_size == 64

    def test_str_representation(self, frame):
        expected_output = (
            "  —  Позиция изображения: (10, 20)\n"
            "  —  Разрешение: 100x200\n"
            "  —  Использование чересстрочной развертки: True\n"
            "  —  Локальная таблица цветов - Есть\n"
            "  —  Количество цветов в локальной таблице: 64\n"
            "  —  Использование сортировки локальной таблицы цветов: True\n"
        )
        assert str(frame) == expected_output


class TestApplicationExtension:
    @pytest.fixture
    def app_ext(self):
        return ApplicationExtension(
            application_id="NETSCAPE",
            authentication_code="2.0",
            data="looping"
        )

    def test_str_representation(self, app_ext):
        expected_output = (
            "** Расширение программы:\n"
            "  —  ID приложения: NETSCAPE\n"
            "  —  Код аутентификации: 2.0\n"
            "  —  Данные: looping"
        )
        assert str(app_ext) == expected_output


class TestCommentExtension:
    @pytest.fixture
    def comment_ext(self):
        return CommentExtension(comment="This is a comment")

    def test_str_representation(self, comment_ext):
        expected_output = (
            "** Расширение комментария:\n"
            "  —  Комментарий: This is a comment"
        )
        assert str(comment_ext) == expected_output


class TestGraphicControlExtension:
    @pytest.fixture
    def graphic_ext(self):
        return GraphicControlExtension(
            disposal_method=2,
            user_input_flag=0,
            transparency_flag=1,
            delay_time=5,
            transparent_color_index=255
        )

    def test_str_representation(self, graphic_ext):
        expected_output = (
            "** Расширение управления графикой:\n"
            "  —  Метод обработки: 2 (Затирание картинки фоном)\n"
            "  —  Использование ввода пользователя: False\n"
            "  —  Использование цвета прозрачности: True\n"
            "  —  Время задержки: 50 мс\n"
            "  —  Цвет прозрачности (индекс): 255"
        )
        assert str(graphic_ext) == expected_output


class TestPlainTextExtension:
    @pytest.fixture
    def plain_text_ext(self):
        return PlainTextExtension(
            left_pos=5,
            top_pos=10,
            height=20,
            width=30,
            cell_width=4,
            cell_height=6,
            foreground_color_index=1,
            background_color_index=0,
            text_data="Sample text"
        )

    def test_str_representation(self, plain_text_ext):
        expected_output = (
            "** Расширение текста:\n"
            "  —  Позиция изображения: (5, 10)\n"
            "  —  Разрешение: 30x20\n"
            "  —  Размер ячейки: 4x6\n"
            "  —  Цвет переднего плана (индекс): 1\n"
            "  —  Цвета заднего плана (индекс): 0\n"
            "  —  Текст: Sample text"
        )
        assert str(plain_text_ext) == expected_output
