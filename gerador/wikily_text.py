"""Save the readable text of a wikily.gg page: wikily_text.py <path> <out.txt>"""
import html
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
page = urllib.request.urlopen(urllib.request.Request('https://wikily.gg/' + sys.argv[1].lstrip('/'), headers=UA), timeout=40).read().decode('utf8', 'replace')
m = re.search(r'<main.*?</main>', page, re.S)
body = m.group(0) if m else page
body = re.sub(r'<(script|style|svg)\b.*?</\1>', '', body, flags=re.S)
body = re.sub(r'</(td|th)>', ' | ', body)
body = re.sub(r'<(br|/p|/div|/tr|/li|/h\d|/section|/a)[^>]*>', '\n', body)
text = html.unescape(re.sub(r'<[^>]+>', '', body))
text = re.sub(r'[ \t]+', ' ', text)
text = re.sub(r'\n\s*\n+', '\n', text).strip()
open(sys.argv[2], 'w', encoding='utf8', newline='\n').write(text + '\n')
print(len(text), 'chars;', 'links:', sorted(set(re.findall(r'href="(%s/[^"#?]+)"' % re.escape('/' + sys.argv[1].lstrip('/')), page))))
