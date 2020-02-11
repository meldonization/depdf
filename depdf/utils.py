from bs4 import BeautifulSoup

from depdf.log import logger_init
from depdf.settings import DEFAULT_HTML_PARSER

log = logger_init(__name__)


def convert_html_to_soup(html):
    return BeautifulSoup(str(html), DEFAULT_HTML_PARSER)


def convert_soup_to_html(soup):
    return str(soup)
