"""Assemble the site from the DOCX guides and the parts written in Python.

Usage: guide_build.py                  the public site: ../index.html, without the owner's own builds
       guide_build.py --local [<out>]  the owner's page, with the builds kept in ../privado (default: ../privado/Guia Aion 2.html)
       guide_build.py <out.html> <progression.docx> <assassin.docx> <config.docx> <boards.json> [<assassin-pvp.docx>]
       add --missing to list the texts that have no English version yet (i18n_missing.txt)

The page is written in Portuguese, as the DOCX files are. i18n_en.json maps each piece of Portuguese text to its
English version; a text that is not there simply stays in Portuguese when the page is switched to English.
"""
import base64
import datetime
import html
import json
import os
import hashlib
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from guide_convert import convert  # noqa: E402
from craft_part import DATA as CRAFT, calc_data, craft_part  # noqa: E402
from routine_part import DATA as ROUTINE, routine_data, routine_part  # noqa: E402
from builder_part import DATA as BUILDER, builder_data, builder_icons, builder_part  # noqa: E402
import tool_parts  # noqa: E402

sys.stdout.reconfigure(encoding='utf8', errors='replace')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
ROOT = os.path.dirname(HERE)              # the repository
SRC = os.path.join(ROOT, 'fontes')        # the DOCX of the public pages
PRIVATE = os.path.join(ROOT, 'privado')   # out of the repository: the owner's builds, their sources and the full translation file
PUBLIC = '--local' not in sys.argv and len(args) < 5
PROG = os.path.join(SRC, 'Progressão Aion 2 Global.docx')
CFG = os.path.join(SRC, 'Checklist de Configurações - Aion 2 Global.docx')
if len(args) >= 5:
    OUT, PROG, ASN, CFG, BOARDS = args[:5]
    PVP = args[5] if len(args) > 5 else ''
elif PUBLIC:
    OUT, ASN, PVP, BOARDS = os.path.join(ROOT, 'index.html'), '', '', ''
else:
    OUT = args[0] if args else os.path.join(PRIVATE, 'Guia Aion 2.html')
    ASN = os.path.join(PRIVATE, 'bldasn', 'Build Assassin PvE - Aion 2 Global.docx')
    PVP = os.path.join(PRIVATE, 'bldpvp', 'Assassin PvP - Aion 2 Global.docx')
    BOARDS = os.path.join(PRIVATE, 'boards_asn.json')
# the routine and crafting parts have no DOCX: their text is in routine_part.py and craft_part.py, their data in JSON
TOOLS = tool_parts.__file__  # the parts written there always exist
PARTS = [('rot', 'Rotina', ROUTINE), ('bld', 'Minha build', BUILDER), ('prog', 'Progressão', PROG),
         ('asn', 'Assassin PvE', ASN), ('pvp', 'Assassin PvP', PVP), ('craft', 'Crafting', CRAFT), ('find', 'Onde consigo?', tool_parts.FINDER),
         ('set', 'Configurações', TOOLS)]
PARTS = [part for part in PARTS if part[2] and os.path.exists(part[2])]
# folders of the left menu: the pages of a class sit inside Classes > <class>
FOLDER = {'asn': ('Classes', 'Assassin'), 'pvp': ('Classes', 'Assassin')}
SHORT = {
    'Critical Hit': 'Crit Hit', 'Critical Hit Resist': 'Crit Resist', 'Max HP': 'HP', 'Max MP': 'MP',
    'Critical Damage Boost': 'Crit Dmg Boost', 'Critical Damage Tolerance': 'Crit Dmg Tolerance',
    'Revitalization Contract': 'Revital. Contract', 'Heightened Sixth Sense': 'Sixth Sense',
    'Cooldown Reduction': 'Cooldown Reduct.', 'Insignia Explosion': 'Insignia Explos.',
}
# the settings part is reference only on the page: no tick boxes, so the sentences about ticking go too
NO_BOXES = {'cfg'}
# parts where every skill name gets its icon (icons/icons.json: skill name -> file in icons/)
ICON_PARTS = {'asn', 'pvp'}
ICON_DIR = os.path.join(PRIVATE, 'icons')  # the icons of the owner's build pages
icons = {}
if not PUBLIC and os.path.exists(os.path.join(ICON_DIR, 'icons.json')):
    for skill, name in json.load(open(os.path.join(ICON_DIR, 'icons.json'), encoding='utf8')).items():
        data = open(os.path.join(ICON_DIR, name), 'rb').read()
        icons[skill] = 'data:image/webp;base64,' + base64.b64encode(data).decode()
# the builds were renumbered on 14 Oct 2026; the settings checklist still points at the old sections
SWAP = (('Seção 1 da build', 'Seção 2 da build'), ('Seção 5 da build', 'Seção 3 da build'))
# the public site: the settings table shows a reference value and each reader writes their own beside it
PUBLIC_SWAP = (('Seu valor', 'Sugestão'),
               ('Os valores abaixo são os que você usa hoje, tirados dos seus prints.',
                'A coluna Sugestão traz uma configuração de referência; em “Seu valor” você anota a sua.'),
               (' (seção 4) é a única parte sem print seu: ali os valores são recomendação dos guias.',
                ' (seção 4): os valores são a recomendação dos guias.'),
               ('Não apareceram no print', 'Confira no jogo'))
