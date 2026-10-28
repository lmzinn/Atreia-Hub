"""Database data, from the records wk_all.py downloaded of wikily.gg. Run inside gerador/; needs Pillow.

Writes:
  ../database/db.js        window.ADB = {items: [...]}: every entry of every category, read by the Database page when it
                           is opened (a script file, so it also works on a copy of the site opened as a file)
  ../database/icons/N.webp the pictures, in sheets of PER squares, COLS a row, CELL pixels a square; an entry's `i` is
                           the number of its square counted through all the sheets (no `i` = no picture)
  recipes.json             {name: [category, picture, [[label, quantity made, [[material, quantity], ...]], ...], faction E/A/'', grade, item level, type]} for
                           every item with a recipe, plus the pictures of the materials ({'@pics': {name: picture}});
                           the Crafting page embeds it
The icons are cached in wikily/icons and not downloaded again."""
import hashlib
import io
import json
import os
import re
import shutil
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'Accept': '*/*'}
CACHE, OUT, CELL, COLS, PER = 'wikily/icons', '../database', 40, 20, 200


def load(slug):
    return json.load(open('wikily/ds_%s.json' % slug, encoding='utf8'))


def links(lst, limit=None):
    """[title, subtitle] pairs of a wikily list of links, without repeats."""
    out = []
    for x in lst or []:
        pair = [x.get('title', ''), x.get('subtitle', '') or x.get('qty', '')]
        if pair[0] and pair not in out:
            out.append(pair)
    return out[:limit] if limit else out


def sources(r):
    out = []
    for s in r.get('sources') or []:
        text = s['title'] + (' — ' + s['subtitle'] if s.get('subtitle') else '')
        if text not in out:
            out.append(text)
    more = len(out) - 8
    return out[:8] + (['+ %d' % more] if more > 0 else [])


def recipes(r):
    out = []
    for k in ('recipe1', 'recipe2', 'recipe3', 'recipe4'):
        if not r.get(k):
            continue
        label = r.get(k + 'Label') or ''
        made = re.search(r'Produces x ([\d,]+)', label)
        mats = [[x['title'], int(re.search(r'x ([\d,]+)', x['subtitle']).group(1).replace(',', ''))] for x in r[k] if re.search(r'x [\d,]+', x.get('subtitle', ''))]
        out.append([' · '.join(x for x in label.split(', ') if not x.startswith('Produces x')), int(made.group(1).replace(',', '')) if made else 1, mats])
    return out


def pairs(lst, a='name', b='value'):
    return [[x.get(a, ''), x.get(b, '')] for x in lst or [] if x.get(a)]


RACE = {'Elyos': 'E', 'Asmodians': 'A'}
items, pics = [], []


def add(cat, r, name=None, **extra):
    e = {'n': name or r['name'], 'c': cat}
    for key, field in (('t', 'type'), ('g', 'grade')):
        if r.get(field):
            e[key] = r[field]
    if RACE.get(r.get('race')):
        e['r'] = RACE[r['race']]
    src = sources(r)
    if src:
        e['o'] = src
    used = links(r.get('usedFor'), 12)
    if used:
        e['u'] = used
    rc = recipes(r)
    if rc:
        e['rc'] = rc
    e.update({k: v for k, v in extra.items() if v not in (None, '', [], {})})
    pics.append(r.get('icon') or r.get('head') or r.get('portrait') or r.get('face') or '')
    items.append(e)


for cat in ('weapons', 'armor', 'accessories'):
    for r in load(cat):
        add(cat, r, l=r.get('itemLevel'), q=r.get('requiredLevel'), k=r.get('classes'), s=pairs(r.get('stats')), x=pairs(r.get('subStats')),
            ms=r.get('manastoneSlots'), me=r.get('maxEnchant'))
for r in load('arcana'):
    add('arcana', r, re.sub(r'^Arcana: ', '', r['name']), l=r.get('itemLevel'), s=pairs(r.get('stats')), set=r.get('setName'),
        sb=pairs(r.get('setBonuses'), 'pieces', 'stats'))
for r in load('pets'):
    add('pets', r, re.sub(r'^Pet: ', '', r['name']), pt=r.get('petType'), pi=links(r.get('petInsight')))
for r in load('wings'):
    add('wings', r, we=r.get('wingEquipped'), wo=r.get('wingOwnedText'))
for r in load('titles'):
    add('titles', r, re.sub(r'^Title: ', '', r['name']), tc=r.get('titleCategory'), te=pairs(r.get('titleEquipped')), to=pairs(r.get('titleOwned')),
        tt=r.get('titleEffectType'))
for r in load('consumables'):
    add('consumables', r, d=r.get('description') if len(r.get('description') or '') < 400 else '', cd=r.get('cooldown'),
        ct=[x.get('title') for x in r.get('contents') or [] if x.get('title')][:12])
for r in load('materials'):
    add('materials', r, d=r.get('description') if len(r.get('description') or '') < 400 else '')
