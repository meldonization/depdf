"""
depdf
====================================
An ultimate pdf file disintegration tool.
DePDF is designed to extract tables and paragraphs
into structured markup language [eg. html] from embedding pdf pages.
You can also use it to convert page/pdf to html.
"""

from depdf.api import *
from depdf.config import Config
from depdf.pdf import DePDF
from depdf.page import DePage
from depdf.version import __version__

__all__ = [
    'Config',
    'DePDF',
    'DePage',
    'convert_pdf_to_html',
    'convert_page_to_html',
    'extract_page_tables',
    'extract_page_paragraphs',
]
