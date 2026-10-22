"""Data of the build editor, from what wk_all.py downloaded of wikily.gg into wikily/:
builder_data.json (skills, Daevanion boards, gear, titles, Arcana, wings, pets) and builder_icons.json (skill icons,
48 px WebP as data URIs). Run wk_all.py first; pass --icons to download the icons that are still missing."""
import base64
import html
import io
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'Accept': '*/*'}
CLASSES = ['Gladiator', 'Templar', 'Assassin', 'Ranger', 'Sorcerer', 'Spiritmaster', 'Cleric', 'Chanter']
WEAPON = {'Gladiator': 'Greatsword', 'Templar': 'Longsword', 'Assassin': 'Dagger', 'Ranger': 'Bow', 'Sorcerer': 'Spellbook',
          'Spiritmaster': 'Orb', 'Cleric': 'Mace', 'Chanter': 'Staff'}
BOARDS = ['Nezekan', 'Zikel', 'Vaizel', 'Triniel', 'Azphel', 'Ariel']
GRADES = ['Common', 'Rare', 'Epic', 'Unique', 'Special']


def load(slug):
    return json.load(open('wikily/ds_%s.json' % slug, encoding='utf8'))


def stats(rows):
    return ', '.join('%s %s' % (s['name'], s['value']) for s in rows or [])


def num(text, default=0):
    m = re.search(r'\d+', str(text or ''))
    return int(m.group(0)) if m else default


# ---------- skills ----------
skills, icon_src = {c: [] for c in CLASSES}, {}
for r in load('skills'):
    if r['category'] == 'Dodge' or r['className'] not in skills:
        continue
    learn = r.get('learn') or []
    skills[r['className']].append({
        'n': r['name'], 'c': r['category'][0],                      # A active, P passive, S stigma
        'cd': r.get('cooldown') or '', 'd': (r.get('description') or '').split('\n')[0],
        'cost': [num(x['cost']) for x in learn],                       # points (or shards) to buy each level, from level 1
        'at': [num(x.get('characterLevel')) for x in learn],           # character level that opens each level
        'sp': [[s['title'], num(s['subtitle'])] for s in r.get('specialties') or []],
    })
    icon_src[r['className'] + '/' + r['name']] = r.get('icon') or ''
for c in CLASSES:
    order = {'A': 0, 'P': 1, 'S': 2}
    skills[c].sort(key=lambda s: (order[s['c']], s['at'][0] if s['at'] else 0))
    assert [sum(s['c'] == k for s in skills[c]) for k in 'APS'] == [12, 10, 13], c

# ---------- Daevanion boards ----------
boards = {}
for c in CLASSES:
    boards[c] = []
    for b in BOARDS:
        page = open('wikily/boards/%s_%s.html' % (c.lower(), b.lower()), encoding='utf8').read()
        desc = {m.group(1): (html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip().rstrip('.'), int(m.group(3) or 0))
                for m in re.finditer(r'id="[^"]*-b0-(n\d+)" class="ext-gwe-skill-item-details">\s*(?:<p class="ext-gwe-skill-pop-desc">(.*?)</p>)?'
                                     r'(?:<ul class="ext-gwe-skill-costs"[^>]*><li[^>]*><span>(\d+)</span>)?', page, re.S)}
        nodes = []
        for m in re.finditer(r'<div class="ext-gwe-skill-node([^"]*)" data-sk-node="(n\d+)"[^>]*style="left:(\d+)px;top:(\d+)px">.*?<span class="sr-only">(.*?)</span>', page, re.S):
            cls, nid, left, top, label = m.groups()
            text, cost = desc.get(nid, ('', 0))
            nodes.append([(int(left) - 20) // 56, (int(top) - 20) // 56, cost, text or html.unescape(label)])
        start = [n for n in nodes if not n[2]]
        assert len(start) == 1, (c, b, len(start), len(nodes))
        boards[c].append({'name': b, 'size': max(max(n[0], n[1]) for n in nodes) + 1, 'nodes': nodes})
    print(c, [(len(b['nodes']) - 1, sum(n[2] for n in b['nodes'])) for b in boards[c]])

# ---------- gear ----------
def gear(slug, keep=lambda r: True):
    out = []
    for r in load(slug):
        if not keep(r):
            continue
        out.append([r['name'], r['type'], GRADES.index(r['grade']), num(r.get('itemLevel')), num(r.get('maxEnchant')), stats(r.get('stats')),
                    {'Elyos': 1, 'Asmodians': 2}.get(r.get('race'), 0)])
    return sorted(out, key=lambda x: (x[1], -x[3], -x[2], x[0]))


weapons, armor, accessories = gear('weapons'), gear('armor'), gear('accessories')
titles = sorted(([r['titleName'], r['titleEffectType'], stats(r.get('titleEquipped')), stats(r.get('titleOwned'))] for r in load('titles')),
                key=lambda t: (t[1], t[0]))
arcana = sorted(([r['name'], r['kind'].split(' ', 1)[1], GRADES.index(r['grade']), stats(r.get('stats')), r.get('setName') or '']
                 for r in load('arcana') if not r['kind'].endswith(' Arcana')), key=lambda a: (a[1], -a[2], a[0]))
wings = sorted([r['grantsWing'] or r['name'], r.get('wingEquipped') or '', r.get('wingOwnedText') or ''] for r in load('wings'))
pets = sorted({r['name'] for r in load('pets')})
data = {'classes': CLASSES, 'weapon': WEAPON, 'grades': GRADES, 'skills': skills, 'boards': boards, 'weapons': weapons, 'armor': armor,
        'accessories': accessories, 'titles': titles, 'arcana': arcana, 'wings': wings, 'pets': pets}
if os.path.exists('enh_bonus.json'):  # Enhance bonus of the gear, made by enh_bonus.py (run it again after new gear)
    data['enh'] = json.load(open('enh_bonus.json', encoding='utf8'))
json.dump(data, open('builder_data.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('builder_data.json', os.path.getsize('builder_data.json') // 1024, 'KB |', len(weapons), 'weapons', len(armor), 'armor', len(accessories),
      'accessories', len(titles), 'titles', len(arcana), 'arcana', len(wings), 'wings', len(pets), 'pets')
import collections
print('types:', collections.Counter(a[1] for a in accessories), collections.Counter(a[1] for a in armor), collections.Counter(a[1] for a in arcana),
      collections.Counter(t[1] for t in titles))

# ---------- icons ----------
ICONS = 'builder_icons.json'
icons = json.load(open(ICONS, encoding='utf8')) if os.path.exists(ICONS) else {}
if '--icons' in sys.argv:
    from PIL import Image
    for key, url in icon_src.items():
        if key in icons or not url:
            continue
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        im = Image.open(io.BytesIO(raw)).convert('RGBA').resize((48, 48), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=72, method=6)
        icons[key] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
        if len(icons) % 40 == 0:
            print(len(icons), 'icons')
            json.dump(icons, open(ICONS, 'w', encoding='utf8'))
    json.dump(icons, open(ICONS, 'w', encoding='utf8'))
print('icons:', len(icons), 'of', len(icon_src), '|', os.path.getsize(ICONS) // 1024 if os.path.exists(ICONS) else 0, 'KB')
