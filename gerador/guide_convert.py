"""Convert the Aion 2 DOCX guides (our own layout) into sections of HTML.

convert(path, part_id, boxes=True, drop=(), strings=None)
    -> {'title', 'subtitle', 'sections': [{'id', 'title', 'meta', 'html'}]}

Every element that holds text gets data-t="N", N being the position of its inner HTML in `strings`; the page
uses that number to swap in the translation.

The DOCX files all use the same small vocabulary: Ttulo/Subttulo/Ttulo1/Ttulo3 paragraphs, a navy "banner"
table for section heads, colour-barred callout tables, data tables, bullet/number lists and checkbox
content controls. Anything else falls back to plain paragraphs.
"""
import html
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
W14 = '{http://schemas.microsoft.com/office/word/2010/wordml}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'

COLOR_CLASS = {'2E7D32': 'g', 'C62828': 'r', '8A6100': 'y', '1F3864': 'n', '6B7280': 'mute', '4B5563': 'mute'}
CELL_CLASS = {'E8F5E9': 'm', 'EAF1FB': 'h', 'F8D7D3': 's', 'DCE6F2': 'key', '1F3864': 'head'}
CALLOUT = {'2E75B6': 'info', 'D4A017': 'warn', '2E7D32': 'good', 'C62828': 'bad'}


def slug(text):
    text = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text[:60] or 'x'


