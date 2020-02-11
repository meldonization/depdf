import pdfplumber

from depdf.base import Container
from depdf.config import Config, check_config
from depdf.log import logger_init

log = logger_init(__name__)


class DePDF(Container):

    @check_config
    def __init__(self, file_name, config=None, **kwargs):
        self.config = config
        self.pdf = pdfplumber.open(file_name, **kwargs)

    @property
    def pages(self):
        return self.pdf.pages

    @property
    def to_soup(self):
        return {}

    @property
    def to_html(self):
        return {}



