from bs4 import BeautifulSoup

from .utils import *

log = logger_init('depdf:base')


class Base(object):

    @property
    def to_json(self):
        return {
            i: getattr(self, i, None)
            for i in dir(self)
            if not i.startswith('__')
        }


class Container(object):

    @property
    def to_soup(self):
        html = getattr(self, 'html', '')
        return self.soup

    @property
    def to_html(self):
        soup = getattr(self, 'soup', BeautifulSoup('', 'html.parser'))
        self.html = str(soup)
        return self.html