class Doc:
    def __init__(self, path, part, boxes=True, drop=(), strings=None, swap=()):
        z = zipfile.ZipFile(path)
        self.part = part
        self.boxes = boxes  # False: leave out the tick-box columns of tables
        self.drop = drop    # sentences to leave out
        self.swap = swap    # (old, new) pieces of text to replace
        self.strings = strings if strings is not None else []
        self.body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
        self.links = {}
        for rel in ET.fromstring(z.read('word/_rels/document.xml.rels')):
            if rel.get('TargetMode') == 'External':
                self.links[rel.get('Id')] = rel.get('Target')
        self.numfmt = {}
        if 'word/numbering.xml' in z.namelist():
            num = ET.fromstring(z.read('word/numbering.xml'))
            abstract = {a.get(W + 'abstractNumId'): a.find(f'{W}lvl/{W}numFmt').get(W + 'val')
                        for a in num.findall(W + 'abstractNum')}
            for n in num.findall(W + 'num'):
                self.numfmt[n.get(W + 'numId')] = abstract.get(n.find(W + 'abstractNumId').get(W + 'val'), 'bullet')
        self.keys = {}
        self.section = 'intro'

    # ---------- inline ----------
    def leaf(self, body):
        """Register a piece of inline HTML; returns the attribute that marks its element."""
        self.strings.append(body)
        return f' data-t="{len(self.strings) - 1}"'

    def key(self, text):
        base = f'{self.part}|{slug(self.section)}|{slug(text)}'
        self.keys[base] = self.keys.get(base, 0) + 1
        return base if self.keys[base] == 1 else f'{base}#{self.keys[base]}'

    def run(self, r):
        out = ''
        for node in r:
            if node.tag == W + 't':
                out += html.escape(node.text or '')
            elif node.tag == W + 'tab':
                out += ' '
            elif node.tag == W + 'drawing':
                doc_pr = node.find(f'.//{WP}docPr')
                name = doc_pr.get('name', '') if doc_pr is not None else ''
                if name.startswith('Daevanion '):
                    out += f'<div class="board" data-board="{html.escape(name[10:])}"></div>'
        if not out.strip() or out.startswith('<div'):
            return out
        rpr = r.find(W + 'rPr')
        if rpr is None:
            return out
        color = rpr.find(W + 'color')
        cls = COLOR_CLASS.get(color.get(W + 'val', '').upper()) if color is not None else None
        bold = rpr.find(W + 'b') is not None and rpr.find(W + 'b').get(W + 'val') not in ('0', 'false')
        if rpr.find(W + 'i') is not None:
            out = f'<i>{out}</i>'
        if bold:
            out = f'<b>{out}</b>'
        if cls:
            out = f'<span class="{cls}">{out}</span>'
        return out

    def inline(self, p):
        """(html, checked) where checked is None when the paragraph has no checkbox."""
        out, checked = '', None
        for node in p:
            if node.tag == W + 'r':
                out += self.run(node)
            elif node.tag == W + 'hyperlink':
                inner = ''.join(self.run(r) for r in node.findall(W + 'r'))
                inner = re.sub(r'</?span[^>]*>', '', inner)
                out += f'<a href="{html.escape(self.links.get(node.get(R + "id"), "#"))}" target="_blank" rel="noopener">{inner}</a>'
            elif node.tag == W + 'sdt':
                box = node.find(f'{W}sdtPr/{W14}checkbox')
                if box is not None:
                    state = box.find(W14 + 'checked')
                    checked = state is not None and state.get(W14 + 'val') == '1'
        return re.sub(r'\s+', ' ', out).strip(), checked

    @staticmethod
    def text(node):
        return re.sub(r'\s+', ' ', ''.join(t.text or '' for t in node.iter(W + 't') if t.text != '☐')).strip()

    # ---------- blocks ----------
    def blocks(self, nodes, in_cell=False):
        out, group = [], None  # group = (tag, [items])

        def flush():
            nonlocal group
            if group:
                tag, items = group
                cls = ' class="checks"' if tag == 'div' else ''
                out.append(f'<{tag}{cls}>' + ''.join(items) + f'</{tag.split()[0]}>')
                group = None

        def push(tag, item):
            nonlocal group
            if group and group[0] != tag:
                flush()
            if not group:
                group = (tag, [])
            group[1].append(item)

        last_num = None
        for node in nodes:
            if node.tag == W + 'tbl':
                flush()
                out.append(self.table(node))
                continue
            if node.tag != W + 'p':
                continue
            ppr = node.find(W + 'pPr')
            style = ppr.find(W + 'pStyle').get(W + 'val') if ppr is not None and ppr.find(W + 'pStyle') is not None else ''
            body, checked = self.inline(node)
            for text in self.drop:
                body = body.replace(text, '').strip()
            for old, new in self.swap:
                body = body.replace(old, new)
            if checked is not None:
                key = self.key(self.text(node) or 'box')
                mark = ' data-default="1"' if checked else ''
                box = f'<input type="checkbox" data-k="{html.escape(key)}"{mark}>'
                if not body:
                    flush()
                    out.append(box)
                else:
                    push('div', f'<label class="chk">{box}<span{self.leaf(body)}>{body}</span></label>')
                continue
            if not body:
                continue
            if body.startswith('<div class="board"'):
                flush()
                out.append(body)
                continue
            numpr = ppr.find(W + 'numPr') if ppr is not None else None
            if numpr is not None:
                num_id = numpr.find(W + 'numId').get(W + 'val')
                level = numpr.find(W + 'ilvl').get(W + 'val')
                tag = f'ol data-n="{num_id}"' if self.numfmt.get(num_id) == 'decimal' else 'ul'
                sub = ' class="sub"' if level != '0' else ''
                push(tag, f'<li{sub}{self.leaf(body)}>{body}</li>')
                continue
            flush()
            last_num = None
            if style == 'Ttulo3':
                out.append(f'<h3{self.leaf(body)}>{body}</h3>')
            elif style in ('Ttulo', 'Subttulo', 'Ttulo1', 'Ttulo2', 'BannerMeta'):
                out.append(f'<!--{style}-->{body}')
            else:
                sizes = {s.get(W + 'val') for s in node.iter(W + 'sz')}
                small = sizes == {'18'} or sizes == {'17'}
                cls = ' class="note"' if small and not in_cell else ''
                out.append(f'<p{cls}{self.leaf(body)}>{body}</p>')
        flush()
        return out

    def table(self, tbl):
        left = tbl.find(f'{W}tblPr/{W}tblBorders/{W}left')
        size = left.get(W + 'sz') if left is not None else None
        rows = tbl.findall(W + 'tr')
        if size == '48':  # section banner
            paras = rows[0].find(W + 'tc').findall(W + 'p')
            title = self.inline(paras[0])[0]
            meta = self.inline(paras[1])[0] if len(paras) > 1 else ''
            return f'<!--Banner-->{re.sub(r"<[^>]+>", "", title)}<!--meta-->{re.sub(r"<[^>]+>", "", meta)}'
        if size == '36':  # callout
            kind = CALLOUT.get(left.get(W + 'color', '').upper(), 'info')
            inner = ''.join(self.blocks(list(rows[0].find(W + 'tc')), in_cell=True))
            return f'<div class="callout {kind}">{inner}</div>'
        fills = [[(tc.find(f'{W}tcPr/{W}shd').get(W + 'fill', '').upper() if tc.find(f'{W}tcPr/{W}shd') is not None else '')
                  for tc in row.findall(W + 'tc')] for row in rows]
        flat = {f for row in fills for f in row}
        bar = bool(flat & {'E8F5E9', 'EAF1FB', 'F8D7D3'}) and len(rows[0].findall(W + 'tc')) >= 6
        has_head = bool(fills) and all(f in ('1F3864', 'DCE6F2') for f in fills[0]) and len(rows) > 1
        head_names = [self.text(tc) for tc in rows[0].findall(W + 'tc')] if has_head else []
        drop = set()
        if not self.boxes:
            drop = {c for row in rows for c, tc in enumerate(row.findall(W + 'tc'))
                    if tc.find(f'.//{W14}checkbox') is not None and not self.text(tc)}
        out = [f'<div class="tw"><table class="{"bar" if bar else "data"}">']
        for r, row in enumerate(rows):
            cells = row.findall(W + 'tc')
            row_text = ' '.join(self.text(tc) for tc in cells)
            tag = 'th' if has_head and r == 0 else 'td'
            out.append('<tr>')
            for c, tc in enumerate(cells):
                if c in drop:
                    continue
                cls = CELL_CLASS.get(fills[r][c], '')
                saved = self.keys
                inner = ''.join(self.blocks(list(tc), in_cell=True))
                if '<input' in inner and not self.text(tc):  # a lone tick box: key it by row and column
                    self.keys = saved
                    col = head_names[c] if c < len(head_names) else str(c)
                    key = f'{self.part}|{slug(self.section)}|{slug(row_text)}|{slug(col)}'
                    inner = re.sub(r'data-k="[^"]*"', f'data-k="{html.escape(key)}"', inner)
                    cls = (cls + ' box').strip()
                attr = f' class="{cls}"' if cls else ''
                one = re.match(r'^<p data-t="(\d+)">(.*)</p>$', inner, flags=re.S) if inner.count('<p') == 1 else None
                if one:  # a cell with one paragraph: the cell itself carries the text
                    attr += f' data-t="{one.group(1)}"'
                    inner = one.group(2)
                out.append(f'<{tag}{attr}>{inner}</{tag}>')
            out.append('</tr>')
        out.append('</table></div>')
        return ''.join(out)


