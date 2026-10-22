"""The counters of the routine page -> routine_data.json.

The list that shows by default is the daily / weekly list of the Shugo.GG app, as the owner saw it on 13 Oct 2026
(same names, same limits), plus Nightmare and the Shugo Festival keys. The other counters of the global client
(ContentsTicket table, as published by metabot.gg's daily-weekly-checklist guide) are there but hidden until asked for.
What is paid with Odyle Energy (Conquest and Transcendence cubes) is left out: it is one shared pool.

Fields: per 'day' with cap = stacks up; per 'day' without cap = daily limit; per 'week' = weekly limit. capSub / nSub =
the value with the Membership. srv = counted per server, not per character; both = part per server, part per
character. subOnly = exists only with the Membership. keep = never resets (a limit for the whole season). until = gone after that
moment (an event). off = hidden until the reader turns it on. pic = the game item
whose icon stands for the counter (icons_data.py downloads it as 'rt:<id>'). note = what it is, in Portuguese and
English ({c} = the cap or limit in force)."""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf8', errors='replace')
ROWS = [
    # ---- every day
    ('', 'Duty Missions', 'day', 5, {'srv': 1, 'pic': 'Command: Verteron (Bound)'},
     'Missões Wanted: 5 conclusões por dia. Dá para guardar até 20 e atualizar a lista 10 vezes.',
     'Wanted missions: 5 completions a day. Up to 20 can be held and the list refreshed 10 times.'),
    ('', 'Reach Kinah cap', 'day', 1, {'pic': 'Kina Chest: 400,000 Kina'},
     'Limite diário de ganho de 1.000.000 Kinah. No limite entra o debuff Item Drop and Obtain Restriction.',
     'Daily gain limit of 1,000,000 Kinah. At the limit you get the Item Drop and Obtain Restriction debuff.'),
    ('', 'Attendance', 'day', 1, {'srv': 1, 'pic': "Daeva's Campaign Supply Chest (Bound)"},
     'A recompensa do dia de cada quadro de presença.', "The day's reward of each attendance board."),
    ('', 'Abyss Supply: Emergency Requests', 'day', 10, {'pic': 'Latesran Western Root Command (Bound)'},
     'Pedidos de emergência do Abyss entregues hoje.', 'Abyss emergency requests delivered today.'),
    ('', 'Nightmare', 'day', 2, {'cap': 14, 'pic': 'Nightmare Dungeon Challenge Ticket (Bound)'},
     'Chefes solo: 2 tentativas por dia, guarda até {c}. Só gasta quando você vence.',
     'Solo bosses: 2 attempts a day, stores up to {c}. Only spent when you win.'),
    ('', 'Shugo Festival', 'day', 3, {'cap': 12, 'capSub': 21, 'srv': 1, 'pic': 'Shugo Festival Reward Key (Bound)'},
     'Chaves para pegar a recompensa do festival: 3 por dia, guarda até {c}.',
     'Keys to claim the festival reward: 3 a day, stores up to {c}.'),
    # ---- every week
    ('', 'Odyle Energy crafts (Substance Morph)', 'week', 20, {'both': 1, 'pic': 'Odyle Energy (Bound)'},
     'Odyle Energy feita no Substance Morph: 16 por semana por conta e 4 por personagem.',
     'Odyle Energy made at Substance Morph: 16 a week per account and 4 per character.'),
    ('', 'Odyle Energy bought (Wind Breeze Merchant, membership)', 'week', 20, {'both': 1, 'subOnly': 1, 'pic': 'Small Odyle Energy (Bound)'},
     'Odyle Energy comprada no Wind Breeze Merchant: 16 por conta e 4 por personagem. Só com Membership.',
     'Odyle Energy bought at the Wind Breeze Merchant: 16 per account and 4 per character. Membership only.'),
    ('', 'Unknown Fissure (daily dungeon)', 'week', 14, {'srv': 1, 'pic': 'Unknown Fissure Challenge Ticket (Bound)'},
     'A dungeon diária: 14 entradas por semana.', 'The daily dungeon: 14 entries a week.'),
    ('', 'Ascension Trial', 'week', 3, {'pic': 'Ascension Trial Challenge Ticket (Bound)'},
     '3 entradas por semana.', '3 entries a week.'),
    ('', 'Abyss time', 'week', 7, {'unit': 'h', 'nSub': 14, 'pic': 'Lower Abyss Rift Stone'},
     '{c} horas por semana em cada camada do Abyss.', '{c} hours a week in each layer of the Abyss.'),
    ('', 'Abyss Supply: Weekly Requests', 'week', 10, {'pic': 'Latesran Western Root Command: Veteran (Bound)'},
     'Pedidos semanais do Abyss entregues.', 'Abyss weekly requests delivered.'),
    ('', 'Abyss Entry Stone missions', 'week', 2, {},
     'Season Missions > Abyss > Weekly: “Spend 1 Hour in the Abyss” e “Defeat the Boss Guardian Lord Nahma Once”. Cada uma '
     'dá Abyss Entry Stone (desde o patch de 14/out/2026). O Nahma aparece sexta e domingo às 21:00.',
     'Season Missions > Abyss > Weekly: “Spend 1 Hour in the Abyss” and “Defeat the Boss Guardian Lord Nahma Once”. Each one '
     'gives Abyss Entry Stones (since the 14 Oct 2026 patch). Nahma shows up on Friday and Sunday at 21:00.'),
    ('', 'Ariel crystals (Substance Morph)', 'week', 30, {'keep': 1, 'pic': 'Daevanion Crystal: Ariel (Bound)'},
     'Daevanion Crystal: Ariel feitos no Substance Morph (Special > Daevanion): 100 Ariel Fragments do modo Hard de Krao Cave '
     'e Draupnir para cada um, até 30 por personagem. Não zera. O que sobrar de fragmento vira 5 Enhance Stones cada.',
     'Daevanion Crystal: Ariel made at Substance Morph (Special > Daevanion): 100 Ariel Fragments from Krao Cave and Draupnir '
     'on Hard for each one, up to 30 per character. It does not reset. Spare fragments turn into 5 Enhance Stones each.'),
    ('', 'Resurrection Spiritstone for Kinah (event)', 'week', 60, {'srv': 1, 'until': '2026-12-16T06:00:00Z', 'pic': 'Resurrection Spiritstone (Bound)'},
     'Evento Rise to the Challenge: Shop > Wind Breeze Merchants vende Resurrection Spiritstone (Season 1) por Kinah, 30 por '
     '25.000 e mais 30 por 50.000, por servidor e por semana. Some sozinho quando o evento acabar (15/dez).',
     'Rise to the Challenge event: Shop > Wind Breeze Merchants sells Resurrection Spiritstone (Season 1) for Kinah, 30 at '
     '25,000 and 30 more at 50,000, per server and per week. It goes away by itself when the event ends (15 Dec).'),
    ('', 'Duty Commands (bought scrolls)', 'week', 32, {'srv': 1, 'pic': 'Latesran Eastern Root Command: Elite (Bound)'},
     'Pergaminhos de Command comprados: 12 na capital e 5 de cada grau em cada raiz do Lower Abyss.',
     'Command scrolls bought: 12 in the capital and 5 of each grade at each Lower Abyss root.'),
    ('', 'Arena', 'week', 80, {'pic': 'Silver Fragment of Merit (Bound)'},
     'Arena of Solitude (1v1) e Arena of Cooperation (5v5): Victory Reward em 30 vitórias e Participation Reward em 10 partidas, em cada uma.',
     'Arena of Solitude (1v1) and Arena of Cooperation (5v5): Victory Reward at 30 wins and Participation Reward at 10 matches, on each.'),
    ('', 'Battlefield', 'week', 6, {'pic': 'Abyss Points'},
     'Arena of Tactics: Victory Reward em 3 vitórias e Participation Reward em 3 partidas.',
     'Arena of Tactics: Victory Reward at 3 wins and Participation Reward at 3 matches.'),
    ('', 'Daeva Pass EXP', 'week', 1, {'pic': 'Daeva Pass Shop Coin'},
     'O limite semanal de EXP de cada passe. Marque quando bater.', "Each pass's weekly EXP limit. Tick it when you reach it."),
    # ---- hidden until asked for
    ('Other dailies', 'Abyss Corridors', 'day', 1, {'off': 1},
     'O tempo (2:10) em cada corredor que os artefatos da sua facção abrem, até o próximo Artifact Siege.',
     "The time (2:10) in each corridor your faction's artifacts open, until the next Artifact Siege."),
    ('Other dailies', 'Dimensional Invasion', 'day', 1, {'cap': 7, 'srv': 1, 'off': 1, 'pic': 'Dimensional Merit Chest: Unique (Bound)'},
     'Chave de recompensa do evento de defesa que acontece toda hora, aos :30. 1 por dia, guarda até {c}.',
     'Reward key of the defence event that runs every hour at :30. 1 a day, stores up to {c}.'),
    ('Other weeklies', 'Subjugation', 'week', 3, {'off': 1},
     '3 tickets por semana para as dungeons de 4 jogadores.', '3 tickets a week for the 4-player dungeons.'),
    ('Other weeklies', 'Silent Graveyard', 'week', 7, {'unit': 'h', 'off': 1},
     'Growth dungeon: 7 horas por semana, contadas só lá dentro.', 'Growth dungeon: 7 hours a week, counted only while inside.'),
    ('Other weeklies', 'Fafnite Amphitheater', 'week', 7, {'unit': 'h', 'off': 1},
     'Growth dungeon: 7 horas por semana, contadas só lá dentro.', 'Growth dungeon: 7 hours a week, counted only while inside.'),
    ('Other weeklies', 'Remaining Unobtained Cube Count', 'week', 10, {'srv': 1, 'off': 1, 'pic': 'Key: Hidden Cube (Bound)'},
     'Quantas vezes dá para sair de Conquest ou Transcendence sem pegar o cubo. Em 0, não entra mais até quarta.',
     'How many times you can leave Conquest or Transcendence without taking the cube. At 0 you cannot enter until Wednesday.'),
    ('Other weeklies', 'Conquest final bosses', 'week', 35, {'off': 1},
     'Teto de chefes finais de Conquest na semana.', 'Cap of Conquest final bosses in the week.'),
    ('Other weeklies', 'Transcendence final bosses', 'week', 28, {'off': 1},
     'Teto de chefes finais de Transcendence na semana.', 'Cap of Transcendence final bosses in the week.'),
] + [('Sanctuary', name, 'week', n, {'off': 1},
      ('Raid: %d tentativas por semana.' if 'final' not in name else 'Chefe final do raid: %d por semana.') % n + ' Em 13/out/2026 não estava aberto no Global.',
      ('Raid: %d attempts a week.' if 'final' not in name else 'Final boss of the raid: %d a week.') % n + ' On 13 Oct 2026 it was not open on Global.')
     for name, n in (('Abyssal Forge', 4), ('Abyssal Forge final boss', 1), ('Chalice of Muspel', 4), ('Chalice of Muspel final boss', 2),
                     ('Corroded Decontamination Facility', 4), ('Corroded Decontamination Facility final boss', 2))
] + [('Exploration', name + ' (Exploration)', 'week', 7, {'off': 1},
      '7 recompensas de Exploration por semana nesta dungeon.', '7 Exploration rewards a week in this dungeon.') for name in (
    'Krao Cave', 'Urugugu Canyon', 'Fire Temple', 'Draupnir', 'Vakron Sky Island', 'Ferocious Horn Den', 'Azure Breath Island',
    'Cradle of Nihility', "Dying Dramata's Nest", 'Hall of Illusion')]


