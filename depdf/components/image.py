from depdf.base import Base, Box
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Image(Base, Box):
    object_type = 'image'

    @check_config
    def __init__(self, bbox=None, src='', pid=1, img_idx=1, scan=False, config=None):
        self.bbox = bbox
        self.scan = scan
        width = bbox[2] - bbox[0]
        img_id = 'page-{pid}-image-{img_idx}'.format(pid=pid, img_idx=img_idx)
        img_class = '{img_class} page-{pid}'.format(img_class=getattr(config, 'image_class'), pid=pid)
        html = '<img id="{img_id}" class="{img_class}" src="{src}" width="{width}">'.format(
            img_id=img_id, img_class=img_class, src=src, width=width
        )
        html += '</img>'
        self.html = html