PUBLIC_EN = {'<b>Sugestão</b>': '<b>Suggested</b>', 'Confira no jogo': 'Check in the game',
             'O jogo não copia configurações de um personagem para o outro. A coluna Sugestão traz uma configuração de '
             'referência; em “Seu valor” você anota a sua.':
             'The game does not copy settings from one character to another. The Suggested column has a reference '
             'setup; under “Your value” you note down your own.',
             '<b>Graphics → Optimize</b> (seção 4): os valores são a recomendação dos guias.':
             '<b>Graphics → Optimize</b> (section 4): the values are the guides&#x27; recommendation.',
             'Configurações de referência, para repetir em cada personagem': 'Reference settings, to repeat on each character'}
DROP = ('Marque a caixa do personagem quando a opção estiver igual nele.',
        'A coluna do Gladiator já está aqui para quando você criar o personagem.')

strings = []  # every piece of text of the page, in order; data-t="N" points here
own_en = {}  # English of the texts that are written in both languages in the scripts (the crafting part)


def t(text):
    """Attribute for an element whose whole content is this plain text."""
    strings.append(html.escape(text))
    return f' data-t="{len(strings) - 1}"'


nav, toc, content = [], [], []  # pages (left bar), topics of each page (second bar), the pages themselves
opened = ()  # folders of the menu that are open at this point of the list


def folders(want):
    """Close and open menu folders so that the next page lands inside the path `want`."""
    global opened
    keep = 0
    while keep < min(len(opened), len(want)) and opened[keep] == want[keep]:
        keep += 1
    nav.extend('</div></details>' for _ in opened[keep:])
    for i in range(keep, len(want)):
        nav.append(f'<details class="fold" data-fold="{html.escape("/".join(want[:i + 1]))}" open><summary>'
                   f'<span{t(want[i])}>{html.escape(want[i])}</span></summary><div class="in">')
    opened = want


for pid, name, path in PARTS:
    folders(FOLDER.get(pid, ()))
    if pid == 'craft':
        doc = craft_part(strings, own_en)
    elif pid == 'rot':
        doc = routine_part(strings, own_en)
    elif pid == 'bld':
        doc = builder_part(strings, own_en)
    elif pid in ('find', 'set'):
        doc = {'find': tool_parts.finder_part, 'set': tool_parts.settings_part}[pid](strings, own_en)
    else:
        doc = convert(path, pid, boxes=pid not in NO_BOXES, drop=DROP if pid in NO_BOXES else (), swap=((PUBLIC_SWAP if PUBLIC else ()) + SWAP) if pid in NO_BOXES else (), strings=strings)
        if PUBLIC and pid == 'cfg':  # the last section only points at the owner's build pages
            doc['subtitle'] = 'Configurações de referência, para repetir em cada personagem'
            doc['sections'] = [sec for sec in doc['sections'] if not sec['title'].startswith('5.')]
    for sec in doc['sections']:  # bullets that only said the original document had a heading with no text under it
        sec['html'] = re.sub(r'<li[^>]*>(?:(?!</li>).)*título sem texto no documento original(?:(?!</li>).)*</li>', '', sec['html'])
    nav.append(f'<button class="partbtn" data-part="{pid}"><span{t(name)}>{html.escape(name)}</span><small></small></button>')
    toc.append(f'<ul class="toc" data-part="{pid}">')
    mark_icons = ' data-icons="1"' if pid in ICON_PARTS else ''
    content.append(f'<section class="part" data-part="{pid}" id="part-{pid}"{mark_icons}><header>'
                   f'<h1{t(doc["title"])}>{html.escape(doc["title"])}</h1>'
                   f'<p class="sub"{t(doc["subtitle"])}>{html.escape(doc["subtitle"])}</p></header>')
    for i, sec in enumerate(doc['sections']):
        title, mark = html.escape(sec['title']), t(sec['title'])
        toc.append(f'<li><a href="#{sec["id"]}"><span{mark}>{title}</span><small></small></a></li>')
        meta = f'<span class="meta"{t(sec["meta"])}>{html.escape(sec["meta"])}</span>' if sec['meta'] else '<span class="meta"></span>'
        content.append(f'<details class="sec" id="{sec["id"]}"{" open" if i == 0 else ""}><summary><span class="t"{mark}>{title}</span>'
                       f'{meta}<span class="cnt"></span></summary><div class="body">{sec["html"]}</div></details>')
    toc.append('</ul>')
    content.append('</section>')

folders(())
# the full translation file holds the text of the owner's builds too, so it stays in privado/; the repository gets
# only the entries the public pages use (written at the end of a public build)
i18n_public = os.path.join(HERE, 'i18n_en.json')
i18n_path = os.path.join(PRIVATE, 'i18n_en.json') if os.path.exists(os.path.join(PRIVATE, 'i18n_en.json')) else i18n_public
i18n = json.load(open(i18n_path, encoding='utf8')) if os.path.exists(i18n_path) else {}
if PUBLIC:
    own_en.update(PUBLIC_EN)


