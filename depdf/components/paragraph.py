from depdf.base import Base, Box
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Paragraph(Base, Box):
    object_type = 'paragraph'

    @check_config
    def __init__(self, bbox=None, text='', pid=1, para_idx=1, config=None, inner_object=None):
        self.bbox = bbox
        para_id = 'page-{pid}-paragraph-{para_id}'.format(pid=pid, para_id=para_idx)
        para_class = '{para_class} page-{pid}'.format(para_class=getattr(config, 'paragraph_class'), pid=pid)
        html = '<p id="{para_id}" class="{para_class}">'.format(
            para_id=para_id, para_class=para_class
        )
        if text:
            self.text = text
            html += str(text)
        else:
            self._inner_object = [inner_object]
            for obj in inner_object:
                self.html += getattr(obj, 'html', '')
        html += '</p>'
        self.html = html

    @property
    def inner_object(self):
        return [obj.to_dict if hasattr(obj, 'to_dict') else obj for obj in self._inner_object]
