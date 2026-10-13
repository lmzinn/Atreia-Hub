"""Download from wikily.gg what the build editor needs: the datasets (raw, as the API gives them) and the 40
Daevanion board pages. Everything lands in wikily/."""
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'Accept': '*/*'}
CLASSES = ['gladiator', 'templar', 'assassin', 'ranger', 'sorcerer', 'spiritmaster', 'cleric', 'chanter']
BOARDS = ['nezekan', 'zikel', 'vaizel', 'triniel', 'azphel']


def get(path):
    return urllib.request.urlopen(urllib.request.Request('https://wikily.gg' + path, headers=UA), timeout=60).read().decode('utf8', 'replace')


for slug in [a for a in sys.argv[1:] if not a.startswith('--')]:
    out = 'wikily/ds_%s.json' % slug
    if os.path.exists(out):
        continue
    rows, total = [], None
    while total is None or len(rows) < total:
        r = json.loads(get('/api/wikis/aion-2/datasets/%s/list?limit=100&locale=en&offset=%d' % (slug, len(rows))))
        total = r['totalCount']
        if not r['rows']:
            break
        rows += [x['data'] for x in r['rows']]
    json.dump(rows, open(out, 'w', encoding='utf8'), ensure_ascii=False)
    print(slug, len(rows), '/', total)
if '--boards' in sys.argv:
    for c in CLASSES:
        for b in BOARDS:
            out = 'wikily/boards/%s_%s.html' % (c, b)
            if not os.path.exists(out):
                open(out, 'w', encoding='utf8').write(get('/aion-2/daevanion/%s/%s' % (c, b)))
        print('boards', c)
