"""wikily's Enhance cost dataset (wikily/enhance.json, saved by enh_fetch.py) -> enhance_data.json: one entry per
kind of gear, with chance, Kina and Enhance Stones of every level."""
import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf8', errors='replace')
rows = json.load(open('wikily/enhance.json', encoding='utf8'))
OWN = ('Amulet', 'Belt', 'Bracelet', 'Rune')  # gear with a cost table of its own
groups = collections.defaultdict(dict)
for r in rows:
    own = r['gear'] in OWN
    if r['grade'] not in ('Epic', 'Unique', 'Special') and not own:
        continue
    kina = re.search(r'([\d,]+) Kina', r['materials'])
    stones = re.search(r'Enhance Stone x ([\d,]+)', r['materials'])
    # the first level of the Rare amulet and belt costs only the scroll
    kina, stones = (int(m.group(1).replace(',', '')) if m else 0 for m in (kina, stones))
    scroll = re.search(r'(?:^|, )([^,]*Scroll \(Bound\)) x 1', r['materials'])
    key = (r['gear'] if own else '', r['grade'], r['itemLevel'])
    level = groups[key].setdefault(r['levelNum'], {'lv': [int(r['chance'].rstrip('%')), kina, stones], 'ex': set(), 'scroll': set()})
    assert level['lv'] == [int(r['chance'].rstrip('%')), kina, stones], r
    level['ex'].add(r['example'])
    if scroll:
        level['scroll'].add(scroll.group(1))

tiers = []
for (gear, grade, ilvl), levels in sorted(groups.items(), key=lambda kv: (kv[0][0] != '', kv[0][0], kv[0][1] != 'Unique', kv[0][2])):
    assert sorted(levels) == list(range(1, len(levels) + 1)), (gear, grade, ilvl)
    lv = [levels[k]['lv'] for k in sorted(levels)]
    chancy = any(x[0] < 100 for x in lv)
    scrolls = sorted(set().union(*(levels[k]['scroll'] for k in levels)))
    tiers.append({
        'id': '%s%s%d' % (gear[:2].lower() or 'g', grade[0].lower(), ilvl), 'gear': gear, 'grade': grade, 'ilvl': ilvl,
        'ex': ' / '.join(sorted(levels[1]['ex'])), 'lv': lv,
        # Special gear (the rune) loses a level when it fails; Unique gear gains 5% for the next try instead
        'drop': chancy and grade == 'Special', 'pity': 5 if chancy and grade != 'Special' else 0,
        'scroll': ' / '.join(scrolls),
    })
assert len({t['id'] for t in tiers}) == len(tiers)
json.dump({'def': 'gu62', 'tiers': tiers}, open('enhance_data.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
for t in tiers:
    print(t['id'].ljust(7), (t['gear'] or 'gear').ljust(9), t['grade'].ljust(8), str(t['ilvl']).rjust(3), '+%d' % len(t['lv']), 'drop' if t['drop'] else 'pity' if t['pity'] else '    ', t['ex'][:50], '|', t['scroll'][:40])
