from depdf.base import Base, Box, InnerWrapper
from depdf.config import check_config
from depdf.log import logger_init
from depdf.utils import calc_bbox, repr_str

log = logger_init(__name__)


class Cell(InnerWrapper, Box):
    object_type = 'cell'

    def __init__(self, bbox=None, text='', inner_objects=None):
        self.bbox = bbox
        if text:
            self.text = text
            self.html = text
        else:
            self._inner_objects = inner_objects
            for obj in inner_objects:
                self.html += getattr(obj, 'html', '')

    def __repr__(self):
        if hasattr(self, 'text'):
            return '<depdf.TableCell: {}>'.format(repr_str(self.text))
        return '<depdf.TableCell[InnerObjects]: {}>'.format(str(tuple(self.bbox)))

    @property
    def to_dict(self):
        attrs = ['bbox', 'height', 'html', 'inner_objects', 'object_type', 'soup', 'width']
        return {k: getattr(self, k, None) for k in attrs}


class Table(Base, Box):
    object_type = 'table'

    @check_config
    def __init__(self, rows, pid='1', tid=1, config=None, bbox=None):
        self.pid = pid
        self.tid = tid
        self.rows = rows
        self.config = config
        self.bbox = bbox if bbox else calc_bbox(rows)

    def __repr__(self):
        return '<depdf.Table: ({}, {})>'.format(self.pid, self.tid)

    @property
    def to_dict(self):
        table_dict = [
            [
                cell.to_dict if hasattr(cell, 'to_dict') else cell
                for cell in row
            ]
            for row in self.rows
        ]
        return table_dict

    def save_html(self):
        table_file_name = '{}_page_{}_table_{}.html'.format(self.config.unique_prefix, self.pid, self.tid)
        return super().write_to(table_file_name)

    @property
    def html(self):
        if not self._html and hasattr(self, 'to_html'):
            return self.to_html
        return self._html

    @property
    def to_html(self):
        table_class = getattr(self.config, 'table_class')
        table_cell_merge_tolerance = getattr(self.config, 'table_cell_merge_tolerance')
        skip_empty_table = getattr(self.config, 'skip_empty_table')
        return convert_table_to_html(
            self.to_dict, pid=self.pid, tid=self.tid, tc_mt=table_cell_merge_tolerance,
            table_class=table_class, skip_et=skip_empty_table
        )


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


def convert_table_to_html(table_dict, pid='1', tid=1, tc_mt=5, table_class='pdf-table', skip_et=False):
    empty_table_html = ''
    none_text_table = True
    html_table_string = '<table id="page-{pid}-table-{tid}" class="{table_class} page-{pid}">'.format(
        pid=pid, tid=tid, table_class=table_class
    )
    row_num = len(table_dict)
    row_heights = [min([tc['height'] for tc in tr if tc]) for tr in table_dict]
    try:
        column_num, column_widths = gen_column_cell_sizes(table_dict)
    except Exception as e:
        log.debug('convert_table_to_html error: {}'.format(e))
        column_num = max([len(tr) for tr in table_dict])
        column_widths = [
            min([tc['width'] for tc in tr if tc])
            if not all(v is None for v in tr) else 0
            for tr in map(list, zip(*table_dict))
        ]
    for rid, tr in enumerate(table_dict):
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
            html_table_string += '>{tc_text}</td>'.format(tc_text=tc['html'])
            none_text_table = False if tc['html'] else none_text_table
        html_table_string += '</tr>'
    html_table_string += '</table>'
    if skip_et and none_text_table:
        return empty_table_html
    return html_table_string
