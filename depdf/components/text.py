from depdf.base import Base


class Text(Base):
    object_type = 'text'

    def __init__(self, text):
        self.text = text
        self.html = text
