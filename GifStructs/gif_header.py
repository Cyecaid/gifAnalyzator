class GifHeader:
    def __init__(self, signature, version):
        self.signature = signature
        self.version = version

    def __str__(self):
        return f"Заголовок: {self.signature}{self.version}"

    def __eq__(self, other):
        return self.signature == other.signature and self.version == other.version
