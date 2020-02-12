from depdf.base import Base, Box
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Paragraph(Base, Box):

    @check_config
    def __init__(self, top_left_x, top_left_y, right_bottom_x, right_bottom_y, text, pid=1, para_id=1,
                 config=None):
        self.x0 = top_left_x
        self.top = top_left_y
        self.x1 = right_bottom_x
        self.bottom = right_bottom_y
        self.text = text
        para_class = getattr(config, 'paragraph_class')
        self.html = (
            '<p id="page-{pid}-paragraph-{para_id}" class="{para_class} page-{pid}">'
            '{para_text}</p>'
        ).format(
            pid=pid, para_id=para_id, para_class=para_class, para_text=text
        )


def extract_pdf_paragraph_by_page(page):
    pass
