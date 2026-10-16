"""Read the Enhance bonus of gear from the official armory into enh_raw.json (kept between runs; enh_bonus.py turns it
into the editor's table). The armory only answers for a piece a character is wearing, so this walks characters:
  py -I enh_fetch_bonus.py search la ka,mi,ra,lo 1500   characters from the name search (words, region, how many)
  py -I enh_fetch_bonus.py list names.txt               "name,serverId,region;..." (e.g. copied from shugo.gg's ranking)
For each piece whose group, grade and item level is not in the file yet, every Enhance level is read. The pieces are
known by name and grade from wikily's datasets (wikily/ds_*.json, see wk_all.py)."""
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
OUT = 'enh_raw.json'
KINDS = {'Weapon', 'Guard', 'Top', 'Legs', 'Helm', 'Pauldrons', 'Gloves', 'Shoes', 'Cloak', 'Necklace', 'Earrings', 'Ring', 'Bracelet', 'Amulet', 'Belt', 'Rune'}
raw = json.load(open(OUT, encoding='utf8')) if os.path.exists(OUT) else {}
lock, pending = threading.Lock(), set()

names = {}
for ds in ('weapons', 'armor', 'accessories'):
    for r in json.load(open('wikily/ds_%s.json' % ds, encoding='utf8')):
        kind = ('Guard' if r['type'] == 'Guard' else 'Weapon') if ds == 'weapons' else r['type']
        names.setdefault((r['name'].replace(' (%s)' % r['grade'], ''), r['grade']), '%s|%s|%s' % (kind, r['grade'], r.get('itemLevel')))


def get(url):
    for k in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception as x:
            if '404' in str(x):
                return None
            time.sleep(1.5 * (k + 1))
    return None


def probe(key, e, q):
    url = 'https://aion2.plaync.com/api/character/equipment/item?id=%d&slotPos=%d&%s&enchantLevel=' % (e['id'], e['slotPos'], q)
    first = get(url + '1')
    top = first and first['maxEnchantLevel']
    with ThreadPoolExecutor(6) as ex:
        ds = list(ex.map(lambda L: get(url + str(L)), range(1, (top or 0) + 1)))
    with lock:
        pending.discard(key)
        if not top or not all(ds) or [d['enchantLevel'] for d in ds] != list(range(1, top + 1)):
            return
        raw[key] = {'name': first['name'], 'base': {s['name']: s['value'] for s in first['mainStats']},
                    'extra': [{s['name']: s.get('extra', '0') for s in d['mainStats']} for d in ds]}
        json.dump(raw, open(OUT, 'w', encoding='utf8', newline='\n'), ensure_ascii=False, indent=0)
        print(key.ljust(26), first['name'][:28].ljust(29), '|', ' '.join(','.join(r.values()) for r in raw[key]['extra']), flush=True)


work = ThreadPoolExecutor(4)


def walk(c):
    q = 'characterId=%s&serverId=%s&region=%s&lang=en-US' % (c['characterId'], c['serverId'], c['region'])
    eq = get('https://aion2.plaync.com/api/character/equipment?' + q)
    for e in (eq or {}).get('equipment', {}).get('equipmentList', []):
        key = names.get((e['name'], {'Legend': 'Epic'}.get(e['grade'], e['grade'])))
        if not key or key.split('|')[0] not in KINDS:
            continue
        with lock:
            if key in raw or key in pending:
                continue
            pending.add(key)
        work.submit(probe, key, e, q)


search = 'https://api-search.plaync.com/aion2global/search/v2/character?keyword=%s&page=%d&size=40&region=%s&localeInfo=en-US'
seen = set()
if sys.argv[1] == 'search':
    region, words, most = sys.argv[2], sys.argv[3].split(','), int(sys.argv[4])
    for w in words:
        for page in range(1, 8):
            s = get(search % (urllib.parse.quote(w), page, region))
            for c in (s or {}).get('list', []):
                if c['characterId'] not in seen and c['level'] >= 8 and len(seen) < most:
                    seen.add(c['characterId']); walk(c)
            if not s or not s['list']:
                break
else:
    for name, sid, region in (t.split(',') for t in open(sys.argv[2], encoding='utf8').read().strip().split(';')):
        s = get(search % (urllib.parse.quote(name), 1, region))
        for c in (s or {}).get('list', []):
            if str(c['serverId']) == sid and c['name'].replace('<strong>', '').replace('</strong>', '') == name and c['characterId'] not in seen:
                seen.add(c['characterId']); walk(c)
work.shutdown(wait=True)
print(len(raw), 'pieces read,', len(seen), 'characters')
