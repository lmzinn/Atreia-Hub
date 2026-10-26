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
PROG_SOURCE = 'https://docs.google.com/document/d/1Iu01j2KDeZ4ebVKifo42SaWYmp7WTBHVw5YKRjLgX1U/edit?tab=t.0'  # the document the page is based on
CFG = os.path.join(SRC, 'Checklist de Configurações - Aion 2 Global.docx')
if len(args) >= 5:
    OUT, PROG, ASN, CFG, BOARDS = args[:5]
    PVP = args[5] if len(args) > 5 else ''
    RGR = RGRP = ''
elif PUBLIC:
    OUT, ASN, PVP, BOARDS = os.path.join(ROOT, 'index.html'), '', '', ''
    RGR = RGRP = ''
else:
    OUT = args[0] if args else os.path.join(PRIVATE, 'Guia Aion 2.html')
    ASN = os.path.join(PRIVATE, 'bldasn', 'Build Assassin PvE - Aion 2 Global.docx')
    PVP = os.path.join(PRIVATE, 'bldpvp', 'Assassin PvP - Aion 2 Global.docx')
    BOARDS = os.path.join(PRIVATE, 'boards_asn.json')
    RGR = os.path.join(PRIVATE, 'bldrgr', 'Build Ranger PvE - Aion 2 Global.docx')
    RGRP = os.path.join(PRIVATE, 'bldrgr', 'Ranger PvP - Aion 2 Global.docx')
# the routine and crafting parts have no DOCX: their text is in routine_part.py and craft_part.py, their data in JSON
TOOLS = tool_parts.__file__  # the parts written there always exist
PARTS = [('rot', 'Rotina', ROUTINE), ('bld', 'Minha build', BUILDER), ('prog', 'Progressão', PROG),
         ('asn', 'Assassin PvE', ASN), ('pvp', 'Assassin PvP', PVP), ('rgr', 'Ranger PvE', RGR), ('rgrp', 'Ranger PvP', RGRP), ('craft', 'Crafting', CRAFT), ('find', 'Onde consigo?', tool_parts.FINDER),
         ('set', 'Configurações', TOOLS)]
PARTS = [part for part in PARTS if part[2] and os.path.exists(part[2])]
# folders of the left menu: the pages of a class sit inside Classes > <class>
FOLDER = {'asn': ('Classes', 'Assassin'), 'pvp': ('Classes', 'Assassin'), 'rgr': ('Classes', 'Ranger'), 'rgrp': ('Classes', 'Ranger')}
SHORT = {
    'Critical Hit': 'Crit Hit', 'Critical Hit Resist': 'Crit Resist', 'Max HP': 'HP', 'Max MP': 'MP',
    'Critical Damage Boost': 'Crit Dmg Boost', 'Critical Damage Tolerance': 'Crit Dmg Tolerance',
    'Revitalization Contract': 'Revital. Contract', 'Heightened Sixth Sense': 'Sixth Sense',
    'Cooldown Reduction': 'Cooldown Reduct.', 'Insignia Explosion': 'Insignia Explos.',
    "Hunter's Resolve": "Hunter's Resolve", 'Unyielding Resolve': 'Unyield. Resolve', 'Concentrated Fire': 'Concentr. Fire',
}
# the settings part is reference only on the page: no tick boxes, so the sentences about ticking go too
NO_BOXES = {'cfg'}
# parts where every skill name gets its icon, and the class whose icons they use: {class: {skill: data URI}}. The
# Assassin ones are the owner's files in icons/ (icons.json: skill name -> file); the others come from the build editor
ICON_PARTS = {'asn': 'Assassin', 'pvp': 'Assassin', 'rgr': 'Ranger', 'rgrp': 'Ranger'}
ICON_DIR = os.path.join(PRIVATE, 'icons')  # the icons of the owner's build pages
icons = {}
if not PUBLIC and os.path.exists(os.path.join(ICON_DIR, 'icons.json')):
    icons['Assassin'] = {}
    for skill, name in json.load(open(os.path.join(ICON_DIR, 'icons.json'), encoding='utf8')).items():
        data = open(os.path.join(ICON_DIR, name), 'rb').read()
        icons['Assassin'][skill] = 'data:image/webp;base64,' + base64.b64encode(data).decode()
