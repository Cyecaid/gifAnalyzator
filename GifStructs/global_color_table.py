class GifGlobalColorTable:
    def __init__(self, colors):
        self.colors = colors

    def __str__(self):
        return (f"Глобальная таблица цветов:\n"
                f"  Число цветов: {len(self.colors)}")