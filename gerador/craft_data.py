"""Turn wikily/recipes.txt (see wikily_fetch.py) into craft_data.json: the Elyos crafting line of every piece an
Assassin wears, from the Orichalcum base up to the Splendent Wise Dragon Lord."""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf8', errors='replace')
PROF = {'blacksmithing': 'Blacksmithing', 'armorsmithing': 'Armorsmithing', 'handicrafting': 'Handicrafting'}
# piece -> (profession, name of the Orichalcum-tier item)
PIECES = [('Dagger', 'blacksmithing', 'Orichalcum Dagger'), ('Guard', 'blacksmithing', 'Orichalcum Guard'),
          ('Breastplate', 'armorsmithing', 'Orichalcum Breastplate'), ('Greaves', 'armorsmithing', 'Orichalcum Greaves'),
          ('Helm', 'armorsmithing', 'Orichalcum Helm'), ('Gloves', 'armorsmithing', 'Orichalcum Gloves'),
          ('Pauldrons', 'armorsmithing', 'Orichalcum Pauldrons'), ('Boots', 'armorsmithing', 'Orichalcum Boots'),
          ('Cloak', 'armorsmithing', 'Orichalcum Cloak'), ('Ring', 'handicrafting', 'Sapphire Ring'),
          ('Earrings', 'handicrafting', 'Diamond Earrings'), ('Necklace', 'handicrafting', 'Ruby Necklace')]

recipes = {}
for line in open('wikily/recipes.txt', encoding='utf8'):
    skill, page, name, text = line.rstrip('\n').split('|', 3)
    if 'asmodians' in page or text.startswith('Asmodians.') or 'Materials:' not in text:
        continue
    lv = re.search(r'Lv\. (\d+)\.', text)
    mats = re.search(r'Materials: (.*?)\.(?: |$)', text).group(1)
    mats = [(m.rsplit(' x ', 1)[0], int(m.rsplit(' x ', 1)[1])) for m in mats.split(', ')]
    gear = re.search(r'Gear Transfer Material: (.*?)\.', text)
    combo = re.search(r'Crafting Combo result: (.*?) x 1', text)
    key = (skill, name)
    if key in recipes and lv and recipes[key]['lv'] and int(lv.group(1)) > recipes[key]['lv']:
        continue  # the bulk version of a material (Lv. 25: x 20 at once)
    recipes[key] = {'lv': int(lv.group(1)) if lv else None, 'mats': mats, 'gear': gear.group(1) if gear else None,
                    'combo': combo.group(1) if combo else None}

# materials that are themselves crafted, from things gathered or bought
sub = {}
for (skill, name), r in recipes.items():
    if not r['combo'] and not r['gear'] and re.search(r'Ingot|Leather|Decoration|Balaur (Horn|Scale)', name):
        sub[name] = r['mats']

pieces = []
for piece, skill, base in PIECES:
    kind = base  # e.g. "Orichalcum Dagger"
    names = [('base', base), ('expert', "Expert's " + kind), ('artisan', "Artisan's " + kind),
             ('true', 'True Dragon Lord ' + piece), ('trueS', 'Splendent True Dragon Lord ' + piece),
             ('white', 'White Dragon Lord ' + piece), ('whiteS', 'Splendent White Dragon Lord ' + piece),
             ('wise', 'Wise Dragon Lord ' + piece), ('wiseS', 'Splendent Wise Dragon Lord ' + piece)]
    steps = []
    for tier, name in names:
        r = recipes[(skill, name)]
        splendent = lambda n: n.startswith(('Splendent', "Expert's Splendent", "Artisan's Splendent"))
        steps.append({'tier': tier, 'name': name, 'lv': r['lv'], 'combo': r['combo'], 'gear': r['gear'],
                      'chain': next((n for n, q in r['mats'] if splendent(n)), None),
                      'mats': [[n, q] for n, q in r['mats'] if not splendent(n)]})
        assert all(q == 1 for n, q in r['mats'] if splendent(n)), name
    assert [s['chain'] for s in steps][1:4] == [s['combo'] for s in steps][0:3], piece
    pieces.append({'piece': piece, 'prof': PROF[skill], 'steps': steps})

used = {n for p in pieces for s in p['steps'] for n, q in s['mats']}
data = {'pieces': pieces, 'sub': {n: m for n, m in sub.items() if n in used}}
json.dump(data, open('craft_data.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(pieces), 'pieces;', 'crafted materials:', sorted(data['sub']))
for s in pieces[0]['steps']:
    print(s['tier'], '|', s['name'], '| lv', s['lv'], '| chain', s['chain'], '| gear', s['gear'], '| combo', s['combo'], '|', s['mats'])
print(sorted(used))
