from decimal import Decimal

from depdf.utils import convert_html_to_soup


class Box(object):
    x0 = Decimal(0)
    x1 = Decimal(0)
    top = Decimal(0)
    bottom = Decimal(0)

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def bbox(self):
        bbox = (self.x0, self.top, self.x1, self.bottom)
        return bbox


class Base(object):
    _cached_properties = ['_html']
    _html = ''

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, html_value):
        self._html = html_value

    @property
    def soup(self):
        return convert_html_to_soup(self._html)

    @property
    def to_dict(self):
        return {
            i: getattr(self, i, None) for i in dir(self)
            if not i.startswith('_') and i != 'to_dict'
        }


