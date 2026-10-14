"""Small pictures for the tools and the text pages, from the records wk_all.py downloaded of wikily.gg:
term_icons.json = {key: data URI}. Keys: a material or currency name; "piece:<Dagger…>" and "type:<gear type>" for
gear; "dg:<dungeon>" for the dungeon thumbnails of the routine; the name of an Arcana or of a pair of wings.
Needs Pillow. Icons already in the file are not downloaded again."""
import base64
import io
import json
import os
import sys
import urllib.request

from PIL import Image

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'Accept': '*/*'}
OUT = 'term_icons.json'


def load(slug):
    return json.load(open('wikily/ds_%s.json' % slug, encoding='utf8'))


want = {}  # key -> (url, (width, height))
craft = json.load(open('craft_data.json', encoding='utf8'))
names = {m for p in craft['pieces'] for s in p['steps'] for m, q in s['mats']} | {n for sub in craft['sub'].values() for n, q in sub}
for r in load('materials'):
    if r['name'] in names and r.get('icon'):
        want[r['name']] = (r['icon'], (40, 40))
for r in load('currencies'):
    if r['name'] in ('Kina', 'Abyss Points', 'Enhance Stone', 'Daevanion Crystal', 'Daevanion Crystal: Azphel', 'Quna') and (r.get('icon') or r.get('head')):
        want[r['name']] = (r.get('icon') or r['head'], (40, 40))
for r in load('consumables'):
    for key, name in (('Shugo Festival', 'Shugo Festival Reward Key (Bound)'), ('Unknown Fissure (Daily Dungeon)', 'Unknown Fissure Challenge Ticket (Bound)'),
                      ('Ascension Trial', 'Ascension Trial Challenge Ticket (Bound)'), ('Odyle Energy', 'Odyle Energy (Bound)')):
        if r['name'] == name and r.get('icon'):
            want['dg:' + key] = (r['icon'], (40, 40))
# gear: the True Dragon Lord piece of each slot of the calculator, and the best Unique of every gear type
gear = load('weapons') + load('armor') + load('accessories')
PIECE = {'Breastplate': 'Top', 'Greaves': 'Legs', 'Boots': 'Shoes'}
for p in craft['pieces']:
    item = next((g for g in gear if g['name'] == 'True Dragon Lord ' + p['piece']), None)
    if item:
        want['piece:' + p['piece']] = (item['icon'], (44, 44))
for kind in sorted({g['type'] for g in gear}):
    best = max((g for g in gear if g['type'] == kind and g.get('icon')), key=lambda g: (g['grade'] == 'Unique', int(g.get('itemLevel') or 0)))
    want['type:' + kind] = (best['icon'], (44, 44))
for r in load('arcana'):
    if not r['kind'].endswith(' Arcana') and r.get('icon'):
        want[r['name']] = (r['icon'], (40, 40))
for r in load('wings'):
    if r.get('icon'):
        want[r.get('grantsWing') or r['name']] = (r['icon'], (40, 40))
for r in load('dungeons'):
    if r.get('category') in ('Expedition', 'Nightmare', 'Sanctuary') and r.get('image'):
        want['dg:' + r['name'].split(':')[0]] = (r['image'], (112, 63))
# dungeon art that wikily does not have: metabot.gg's dungeon pages, and thegameswiki.com for the Dimensional Invasion
# portal (a screenshot: only the middle of it, where the portal is, is kept)
MB = 'https://metabot.gg/web/aion2/art/dungeons/%s.webp'
for name, slug in (('Chalice of Muspel', 'chalice-of-muspel'), ('Corroded Decontamination Facility', 'corroded-decontamination-facility'),
                   ('Azure Breath Island', 'azure-breath-island'), ('Cradle of Nihility', 'cradle-of-nihility'),
                   ("Dying Dramata's Nest", 'dying-dramatas-nest'), ('Hall of Illusion', 'hall-of-illusion')):
    want['dg:' + name] = (MB % slug, (112, 63))
want['dg:Dimensional Invasion'] = ('https://1cb6tlwvfkhv5nag.public.blob.vercel-storage.com/wiki-images/71ad1443-5fce-4b63-9d7a-6dfd427eb614/'
                                   'aion-2-dimensional-invasion-portal.jpg', (112, 63), (560, 150, 1040, 420))
# the pass coin for the Daeva Pass card of the routine (the cards with no art of their own get a drawn icon in the page)
coin = next((r.get('icon') or r.get('head') for r in load('currencies') if r['name'] == 'Daeva Pass Shop Coin'), None)
if coin:
    want['dg:Daeva Pass'] = (coin, (40, 40))

# the game item that stands for each counter of the routine (the 'pic' of routine_data.json): its icon, as 'rt:<id>'
if os.path.exists('routine_data.json'):
    item_icon = {r['name']: r.get('icon') or r.get('head') for slug in ('consumables', 'materials', 'currencies') for r in load(slug)}
    for row in json.load(open('routine_data.json', encoding='utf8')):
        if item_icon.get(row.get('pic')):
            want['rt:' + row['id']] = (item_icon[row['pic']], (44, 44))

icons = json.load(open(OUT, encoding='utf8')) if os.path.exists(OUT) else {}
for key, (url, (w, h), *box) in want.items():
    if key in icons:
        continue
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        im = Image.open(io.BytesIO(raw)).convert('RGBA')
        if box:  # only this part of the picture
            im = im.crop(box[0])
        scale = max(w / im.width, h / im.height)  # cover the box, then cut the middle
        im = im.resize((max(w, round(im.width * scale)), max(h, round(im.height * scale))), Image.LANCZOS)
        left, top = (im.width - w) // 2, (im.height - h) // 2
        im = im.crop((left, top, left + w, top + h))
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=74, method=6)
        icons[key] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print('  failed', key, str(e)[:70])
icons = {k: icons[k] for k in sorted(icons) if k in want}
json.dump(icons, open(OUT, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(len(icons), 'of', len(want), 'pictures |', os.path.getsize(OUT) // 1024, 'KB')
print(sorted(k for k in want if k.startswith(('dg:', 'piece:', 'type:')) or k in ('Kina', 'Enhance Stone')))
print('missing materials:', sorted(names - set(want)))
