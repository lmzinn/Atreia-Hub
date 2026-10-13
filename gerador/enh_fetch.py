"""Download wikily's gear Enhance cost dataset (the table behind /aion-2/enhancement/gear) -> wikily/enhance.json"""
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
      'Accept': 'application/json', 'Referer': 'https://wikily.gg/aion-2/enhancement/gear'}
base = ('https://wikily.gg/api/wikis/aion-2/datasets/%s/list?fields=%s&locale=en&filters=%s&sortField=itemLevel&sortDir=asc&sortNumeric=1'
        % (sys.argv[1], urllib.parse.quote(sys.argv[2]), urllib.parse.quote(json.dumps([{'fieldRef': 'listed', 'value': 'yes', 'operator': 'equals'}]))))
rows, total = [], None
while total is None or len(rows) < total:
    r = json.load(urllib.request.urlopen(urllib.request.Request(base + '&limit=100&offset=%d' % len(rows), headers=UA), timeout=40))
    total = r['totalCount']
    if not r['rows']:
        break
    rows += [x['data'] for x in r['rows']]
    print(len(rows), '/', total)
json.dump(rows, open(sys.argv[3], 'w', encoding='utf8'), ensure_ascii=False)
