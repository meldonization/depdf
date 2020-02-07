from .base import Base


class Cell(Base):

    def __init__(self, top_left_x, top_left_y, width, height, text, font_size):
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size


class Table(object):
    pass


def extract_page_table(pdf, pid):
    pass
