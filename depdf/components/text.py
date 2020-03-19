from depdf.base import Base, Box
from depdf.utils import repr_str


class Text(Base, Box):
    object_type = 'text'

    def __init__(self, bbox='', text=''):
        self.bbox = bbox
        self.text = text
        self.html = text

    def __repr__(self):
        return '<depdf.Text: {}>'.format(repr_str(self.text))
