import pdfplumber

from .config import Config, DEFAULT_CONFIG
from . import logger_init

log = logger_init('depdf/pdf')


class DePDF(object):

    def __init__(self, file_name, config=DEFAULT_CONFIG, **kwargs):
        if not isinstance(config, Config):
            log.warning('wrong config type parsed')
            config = DEFAULT_CONFIG
        self.config = config
        self.pdf = pdfplumber.open(file_name, **kwargs)

