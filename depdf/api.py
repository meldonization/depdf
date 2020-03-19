from functools import wraps

from pdfplumber.pdf import PDF

from depdf.error import PDFTypeError
from depdf.log import logger_init
from depdf.pdf import DePDF
from depdf.page import DePage

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
            pdf = DePDF.load(pdf_file_path, config=config, **kwargs)
        else:
            raise PDFTypeError
        res = api_func(pdf, pid) if pid > 0 else api_func(pdf)
        pdf.close()
        return res
    return wrapper


@api_load_pdf
def convert_pdf_to_html(pdf, **kwargs):
    """
    :param pdf: pdf file path
    :param kwargs: config keyword arguments
    :return: pdf html string
    """
    return pdf.html


@api_load_pdf
def convert_page_to_html(pdf, pid, **kwargs):
    """
    :param pdf: pdf file path
    :param pid: page number start from 1
    :param kwargs: config keyword arguments
    :return: page html string
    """
    page = DePage(pdf.pdf.pages[pid - 1], pid=pid, same=pdf.same, logo=pdf.logo, config=pdf.config)
    return page.html


@api_load_pdf
def extract_page_tables(pdf, pid, **kwargs):
    """
    :param pdf: pdf file path
    :param pid: page number start from 1
    :param kwargs: config keyword arguments
    :return: page tables list
    """
    page = DePage(pdf.pdf.pages[pid - 1],  pid=pid, same=pdf.same, logo=pdf.logo, config=pdf.config)
    return page.tables


@api_load_pdf
def extract_page_paragraphs(pdf, pid, **kwargs):
    """
    :param pdf: pdf file path
    :param pid: page number start from 1
    :param kwargs: config keyword arguments
    :return: page paragraphs list
    """
    page = DePage(pdf.pdf.pages[pid - 1], pid=pid, same=pdf.same, logo=pdf.logo, config=pdf.config)
    return page.paragraphs
