from decimal import Decimal

from depdf.error import BoxValueError
from depdf.utils import convert_html_to_soup, repr_str


class Box(object):
    x0 = Decimal(0)
    x1 = Decimal(0)
    top = Decimal(0)
    bottom = Decimal(0)
    _bbox = (x0, top, x1, bottom)

    def __repr__(self):
        return '<depdf.Box: {}>'.format(tuple(self.bbox))

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def bbox(self):
        return self._bbox

    @bbox.setter
    def bbox(self, value):
        if value is not None:
            bbox = self.normalize_bbox(value)
            self.x0, self.top, self.x1, self.bottom = bbox
            self._bbox = bbox

    @staticmethod
    def normalize_bbox(bbox):
        if not (isinstance(bbox, list) or isinstance(bbox, tuple)):
            raise BoxValueError(bbox)
        if isinstance(bbox, str):
            raise BoxValueError(bbox)
        if len(bbox) != 4:
            raise BoxValueError(bbox)
        bbox = [Decimal(i) for i in bbox]
        return bbox


class Base(object):
    _cached_properties = ['_html']
    _html = ''

    def __repr__(self):
        return '<depdf.Base: {}>'.format(repr_str(self.soup.text))

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, html_value):
        self._html = html_value

    @property
    def soup(self):
        return convert_html_to_soup(self._html)

    def to_soup(self, parser):
        return convert_html_to_soup(self._html, parser=parser)

    def write_to(self, file_name):
        with open(file_name, "w") as file:
            file.write(self.html)

    @property
    def to_dict(self):
        return {
            i: getattr(self, i, None) for i in dir(self)
            if not i.startswith('_') and i not in ['to_dict', 'refresh', 'reset', 'write_to', 'to_soup']
        }

    def _get_cached_property(self, key, calculate_function, *args, **kwargs):
        """
        :param key: cached key string
        :param calculate_function: calculate value function from key
        :param args: calculate_function arguments
        :param kwargs: calculate_function keyword arguments
        :return: value of property key
        """
        cached_value = getattr(self, key, None)
        if cached_value is None:
            cached_value = calculate_function(*args, **kwargs)
            setattr(self, key, cached_value)
        return cached_value

    def refresh(self):
        for p in self._cached_properties:
            if hasattr(self, p):
                delattr(self, p)
        self.reset()

    def reset(self):
        pass


class InnerWrapper(Base):
    _inner_objects = []

    @property
    def inner_objects(self):
        return self._inner_objects

    @property
    def to_dict(self):
        return [obj.to_dict if hasattr(obj, 'to_dict') else obj for obj in self._inner_objects]
