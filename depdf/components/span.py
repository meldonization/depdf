from depdf.base import Base
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Span(Base):

    @check_config
    def __init__(self, top_left_x, top_left_y, right_bottom_x, right_bottom_y, span_text, pid=1, config=None):
        self.x0 = top_left_x
        self.top = top_left_y
        self.x1 = right_bottom_x
        self.bottom = right_bottom_y
        self.text = span_text
        span_class = getattr(config, 'span_class')
        self.html = '<span class="{span_class} page-{pid}">{span_text}</span>'.format(
            span_class=span_class, pid=pid, span_text=span_text
        )