for r in load('manastones'):
    add('stones', r, ss=[[x.get('name'), x.get('chance'), x.get('values')] for x in r.get('stoneStats') or []], sn=r.get('stoneNote'))
for r in load('skills'):
    add('skills', r, k=r.get('className'), sc=r.get('category'), cd=r.get('cooldown'), rg=r.get('range'), d=r.get('description'),
        ml=r.get('maxLevel'), ac=r.get('acquire'))
for r in load('dungeons'):
    add('dungeons', r, dc=r.get('category'), pl=r.get('players'), rl=r.get('recommendedLevel'), rg=r.get('region'), en=r.get('energy'),
        d=(r.get('description') or '')[:600], bo=links(r.get('bosses'), 10), rw=[x[0] for x in links(r.get('rewardItems1'), 16)],
        md=[[m.get('mode'), m.get('level'), m.get('itemLevel'), m.get('players'), m.get('entry')] for m in r.get('modes') or []])
for r in load('bosses'):
    add('monsters', r, lv=r.get('level'), rg=r.get('where') or r.get('region'), ty=r.get('type'), cr=r.get('creature'),
        dr=links(r.get('dropTop'), 12), gl=[[g.get('title'), g.get('subtitle')] for g in r.get('gearLines') or []][:10], rs=r.get('respawn'))
for r in load('monsters'):
    drops = [[x.get('title'), x.get('qty')] for t in r.get('dropTables') or [] for x in t.get('drops') or []]
    add('monsters', r, lv=r.get('level'), rg=r.get('region'), ty=r.get('type'), cr=r.get('creature'), dr=drops[:12],
        pc=[x.get('subtitle') for x in r.get('places') or [] if x.get('subtitle')][:3])
# a name shared by two entries of one category gets its faction, so each one can be found
count = {}
for e in items:
    count[(e['n'], e['c'])] = count.get((e['n'], e['c']), 0) + 1
for e in items:
    if count[(e['n'], e['c'])] > 1 and e.get('r'):
        e['n'] += ' (' + {'E': 'Elyos', 'A': 'Asmodian'}[e['r']] + ')'


def cached(url):
    return os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + '.img')


def fetch(url):
    path = cached(url)
    if os.path.exists(path):
        return
    err = None
    for _ in range(3):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            Image.open(io.BytesIO(raw)).load()
            open(path, 'wb').write(raw)
            return
        except Exception as e:
            err = e
    print('  failed', url[-60:], str(err)[:60])


os.makedirs(CACHE, exist_ok=True)
urls = list(dict.fromkeys(u for u in pics if u))
with ThreadPoolExecutor(8) as pool:
    list(pool.map(fetch, urls))
have = [u for u in urls if os.path.exists(cached(u))]
place = {u: i for i, u in enumerate(have)}
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT + '/icons')
size = 0
for n in range(-(-len(have) // PER)):
    part = have[n * PER:(n + 1) * PER]
    sheet = Image.new('RGBA', (COLS * CELL, -(-len(part) // COLS) * CELL), (0, 0, 0, 0))
    for i, u in enumerate(part):
        im = Image.open(cached(u)).convert('RGBA')
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        sheet.paste(im, (i % COLS * CELL + (CELL - im.width) // 2, i // COLS * CELL + (CELL - im.height) // 2))
    sheet.save('%s/icons/%d.webp' % (OUT, n), 'WEBP', quality=72, method=6)
    size += os.path.getsize('%s/icons/%d.webp' % (OUT, n))
for e, u in zip(items, pics):
    if u in place:
        e['i'] = place[u]

body = json.dumps({'items': items}, ensure_ascii=False, separators=(',', ':'))
version = hashlib.sha1(body.encode()).hexdigest()[:8]
open(OUT + '/db.js', 'w', encoding='utf8', newline='\n').write('window.ADB=' + body.replace('</', '<\\/') + ';ADB.v="' + version + '";\n')
# the recipes for the Crafting page, with the pictures of everything they use
by_name = {}
for e in items:
    by_name.setdefault(e['n'], e)
rec = {e['n']: [e['c'], e.get('i', -1), e['rc'], e.get('r', ''), e.get('g', ''), e.get('l', ''), e.get('t', '')] for e in items if e.get('rc')}
need = {m for v in rec.values() for r in v[2] for m, q in r[2]}
rec['@pics'] = {m: by_name[m]['i'] for m in sorted(need) if m in by_name and 'i' in by_name[m]}
json.dump(rec, open('recipes.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(len(items), 'entries |', os.path.getsize(OUT + '/db.js') // 1024, 'KB db.js |', len(have), 'of', len(urls), 'pictures,',
      n + 1, 'sheets,', size // 1024, 'KB |', len(rec) - 1, 'recipes,', os.path.getsize('recipes.json') // 1024, 'KB')
print({c: sum(e['c'] == c for e in items) for c in dict.fromkeys(e['c'] for e in items)})
for name in ('Yggdrasil Wood', 'True Dragon Lord Bow', 'Odyle Energy (Bound)'):
    print(name, json.dumps(rec.get(name), ensure_ascii=False)[:300])
