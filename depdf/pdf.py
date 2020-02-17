import pdfplumber

from depdf.base import Base
from depdf.error import PDFTypeError, ConfigTypeError
from depdf.config import Config, check_config
from depdf.log import logger_init
from depdf.pdf_tools import pdf_head_tail, pdf_logo

log = logger_init(__name__)


class DePDF(Base):
    _cached_properties = Base._cached_properties + ['_same', '_logo', '_html_pages']

    @check_config
    def __init__(self, pdf, config=None, **kwargs):
        """
        :param pdf: pdfplumber.pdf.PDF class
        :param config: depdf.config.Config class
        """
        self.check_config_type(config)
        config.update(**kwargs)
        self._config = config
        self.check_pdf_type(pdf)
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
        self.check_config_type(value)
        self.refresh()
        self._config = value

    @property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, value):
        self.check_pdf_type(value)
        self.refresh()
        self._pdf = value

    @property
    def pages(self):
        return self.pdf.pages

    @property
    def page_num(self):
        return len(self.pages)

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

    @property
    def same(self):
        return self._get_cached_property('_same', pdf_head_tail, self.pdf, config=self.config)

    @property
    def logo(self):
        return self._get_cached_property('_logo', pdf_logo, self.pdf)

    @property
    def html_pages(self):
        return self._get_cached_property('_html_pages', self.extract_html_pages)

    def extract_html_pages(self):
        # todo
        html_pages = []
        return html_pages

    @property
    def to_html(self):
        # todo
        html = {}
        self.html = html
        return html

    def __enter__(self):
        return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.close()

    def close(self):
        self.pdf.flush_cache()
        self.pdf.close()

    def refresh(self):
        for p in self._cached_properties:
            if hasattr(self, p):
                delattr(self, p)

    @staticmethod
    def check_config_type(config):
        if not isinstance(config, Config):
            raise ConfigTypeError(config)

    @staticmethod
    def check_pdf_type(pdf):
        if not isinstance(pdf, pdfplumber.PDF):
            raise PDFTypeError(pdf)
