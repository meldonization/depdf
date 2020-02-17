from functools import wraps

from pdfplumber.pdf import PDF

from depdf.error import PDFTypeError
from depdf.log import logger_init
from depdf.pdf import DePDF

log = logger_init(__name__)


def api_load_pdf(api_func):
    @wraps(api_func)
    def wrapper(pdf_file_path, *args, **kwargs):
        pid = args[0] if args else -1
        pid = pid if isinstance(pid, int) else 1
        config = kwargs['config'] if 'config' in kwargs else None
        if isinstance(pdf_file_path, DePDF):
            pdf = pdf_file_path
        elif isinstance(pdf_file_path, PDF):
            pdf = DePDF(pdf_file_path, config=config, **kwargs)
        elif isinstance(pdf_file_path, str):
            pdf = DePDF.open(pdf_file_path, config=config, **kwargs)
        else:
            raise PDFTypeError
        res = api_func(pdf, pid) if pid > 0 else api_func(pdf)
        pdf.close()
        return res
    return wrapper


@api_load_pdf
def convert_pdf_to_html(pdf_file_path, **kwargs):
    """
    :param pdf_file_path: pdf file absolute path
    :param kwargs: config keyword arguments
    :return:
    """
    html = []
    return html


@api_load_pdf
def convert_pdf_to_html_by_page(pdf_file_path, pid, **kwargs):
    """
    :param pdf_file_path: pdf file absolute path
    :param pid: page number start from 1
    :param kwargs: config keyword arguments
    :return:
    """
    html_page = ''
    return html_page


@api_load_pdf
def extract_page_tables(pdf_file_path, pid, **kwargs):
    """
    :param pdf_file_path: pdf file absolute path
    :param pid: page number start from 1
    :param kwargs: config keyword arguments
    :return:
    """
    tables = []
    return tables


@api_load_pdf
def extract_page_paragraphs(pdf_file_path, pid, **kwargs):
    """
    :param pdf_file_path: pdf file absolute path
    :param pid: page number start from 1
    :param kwargs: config keyword arguments
    :return:
    """
    paragraphs = []
    return paragraphs
