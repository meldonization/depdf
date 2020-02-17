from bs4 import BeautifulSoup

from depdf.log import logger_init
from depdf.settings import DEFAULT_HTML_PARSER

log = logger_init(__name__)


def convert_html_to_soup(html):
    return BeautifulSoup(str(html), DEFAULT_HTML_PARSER)


def convert_soup_to_html(soup):
    return str(soup)


def calc_overlap(a, b):
    """检查两个线段的重叠部分长度
    :param a: [a_lower, a_upper]
    :param b: [b_lower, b_upper]
    :return: overlapping length
    """
    if a[0] >= b[0] and a[1] <= b[1]:
        overlap_length = a[1] - a[0]
    elif a[0] <= b[0] and a[1] >= b[1]:
        overlap_length = b[1] - b[0]
    elif b[0] <= a[0] <= b[1]:
        overlap_length = b[1] - a[0]
    elif b[0] <= a[1] <= b[1]:
        overlap_length = a[1] - b[0]
    else:
        overlap_length = 0
    return abs(overlap_length)
