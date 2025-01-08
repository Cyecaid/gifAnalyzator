class GifCommentExtension:
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return (f"Расширение комментария:\n"
                f"  Комментарий: {self.comment}")

    def __eq__(self, other):
        return self.comment == other.comment