def join_lists(text):
    """Top-level nodes are converted one at a time, so a list comes out as one list per item: put them back together."""
    text = text.replace('</li></ul><ul><li', '</li><li').replace('</label></div><div class="checks"><label', '</label><label')
    return _same_ol(text)


def _same_ol(text):
    # numbered lists: join only neighbours that share the same Word numbering
    out, last = [], None
    for piece in re.split(r'(<ol data-n="\d+">)', text):
        m = re.match(r'<ol data-n="(\d+)">', piece)
        if m:
            joined = out and out[-1].endswith('</li></ol>') and last == m.group(1)
            if joined:
                out[-1] = out[-1][:-len('</ol>')]
            else:
                out.append('<ol>')
            last = m.group(1)
        else:
            out.append(piece)
    return ''.join(out)


def convert(path, part, boxes=True, drop=(), strings=None, swap=()):
    doc = Doc(path, part, boxes, drop, strings, swap)
    result = {'title': '', 'subtitle': '', 'sections': []}
    current = {'id': f'{part}-inicio', 'title': 'Visão geral', 'meta': '', 'html': []}

    def close():
        if current['html']:
            current['html'] = join_lists(''.join(current['html']))
            result['sections'].append(dict(current))

    # walk top-level nodes one by one so section titles are known before their checkboxes are keyed
    for node in list(doc.body):
        for piece in doc.blocks([node]):
            m = re.match(r'<!--(Ttulo|Subttulo|Ttulo1|Ttulo2|BannerMeta|Banner)-->(.*)', piece, flags=re.S)
            if not m:
                current['html'].append(piece)
                continue
            kind, text = m.groups()
            if kind == 'Ttulo':
                result['title'] = re.sub(r'<[^>]+>', '', text)
            elif kind == 'Subttulo':
                result['subtitle'] = re.sub(r'<[^>]+>', '', text)
            elif kind in ('Ttulo1', 'Banner'):
                close()
                title, _, meta = text.partition('<!--meta-->')
                title = re.sub(r'<[^>]+>', '', title)
                doc.section = title
                current = {'id': f'{part}-{slug(title)}', 'title': title, 'meta': meta, 'html': [],
                           'group': kind == 'Ttulo1'}
            else:
                current['html'].append(f'<p{doc.leaf(text)}>{text}</p>')
    close()
    return result


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf8')
    for path in sys.argv[1:]:
        res = convert(path, 'x')
        print(res['title'], '|', res['subtitle'])
        for s in res['sections']:
            print('  -', s['title'], '|', s['meta'][:50], '|', len(s['html']), 'chars | boxes', s['html'].count('<input'))
