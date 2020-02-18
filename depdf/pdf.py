import pdfplumber

from depdf.base import Base
from depdf.error import PDFTypeError
from depdf.config import check_config_type, check_config
from depdf.log import logger_init
from depdf.page import DePage
from depdf.pdf_tools import pdf_head_tail, pdf_logo

log = logger_init(__name__)


class DePDF(Base):
    _cached_properties = Base._cached_properties + ['_same', '_logo', '_pages', '_html_pages']

    @check_config
    def __init__(self, pdf, config=None, **kwargs):
        """
        :param pdf: pdfplumber.pdf.PDF class
        :param config: depdf.config.Config class
        """
        check_config_type(config)
        config.update(**kwargs)
        self._config = config
        check_pdf_type(pdf)
        self._pdf = pdf

    @classmethod
    @check_config
    def open(cls, file_name, config=None, **kwargs):
        plumber_pdf = pdfplumber.open(file_name, **kwargs)
        return cls(plumber_pdf, config=config, **kwargs)

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        check_config_type(value)
        self.refresh()
        self._config = value

    @property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, value):
        check_pdf_type(value)
        self.refresh()
        self._pdf = value

    @property
    def page_num(self):
        return len(self.pdf.pages)

    @property
    def same(self):
        same_flag = getattr(self.config, 'header_footer_flag')
        same = self._get_cached_property('_same', pdf_head_tail, self.pdf, config=self.config) if same_flag else []
        return same

    @property
    def logo(self):
        logo_flag = getattr(self.config, 'logo_flag')
        logo = self._get_cached_property('_logo', pdf_logo, self.pdf) if logo_flag else []
        return logo

    @property
    def pages(self):
        return self._get_cached_property('_pages', self.generate_pages)

    def generate_pages(self):
        pages = [
            DePage(page, pid=pid + 1, same=self.same, logo=self.logo)
            for page, pid in enumerate(self.pdf.pages)
        ]
        return pages

    @property
    def html_pages(self):
        return self._get_cached_property('_html_pages', self.extract_html_pages)

    def extract_html_pages(self):
        html_pages = [page.to_html for page in self.pages]
        return html_pages

    @property
    def to_html(self):
        pdf_class = getattr(self.config, 'pdf_class')
        html = '<div class="{pdf_class}">'.format(pdf_class=pdf_class)
        for pid, html_page in enumerate(self.html_pages):
            html += '<!--page-{pid}-->{html_page}'.format(pid=pid + 1, html_page=html_page)
        html += '</div>'
        self.html = html
        return html

    def __enter__(self):
        return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.close()

    def close(self):
        self.pdf.flush_cache()
        self.pdf.close()


def check_pdf_type(pdf):
    if not isinstance(pdf, pdfplumber.PDF):
        raise PDFTypeError(pdf)
