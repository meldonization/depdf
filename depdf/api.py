from functools import wraps

from depdf.log import logger_init
from depdf.pdf import DePDF

log = logger_init(__name__)


def api_load_pdf(func):
    @wraps(func)
    def wrapper(pdf_file, config=None, **kwargs):
        pid = kwargs.get('pid')
        if pid:
            _ = kwargs.pop('pid')
        pdf = DePDF(pdf_file, config=config, **kwargs)
        if pid:
            return func(pdf, pid=pid)
        else:
            return func(pdf)
    return wrapper


@api_load_pdf
def convert_pdf_to_html(pdf_file, config=None):
    html = []
    return html


@api_load_pdf
def convert_pdf_to_html_by_page(pdf_file, config=None, pid=1):
    html_page = ''
    return html_page


@api_load_pdf
def extract_page_table(pdf_file, config=None, pid=1):
    table = []
    return table
