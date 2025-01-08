class GifLocalColorTable:
    def __init__(self, colors):
        self.colors = colors

    def __eq__(self, other):
        return self.colors == other.colors