def auto_en(s):
    """Texts with no translation of their own still get English numbers: 1.400 -> 1,400 and 23,2% -> 23.2%."""
    out = re.sub(r'(?<=\d),(?=\d)', '\u0001', s)
    out = re.sub(r'(?<=\d)\.(?=\d{3}(?!\d))', ',', out).replace('\u0001', '.')
    return out if out != s else None


i18n = {**i18n, **own_en}
english = [i18n.get(s) or auto_en(s) for s in strings]
missing = [s for s in dict.fromkeys(strings) if s not in i18n and re.search(r'[a-zà-ú]{3}', s)]
if '--missing' in sys.argv:
    for name, rows in (('i18n_missing.txt', missing), ('i18n_rest.txt', [s for s in dict.fromkeys(strings) if s not in i18n])):
        with open(os.path.join(HERE, name), 'w', encoding='utf8', newline='\n') as f:
            f.write('\n'.join(rows) + '\n')
    print(len(missing), 'texts without an English version -> i18n_missing.txt')
    sys.exit()

TOP_NODES = {'Nezekan': 65, 'Zikel': 61, 'Vaizel': 58, 'Triniel': 73, 'Azphel': 27}  # top 10 Global, 13 Oct 2026
boards = {}
for b in json.load(open(BOARDS, encoding='utf8')) if BOARDS and os.path.exists(BOARDS) else []:
    first = [n for n in b['nodes'] if not n['later'] and n['kind'] != 'start']
    boards[b['name']] = {
        'name': b['name'], 'size': b['size'], 'total': b['crystals'], 'def': max(n['spent'] for n in first),
        'own': b['name'] == 'Azphel',  # PvP board: crystals of its own, kept out of the PvE total
        # crystals spent by the median top-40 Global Assassin (shugo.gg, 13 Oct 2026): nodes open, in the site's order
        'top': max(n['spent'] for n in b['nodes'] if n['kind'] != 'start' and n['order'] <= TOP_NODES[b['name']]),
        'edges': b['edges'],
        'nodes': [{'c': n['col'], 'r': n['row'], 'k': n['kind'], 'o': n['order'], 'l': SHORT.get(n['name'], n['name']),
                   't': n['tip'].split('\n')[0].split('. In the game')[0], 'x': n['cost'], 'p': n['pct'], 's': n['spent'],
                   **({'i': n['name']} if n['name'] in icons else {})}
                  for n in b['nodes']],
    }


def js(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


# the pictures of 'Onde consigo?' are files beside the page (finder_data.py makes them): they go with every copy of it
SHEETS = os.path.join(ROOT, 'finder_icons')
sheets = sorted(os.listdir(SHEETS)) if os.path.isdir(SHEETS) else []
sheets_version = hashlib.sha1(b''.join(open(os.path.join(SHEETS, f), 'rb').read() for f in sheets)).hexdigest()[:8]
page = open(os.path.join(HERE, 'guide_template.html'), encoding='utf8').read()
for token, value in (('__NAV__', ''.join(nav)), ('__TOC__', ''.join(toc)), ('__CONTENT__', ''.join(content)), ('__BOARDS__', js(boards)),
                     ('__EN__', js(english)), ('__ICONS__', js(icons)), ('__CALC__', js(calc_data() if os.path.exists(CRAFT) else {})),
                     ('__ROUTINE__', js(routine_data() if os.path.exists(ROUTINE) else [])),
                     ('__PUBLIC__', 'true' if PUBLIC else 'false'), ('__FIND__', js(tool_parts.finder_data())), ('__NEWS__', js(tool_parts.news_data())), ('__FICV__', sheets_version),
                     ('__TIC__', js(json.load(open(os.path.join(HERE, 'term_icons.json'), encoding='utf8'))
                                    if os.path.exists(os.path.join(HERE, 'term_icons.json')) else {})),  # pictures, made by icons_data.py
                     ('__BLD__', js(builder_data() if os.path.exists(BUILDER) else {})), ('__BIC__', js(builder_icons())), ('__BUILT__', datetime.date.today().strftime('%d/%m/%Y'))):
    assert page.count(token) == 1, token
    page = page.replace(token, value)
open(OUT, 'w', encoding='utf8', newline='\n').write(page)
beside = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'finder_icons')
if sheets and os.path.normcase(beside) != os.path.normcase(SHEETS):
    shutil.rmtree(beside, ignore_errors=True)
    shutil.copytree(SHEETS, beside)
if PUBLIC and i18n_path != i18n_public:
    used = {s: i18n[s] for s in dict.fromkeys(strings) if s in i18n and s not in own_en}
    json.dump(used, open(i18n_public, 'w', encoding='utf8', newline='\n'), ensure_ascii=False, indent=0, sort_keys=True)
print('wrote', OUT, len(page) // 1024, 'KB |', page.count('data-k='), 'checkboxes |', len(boards), 'boards |', len(icons), 'icons |',
      sum(e is not None for e in english), 'of', len(strings), 'texts in English')
