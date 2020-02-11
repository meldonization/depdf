from depdf.base import Base, Container
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Cell(Base):

    def __init__(self, top_left_x, top_left_y, width, height, text, font_size, inner_object):
        self.x0 = top_left_x
        self.top = top_left_y
        self.width = width
        self.height = height
        self.text = text
        self.fs = font_size
        self.inner_object = inner_object


class Table(Container):

    @check_config
    def __init__(self, rows, pid=1, tid=1, config=None):
        self.pid = pid
        self.tid = tid
        self.rows = rows
        self.config = config

    @property
    def to_dict(self):
        return {}

    @property
    def to_html(self):
        table_class = getattr(self.config, 'table_class')
        table_cell_merge_tolerance = getattr(self.config, 'table_cell_merge_tolerance')
        skip_empty_table = getattr(self.config, 'skip_empty_table')
        table_html = convert_table_to_html(
            self.to_dict, pid=self.pid, tid=self.tid, tc_mt=table_cell_merge_tolerance,
            table_class=table_class, skip_et=skip_empty_table
        )
        return table_html


def extract_pdf_table_by_page(pdf, pid):
    pass


def gen_column_cell_sizes(t):
    raw_sizes = [[tc['width'] if tc else 0 for tc in tr] for tr in t]
    cell_num = max([len(tr) for tr in t])
    trans_sizes = list(map(list, zip(*raw_sizes)))
    cell_sizes = []
    for i in range(cell_num):
        ss = min([j for j in trans_sizes[i] if j])
        cell_sizes.append(ss)
        if i >= cell_num - 1:
            break
        tmp = [j - ss if j >= ss else j for j in trans_sizes[i]]
        trans_sizes[i + 1] = [ts if ts else tmp[ts_id] for ts_id, ts in enumerate(trans_sizes[i + 1])]
    return cell_num, cell_sizes


def convert_table_to_html(table_dict, pid=1, tid=1, tc_mt=5, table_class='pdf-table', skip_et=False):
    empty_table_html = ''
    none_text_table = True
    html_table_string = '<table id="page-{pid}-table-{tid}" class="{table_class} page-{pid}">'.format(
        pid=pid, tid=tid, table_class=table_class
    )
    for rows in table_dict:
        row_num = len(rows)
        row_heights = [min([tc['height'] for tc in tr if tc]) for tr in rows]
        try:
            column_num, column_widths = gen_column_cell_sizes(rows)
        except Exception as e:
            log.debug('convert_table_to_html: {}'.format(e))
            column_num = max([len(tr) for tr in rows])
            column_widths = [
                min([tc['width'] for tc in tr if tc])
                if not all(v is None for v in tr) else 0
                for tr in map(list, zip(*rows))
            ]
        for rid, tr in enumerate(rows):
            html_table_string += '<tr>'
            for cid, tc in enumerate(tr):
                if tc is None:
                    continue
                html_table_string += '<td'
                row_span = col_span = 1
                for i in range(rid + 1, row_num):
                    if abs(tc['height'] - sum(row_heights[rid:i])) > tc_mt:
                        row_span += 1
                    else:
                        break
                for i in range(cid + 1, column_num):
                    if abs(tc['width'] - sum(column_widths[cid:i])) > tc_mt:
                        col_span += 1
                    else:
                        break
                if row_span > 1:
                    html_table_string += ' rowspan="{}"'.format(row_span)
                if col_span > 1:
                    html_table_string += ' colspan="{}"'.format(col_span)
                html_table_string += ' style="font-size: {font_size}px;">{tc_text}</td>'.format(
                    font_size=tc['fs'], tc_text=tc['text']
                )
                none_text_table = False if tc['text'] else none_text_table
            html_table_string += '</tr>'
    html_table_string += '</table>'
    if skip_et and none_text_table:
        return empty_table_html
    return html_table_string