if not PUBLIC and RGR and os.path.exists(RGR):
    icons['Ranger'] = {k.split('/', 1)[1]: v for k, v in builder_icons().items() if k.startswith('Ranger/')}
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


def hard_mode(strings, own_en):
    """The step the patch of 21 Oct 2026 added inside the 6th objective: Krao Cave and Draupnir on Hard."""
    def t(pt, en):
        strings.append(pt)
        own_en[pt] = en
        return ' data-t="%d"' % (len(strings) - 1)
    rows = ''.join('<tr><td%s><span class="g"><b>%s</b></span></td><td%s><span class="g"><b>Hard</b></span></td><td%s>%s</td></tr>' % (
        t(name, name), name, t('Hard', 'Hard'), t(pt, en), pt) for name, pt, en in (
        ('Krao Cave', 'Ariel Fragment, Philosopher’s Stone: Revelation (dá para escolher como recompensa garantida) e todos os materiais Unique de craft (Wrathful Mind, Will e Ego)',
         'Ariel Fragment, Philosopher’s Stone: Revelation (it can be picked as the guaranteed reward) and every Unique crafting material (Wrathful Mind, Will and Ego)'),
        ('Draupnir', 'O mesmo, com o Ariel Fragment desta dungeon (cada uma tem o seu)', 'The same, with this dungeon’s own Ariel Fragment (each has its own)')))
    head = ''.join('<th class="head"%s><b>%s</b></th>' % (t(pt, en), pt) for pt, en in (('Dungeon', 'Dungeon'), ('Modo', 'Mode'), ('O que dá', 'What it gives')))
    check = ('<div class="checks"><label class="chk"><input type="checkbox" data-k="prog|6o-objetivo-2-800-gs|modo-hard-ariel"><span%s>%s</span></label></div>'
             % (t('Converter os Ariel Fragments em Daevanion Crystal: Ariel (100 para 1, até 30 por personagem) e gastar no tabuleiro Ariel',
                  'Turn the Ariel Fragments into Daevanion Crystal: Ariel (100 to 1, up to 30 per character) and spend them on the Ariel board'),
                'Converter os Ariel Fragments em Daevanion Crystal: Ariel (100 para 1, até 30 por personagem) e gastar no tabuleiro Ariel'))
    intro_pt = ('Novo no patch de 21/out/2026. Pede 2.600 GS (item level); os chefes entram em Frenzy aos 4 minutos e cada jogador tem 3 '
                'revives. É de onde vem o tabuleiro Ariel.')
    intro_en = ('New in the 21 Oct 2026 patch. It asks for 2,600 GS (item level); bosses go into Frenzy after 4 minutes and each player has '
                '3 revives. It is where the Ariel board comes from.')
    title_pt = 'Modo Hard: Krao Cave e Draupnir (2.600 GS)'
    return ('<h3%s>%s</h3><p%s>%s</p><div class="tw"><table class="data"><tr>%s</tr>%s</table></div>%s'
            % (t(title_pt, 'Hard mode: Krao Cave and Draupnir (2,600 GS)'), title_pt, t(intro_pt, intro_en), intro_pt, head, rows, check))


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
        if pid == 'prog':  # the page ends at the last Gear Score goal; what the DOCX has after it is left out
            last = next(i for i, sec in enumerate(doc['sections']) if sec['id'].startswith('prog-6o-objetivo'))
            doc['sections'], first = doc['sections'][:last + 1], doc['sections'][0]
            first['html'], cut = re.subn(r'<tr>(?:(?!</tr>).)*Próximas sugestões: Odyle, pets e estátuas(?:(?!</tr>).)*</tr>', '', first['html'], flags=re.S)
            assert cut == 1, cut
            credit = f'<a href="{PROG_SOURCE}" target="_blank" rel="noopener">'
            pt, en = f'Baseado no {credit}documento de progressão inicial</a> do guia de início.', f'Based on the {credit}initial progression document</a> of the starter guide.'
            strings.append(pt)
            own_en[pt] = en
            first['html'] += f'<p class="note" data-t="{len(strings) - 1}">{pt}</p>'
            doc['sections'][last]['html'] += hard_mode(strings, own_en)
        if PUBLIC and pid == 'cfg':  # the last section only points at the owner's build pages
            doc['subtitle'] = 'Configurações de referência, para repetir em cada personagem'
            doc['sections'] = [sec for sec in doc['sections'] if not sec['title'].startswith('5.')]
    for sec in doc['sections']:  # bullets that only said the original document had a heading with no text under it
        sec['html'] = re.sub(r'<li[^>]*>(?:(?!</li>).)*título sem texto no documento original(?:(?!</li>).)*</li>', '', sec['html'])
    nav.append(f'<button class="partbtn" data-part="{pid}"><span{t(name)}>{html.escape(name)}</span><small></small></button>')
    toc.append(f'<ul class="toc" data-part="{pid}">')
    mark_icons = f' data-icons="{ICON_PARTS[pid]}"' if pid in ICON_PARTS else ''
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

