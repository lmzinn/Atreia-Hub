"""The 'Crafting' part of the guide: the calculator (drawn by the page script into #calc), the Dragon Lord line,
where to put the Essence Extraction points and where each material comes from.

Unlike the other parts it does not come from a DOCX: the text lives here, in Portuguese and English.
Sources, read on 13 Oct 2026: the recipe and gathering pages of wikily.gg (craft_data.json is made from them by
craft_data.py) and Screamheart's "Aion 2 Content Guide" spreadsheet (Crafting Tips / Crafting Calculator tabs).
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'craft_data.json')
ENH = os.path.join(HERE, 'enhance_data.json')  # made by enh_data.py
SHEET = 'https://docs.google.com/spreadsheets/d/1bNxC1wd0S_ILGYAyWnO0aTo_G_AOrjkv7bTcOj_NRz8/'
WIKILY = 'https://wikily.gg/aion-2/'

# where the raw materials come from (keys are spelled out by the page script) and what the Merchants charge
SOURCE = {'Raw Leather': 'mob', "Balaur's Essence": 'essence', 'Refining Stone': 'stone', "Expert's Refining Stone": 'stone',
          "Artisan's Refining Stone": 'stone', "Artisan's Ultimate Refining Stone": 'exped', 'Wrathful Mind': 'exped',
          'Wrathful Will': 'exped', 'Wrathful Ego': 'exped'}
NPC = {'Orichalcum Solvent (Bound)': 400, 'Abrasive (Bound)': 400, 'Zircon Hammer (Bound)': 4650, 'Lazuli Hammer (Bound)': 5600,
       'Moonstone Hammer (Bound)': 6550, 'Lesser Dragon Leather Softener (Bound)': 4650,
       'Intermediate Dragon Leather Softener (Bound)': 5600, 'Superior Dragon Leather Softener (Bound)': 6550,
       'Lesser Dragon Scale Hardener (Bound)': 4650, 'Intermediate Dragon Scale Hardener (Bound)': 5600,
       'Superior Dragon Scale Hardener (Bound)': 6550}


def source(name):
    if name in NPC:
        return 'npc'
    if name in SOURCE:
        return SOURCE[name]
    return 'ore' if 'Orichalcum Ore' in name else 'odyle' if 'Odyle' in name else 'gem' if 'Gemstone' in name else ''


def calc_data():
    data = json.load(open(DATA, encoding='utf8'))
    raw = {n for p in data['pieces'] for s in p['steps'] for m, q in s['mats'] for n, q2 in data['sub'].get(m, [[m, 1]])}
    assert all(source(n) for n in raw), [n for n in raw if not source(n)]
    data['src'] = {n: source(n) for n in sorted(raw)}
    data['npc'] = {n: NPC[n] for n in sorted(raw) if n in NPC}
    if os.path.exists(ENH):
        data['enh'] = json.load(open(ENH, encoding='utf8'))
    return data


def craft_part(strings, english):
    """Same shape as guide_convert.convert(); every text goes to `strings` and its English version to `english`."""
    def mark(pt, en):
        strings.append(pt)
        english[pt] = en
        return f' data-t="{len(strings) - 1}"'

    def el(tag, pt, en, cls=''):
        c = f' class="{cls}"' if cls else ''
        return f'<{tag}{c}{mark(pt, en)}>{pt}</{tag}>'

    def p(pt, en, cls=''):
        return el('p', pt, en, cls)

    def h3(pt, en):
        return el('h3', pt, en)

    def ul(*items):
        return '<ul>' + ''.join(el('li', pt, en) for pt, en in items) + '</ul>'

    def table(head, rows):
        out = ['<div class="tw"><table class="data"><tr>' + ''.join(el('th', f'<b>{a}</b>', f'<b>{b}</b>') for a, b in head) + '</tr>']
        for row in rows:
            out.append('<tr>' + ''.join(el('td', a, b, 'key' if i == 0 else '') for i, (a, b) in enumerate(row)) + '</tr>')
        return ''.join(out) + '</table></div>'

    def same(s):
        return html.escape(s, quote=False), html.escape(s, quote=False)

    def link(url, text):
        return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'

    data = json.load(open(DATA, encoding='utf8'))

    # ---------- 1: calculator ----------
    calc = (
        p('Coloque quantidade nas peças que vai fabricar e escolha até onde quer levar cada uma. A lista de material no '
          'fim soma todas; em “Tenho”, digite o que já juntou para ver o que falta. As receitas são as dos Elyos.',
          'Set a quantity on the pieces you are going to craft and choose how far to take each one. The material list at '
          'the end adds them all up; under “I have”, enter what you have gathered to see what is missing. The recipes are '
          'the Elyos ones.')
        + '<div id="calc" class="tool"></div>'
        + h3('Como ler a calculadora', 'How to read the calculator')
        + ul(
            ('<b>Peças:</b> quantidade 0 deixa a peça fora da conta. “Já tenho” é a versão da peça que você já possui.',
             '<b>Pieces:</b> a quantity of 0 leaves the piece out. “I have” is the version of the piece you already own.'),
            ('<b>Etapas de:</b> mostra os crafts de uma peça por vez; troque a peça no seletor ao lado do título.',
             '<b>Steps of:</b> it shows the crafts of one piece at a time; change the piece in the selector beside the title.'),
            ('<b>Sucesso %:</b> está na janela Crafting Chance da receita, na linha da diferença entre a sua proficiência '
             'e a exigida. Vem em 80% porque é o que os guias dão para diferença zero; troque pelo seu número. O valor '
             'vale para a mesma etapa de todas as peças da profissão.',
             '<b>Success %:</b> it is in the recipe\'s Crafting Chance window, on the row of the difference between your '
             'proficiency and the required one. It starts at 80% because that is what the guides give for a difference of '
             'zero; replace it with your number. The value applies to the same step of every piece of that profession.'),
            ('<b>Combo %:</b> a chance de a peça sair na versão Splendent. Os 25% vêm da planilha do Screamheart; troque '
             'se o jogo mostrar outro número.',
             '<b>Combo %:</b> the chance of the piece coming out as the Splendent version. The 25% comes from '
             'Screamheart\'s spreadsheet; replace it if the game shows another number.'),
            ('<b>Já tenho (nas etapas):</b> quantas peças Splendent daquela etapa você já guardou. A conta desconta.',
             '<b>I have (on the steps):</b> how many Splendent pieces of that step you already keep. They are deducted.'),
            ('<b>Tenho e Falta:</b> digite quanto já tem de cada material. “Falta” e o custo contam só o que falta.',
             '<b>I have and Missing:</b> enter how much of each material you have. “Missing” and the cost count only what is missing.'),
            ('<b>Preço:</b> opcional, para ver o custo em Kina. Os itens de Merchant já vêm com o preço do NPC.',
             '<b>Price:</b> optional, to see the cost in Kina. Merchant items already come with the NPC price.'),
            ('<b>É uma média, e do lado pessimista.</b> A conta supõe que um craft que falha gasta o material e a peça '
             'Splendent usada como ingrediente, mas não destrói a peça que o Transfer Crafting transforma. Não achei fonte '
             'que diga o que a falha consome: confira na sua primeira falha.',
             '<b>It is an average, and on the pessimistic side.</b> The maths assumes a failed craft spends the material '
             'and the Splendent piece used as an ingredient, but does not destroy the piece that Transfer Crafting '
             'transforms. I found no source saying what a failure consumes: check it on your first failure.'),
            ('Para receitas que não estão aqui (outras armas, Alchemy, Cooking), o wikily tem a '
             + link(WIKILY + 'crafting/calculator', 'Crafting Materials Calculator') + ' dele.',
             'For recipes that are not here (other weapons, Alchemy, Cooking), wikily has its own '
             + link(WIKILY + 'crafting/calculator', 'Crafting Materials Calculator') + '.'),
        ))

    # ---------- 2: enhancement ----------
    enh = (
        p('Quanto custa, em média, levar uma peça de um nível de aprimoramento a outro, já contando as falhas. A peça é '
          'escolhida pelo item level dela, que aparece no tooltip do item.',
          'How much it costs, on average, to take a piece from one enhancement level to another, failures included. The '
          'piece is picked by its item level, which shows in the item tooltip.')
        + '<div id="enh" class="tool"></div>'
        + ul(
            ('<b>Chances:</b> até +10 é 100% nas peças Epic e Unique. Do +11 ao +15, só nas Unique, é 65%, 50%, 35%, 25% '
             'e 20%, e cada falha soma 5% na tentativa seguinte.',
             '<b>Chances:</b> up to +10 it is 100% on Epic and Unique pieces. From +11 to +15, Unique only, it is 65%, 50%, '
             '35%, 25% and 20%, and each failure adds 5% to the next attempt.'),
            ('<b>Item level das Dragon Lord:</b> True 62, Splendent True 70, White 78, Wise 94, Splendent Wise 102. A '
             'Splendent White deve ser 86, pela sequência; confira no tooltip.',
             '<b>Item level of the Dragon Lord pieces:</b> True 62, Splendent True 70, White 78, Wise 94, Splendent Wise 102. '
             'Splendent White should be 86, following the sequence; check the tooltip.'),
            ('<b>O Transfer Crafting mantém o nível de aprimoramento:</b> o que você gastar na True segue para a White e a Wise.',
             '<b>Transfer Crafting keeps the enhancement level:</b> what you spend on the True one carries on to White and Wise.'),
            ('<b>Amuleto, cinto e runa</b> gastam também 1 Enhance Scroll (Bound) do próprio item por tentativa.',
             '<b>Amulet, belt and rune</b> also spend 1 Enhance Scroll (Bound) of the item itself per attempt.'),
            ('<b>Clash Rune:</b> a falha baixa o nível. A conta supõe 1 nível por falha; não achei confirmação.',
             '<b>Clash Rune:</b> a failure lowers the level. The maths assumes 1 level per failure; I found no confirmation.'),
            ('Custos e chances: ' + link(WIKILY + 'enhancement', 'Enhancement') + ' do wikily.gg, lido em 13/out/2026.',
             'Costs and chances: wikily.gg\'s ' + link(WIKILY + 'enhancement', 'Enhancement') + ', read on 13 Oct 2026.'),
        ))

    # ---------- 2: the Dragon Lord line ----------
    steps = [
        ('1. Orichalcum Dagger',
         ('Craft normal. Só a versão Splendent, que sai no combo, serve para a etapa seguinte',
          'Regular craft. Only the Splendent version, which comes out on a combo, works for the next step')),
        ("2. Expert's Orichalcum Dagger",
         ('Gasta 1 Splendent Orichalcum Dagger. De novo, só a Splendent segue adiante',
          'Spends 1 Splendent Orichalcum Dagger. Again, only the Splendent one moves on')),
        ("3. Artisan's Orichalcum Dagger",
         ("Gasta 1 Expert's Splendent Orichalcum Dagger", "Spends 1 Expert's Splendent Orichalcum Dagger")),
        ('4. True Dragon Lord Dagger',
         ("Gasta 1 Artisan's Splendent Orichalcum Dagger. É a primeira Dragon Lord; item level 62",
          "Spends 1 Artisan's Splendent Orichalcum Dagger. It is the first Dragon Lord; item level 62")),
        ('5. Splendent True Dragon Lord Dagger',
         ('Sai no combo da etapa 4. Se não sair, Transfer Crafting a partir da True: 11 Fine Thick Balaur Horn e 4 '
          'Wrathful Mind',
          'Comes out on the combo of step 4. If it does not, Transfer Crafting from the True one: 11 Fine Thick Balaur '
          'Horn and 4 Wrathful Mind')),
        ('6. White Dragon Lord Dagger',
         ("Transfer Crafting: transforma a Splendent True e gasta mais 1 Artisan's Splendent Orichalcum Dagger",
          "Transfer Crafting: transforms the Splendent True one and spends 1 more Artisan's Splendent Orichalcum Dagger")),
        ('7. Splendent White Dragon Lord Dagger',
         ('Combo da etapa 6, ou Transfer Crafting a partir da White', 'Combo of step 6, or Transfer Crafting from the White one')),
        ('8. Wise Dragon Lord Dagger',
         ("Transfer Crafting: transforma a Splendent White e gasta mais 1 Artisan's Splendent Orichalcum Dagger; item "
          'level 94',
          "Transfer Crafting: transforms the Splendent White one and spends 1 more Artisan's Splendent Orichalcum "
          'Dagger; item level 94')),
        ('9. Splendent Wise Dragon Lord Dagger',
         ('Combo da etapa 8, ou Transfer Crafting a partir da Wise; item level 102',
          'Combo of step 8, or Transfer Crafting from the Wise one; item level 102')),
    ]
    levels = [(same(pc['piece']), same(pc['prof'])) + tuple(same(str(s['lv'])) for s in pc['steps'][:4])
              for pc in data['pieces']]
    line = (
        p('O exemplo é a adaga; guarda, armadura e joias seguem a mesma sequência, só mudam os materiais.',
          'The example is the dagger; guard, armour and jewellery follow the same sequence, only the materials change.')
        + table([('Etapa', 'Step'), ('Como se faz', 'How it is made')], [(same(n), how) for n, how in steps])
        + ul(
            ("<b>A cadeia Orichalcum se repete três vezes.</b> True, White e Wise gastam, cada uma, uma Artisan's "
             'Splendent. Para chegar na Wise são três.',
             "<b>The Orichalcum chain repeats three times.</b> True, White and Wise each spend one Artisan's Splendent. "
             'Reaching Wise takes three.'),
            ("<b>Em média, 64 → 16 → 4 → 1:</b> 64 crafts da base, 16 do Expert's e 4 do Artisan's para cada Artisan's "
             'Splendent, com 25% de combo e sem contar falhas.',
             "<b>On average, 64 → 16 → 4 → 1:</b> 64 base crafts, 16 Expert's and 4 Artisan's for each Artisan's "
             'Splendent, with a 25% combo and not counting failures.'),
            ('<b>Da True em diante o combo não é obrigatório.</b> Se a peça não sair Splendent, o Transfer Crafting '
             'resolve com material.',
             '<b>From True onwards the combo is not mandatory.</b> If the piece does not come out Splendent, Transfer '
             'Crafting gets it done with materials.'),
            ('<b>Elyos: True → White → Wise. Asmodians: Star → Dark → Ebony.</b> Mesmos níveis e materiais.',
             '<b>Elyos: True → White → Wise. Asmodians: Star → Dark → Ebony.</b> Same levels and materials.'),
            ('<b>Por que craftar:</b> peça craftada tem 5 linhas de Soul Bind; a de Expedition tem 4.',
             '<b>Why craft:</b> a crafted piece has 5 Soul Bind lines; an Expedition one has 4.'),
        )
        + h3('Proficiência que cada receita pede', 'Proficiency each recipe requires')
        + table([('Peça', 'Piece'), ('Profissão', 'Profession'), same('Orichalcum'), same("Expert's"), same("Artisan's"),
                 same('True Dragon Lord')], levels)
        + p('No anel, nos brincos e no colar a base é Sapphire Ring, Diamond Earrings e Ruby Necklace. O wikily não '
            'mostra o nível das receitas de Transfer Crafting.',
            'For the ring, earrings and necklace the base is Sapphire Ring, Diamond Earrings and Ruby Necklace. Wikily '
            'does not show the level of the Transfer Crafting recipes.', 'note')
        + h3('O que passa para a peça nova no Transfer Crafting', 'What carries over to the new piece in Transfer Crafting')
        + table([('Passa', 'Carries over'), ('Não passa', 'Does not carry over')], [
            (('Nível de aprimoramento (+12 etc.)', 'Enhancement level (+12 etc.)'), same("Philosopher's Stat")),
            (('Níveis extras de Amp', 'Additional Amp levels'), same('Manastones / Soulstones')),
            (('Linhas de Soul Binding', 'Soul Binding stat lines'), same('Theostones')),
            (('Valores melhorados de Soul Binding', 'Soul Binding upgraded values'), same('Potential Stats')),
        ])
        + ul(
            ("<b>Artisan's Refining Stones:</b> também vêm da conquista de nível 50 de cada categoria de craft, em cada "
             'personagem.',
             "<b>Artisan's Refining Stones:</b> they also come from the level 50 achievement of each crafting category, "
             'on every character.'),
            ('Dá para craftar AFK.', 'You can craft while AFK.'),
            ('Segundo a planilha, fabricar os materiais um a um rende mais do que em lote.',
             'According to the spreadsheet, crafting materials one at a time is more efficient than in bulk.'),
        ))

    # ---------- 3: Essence Extraction ----------
    ee = (
        p('São dois tipos de ponto. Os <b>Common Skill Points</b> valem para toda coleta e não mudam de uma peça para '
          'outra. Os <b>Specialty Skill Points</b> são por tipo de nó, e é só neles que o respec faz diferença.',
          'There are two kinds of points. <b>Common Skill Points</b> apply to all gathering and do not change from one '
          'piece to another. <b>Specialty Skill Points</b> are per node type, and only there does a respec matter.')
        + h3('O que marcar para cada peça', 'What to pick for each piece')
        + table([('Vou fabricar', 'I am going to craft'), ('Profissão', 'Profession'), ('Especialidades', 'Specialties'),
                 ('O que a coleta entrega', 'What gathering gives')], [
            (same('Dagger, Guard'), same('Blacksmithing'), same('Ore + Odyle'),
             ('Orichalcum Ore e Odyle, nos quatro graus', 'Orichalcum Ore and Odyle, in the four grades')),
            (same('Breastplate, Greaves, Helm, Gloves, Pauldrons, Boots, Cloak'), same('Armorsmithing'), same('Ore + Odyle'),
             ('Os mesmos. O Raw Leather cai de monstros', 'The same ones. Raw Leather drops from monsters')),
            (same('Ring, Earrings, Necklace'), same('Handicrafting'), same('Gem + Odyle'),
             ('Sapphire (anel), Diamond (brincos), Ruby (colar) e Odyle', 'Sapphire (ring), Diamond (earrings), Ruby (necklace) and Odyle')),
        ])
        + ul(
            ('<b>Arma e armadura usam o mesmo setup.</b> Entre a adaga e o peitoral você não precisa de respec.',
             '<b>Weapon and armour use the same setup.</b> Between the dagger and the breastplate you need no respec.'),
            ('<b>O respec de 50.000 Kina só entra ao ir para as joias:</b> sai Ore, entra Gem. Odyle fica sempre.',
             '<b>The 50,000 Kina respec only comes in when you move to jewellery:</b> Ore out, Gem in. Odyle always stays.'),
            ('<b>A especialidade Gem vale para as três gemas.</b> O que muda é só o nó que você procura.',
             '<b>The Gem specialty covers all three gems.</b> Only the node you look for changes.'),
            ('Log, Herb e Cooking Ingredient não entram em nenhuma peça do Assassin.',
             'Log, Herb and Cooking Ingredient do not go into any Assassin piece.'),
        )
        + h3('Specialty Skill Points: ordem por nível', 'Specialty Skill Points: order by level')
        + p('Cada tipo de nó tem as mesmas três skills, 1 ponto por nível. Os níveis 2 e 3 pedem o grau Professional.',
            'Every node type has the same three skills, 1 point per level. Levels 2 and 3 require the Professional grade.')
        + table([('Skill', 'Skill'), ('Níveis', 'Levels'), ('Texto do jogo (nível 1 / 2 / 3)', 'Game text (level 1 / 2 / 3)')], [
            (('Ore Seeker / Gem Seeker / Odyle Seeker',) * 2, same('1'),
             same('Ore locations are displayed on the minimap. (Can be toggled in the minimap options.)')),
            (same('Plentiful Harvest'), same('3'),
             same('Upon a successful Essence Extraction, has a 10% / 20% / 30% chance to obtain double Gathered Materials.')),
            (('Ore Appraiser / Gem Appraiser / Odyle Appraiser',) * 2, same('3'),
             same('Successful Essence Extraction grants a 10% / 20% / 30% chance to reselect Ore grades. (Does not '
                  'activate if higher-grade Ores have already been discovered)')),
        ])
        + table([('Nível de Essence Extraction', 'Essence Extraction level'), ('Pontos no total', 'Points in total'),
                 ('O que pegar com o ponto novo', 'What to take with the new point')], [
            (same('10'), same('1'), ('Seeker de Ore (ou de Gem, na fase das joias)', 'Ore Seeker (or Gem Seeker, in the jewellery phase)')),
            (same('20'), same('2'), same('Odyle Seeker')),
            (same('30'), same('3'), ('Plentiful Harvest 1 de Ore/Gem', 'Plentiful Harvest 1 for Ore/Gem')),
            (same('40'), same('4'), ('Plentiful Harvest 1 de Odyle', 'Plentiful Harvest 1 for Odyle')),
            (same('50'), same('6'), ('Appraiser 1 nos dois. É o teto do grau Novice: dois tipos completos',
                                     'Appraiser 1 on both. It is the cap of the Novice grade: two full types')),
            (same('60'), same('7'), ('Plentiful Harvest 2 de Ore/Gem', 'Plentiful Harvest 2 for Ore/Gem')),
            (same('70'), same('8'), ('Plentiful Harvest 2 de Odyle', 'Plentiful Harvest 2 for Odyle')),
            (same('80'), same('10'), ('Plentiful Harvest 3 nos dois', 'Plentiful Harvest 3 on both')),
            (same('90'), same('12'), ('Appraiser 2 nos dois', 'Appraiser 2 on both')),
            (same('100'), same('14'), ('Appraiser 3 nos dois: dois tipos no máximo', 'Appraiser 3 on both: two types maxed')),
        ])
        + ul(
            ('<b>Os pontos dão exatamente para dois tipos:</b> 6 pontos no nível 50 e 14 no nível 100; um tipo completo '
             'custa 3 no grau Novice e 7 no total.',
             '<b>The points are exactly enough for two types:</b> 6 points at level 50 and 14 at level 100; a full type '
             'costs 3 in the Novice grade and 7 in total.'),
            ('<b>A ordem dentro do tipo é leitura minha.</b> Seeker primeiro para achar mais nós; Plentiful Harvest antes '
             'do Appraiser porque as etapas de baixo pedem centenas de Orichalcum Ore comum. Para as etapas White e Wise, '
             'que pedem Radiant, o Appraiser pesa mais.',
             '<b>The order inside a type is my own reading.</b> Seeker first to find more nodes; Plentiful Harvest before '
             'Appraiser because the lower steps ask for hundreds of common Orichalcum Ore. For the White and Wise steps, '
             'which ask for Radiant, Appraiser matters more.'),
            ('<b>Ore antes de Odyle</b> porque cada craft de arma gasta três vezes mais Orichalcum Ore do que Odyle.',
             '<b>Ore before Odyle</b> because each weapon craft spends three times more Orichalcum Ore than Odyle.'),
        )
        + h3('Common Skill Points: iguais para qualquer peça', 'Common Skill Points: the same for any piece')
        + table([('Skill', 'Skill'), ('Texto do jogo', 'Game text'), ('Nível 5', 'Level 5'), ('Nível 10', 'Level 10')], [
            (same('Proficient Handling'),
             same('On Every Successful Roll. Improves Success Gauge increase amount through proficient handling.'),
             same('Increases Success Gauge Gain by 25'), same('Increases Success Gauge Gain by 50')),
            (same('Delicate Touch'),
             same('All failure rolls. Reduces Failure Gauge increase amount through a delicate touch.'),
             same('Reduces Failure Gauge Gain by 40'), same('Reduces Failure Gauge Gain by 80')),
            (same('Lady Luck'),
             same('On Every Successful Roll. Improves the chance of greatly increasing the Success Gauge at a critical moment.'),
             same('24% chance to increase Success Gauge by x2.5.'),
             same('40% chance to increase Success Gauge by x2.5 or x4.')),
        ])
        + table([('Fase', 'Phase'), ('Pontos', 'Points'), same('Proficient Handling'), same('Delicate Touch'), same('Lady Luck')], [
            (('Grau Novice (até o nível 50)', 'Novice grade (up to level 50)'), same('45'), same('5'), same('5'), same('5')),
            (('Grau Professional (nível 100)', 'Professional grade (level 100)'), same('95'), same('10'), same('9'), same('6')),
        ])
        + ul(
            ('<b>Custo:</b> os níveis 1 a 5 custam 1, 2, 3, 4 e 5 pontos (15 no total); do 6 ao 10 são 5 pontos cada e '
             'pedem o grau Professional.',
             '<b>Cost:</b> levels 1 to 5 cost 1, 2, 3, 4 and 5 points (15 in total); 6 to 10 cost 5 points each and '
             'require the Professional grade.'),
            ('<b>No Novice os 45 pontos fecham os três no nível 5.</b> Enquanto não chega lá: Proficient Handling, depois '
             'Delicate Touch, depois Lady Luck.',
             '<b>In Novice the 45 points bring all three to level 5.</b> Until then: Proficient Handling, then Delicate '
             'Touch, then Lady Luck.'),
            ('<b>10 / 9 / 6 é a distribuição da planilha do Screamheart</b> e gasta exatamente os 95 pontos do nível 100.',
             '<b>10 / 9 / 6 is the distribution from Screamheart\'s spreadsheet</b> and spends exactly the 95 points of '
             'level 100.'),
            ('<b>Para passar do nível 50:</b> quest [Upgrade] Essence Extraction Specialty Skill, com o NPC Korius. Os '
             'guias dizem que ela pede uma Splendent Ruby (Bound).',
             '<b>To go past level 50:</b> the [Upgrade] Essence Extraction Specialty Skill quest, with the NPC Korius. '
             'The guides say it asks for a Splendent Ruby (Bound).'),
        )
        + h3('Onde ficam os nós', 'Where the nodes are')
        + table([('Nó', 'Node'), same('Verteron'), same('Altgard'), ('Outros', 'Others')], [
            (same('Orichalcum (Ore)'), same('546'), same('530'), same('—')),
            (same('Odyle'), same('706'), same('650'),
             ('240 em Chaotic Lower Reshanta e 15 em cada Expedition', '240 in Chaotic Lower Reshanta and 15 in each Expedition')),
            (same('Sapphire (Gem)'), same('192'), same('200'), same('—')),
            (same('Diamond (Gem)'), same('192'), same('200'), same('—')),
            (same('Ruby (Gem)'), same('196'), same('190'), same('—')),
        ])
        + ul(
            ('Cada extração dá um material de um dos quatro graus (comum, Fine, Pure, Radiant). Não achei a chance de '
             'cada grau.',
             'Each extraction gives one material of one of the four grades (common, Fine, Pure, Radiant). I could not '
             'find the chance of each grade.'),
            ('Cada nó rende de duas a quatro extrações. O Odyle fica no ar: precisa das asas.',
             'Each node yields two to four extractions. Odyle floats in the air: you need your wings.'),
            ('Com o Seeker, os nós aparecem no minimapa; o '
             + link(WIKILY + 'interactive-map', 'mapa interativo do wikily') + ' mostra todos.',
             'With Seeker, nodes show on the minimap; the '
             + link(WIKILY + 'interactive-map', 'wikily interactive map') + ' shows them all.'),
        ))

    # ---------- 4: where each material comes from ----------
    mats = (
        table([('Material', 'Material'), ('De onde vem', 'Where it comes from'), ('Detalhe', 'Detail')], [
            (same('Orichalcum Ore, Fine / Pure / Radiant Orichalcum Ore'), same('Essence Extraction: Ore'),
             ('Um nó só; o grau é sorteado a cada extração', 'A single node; the grade is rolled on each extraction')),
            (same('Odyle, Fine / Pure / Radiant Odyle'), same('Essence Extraction: Odyle'),
             ('Entra em todas as receitas', 'Goes into every recipe')),
            (same('Sapphire / Diamond / Ruby Gemstone'), same('Essence Extraction: Gem'),
             ('Anel, brincos e colar, nessa ordem', 'Ring, earrings and necklace, in that order')),
            (same('Raw Leather'), ('Monstros de nível 10 a 49', 'Monsters of level 10 to 49'),
             ('2 Raw Leather viram 1 Strong Leather, para a armadura', '2 Raw Leather become 1 Strong Leather, for armour')),
            (("Refining Stone, Expert's e Artisan's Refining Stone", "Refining Stone, Expert's and Artisan's Refining Stone"),
             ('Monstros e Expeditions no modo Conquest', 'Monsters and Expeditions in Conquest mode'),
             ("A Artisan's também vem da conquista de nível 50 de cada craft",
              "The Artisan's one also comes from the level 50 achievement of each craft")),
            (same("Artisan's Ultimate Refining Stone"), ('Expeditions no modo Conquest', 'Expeditions in Conquest mode'),
             ('As seis Expeditions e o Abyssal Forge: Ludra', 'All six Expeditions and Abyssal Forge: Ludra')),
            (same('Wrathful Mind'), ('Expeditions no modo Conquest', 'Expeditions in Conquest mode'),
             ('As seis Expeditions e o Abyssal Forge: Ludra', 'All six Expeditions and Abyssal Forge: Ludra')),
            (same('Wrathful Will'), ('Expeditions no modo Conquest', 'Expeditions in Conquest mode'),
             same('Urugugu Canyon, Fire Temple, Vakron Sky Island, Ferocious Horn Den, Abyssal Forge: Ludra')),
            (same('Wrathful Ego'), ('Expeditions no modo Conquest', 'Expeditions in Conquest mode'),
             same('Fire Temple, Ferocious Horn Den, Abyssal Forge: Ludra')),
            (same("Balaur's Essence"), ('Chefes de campo de nível 45 e Expeditions (Conquest)', 'Level 45 field bosses and Expeditions (Conquest)'),
             ('60,7% por chefe em Verteron; 2 viram 1 Balaur Horn, Leather ou Scale',
              '60.7% per boss in Verteron; 2 become 1 Balaur Horn, Leather or Scale')),
            (same('Orichalcum Solvent (Bound), Abrasive (Bound)'), ('Merchant da profissão ou Shop do menu', 'Profession Merchant or the menu Shop'),
             same('400 Kina')),
            (('Hammer, Leather Softener e Scale Hardener (Bound)', 'Hammer, Leather Softener and Scale Hardener (Bound)'),
             ('Merchant da profissão ou Shop do menu', 'Profession Merchant or the menu Shop'),
             ('4.650 Kina (Thick), 5.600 (Hard), 6.550 (Durable)', '4,650 Kina (Thick), 5,600 (Hard), 6,550 (Durable)')),
        ])
        + h3('Materiais que você fabrica antes', 'Materials you craft first')
        + table([('Material', 'Material'), ('Receita', 'Recipe'), ('Nível', 'Level')], [
            (same('Orichalcum Ingot'), same('2 Orichalcum Ore + 1 Orichalcum Solvent (Bound)'), same('1')),
            (same('Strong Leather'), same('2 Raw Leather'), same('1')),
            (same('Sapphire / Diamond / Ruby Decoration'), same('2 Gemstone + 1 Abrasive (Bound)'), same('1')),
            (same('Fine Thick / Hard / Durable Balaur Horn'), same("2 Balaur's Essence + 1 Zircon / Lazuli / Moonstone Hammer (Bound)"),
             same('51 / 65 / 80')),
            (same('Tanned Thick / Hard / Durable Balaur Leather'),
             same("2 Balaur's Essence + 1 Lesser / Intermediate / Superior Dragon Leather Softener (Bound)"), same('51 / 65 / 80')),
            (same('Enhanced Thick / Hard / Durable Balaur Scale'),
             same("2 Balaur's Essence + 1 Lesser / Intermediate / Superior Dragon Scale Hardener (Bound)"), same('51 / 65 / 80')),
        ])
        + p('A calculadora já abre esses materiais: a lista dela mostra o que você coleta, dropa ou compra.',
            'The calculator already breaks these materials down: its list shows what you gather, loot or buy.', 'note')
        + p('Fontes: receitas, coleta e materiais do ' + link(WIKILY + 'crafting', 'wikily.gg') + '; planilha '
            + link(SHEET, 'Aion 2 Content Guide') + ', do Screamheart (abas Crafting Tips e Crafting Calculator). Lido em '
            '13/out/2026: confira a receita na mesa antes de juntar material.',
            'Sources: recipes, gathering and materials from ' + link(WIKILY + 'crafting', 'wikily.gg') + "; Screamheart's "
            + link(SHEET, 'Aion 2 Content Guide') + ' spreadsheet (Crafting Tips and Crafting Calculator tabs). Read on '
            '13 Oct 2026: check the recipe at the table before gathering materials.', 'note'))

    english.update({'Crafting': 'Crafting',
                    'Calculadoras, linha Dragon Lord e Essence Extraction': 'Calculators, the Dragon Lord line and Essence Extraction',
                    '1. Calculadora de craft': '1. Crafting calculator',
                    '2. Calculadora de aprimoramento': '2. Enhancement calculator', '3. Linha Dragon Lord': '3. The Dragon Lord line',
                    '4. Essence Extraction: onde pôr os pontos': '4. Essence Extraction: where to put the points',
                    '5. De onde vem cada material': '5. Where each material comes from'})
    return {
        'title': 'Crafting', 'subtitle': 'Calculadoras, linha Dragon Lord e Essence Extraction',
        'sections': [
            {'id': 'craft-calculadora', 'title': '1. Calculadora de craft', 'meta': '', 'html': calc},
            {'id': 'craft-aprimoramento', 'title': '2. Calculadora de aprimoramento', 'meta': '', 'html': enh},
            {'id': 'craft-linha-dragon-lord', 'title': '3. Linha Dragon Lord', 'meta': '', 'html': line},
            {'id': 'craft-essence-extraction', 'title': '4. Essence Extraction: onde pôr os pontos', 'meta': '', 'html': ee},
            {'id': 'craft-materiais', 'title': '5. De onde vem cada material', 'meta': '', 'html': mats},
        ],
    }
