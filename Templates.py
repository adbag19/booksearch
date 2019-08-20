class BookTemplate:
    def __init__(self, isbn=None, title=None, author=None):
        self.isbn = isbn
        self.title = title
        self.author = author

    def isFavorite(self, isFavorite):
        self.favorite = isFavorite

    def jsonSerialize(self):
        return self.__dict__


def setAttributes(obj, dict):
    for key, value in dict.items():
        setattr(obj, key, value)

class AuthorTemplate:
    def jsonSerialize(self):
        return self.__dict__