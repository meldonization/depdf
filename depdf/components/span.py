from depdf.base import Base, Box
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Span(Base, Box):
    object_type = 'span'

    @check_config
    def __init__(self, bbox=None, span_text='', pid=1, config=None):
        self.bbox = bbox
        self.text = span_text
        span_class = getattr(config, 'span_class')
        self.html = '<span class="{span_class} page-{pid}">{span_text}</span>'.format(
            span_class=span_class, pid=pid, span_text=span_text
        )
