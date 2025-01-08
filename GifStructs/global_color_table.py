class GifGlobalColorTable:
    def __init__(self, colors):
        self.colors = colors

    def __str__(self):
        return (f"Глобальная таблица цветов:\n"
                f"  Число цветов: {len(self.colors)}")

    def __eq__(self, other):
        for color1, color2 in zip(self.colors, other.colors):
            if color1 != color2:
                return False
        return True
