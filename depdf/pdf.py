import pdfplumber

from .config import Config
from .utils import logger_init

log = logger_init('depdf:pdf')


class DePDF(object):

    def __init__(self, file_name, config=Config(), **kwargs):
        if not isinstance(config, Config):
            log.warning('wrong config type parsed')
            config = Config()
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



