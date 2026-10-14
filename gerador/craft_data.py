"""The crafting lines of the calculator -> craft_data.json, from the gear and material records wk_all.py downloaded
of wikily.gg: every weapon, the guard, the seven armour pieces and ring, earrings and necklace, for both factions,
from the base piece up to the Splendent version of the last Dragon Lord.

The tiers have the same keys for both factions (true / white / wise are the first, second and third Dragon Lord:
True, White, Wise for the Elyos and Star, Dark, Ebony for the Asmodians), so the page script treats them alike."""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf8', errors='replace')
LINES = {'Elyos': ('True', 'White', 'Wise'), 'Asmodians': ('Star', 'Dark', 'Ebony')}
CLASS = {'Greatsword': 'Gladiator', 'Longsword': 'Templar', 'Dagger': 'Assassin', 'Bow': 'Ranger', 'Spellbook': 'Sorcerer',
         'Orb': 'Spiritmaster', 'Mace': 'Cleric', 'Staff': 'Chanter'}
# piece -> group of the picker; the weapons carry the class that wields them
PIECES = [(w, 'weapon') for w in CLASS] + [('Guard', 'guard')] + [(a, 'armor') for a in (
    'Helm', 'Pauldrons', 'Breastplate', 'Gloves', 'Greaves', 'Boots', 'Cloak')] + [(a, 'acc') for a in ('Necklace', 'Earrings', 'Ring')]


def load(slug):
    return json.load(open('wikily/ds_%s.json' % slug, encoding='utf8'))


gear = {}
for r in load('weapons') + load('armor') + load('accessories'):
    gear.setdefault(r['name'], []).append(r)
materials = {r['name']: r for r in load('materials')}


def record(name, race):
    found = [r for r in gear[name] if r['race'] in (race, 'Elyos and Asmodians')]
    assert len(found) == 1, (name, race, len(found))
    return found[0]


def recipe(r):
    """(profession, level or None, [[material, quantity]], piece that is transformed or None) of the first recipe that
    is not the Crafting Combo."""
    for k in ('recipe1', 'recipe2'):
        label = r.get(k + 'Label') or ''
        if not r.get(k) or 'Crafting Combo' in label:
            continue
        prof = re.search(r'(Blacksmithing|Armorsmithing|Handicrafting|Alchemy)', label).group(1)
        lv = re.search(r'Lv\. (\d+)', label)
        mats, turned = [], None
        for x in r[k]:
            q = int(re.match(r'x (\d+)', x['subtitle']).group(1))
            if 'Gear Transfer Material' in x['subtitle']:
                assert q == 1 and not turned
                turned = x['title']
            else:
                mats.append([x['title'], q])
        return prof, int(lv.group(1)) if lv else None, mats, turned
    raise ValueError(r['name'])


splendent = lambda n: n.startswith(('Splendent', "Expert's Splendent", "Artisan's Splendent"))
pieces = []
for race, (first, second, third) in LINES.items():
    for piece, group in PIECES:
        top = record('%s Dragon Lord %s' % (first, piece), race)
        base = next(n for n, q in recipe(top)[2] if n.startswith("Artisan's Splendent "))[len("Artisan's Splendent "):]
        names = [('base', base), ('expert', "Expert's " + base), ('artisan', "Artisan's " + base)]
        for tier, line in (('true', first), ('white', second), ('wise', third)):
            names += [(tier, '%s Dragon Lord %s' % (line, piece)), (tier + 'S', 'Splendent %s Dragon Lord %s' % (line, piece))]
        steps, profs = [], set()
        for tier, name in names:
            r = record(name, race)
            prof, lv, mats, turned = recipe(r)
            profs.add(prof)
            combo = next((x['title'] for x in r.get('craftingResults') or [] if 'Combo produces' in x.get('subtitle', '')), None)
            assert all(q == 1 for n, q in mats if splendent(n)), name
            steps.append({'tier': tier, 'name': name, 'lv': lv, 'combo': combo, 'gear': turned,
                          'chain': next((n for n, q in mats if splendent(n)), None),
                          'mats': [[n, q] for n, q in mats if not splendent(n)], 'ilvl': int(r['itemLevel'])})
        assert len(profs) == 1, (piece, profs)
        assert [s['chain'] for s in steps][1:4] == [s['combo'] for s in steps][0:3], piece
        assert [s['gear'] for s in steps][4:] == [names[i][1] for i in (3, 4, 5, 6, 7)], (piece, [s['gear'] for s in steps])
        pieces.append({'piece': piece, 'race': race, 'group': group, 'cls': CLASS.get(piece, ''), 'prof': profs.pop(), 'steps': steps})

# materials that are themselves crafted, opened down to what is gathered, dropped or bought
used = {n for p in pieces for s in p['steps'] for n, q in s['mats']}


def crafted(name):
    r = materials.get(name)
    if not r or not re.search(r'Ingot|Leather|Decoration|Wood|Crystal|Balaur (Horn|Scale)', name):
        return None
    for k in ('recipe1', 'recipe2', 'recipe3', 'recipe4'):
        label = r.get(k + 'Label') or ''
        if r.get(k) and re.search(r'Lv\. \d+, Produces x 1$', label):
            return [[x['title'], int(re.match(r'x (\d+)', x['subtitle']).group(1))] for x in r[k]]
    return None


sub = {n: crafted(n) for n in sorted(used) if crafted(n)}
assert not any(crafted(m) for mats in sub.values() for m, q in mats)
raw = sorted({m for n in used for m, q in sub.get(n, [[n, 1]])})
# where each raw material comes from (the page script spells the keys out), and what the Merchants charge for it
SOURCE = {'Raw Leather': 'mob', 'Spiritstone': 'mob', "Balaur's Essence": 'essence', 'Refining Stone': 'stone',
          "Expert's Refining Stone": 'stone', "Artisan's Refining Stone": 'stone', "Artisan's Ultimate Refining Stone": 'exped',
          'Wrathful Mind': 'exped', 'Wrathful Will': 'exped', 'Wrathful Ego': 'exped'}
src, npc = {}, {}
for n in raw:
    shop = next((s['subtitle'] for s in materials[n].get('sources') or [] if s['title'] == 'Shop'), None)
    if shop:
        src[n], npc[n] = 'npc', int(re.search(r'([\d,]+) Kina', shop).group(1).replace(',', ''))
    else:
        src[n] = SOURCE.get(n) or next(key for word, key in (('Orichalcum Ore', 'ore'), ('Odyle', 'odyle'), ('Gemstone', 'gem'), (' Log', 'log')) if word in n)
data = {'pieces': pieces, 'sub': sub, 'src': src, 'npc': npc}
json.dump(data, open('craft_data.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(len(pieces), 'pieces |', len(sub), 'crafted materials |', len(raw), 'raw materials')
for p in pieces:
    if p['piece'] in ('Dagger', 'Bow', 'Spellbook', 'Breastplate', 'Ring'):
        print(p['race'], p['piece'], p['prof'], [(s['name'], s['lv'], s['ilvl']) for s in p['steps']][:4])
print('crafted:', json.dumps(sub, ensure_ascii=False))
print('bought:', npc)
print('sources:', {k: [n for n in raw if src[n] == k] for k in sorted(set(src.values())) if k != 'npc'})
