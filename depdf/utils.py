import logging

from bs4 import BeautifulSoup

log_format = '%(levelname)s:%(name)s:%(asctime)-15s %(message)s'
log_fmt = '%Y-%m-%dT%H:%M:%S'
logging.basicConfig(level=logging.WARNING, format=log_format, datefmt=log_fmt)


def logger_init(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    return logger


def convert_html_to_soup(html):
    return BeautifulSoup(str(html), 'html.parser')


def convert_soup_to_html(soup):
    return str(soup)


log = logger_init('depdf:utils')
