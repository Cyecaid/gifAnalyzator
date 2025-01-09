import pytest
from file_description import FileDescription


class TestFileDescription:
    @pytest.fixture
    def file_description(self):
        return FileDescription(
            signature="GIF",
            version="89a",
            width=640,
            height=480,
            packed=0b10010111,
            bg_color_index=5,
            pixel_aspect_ratio=0
        )

    def test_global_color_table_flag(self, file_description):
        assert file_description.global_color_table_flag == 1

    def test_sort_flag(self, file_description):
        assert file_description.sort_flag == 0

    def test_global_color_table_size(self, file_description):
        assert file_description.global_color_table_size == 256

    def test_str_representation(self, file_description):
        expected_output = (
            "* Тип файла: GIF89a\n"
            "* Дескриптор экрана:\n"
            "  —  Разрешение: 640x480\n"
            "  —  Использования глобальной таблицы цветов: True\n"
            "  —  Использование сортировки: False\n"
            "  —  Количество цветов в общей таблице: 256\n"
            "  —  Цвета фона (индекс): 5\n"
            "  —  Соотношение сторон: 0"
        )
        assert str(file_description) == expected_output

    def test_default_aspect_ratio(self):
        fd = FileDescription(
            signature="GIF",
            version="89a",
            width=800,
            height=600,
            packed=0b10010110,
            bg_color_index=0,
            pixel_aspect_ratio=0
        )
        assert fd.pixel_aspect_ratio == 0
