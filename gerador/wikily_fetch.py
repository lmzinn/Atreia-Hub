"""Download the crafting recipe pages of wikily.gg and save every recipe as one line: skill|page|name|text."""
import html
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}


def get(path):
    req = urllib.request.Request('https://wikily.gg' + path, headers=UA)
    return urllib.request.urlopen(req, timeout=40).read().decode('utf8', 'replace')


def text(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


rows = []
for skill in sys.argv[1:]:
    first = get('/aion-2/crafting/' + skill)
    subs = list(dict.fromkeys(re.findall(r'href="(/aion-2/crafting/%s/[^"#?]+)"' % skill, first)))
    for url, page in [('/aion-2/crafting/' + skill, first)] + [(s, None) for s in subs]:
        page = page or get(url)
        found = re.findall(r'<a class="ext-gwe-card-list-title[^"]*"[^>]*>(.*?)</a><span class="ext-gwe-card-list-subtitle">(.*?)</span></span>', page, re.S)
        print(url, len(found))
        rows += [(skill, url.split('/')[-1], text(n), text(t)) for n, t in found]
open('wikily/recipes.txt', 'a', encoding='utf8', newline='\n').write(''.join('|'.join(r) + '\n' for r in rows))
