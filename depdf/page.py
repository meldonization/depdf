from pdfplumber.page import Page

from depdf.base import Base
from depdf.config import check_config, check_config_type
from depdf.error import PageTypeError
from depdf.log import logger_init
from depdf.components import *

log = logger_init(__name__)


class DePage(Base):
    _cached_properties = Base._cached_properties + ['_paragraphs', '_tables', '_objects']

    new_para_start_flag = True  # 该页面起始段落为新段落
    new_para_end_flag = True  # 该页面结尾段落为新段落

    @check_config
    def __init__(self, page, pid=1, same=None, logo=None, config=None):
        """
        :param page: pdfplumber page object
        :param pid: page number start from 1
        :param same: header & footer
        :param logo: watermark and logo
        :param config: depdf config
        """
        check_page_type(page)
        self._page = page
        self._pid = int(pid)
        check_config_type(config)
        self._config = config

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        check_config_type(value)
        self.refresh()
        self._config = value

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, value):
        self.refresh()
        self._pid = int(value)

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        check_page_type(value)
        self.refresh()
        self._page = value

    @property
    def width(self):
        return len(self.page.width)

    @property
    def height(self):
        return len(self.page.height)

    @property
    def paragraphs(self):
        paragraph_list = [i for i in self.objects if isinstance(i, Paragraph)]
        return paragraph_list

    @property
    def tables(self):
        table_list = [i for i in self.objects if isinstance(i, Table)]
        return table_list

    @property
    def objects(self):
        # todo
        object_list = []
        return object_list

    @property
    def to_html(self):
        # todo
        html = ''
        self.html = html
        return html


def check_page_type(page):
    if not isinstance(page, Page):
        raise PageTypeError(page)
