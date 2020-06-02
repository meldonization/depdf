from collections import Counter
from decimal import Decimal
import re

from depdf.config import PDF_IMAGE_KEYS
from depdf.log import logger_init
from depdf.utils import calc_overlap

log = logger_init(__name__)
PAGE_PORTRAIT = 'portrait'
PAGE_LANDSCAPE = 'landscape'
NUM_SYMBOLS = '0-9lxvi'  # 页码的可能数字
PAGE_NUM_RE = re.compile((
    r"^[-－]*[{0}]+(?:[-－]+[{0}]+)*[-－]*$|^[-－]+[{0}]+[-－]+$|"
    r"^[-－]*[{0}]+[-－]*$|^[{0}]+(?:-[{0}]+)*[-－]+[{0}]+$|"
    r'^第\s*[{0}]+\s*页$|^第\s*[一二三四五六七八九十百〇]+\s*页$'
).format(NUM_SYMBOLS), re.I)  # 1-1-1 or 11 or -1- or iv or 1-1-XVI

TOC_SYMBOLS = '.…·'  # add to toc symbol list if new separator is found
TOC_OCCURRENCE = '+'
TOC_LINE_RE = re.compile(r"^(.*?)[{}]{}[-－]*[0-9]+[-－]*$".format(TOC_SYMBOLS, TOC_OCCURRENCE))


def remove_duplicate_chars(chars, overlap_size=3):
    # 去除通过叠加字符来实现加粗的多余字符
    delete_index_list = []
    for char_index, char in enumerate(chars):
        for i in reversed(range(char_index)):
            tmp_char = chars[i]
            if abs(tmp_char['x0'] - char['x0']) < overlap_size and \
                    abs(tmp_char['y0'] - char['y0']) < overlap_size and \
                    abs(tmp_char['x1'] - char['x1']) < overlap_size and \
                    abs(tmp_char['y1'] - char['y1']) < overlap_size and \
                    tmp_char['text'] == char['text']:
                delete_index_list.append(char_index)
                break
    deleted_chars = []
    deleted_count = 0
    for each_delete_index in delete_index_list:
        deleted_chars.append(chars[each_delete_index - deleted_count])
        del chars[each_delete_index - deleted_count]
        deleted_count += 1
    return deleted_chars


def analyze_char_size(chars, char_size_upper=30, char_size_lower=3, default_char_size=12):
    char_sizes = []
    dcs = Decimal(default_char_size)
    for char in chars:
        cs_tmp = char['width'] / char['adv']
        if not (char_size_lower <= cs_tmp <= char_size_upper):
            cs_tmp = char['size']
        if not (char_size_lower <= cs_tmp <= char_size_upper):
            cs_tmp = dcs
        char_sizes.append(cs_tmp)
    ave_cs = max(set(char_sizes), key=char_sizes.count) if char_sizes else dcs
    min_cs = min(char_sizes) if char_sizes else dcs
    return ave_cs, min_cs


def analyze_page_orientation(plumber_page):
    """
    :param plumber_page: pdfplumber.page.Page class
    :return:
    """
    page_width = plumber_page.width
    page_height = plumber_page.height
    orientation = PAGE_LANDSCAPE if page_width >= page_height else PAGE_PORTRAIT
    return orientation


def analyze_page_num_word(phrases, page_height, page_width, top_fraction=Decimal('0.7'),
                          left_fraction=Decimal('0.4'), right_fraction=Decimal('0.6')):
    pagination_phrases = []
    if phrases and PAGE_NUM_RE.findall(phrases[-1]['text']):
        for phrase in reversed(phrases):
            if phrase['bottom'] >= page_height * top_fraction and \
                    phrase['x0'] >= page_width * left_fraction and \
                    phrase['x1'] <= page_width * right_fraction:
                pagination_phrases.append(phrase)
            else:
                break
    return pagination_phrases


def edges_to_lines(edges):
    h_lines, v_lines = [], []
    for i in edges:
        if i['orientation'] == 'h':
            if i not in h_lines:
                h_lines.append(i)
        else:
            if i not in v_lines:
                v_lines.append(i)
    return h_lines, v_lines


def remove_single_lines(lines, max_double=3, min_double=0.05, vertical_double=2, m='h'):
    new_lines = []
    key_1 = 'y0' if m == 'h' else 'x0'
    key_2 = 'x0' if m == 'h' else 'y0'
    key_3 = 'x1' if m == 'h' else 'y1'
    for i, li in enumerate(lines):
        if li not in new_lines:
            nearest_lines = list(filter(
                lambda x:
                    min_double < abs(li[key_1] - x[key_1]) <= max_double
                    and abs(li[key_2] - x[key_2]) <= vertical_double
                    and abs(li[key_3] - x[key_3]) <= vertical_double
                    and li != x, lines[:]
            ))
            if nearest_lines:
                new_lines.append(li)
                new_lines.extend(nearest_lines)
    return new_lines