def icon(name):
    """The drawn icon of a card that has no game picture (see RICO in the page script)."""
    for word, key in (('final boss', 'boss'), ('Abyss', 'layers'), ('Subjugation', 'swords'), ('Cube', 'cube'), ('Graveyard', 'growth'),
                      ('Amphitheater', 'growth'), ('Chalice', 'raid'), ('Corroded', 'raid'), ('Pass', 'pass'), ('Duty', 'target'),
                      ('Dimensional', 'portal')):
        if word in name:
            return key
    return 'dungeon'


# the names in Portuguese, for the page in Portuguese (the English name stays as the id and on the English page;
# names of places and dungeons stay as in the game)
PT = {
    'Duty Missions': 'Missões de Dever', 'Reach Kinah cap': 'Limite diário de Kinah', 'Attendance': 'Presença diária',
    'Abyss Supply: Emergency Requests': 'Abyss: pedidos de emergência', 'Nightmare': 'Nightmare', 'Shugo Festival': 'Festival Shugo',
    'Odyle Energy crafts (Substance Morph)': 'Odyle Energy fabricada (Substance Morph)',
    'Odyle Energy bought (Wind Breeze Merchant, membership)': 'Odyle Energy comprada (Membership)',
    'Unknown Fissure (daily dungeon)': 'Unknown Fissure (dungeon diária)', 'Ascension Trial': 'Ascension Trial',
    'Abyss time': 'Tempo no Abyss', 'Abyss Supply: Weekly Requests': 'Abyss: pedidos semanais',
    'Abyss Entry Stone missions': 'Abyss: missões da Entry Stone', 'Ariel crystals (Substance Morph)': 'Ariel: cristais convertidos',
    'Resurrection Spiritstone for Kinah (event)': 'Resurrection Spiritstone por Kinah (evento)', 'Duty Commands (bought scrolls)': 'Pergaminhos de comando comprados', 'Arena': 'Arena', 'Battlefield': 'Campo de batalha',
    'Daeva Pass EXP': 'EXP do Daeva Pass', 'Abyss Corridors': 'Corredores do Abyss', 'Dimensional Invasion': 'Invasão Dimensional',
    'Subjugation': 'Subjugação', 'Silent Graveyard': 'Silent Graveyard', 'Fafnite Amphitheater': 'Fafnite Amphitheater',
    'Remaining Unobtained Cube Count': 'Cubos ainda não pegos', 'Conquest final bosses': 'Chefes finais do Conquest',
    'Transcendence final bosses': 'Chefes finais do Transcendence',
}


def pt_name(name):
    if name in PT:
        return PT[name]
    if name.endswith(' final boss'):
        return name[:-len(' final boss')] + ': chefe final'
    if name.endswith(' (Exploration)'):
        return name[:-len(' (Exploration)')] + ' (Exploração)'
    return name


rows = [dict({'id': re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-'), 'group': group, 'name': name, 'pt': pt_name(name), 'per': per, 'n': n, 'ico': icon(name),
              'note': [pt, en]}, **more) for group, name, per, n, more, pt, en in ROWS]
assert len({r['id'] for r in rows}) == len(rows)
json.dump(rows, open('routine_data.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
shown = [r for r in rows if not r.get('off')]
print(len(rows), 'counters |', sum(r['per'] == 'day' for r in shown), 'daily and', sum(r['per'] == 'week' for r in shown), 'weekly shown |',
      len(rows) - len(shown), 'hidden by default |', sum('pic' in r for r in rows), 'with an item icon')
