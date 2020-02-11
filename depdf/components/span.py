from depdf.base import Container
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Span(Container):

    @check_config
    def __init__(self, span_text, pid=1, config=None):
        span_class = getattr(config, 'span_class')
        self.text = span_text
        self.html = '<span class="{span_class} page-{pid}">{span_text}</span>'.format(
            span_class=span_class, pid=pid, span_text=span_text
        )
