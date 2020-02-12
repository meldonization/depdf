import pdfplumber

from depdf.base import Base
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class DePDF(Base):

    @check_config
    def __init__(self, file_name, config=None, **kwargs):
        self.config = config
        self.file_name = file_name
        self.pdf = pdfplumber.open(self.file_name, **kwargs)
        self._pages = self.pdf.pages

    @property
    def extract_pages(self):
        # todo
        page_list = []
        return page_list

    @property
    def to_html(self):
        # todo
        return {}

    def __enter__(self):
        return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.close()

    def close(self):
        self.pdf.flush_cache()
        self.pdf.close()