def curve_to_lines(curves):
    h_curves, v_curves = [], []
    for i in curves:
        if 'x0' not in i or 'x1' not in i or 'top' not in i or 'bottom' not in i:
            continue
        h_curves.extend([
            {'orientation': 'h', 'x0': i['x0'], 'x1': i['x1'], 'top': i['top'], 'bottom': i['top']},
            {'orientation': 'h', 'x0': i['x0'], 'x1': i['x1'], 'top': i['bottom'], 'bottom': i['bottom']}
        ])
        v_curves.extend([
            {'orientation': 'v', 'x0': i['x0'], 'x1': i['x0'], 'top': i['top'], 'bottom': i['top']},
            {'orientation': 'v', 'x0': i['x1'], 'x1': i['x1'], 'top': i['bottom'], 'bottom': i['bottom']}
        ])
        if 'points' in i:
            for kk in i['points']:
                v_curves.append({'orientation': 'v', 'x0': kk[0], 'x1': kk[0], 'top': i['top'], 'bottom': i['bottom']})
                h_curves.append({'orientation': 'h', 'x0': i['x0'], 'x1': i['x1'], 'top': kk[1], 'bottom': kk[1]})
    return h_curves, v_curves


def add_vertical_lines(v_lines, h_lines, page_rects, page, ave_cs):
    page_width = page.width
    extra_vl = []
    if not page_rects:
        return extra_vl
    hls = [i['x0'] for i in h_lines if i['width'] > 3]  # horizontal lefts
    vls = [i['x0'] for i in v_lines if i['height'] > 3]  # vertical lefts
    hll = min(hls) if page_rects and hls else 0
    vll = min(vls) if page_rects and vls else 0
    if hll > vll:
        return extra_vl
    h_rects = [i for i in page_rects if i['height'] <= 5 and i['height'] < i['width']]
    v_rects = [i for i in page_rects if i['width'] <= 5 and i['height'] > i['width']]
    htr = [i['top'] for i in h_rects]
    htr.extend([i['bottom'] for i in h_rects])
    h_tops = sorted(set(htr))
    htl = len(h_tops)
    link_info = [False for i in range(len(h_tops))]  # is vertical line connects current horizontal line
    for idx, i in enumerate(h_tops):
        if idx == htl - 1:
            break
        if abs(i - h_tops[idx + 1]) <= 2 * ave_cs:
            link_info[idx] = True
            try:
                sliced_cell = page.crop([0, i, page_width, h_tops[idx + 1]])
                if sliced_cell.rect_edges + sliced_cell.lines:
                    continue
            except:
                continue
        for j in v_rects:
            overlap_length = calc_overlap([j['top'], j['bottom']], [i, h_tops[idx + 1]])
            if j['height'] > ave_cs and overlap_length > abs(h_tops[idx + 1] - i) / 3:
                link_info[idx] = True
                break
    link_trigger, l_top = False, h_tops[0] if h_tops else 0
    for idx, i in enumerate(h_tops):
        if link_info[idx]:
            link_trigger = True
        if not link_trigger:
            continue
        if link_info[idx]:
            if not link_info[idx - 1]:
                l_top = i
        elif link_info[idx - 1]:
            l_bottom = i
            h_left = min([j['x0'] for j in h_rects if j['top'] >= l_top and j['bottom'] <= l_bottom])
            h_right = max([j['x1'] for j in h_rects if j['top'] >= l_top and j['bottom'] <= l_bottom])
            extra_vl.extend([
                {'orientation': 'v', 'x0': h_left, 'x1': h_left, 'top': l_top, 'bottom': l_bottom},
                {'orientation': 'v', 'x0': h_right, 'x1': h_right, 'top': l_top, 'bottom': l_bottom},
            ])


def add_horizontal_lines(v_lines, h_lines, vlts_tolerance=0.1):
    extra_hl = []
    # 补表格顶部缺失的横线
    vlts = [i['top'] for i in v_lines if 'height' in i and i['height'] > 3]
    vltls = [i for i in v_lines if abs(i['top'] - min(vlts)) < vlts_tolerance] if vlts else []
    vhls = [i for i in h_lines if i['width'] > 3 and abs(i['top'] - min(vlts)) < vlts_tolerance] if vlts else []
    if vltls and vhls:
        vhlsl, vhlsr = min([i['x0'] for i in vhls]), max([i['x1'] for i in vhls])
        vltl, vltr = min([i['x0'] for i in vltls]), max([i['x1'] for i in vltls])
        if abs(vhlsl - vltl) > vlts_tolerance or abs(vhlsr - vltr) > vlts_tolerance:
            extra_hl.append({'orientation': 'h', 'x0': vltl, 'x1': vltr, 'top': min(vlts), 'bottom': min(vlts)})
    # 补表格底部缺失的横线
    vl_bs = [i["bottom"] for i in v_lines if "height" in i and i["height"] > 3]
    vl_bls = [i for i in v_lines if abs(i["bottom"] - max(vl_bs)) < vlts_tolerance] if vl_bs else []
    vhls = [
        i for i in h_lines
        if "width" in i and i["width"] > 3 and abs(i["bottom"] - max(vl_bs)) < vlts_tolerance
    ] if vl_bs else []
    if vl_bs and vhls:
        vhlsl, vhlsr = min([i['x0'] for i in vhls]), max([i['x1'] for i in vhls])
        vl_bl, vl_br = min([i['x0'] for i in vl_bls]), max([i['x1'] for i in vl_bls])
        if abs(vhlsl - vl_bl) > vlts_tolerance or abs(vhlsr - vl_br) > vlts_tolerance:
            extra_hl.append({'orientation': 'h', 'x0': vl_bl, 'x1': vl_br, 'top': max(vl_bs), 'bottom': max(vl_bs)})
    return extra_hl


