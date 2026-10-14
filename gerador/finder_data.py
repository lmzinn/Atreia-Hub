"""'Onde consigo?' data, from the records wk_all.py downloaded of wikily.gg: finder_data.json =
[[name, kind, [source, ...], picture], ...] for materials, gear, Arcana, wings, consumables and titles.

The pictures go to ../finder_icons/0.webp, 1.webp, …: sheets of PER squares each, COLS a row, CELL pixels a square.
`picture` is the number of the square counted through all the sheets (-1 = no picture). They follow the names in
alphabetical order, so the results of one search mostly sit in one or two sheets, and the page only downloads the
sheets it shows. Needs Pillow. The icons are kept in wikily/icons and not downloaded again."""
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
CACHE, SHEETS, CELL, COLS, PER = 'wikily/icons', '../finder_icons', 40, 20, 200


def load(slug):
    return json.load(open('wikily/ds_%s.json' % slug, encoding='utf8'))


def cached(url):
    return os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + '.img')


def fetch(url):
    path = cached(url)
    if os.path.exists(path):
        return
    for attempt in range(3):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            Image.open(io.BytesIO(raw)).load()  # a real picture, or it is not kept
            open(path, 'wb').write(raw)
            return
        except Exception as e:
            err = e
    print('  failed', url[-60:], str(err)[:60])


rows, seen, urls = [], set(), []
for slug in ('materials', 'weapons', 'armor', 'accessories', 'arcana', 'wings', 'consumables', 'titles'):
    for r in load(slug):
        name = re.sub(r'^(Title|Arcana): ', '', r['name'])
        sources = []
        for s in r.get('sources') or []:
            text = s['title'] + (' — ' + s['subtitle'] if s.get('subtitle') else '')
            if text not in sources:
                sources.append(text)
        if not sources or (name, r['kind']) in seen:
            continue
        seen.add((name, r['kind']))
        more = len(sources) - 6
        rows.append([name, r['kind'], sources[:6] + (['+ %d' % more] if more > 0 else []), r.get('icon') or r.get('head') or ''])
rows.sort(key=lambda x: x[0].lower())

os.makedirs(CACHE, exist_ok=True)
urls = list(dict.fromkeys(r[3] for r in rows if r[3]))
with ThreadPoolExecutor(6) as pool:
    list(pool.map(fetch, urls))
have = [u for u in urls if os.path.exists(cached(u))]
place = {u: i for i, u in enumerate(have)}
shutil.rmtree(SHEETS, ignore_errors=True)
os.makedirs(SHEETS)
size = 0
for n in range(-(-len(have) // PER)):
    part = have[n * PER:(n + 1) * PER]
    sheet = Image.new('RGBA', (COLS * CELL, -(-len(part) // COLS) * CELL), (0, 0, 0, 0))
    for i, u in enumerate(part):
        im = Image.open(cached(u)).convert('RGBA')
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        sheet.paste(im, (i % COLS * CELL + (CELL - im.width) // 2, i // COLS * CELL + (CELL - im.height) // 2))
    sheet.save('%s/%d.webp' % (SHEETS, n), 'WEBP', quality=70, method=6)
    size += os.path.getsize('%s/%d.webp' % (SHEETS, n))
for r in rows:
    r[3] = place.get(r[3], -1)

json.dump(rows, open('finder_data.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(len(rows), 'entries |', os.path.getsize('finder_data.json') // 1024, 'KB |', len(have), 'of', len(urls), 'pictures |',
      sum(r[3] < 0 for r in rows), 'entries without one |', n + 1, 'sheets,', size // 1024, 'KB')
for name in ('Refining Stone', 'True Dragon Lord Dagger', 'Wrathful Ego', 'Golden Glow'):
    print(next((r for r in rows if r[0] == name), name))
