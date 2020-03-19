from bs4 import BeautifulSoup

from depdf.log import logger_init
from depdf.settings import DEFAULT_HTML_PARSER

log = logger_init(__name__)


def convert_html_to_soup(html, parser=DEFAULT_HTML_PARSER):
    return BeautifulSoup(str(html), parser)


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


def calc_bbox(objects):
    x0_list, top_list, x1_list, bottom_list = [], [], [], []
    for inner in objects:
        if isinstance(inner, list):
            for cell in inner:
                if cell and hasattr(cell, 'bbox'):
                    x0_list.append(cell.x0)
                    top_list.append(cell.top)
                    x1_list.append(cell.x1)
                    bottom_list.append(cell.bottom)
        else:
            if inner and hasattr(inner, 'bbox'):
                x0_list.append(inner.x0)
                top_list.append(inner.top)
                x1_list.append(inner.x1)
                bottom_list.append(inner.bottom)
    bbox = [
        min(x0_list) if x0_list else 0,
        min(top_list) if top_list else 0,
        max(x1_list) if x1_list else 0,
        max(bottom_list) if bottom_list else 0,
    ]
    return bbox


def construct_style(style=None):
    if not style or not isinstance(style, dict):
        return ''
    style_list = ['{}: {};'.format(k, v) for k, v in style.items()]
    style_string = ' style="{}"'.format(' '.join(style_list))
    return style_string


def repr_str(text, max_length=5):
    repr_text = text[:max_length] + ' ...' if len(text) > max_length else text
    return '"{}"'.format(repr_text)