def merge_page_figures(pdf_page, tables_raw=None, logo=None, min_width=3, min_height=3, pid='1'):
    logo_figures, figures_in_table = [], []
    fig_merge = pdf_page.figures
    figures_ori = pdf_page.images
    for idx, i in enumerate(figures_ori):
        if i is None:
            continue
        if 'srcsize' in i and (i['srcsize'][0] <= min_width or i['srcsize'][1] <= min_height):
            figures_ori[idx] = None
            continue
        # merge properties of the same figure & image
        replace_trigger = False
        if 'x0' not in i:
            img_tmp = {k: v for k, v in i.items() if k in ['height', 'width']}
            for j in fig_merge:
                if img_tmp.items() <= j.items():
                    figures_ori[idx].update(j)
                    replace_trigger = True
                    break
            if not replace_trigger:
                log.debug('merge_page_figures: figure ignored in page {0}'.format(pid))
                figures_ori[idx] = None
        # check if image within table region
        if tables_raw:
            for table in tables_raw:
                if figures_ori[idx]['top'] >= table.bbox[1] and \
                        figures_ori[idx]['bottom'] <= table.bbox[3]:
                    figures_in_table.append(figures_ori[idx])
        # check if the image is a logo
        if logo:
            img_tmp = {k: v for k, v in i.items() if k in PDF_IMAGE_KEYS}
            if img_tmp in logo:
                logo_figures.append(figures_ori[idx])
    figures_raw = sorted([
        i for i in figures_ori
        if i not in figures_in_table and i not in logo_figures and i is not None
    ], key=lambda x: x['top'])
    return figures_raw


def calculate_paragraph_border(depdf_page_object):
    tables_raw = depdf_page_object.tables_raw
    images_raw = depdf_page_object.images_raw
    ave_cs = depdf_page_object.ave_cs
    pagination_phrases = depdf_page_object.pagination_phrases
    phrases = depdf_page_object.phrases
    same = depdf_page_object.same
    page_width = depdf_page_object.width
    page_height = depdf_page_object.height
    same_tmp = depdf_page_object.same_tmp
    table_words = depdf_page_object._table_phrases
    image_words = depdf_page_object._image_phrases

    tts, tbs, lls, lrs = [], [], [], []
    tt = tb = ll = lr = None  # top-top, top-bottom, left-left, left-right
    for i in phrases:
        if (same and i in same_tmp) or i in image_words or i in pagination_phrases:
            continue
        inside = 0
        for idx, table in enumerate(tables_raw):
            if table.bbox[1] <= (i['top'] + i['bottom']) / 2 <= table.bbox[3]:
                inside = 1
                table_words.append(i)
        for img in images_raw:
            if 'bbox' in img and i['top'] >= img['bbox'][1] - ave_cs and i['bottom'] <= img['bbox'][3] + ave_cs:
                image_words.append(i)
                inside = 1
        if inside:
            continue
        tts.append(i['top'])
        tbs.append(i['bottom'])
        lls.append(i['x0'])
        lrs.append(i['x1'])
        tt = i['top'] if tt is None else tt
        tb = i['bottom'] if tb is None else tb
        ll = i['x0'] if ll is None else ll
        lr = i['x1'] if lr is None else lr
        tt = i['top'] if i['top'] < tt else tt
        tb = i['bottom'] if i['bottom'] > tb else tb
        ll = i['x0'] if i['x0'] < ll else ll
        lr = i['x1'] if i['x1'] > lr else lr
    tt = 0 if tt is None else tt
    tb = page_height if tb is None else tb
    ll = 0 if ll is None else ll
    lr = page_width if lr is None else lr
    ll_mc = Counter(sorted([int(i) for i in lls])).most_common(5)
    lr_mc = Counter(sorted([int(i) for i in lrs])).most_common(1)
    lls = [k[0] for k in ll_mc if k[1] >= 5] if ll_mc else []
    ll = Decimal(min(lls)) if lls else ll
    lr = Decimal(lr_mc[0][0]) if lr_mc else lr
    lr = page_width * 4 / 5 if lr <= page_width * 7 / 10 else lr
    return ll, tt, lr, tb


def format_text(text):
    return text.strip().replace('\xa0', '').replace('\n', '')
