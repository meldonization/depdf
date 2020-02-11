from depdf.utils import convert_html_to_soup


class Base(object):

    @property
    def to_dict(self):
        return {
            i: getattr(self, i, None)
            for i in dir(self)
            if not i.startswith('__')
        }


class Container(object):
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


