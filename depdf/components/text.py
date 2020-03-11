from depdf.base import Base, Box


class Text(Base, Box):
    object_type = 'text'

    def __init__(self, bbox='', text=''):
        self.bbox = bbox
        self.text = text
        self.html = text
