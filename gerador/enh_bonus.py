"""Enhance bonus of the gear in the build editor -> enh_bonus.json, also written into builder_data.json as 'enh'.

Where it comes from: the official armory (aion2.plaync.com/api/character/equipment/item?...&enchantLevel=N) gives, for
the gear a character wears, the bonus of each main stat at any Enhance level (mainStats[].extra). enh_fetch_bonus.py
reads it from many characters into enh_raw.json. What the data shows:
- the bonus depends only on the group of the piece, its grade and item level, not on its own stats: weapons and guards
  are one group, all armor pieces another, necklace / earrings / ring / bracelet another; amulet, belt and rune apart;
- the bonus at the top level (T) is spread over the levels in whole steps, the bigger steps last:
  level L gives b*L + max(0, L - (n - r)), with T = b*n + r and n the top level (checked on every level read).
So each entry keeps only T for each stat. A group, grade and item level never read is estimated from the nearest ones
of the same group and grade (the bonus grows in step with the item level) and listed in 'est'. The rune's bonus
does not follow the rule, so it keeps every level as read."""
import json
import sys

sys.stdout.reconfigure(encoding='utf8', errors='replace')
GROUP = {'Weapon': 'W', 'Guard': 'W', 'Necklace': 'X', 'Earrings': 'X', 'Ring': 'X', 'Bracelet': 'X', 'Amulet': 'Am', 'Belt': 'Be', 'Rune': 'Ru'}


def group(kind):
    return GROUP.get(kind, 'A')


def num(text):
    return float(str(text).replace(',', '').rstrip('%') or 0)


def spread(T, n, L):
    b, r = divmod(T, n)
    return b * L + max(0, L - (n - r))


raw = json.load(open('enh_raw.json', encoding='utf8'))
known, levels = {}, {}
for key, v in raw.items():
    kind, grade, ilvl = key.split('|')
    k = '%s|%s|%s' % (group(kind), grade, ilvl)
    n = len(v['extra'])
    if group(kind) == 'Ru':
        levels[k] = {s: [r[s] for r in v['extra']] for s in v['extra'][0] if any(num(r[s]) for r in v['extra'])}
        continue
    tops = {}
    for s in v['extra'][0]:
        vals = [num(r[s]) for r in v['extra']]
        if not vals[-1]:
            continue
        assert all(x == int(x) for x in vals) and [spread(int(vals[-1]), n, L) for L in range(1, n + 1)] == vals, (key, s, vals)
        tops[s] = int(vals[-1])
    old = known.get(k)
    assert old is None or old == tops, (k, old, tops)  # every piece of a group gives the same
    known[k] = tops

# what the editor needs
B = json.load(open('builder_data.json', encoding='utf8'))
need = set()
for set_ in ('weapons', 'armor', 'accessories'):
    for x in B[set_]:
        if x[4] > 0:
            kind = ('Guard' if x[1] == 'Guard' else 'Weapon') if set_ == 'weapons' else x[1]
            need.add('%s|%s|%d' % (group(kind), B['grades'][x[2]], x[3]))

est = {}
for k in sorted(need - set(known) - set(levels)):
    g, grade, ilvl = k.split('|')
    ilvl = int(ilvl)
    same = sorted((int(q.split('|')[2]), t) for q, t in known.items() if q.startswith('%s|%s|' % (g, grade)))
    if not same:
        print('no data at all for', k)
        continue
    below = [p for p in same if p[0] < ilvl]
    above = [p for p in same if p[0] > ilvl]
    out = {}
    for s in set().union(*(t for _, t in same)):
        if below and above and s in below[-1][1] and s in above[0][1]:
            (i0, t0), (i1, t1) = below[-1], above[0]
            out[s] = round(t0[s] + (t1[s] - t0[s]) * (ilvl - i0) / (i1 - i0))
        else:
            near = min((p for p in same if s in p[1]), key=lambda p: abs(p[0] - ilvl))
            out[s] = round(near[1][s] * ilvl / near[0])
    est[k] = out

enh = {'top': {**known, **est}, 'lv': levels, 'est': sorted(est)}
json.dump(enh, open('enh_bonus.json', 'w', encoding='utf8', newline='\n'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
B['enh'] = enh
json.dump(B, open('builder_data.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('read', len(known) + len(levels), '| needed', len(need), '| estimated', len(est), sorted(est))
print('still missing', sorted(need - set(known) - set(levels) - set(est)))
