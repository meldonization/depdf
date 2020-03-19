from decimal import Decimal

from depdf.config import check_config, PDF_IMAGE_KEYS
from depdf.page_tools import analyze_page_orientation


def check_page_orientation(pdf, pid):
    """
    :param pdf: pdfplumber class
    :param pid: page number starts from 0
    :return:
    """
    return analyze_page_orientation(pdf.pages[pid])


@check_config
def pdf_head_tail(pdf, config=None):
    """
    :param pdf: plumber pdf object
    :param config: depdf config class
    :return: PDF 文件的页眉和页脚
    """
    offset = getattr(config, 'default_head_tail_page_offset_percent')
    same_diff_tolerance = Decimal('0.5')  # todo parameter
    page_1, page_2 = 0, 1  # 需要拿来对比页眉和页脚的页码  # todo parameter
    same = []
    page_num = len(pdf.pages)
    # Portrait pages
    port_pages = [i for i in range(page_num) if pdf.pages[i].width < pdf.pages[i].height and i != 0]
    pt_size = len(port_pages)
    # Landscape pages
    land_pages = [i for i in range(page_num) if pdf.pages[i].width >= pdf.pages[i].height]
    ld_size = len(land_pages)

    def check_same(p1, p2, orientation=None, pure_text=False, same_text=None):
        fpage = pdf.pages[p1].extract_words(x_tolerance=6, y_tolerance=6, keep_blank_chars=True)
        fpl = len(fpage)
        spage = pdf.pages[p2].extract_words(x_tolerance=6, y_tolerance=6, keep_blank_chars=True) if p2 else None
        spl = len(spage) if p2 else None

        def head_tail(s='head', pt=False, st=same_text):
            sps = fpl + 1 if spl is None else spl
            start = 0 if s == 'head' else 1
            end = min(fpl, sps) if s == 'head' else min(fpl, sps) + 1
            for i in range(start, end):
                k = i if s == 'head' else -i
                if abs(fpage[k]['top'] / pdf.pages[p1].height - Decimal('0.5')) <= Decimal('0.5') - Decimal(offset):
                    break
                fpc = fpage[k]['text'] if pt else fpage[k]
                if st:
                    if fpc in st:
                        fpage[k]['mode'] = check_page_orientation(pdf, p1)
                        fpage[k]['level'] = s
                        if fpage[k] not in same:
                            same.append(fpage[k])
                    else:
                        break
                else:
                    spc = spage[k]['text'] if pt else spage[k]
                    diff = abs(fpc['top'] - spc['top']) + abs(fpc['bottom'] - spc['bottom']) + \
                        abs(fpc['x1'] - spc['x1']) + abs(fpc['x0'] - spc['x0'])
                    if fpc['text'] == spc['text'] and diff <= same_diff_tolerance:  # 给一些冗余度
                        fpage[k]['mode'] = orientation
                        fpage[k]['level'] = s
                        if fpage[k] not in same:
                            same.append(fpage[k])
                    else:
                        break
            if s != 'tail':
                head_tail(s='tail', pt=pt, st=st)

        if pure_text:
            if p2:
                head_tail(s='head', pt=True)
            else:
                head_tail(s='head', pt=True, st=same_text)
        else:
            head_tail(s='head')

    if pt_size + ld_size <= 1:
        return same
    elif pt_size == ld_size == 1:
        check_same(port_pages[0], land_pages[0], pure_text=True)
    elif pt_size == 1:
        check_same(land_pages[page_1], land_pages[page_2], orientation='landscape')
        st_tmp = [i['text'] for i in same]
        if st_tmp:
            check_same(port_pages[0], None, pure_text=True, same_text=st_tmp)
    elif ld_size == 1:
        check_same(port_pages[page_1], port_pages[page_2], orientation='portrait')
        st_tmp = [i['text'] for i in same]
        if st_tmp:
            check_same(land_pages[0], None, pure_text=True, same_text=st_tmp)
    elif pt_size == 0:
        check_same(land_pages[page_1], land_pages[page_2], orientation='landscape')
    elif ld_size == 0:
        check_same(port_pages[page_1], port_pages[page_2], orientation='portrait')
    else:
        check_same(port_pages[page_1], port_pages[page_2], orientation='portrait')
        check_same(land_pages[page_1], land_pages[page_2], orientation='landscape')

    return same


def pdf_logo(pdf):
    page_1, page_2 = 0, 1  # 需要拿来对比水印的页码  # todo parameter
    logo = []
    page_num = len(pdf.pages)
    port_pages = [i for i in range(page_num) if pdf.pages[i].width < pdf.pages[i].height and i != 0]
    pt_size = len(port_pages)
    land_pages = [i for i in range(page_num) if pdf.pages[i].width >= pdf.pages[i].height]
    ld_size = len(land_pages)

    def compare_image(p1, p2, s='head'):
        fpage = pdf.pages[p1].images
        spage = pdf.pages[p2].images
        fpl = len(fpage)
        spl = len(spage)
        start = 0 if s == 'head' else 1
        end = min(fpl, spl) if s == 'head' else min(fpl, spl) + 1
        for i in range(start, end):
            k = i if s == 'head' else -i
            raw_fpc = fpage[k]
            raw_spc = spage[k]
            fpc = {bk: raw_fpc[bk] for bk in raw_fpc.keys() if bk in PDF_IMAGE_KEYS}
            spc = {bk: raw_spc[bk] for bk in raw_spc.keys() if bk in PDF_IMAGE_KEYS}
            if fpc == spc:
                if fpc not in logo:
                    logo.append(fpc)
            else:
                break
        if s != 'tail':
            compare_image(p1, p2, s='tail')

    if pt_size >= 2:
        compare_image(port_pages[page_1], port_pages[page_2])
    if ld_size >= 2:
        compare_image(land_pages[page_1], land_pages[page_2])

    return logo