# nodes open by the median of the Global top 10 of each class (shugo.gg): Assassin on 13 Oct 2026, Ranger on 14 Oct
TOP_NODES = {'Assassin': {'Nezekan': 65, 'Zikel': 61, 'Vaizel': 58, 'Triniel': 73, 'Azphel': 27},
             'Ranger': {'Nezekan': 60, 'Zikel': 56, 'Vaizel': 60, 'Triniel': 75, 'Azphel': 23}}
# the boards of each class, in the site's order; the Assassin ones keep their old keys (the marks saved in the browser
# are under them), the others are "Class/Board"
CLASS_BOARDS = [('Assassin', BOARDS, '')] + ([('Ranger', os.path.join(PRIVATE, 'boards_rgr.json'), 'Ranger/')] if 'Ranger' in icons else [])
boards = {}
for cls, path, prefix in CLASS_BOARDS:
    for b in json.load(open(path, encoding='utf8')) if path and os.path.exists(path) else []:
        first = [n for n in b['nodes'] if not n['later'] and n['kind'] != 'start']
        mine = icons.get(cls, {})
        boards[prefix + b['name']] = {
            'name': prefix + b['name'], 'cls': cls, 'size': b['size'], 'total': b['crystals'], 'def': max(n['spent'] for n in first),
            'own': b['name'] == 'Azphel',  # PvP board: crystals of its own, kept out of the PvE total
            # the crystals the top 10 spent (a board in its own order, as the Ranger's damage route, says it itself)
            'top': b.get('topSpent') or max(n['spent'] for n in b['nodes'] if n['kind'] != 'start' and n['order'] <= TOP_NODES[cls][b['name']]),
            **({'ver': b['ver']} if b.get('ver') else {}),  # a new order of the numbers: the marks saved under the old one go
            'edges': b['edges'],
            'nodes': [{'c': n['col'], 'r': n['row'], 'k': n['kind'], 'o': n['order'], 'l': SHORT.get(n['name'], n['name']),
                       't': n['tip'].split('\n')[0].split('. In the game')[0], 'x': n['cost'], 'p': n['pct'], 's': n['spent'],
                       **({'i': n['name']} if n['name'] in mine else {})}
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
print('wrote', OUT, len(page) // 1024, 'KB |', page.count('data-k='), 'checkboxes |', len(boards), 'boards |', sum(len(v) for v in icons.values()), 'icons |',
      sum(e is not None for e in english), 'of', len(strings), 'texts in English')
