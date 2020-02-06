from .api import convert_pdf_to_html, convert_pdf_to_html_by_page
from .version import __version__
import logging

__all__ = [
    'convert_pdf_to_html',
    'convert_pdf_to_html_by_page'
]

log_format = '%(levelname)s:%(name)s:%(asctime)-15s %(message)s'
log_fmt = '%Y-%m-%dT%H:%M:%S'
logging.basicConfig(level=logging.INFO, format=log_format, datefmt=log_fmt)


def logger_init(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    return logger
