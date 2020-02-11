from depdf.base import Container
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Paragraph(Container):

    @check_config
    def __init__(self, para_text, pid=1, para_id=1, config=None):
        para_class = getattr(config, 'paragraph_class')
        self.text = para_text
        self.html = '<p id="page-{pid}-paragraph-{para_id}" class="{para_class} page-{pid}">{para_text}</p>'.format(
            pid=pid, para_id=para_id, para_class=para_class, para_text=para_text
        )


def extract_pdf_paragraph_by_page(pdf, pid):
    pass

