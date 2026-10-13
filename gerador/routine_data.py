"""wikily's Homework Checklist (wikily/p_homework.txt, saved by wikily_text.py) -> routine_data.json"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf8', errors='replace')
text = open('wikily/p_homework.txt', encoding='utf8').read()
text = text[text.index('This week'):text.index('Daily limits clear')]
text = re.sub(r'−\d+/\d+\+', '\n', text)          # the page's own counters
groups = ['Dungeons', 'Final bosses', 'Sanctuary', 'Abyss and growth time', 'Other']
rows, group = [], None
flat = re.sub(r'\s*\n\s*', '\n', text).split('\n')
buf = ''
for line in flat[1:]:
    line = line.strip()
    if not line:
        continue
    if line in groups:
        group = line
        buf = ''
        continue
    buf = (buf + ' ' + line).strip()
    m = re.match(r'^(.*?)\s*(\d+) (h )?a (day|week)(?: · up to (\d+))?$', buf)
    if m:
        name, n, hours, per, cap = m.groups()
        if name.endswith('Draft Level'):  # 'Level 1' + '7 h' arrive glued as 'Level 17 h'
            name, n = name + ' ' + n[0], n[1:]
        row = {'id': re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-'), 'group': group, 'name': name, 'per': per, 'n': int(n)}
        if hours:
            row['unit'] = 'h'
        if cap:
            row['cap'] = int(cap)
        rows.append(row)
        buf = ''
assert not buf, buf
ids = [r['id'] for r in rows]
assert len(ids) == len(set(ids)), ids
json.dump(rows, open('routine_data.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(rows), 'activities;', sum(r['per'] == 'day' for r in rows), 'daily,', sum(r['per'] == 'week' for r in rows), 'weekly')
for r in rows:
    print(r['group'][:10].ljust(10), r['name'].ljust(46), r['n'], r.get('unit', ''), 'a', r['per'], 'cap', r.get('cap', ''))
