"""The 'Crafting' part of the guide: the calculator (drawn by the page script into #calc), the Dragon Lord line,
where to put the Essence Extraction points and where each material comes from.

Unlike the other parts it does not come from a DOCX: the text lives here, in Portuguese and English. Each section
shows the short version; the reference tables sit in blocks that open on a click (more()).
Sources, read on 13 Oct 2026: the gear, material and gathering records of wikily.gg (craft_data.json is made from
them by craft_data.py) and Screamheart's "Aion 2 Content Guide" spreadsheet (Crafting Tips / Crafting Calculator tabs).
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'craft_data.json')
ENH = os.path.join(HERE, 'enhance_data.json')  # made by enh_data.py
SHEET = 'https://docs.google.com/spreadsheets/d/1bNxC1wd0S_ILGYAyWnO0aTo_G_AOrjkv7bTcOj_NRz8/'
WIKILY = 'https://wikily.gg/aion-2/'


def calc_data():
    data = json.load(open(DATA, encoding='utf8'))
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

    def ul(*items):
        return '<ul>' + ''.join(el('li', pt, en) for pt, en in items) + '</ul>'

    def more(pt, en, inner):
        """A block that stays closed until the reader asks for it."""
        return '<details class="more">' + el('summary', pt, en) + f'<div class="in">{inner}</div></details>'

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
    elyos = [pc for pc in data['pieces'] if pc['race'] == 'Elyos']

    # ---------- 1: calculator ----------
    calc = (
        p('Escolha a facção e a classe, clique nas peças que vai fabricar e diga até onde quer levar cada uma. A lista de '
          'material soma todas; em “Tenho”, digite o que já juntou para ver o que falta.',
          'Pick the faction and the class, click the pieces you are going to craft and say how far to take each one. The '
          'material list adds them all up; under “I have”, enter what you have gathered to see what is missing.')
        + '<div id="calc" class="tool"></div>'
        + more('Como ler a calculadora', 'How to read the calculator', ul(
            ('<b>Facção e classe:</b> a facção troca os nomes da linha (True, White, Wise ou Star, Dark, Ebony) e a madeira do '
             'Bow e do Staff. A classe define a arma; “Todas as armas” mostra as oito, para quem fabrica para vender.',
             '<b>Faction and class:</b> the faction changes the names of the line (True, White, Wise or Star, Dark, Ebony) and '
             'the wood of the Bow and the Staff. The class sets the weapon; “All weapons” shows all eight, for those who craft to sell.'),
            ('<b>Peças escolhidas:</b> “Quero chegar em” é a versão final; “Já tenho” é a versão que você já possui. '
             'Quantidade 0 tira a peça da lista.',
             '<b>Chosen pieces:</b> “I want to reach” is the final version; “I have” is the version you already own. A '
             'quantity of 0 takes the piece off the list.'),
            ('<b>Tenho e Falta:</b> digite quanto já tem de cada material. “Falta” conta só o que falta.',
             '<b>I have and Missing:</b> enter how much of each material you have. “Missing” counts only what is missing.'),
            ('<b>Mostrar custo em Kina:</b> abre as colunas de preço e custo. Os itens de Merchant já vêm com o preço do NPC; '
             'nos outros, digite o preço que você paga.',
             '<b>Show the cost in Kina:</b> opens the price and cost columns. Merchant items already come with the NPC '
             'price; for the others, enter the price you pay.'),
            ('<b>Etapas, chances e peças Splendent guardadas:</b> mostra os crafts de uma peça por vez e deixa trocar os '
             'números da conta.',
             '<b>Steps, chances and Splendent pieces in stock:</b> shows the crafts of one piece at a time and lets you '
             'change the numbers of the maths.'),
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
            ('<b>É uma média, e do lado pessimista.</b> A conta supõe que um craft que falha gasta o material e a peça '
             'Splendent usada como ingrediente, mas não destrói a peça que o Transfer Crafting transforma. Não achei fonte '
             'que diga o que a falha consome: confira na sua primeira falha.',
             '<b>It is an average, and on the pessimistic side.</b> The maths assumes a failed craft spends the material '
             'and the Splendent piece used as an ingredient, but does not destroy the piece that Transfer Crafting '
             'transforms. I found no source saying what a failure consumes: check it on your first failure.'),
            ('Para receitas que não estão aqui (poções, comida, braceletes), o wikily tem a '
             + link(WIKILY + 'crafting/calculator', 'Crafting Materials Calculator') + ' dele.',
             'For recipes that are not here (potions, food, bracelets), wikily has its own '
             + link(WIKILY + 'crafting/calculator', 'Crafting Materials Calculator') + '.'),
        )))

    # ---------- 2: enhancement ----------
    enh = (
        p('Quanto custa, em média, levar uma peça de um nível de aprimoramento a outro, já contando as falhas. A peça é '
          'escolhida pelo item level dela, que aparece no tooltip do item.',
          'How much it costs, on average, to take a piece from one enhancement level to another, failures included. The '
          'piece is picked by its item level, which shows in the item tooltip.')
        + '<div id="enh" class="tool"></div>'
        + more('Chances, item level das Dragon Lord e fonte', 'Chances, item level of the Dragon Lord pieces and source', ul(
            ('<b>Chances:</b> até +10 é 100% nas peças Epic e Unique. Do +11 ao +15, só nas Unique, é 65%, 50%, 35%, 25% '
             'e 20%, e cada falha soma 5% na tentativa seguinte.',
             '<b>Chances:</b> up to +10 it is 100% on Epic and Unique pieces. From +11 to +15, Unique only, it is 65%, 50%, '
             '35%, 25% and 20%, and each failure adds 5% to the next attempt.'),
            ('<b>Item level das Dragon Lord:</b> True ou Star 62, White ou Dark 78, Wise ou Ebony 94. A versão Splendent de '
             'cada uma tem 8 a mais: 70, 86 e 102.',
             '<b>Item level of the Dragon Lord pieces:</b> True or Star 62, White or Dark 78, Wise or Ebony 94. The Splendent '
             'version of each has 8 more: 70, 86 and 102.'),
            ('<b>O Transfer Crafting mantém o nível de aprimoramento:</b> o que você gastar na primeira Dragon Lord segue '
             'para as seguintes.',
             '<b>Transfer Crafting keeps the enhancement level:</b> what you spend on the first Dragon Lord carries on to '
             'the next ones.'),
            ('<b>Amuleto, cinto e runa</b> gastam também 1 Enhance Scroll (Bound) do próprio item por tentativa.',
             '<b>Amulet, belt and rune</b> also spend 1 Enhance Scroll (Bound) of the item itself per attempt.'),
            ('<b>Clash Rune:</b> a falha baixa o nível. A conta supõe 1 nível por falha; não achei confirmação.',
             '<b>Clash Rune:</b> a failure lowers the level. The maths assumes 1 level per failure; I found no confirmation.'),
            ('<b>Atributos no nível:</b> o bônus total da peça naquele nível, da armaria oficial do jogo (o mesmo do editor '
             'de build). Arma e guarda ganham igual; todas as partes de armadura também; e colar, brinco, anel e bracelete '
             'também. Por isso, nas peças comuns, escolha o tipo.',
             '<b>Stats at the level:</b> the total bonus of the piece at that level, from the official armory (the same as in '
             'the build editor). Weapon and guard gain the same; so do all armour pieces; and so do necklace, earring, ring '
             'and bracelet. That is why the common pieces ask for the type.'),
            ('Custos e chances: ' + link(WIKILY + 'enhancement', 'Enhancement') + ' do wikily.gg, lido em 13/out/2026.',
             'Costs and chances: wikily.gg\'s ' + link(WIKILY + 'enhancement', 'Enhancement') + ', read on 13 Oct 2026.'),
        )))

    # ---------- 3: the Dragon Lord line ----------
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
         ('Sai no combo da etapa 4. Se não sair, Transfer Crafting a partir da True',
          'Comes out on the combo of step 4. If it does not, Transfer Crafting from the True one')),
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
    levels = [(same(pc['piece']), same(pc['prof'])) + tuple(same(str(s['lv'])) for s in pc['steps'][:4]) for pc in elyos]
    line = (
        p('Toda arma, armadura e joia segue a mesma sequência de nove etapas; só mudam os materiais e o nome da peça de '
          'base. O exemplo é a adaga dos Elyos.',
          'Every weapon, armour piece and jewel follows the same sequence of nine steps; only the materials and the name of '
          'the base piece change. The example is the Elyos dagger.')
        + table([('Etapa', 'Step'), ('Como se faz', 'How it is made')], [(same(n), how) for n, how in steps])
        + ul(
            ('<b>Elyos: True → White → Wise. Asmodians: Star → Dark → Ebony.</b> Mesmos níveis e materiais.',
             '<b>Elyos: True → White → Wise. Asmodians: Star → Dark → Ebony.</b> Same levels and materials.'),
            ("<b>A cadeia da peça de base se repete três vezes.</b> Cada Dragon Lord gasta uma Artisan's Splendent. Em "
             'média são 64 crafts da base, 16 do Expert\'s e 4 do Artisan\'s para cada uma, com 25% de combo.',
             "<b>The chain of the base piece repeats three times.</b> Each Dragon Lord spends one Artisan's Splendent. On "
             "average that is 64 base crafts, 16 Expert's and 4 Artisan's for each one, with a 25% combo."),
            ('<b>Da primeira Dragon Lord em diante o combo não é obrigatório.</b> Se a peça não sair Splendent, o Transfer '
             'Crafting resolve com material.',
             '<b>From the first Dragon Lord onwards the combo is not mandatory.</b> If the piece does not come out '
             'Splendent, Transfer Crafting gets it done with materials.'),
            ('<b>Por que craftar:</b> peça craftada tem 5 linhas de Soul Bind; a de Expedition tem 4.',
             '<b>Why craft:</b> a crafted piece has 5 Soul Bind lines; an Expedition one has 4.'),
        )
        + more('Peça de base e proficiência que cada receita pede', 'Base piece and proficiency each recipe requires',
               table([('Peça', 'Piece'), ('Profissão', 'Profession'), ('Base', 'Base'), same("Expert's"), same("Artisan's"),
                      ('1ª Dragon Lord', '1st Dragon Lord')], levels)
               + p('A peça de base é Orichalcum nas armas de Blacksmithing e na armadura; Yggdrasil (Elyos) ou Asvata '
                   '(Asmodians) no Bow e no Staff; Truth no Spellbook e no Orb; Sapphire Ring, Diamond Earrings e Ruby '
                   'Necklace nas joias. O wikily não mostra o nível das receitas de Transfer Crafting.',
                   'The base piece is Orichalcum for the Blacksmithing weapons and the armour; Yggdrasil (Elyos) or Asvata '
                   '(Asmodians) for the Bow and the Staff; Truth for the Spellbook and the Orb; Sapphire Ring, Diamond '
                   'Earrings and Ruby Necklace for the jewellery. Wikily does not show the level of the Transfer Crafting '
                   'recipes.', 'note'))
        + more('O que passa para a peça nova no Transfer Crafting', 'What carries over to the new piece in Transfer Crafting',
               table([('Passa', 'Carries over'), ('Não passa', 'Does not carry over')], [
                   (('Nível de aprimoramento (+12 etc.)', 'Enhancement level (+12 etc.)'), same("Philosopher's Stat")),
                   (('Níveis extras de Amp', 'Additional Amp levels'), same('Manastones / Soulstones')),
                   (('Linhas de Soul Binding', 'Soul Binding stat lines'), same('Theostones')),
                   (('Valores melhorados de Soul Binding', 'Soul Binding upgraded values'), same('Potential Stats')),
               ]))
        + more('Dicas da planilha do Screamheart', "Tips from Screamheart's spreadsheet", ul(
            ("<b>Artisan's Refining Stones:</b> também vêm da conquista de nível 50 de cada categoria de craft, em cada "
             'personagem.',
             "<b>Artisan's Refining Stones:</b> they also come from the level 50 achievement of each crafting category, "
             'on every character.'),
            ('Dá para craftar AFK.', 'You can craft while AFK.'),
            ('Fabricar os materiais um a um rende mais do que em lote.',
             'Crafting materials one at a time is more efficient than in bulk.'),
        )))

    # ---------- 4: Essence Extraction ----------
    ee = (
        p('São dois tipos de ponto. Os <b>Common Skill Points</b> valem para toda coleta e não mudam de uma peça para '
          'outra. Os <b>Specialty Skill Points</b> são por tipo de nó, e os pontos dão para dois tipos completos: escolha '
          'pela tabela.',
          'There are two kinds of points. <b>Common Skill Points</b> apply to all gathering and do not change from one '
          'piece to another. <b>Specialty Skill Points</b> are per node type, and the points are enough for two full '
          'types: pick them from the table.')
        + table([('Vou fabricar', 'I am going to craft'), ('Profissão', 'Profession'), ('Especialidades', 'Specialties'),
                 ('O que a coleta entrega', 'What gathering gives')], [
            (same('Greatsword, Longsword, Dagger, Mace, Guard'), same('Blacksmithing'), same('Ore + Odyle'),
             ('Orichalcum Ore e Odyle, nos quatro graus', 'Orichalcum Ore and Odyle, in the four grades')),
            (same('Helm, Pauldrons, Breastplate, Gloves, Greaves, Boots, Cloak'), same('Armorsmithing'), same('Ore + Odyle'),
             ('Os mesmos. O Raw Leather cai de monstros', 'The same ones. Raw Leather drops from monsters')),
            (same('Bow, Staff'), same('Handicrafting'), same('Log + Odyle'),
             ('Yggdrasil Log (Elyos, em Verteron) ou Asvata Log (Asmodians, em Altgard) e Odyle',
              'Yggdrasil Log (Elyos, in Verteron) or Asvata Log (Asmodians, in Altgard) and Odyle')),
            (same('Ring, Earrings, Necklace'), same('Handicrafting'), same('Gem + Odyle'),
             ('Sapphire (anel), Diamond (brincos), Ruby (colar) e Odyle', 'Sapphire (ring), Diamond (earrings), Ruby (necklace) and Odyle')),
            (same('Spellbook, Orb'), same('Alchemy'), same('Gem + Odyle'),
             ('Ruby (Spellbook), Sapphire (Orb) e Odyle. A peça de base usa Magic Crystal, feito de Spiritstone, que cai de monstros',
              'Ruby (Spellbook), Sapphire (Orb) and Odyle. The base piece uses Magic Crystal, made of Spiritstone, which drops from monsters')),
        ])
        + ul(
            ('<b>Odyle fica sempre:</b> entra em todas as receitas. O outro tipo depende da peça.',
             '<b>Odyle always stays:</b> it goes into every recipe. The other type depends on the piece.'),
            ('<b>O respec custa 50.000 Kina</b> e só é preciso ao trocar o segundo tipo: de Ore para Gem ao passar da arma '
             'ou armadura para as joias, por exemplo.',
             '<b>A respec costs 50,000 Kina</b> and is only needed when the second type changes: from Ore to Gem when '
             'moving from the weapon or armour to the jewellery, for example.'),
            ('<b>A especialidade Gem vale para as três gemas.</b> O que muda é só o nó que você procura.',
             '<b>The Gem specialty covers all three gems.</b> Only the node you look for changes.'),
            ('Herb e Cooking Ingredient não entram em nenhuma peça de equipamento.',
             'Herb and Cooking Ingredient do not go into any piece of gear.'),
        )
        + more('Specialty Skill Points: as skills e a ordem por nível', 'Specialty Skill Points: the skills and the order by level',
               p('Cada tipo de nó tem as mesmas três skills, 1 ponto por nível. Os níveis 2 e 3 pedem o grau Professional. '
                 'Na tabela de ordem, “1º tipo” é Ore, Log ou Gem, conforme a peça.',
                 'Every node type has the same three skills, 1 point per level. Levels 2 and 3 require the Professional '
                 'grade. In the order table, “1st type” is Ore, Log or Gem, depending on the piece.')
               + table([('Skill', 'Skill'), ('Níveis', 'Levels'), ('Texto do jogo (nível 1 / 2 / 3)', 'Game text (level 1 / 2 / 3)')], [
                   (('Ore Seeker / Gem Seeker / Log Seeker / Odyle Seeker',) * 2, same('1'),
                    same('Ore locations are displayed on the minimap. (Can be toggled in the minimap options.)')),
                   (same('Plentiful Harvest'), same('3'),
                    same('Upon a successful Essence Extraction, has a 10% / 20% / 30% chance to obtain double Gathered Materials.')),
                   (('Ore Appraiser / Gem Appraiser / Log Appraiser / Odyle Appraiser',) * 2, same('3'),
                    same('Successful Essence Extraction grants a 10% / 20% / 30% chance to reselect Ore grades. (Does not '
                         'activate if higher-grade Ores have already been discovered)')),
               ])
               + table([('Nível de Essence Extraction', 'Essence Extraction level'), ('Pontos no total', 'Points in total'),
                        ('O que pegar com o ponto novo', 'What to take with the new point')], [
                   (same('10'), same('1'), ('Seeker do 1º tipo', 'Seeker of the 1st type')),
                   (same('20'), same('2'), same('Odyle Seeker')),
                   (same('30'), same('3'), ('Plentiful Harvest 1 do 1º tipo', 'Plentiful Harvest 1 for the 1st type')),
                   (same('40'), same('4'), ('Plentiful Harvest 1 de Odyle', 'Plentiful Harvest 1 for Odyle')),
                   (same('50'), same('6'), ('Appraiser 1 nos dois. É o teto do grau Novice: dois tipos completos',
                                            'Appraiser 1 on both. It is the cap of the Novice grade: two full types')),
                   (same('60'), same('7'), ('Plentiful Harvest 2 do 1º tipo', 'Plentiful Harvest 2 for the 1st type')),
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
                    'do Appraiser porque as etapas de baixo pedem centenas de material comum. Para a segunda e a terceira '
                    'Dragon Lord, que pedem Radiant, o Appraiser pesa mais.',
                    '<b>The order inside a type is my own reading.</b> Seeker first to find more nodes; Plentiful Harvest before '
                    'Appraiser because the lower steps ask for hundreds of common material. For the second and third Dragon '
                    'Lord, which ask for Radiant, Appraiser matters more.'),
                   ('<b>O 1º tipo antes de Odyle</b> porque cada craft de arma gasta três vezes mais dele do que de Odyle.',
                    '<b>The 1st type before Odyle</b> because each weapon craft spends three times more of it than of Odyle.'),
               ))
        + more('Common Skill Points: iguais para qualquer peça', 'Common Skill Points: the same for any piece',
               table([('Skill', 'Skill'), ('Texto do jogo', 'Game text'), ('Nível 5', 'Level 5'), ('Nível 10', 'Level 10')], [
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
               ))
        + more('Onde ficam os nós', 'Where the nodes are',
               table([('Nó', 'Node'), same('Verteron'), same('Altgard'), ('Outros', 'Others')], [
                   (same('Orichalcum (Ore)'), same('546'), same('530'), same('—')),
                   (same('Odyle'), same('706'), same('650'),
                    ('240 em Chaotic Lower Reshanta e 15 em cada Expedition', '240 in Chaotic Lower Reshanta and 15 in each Expedition')),
                   (same('Yggdrasil (Log)'), same('125'), same('—'), same('—')),
                   (same('Asvata (Log)'), same('—'), same('158'), same('—')),
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
               )))

    # ---------- 5: where each material comes from ----------
    mats = (
        p('A calculadora já diz de onde vem cada material da sua lista. Aqui está o resumo de todos.',
          'The calculator already says where each material on your list comes from. Here is the summary of all of them.')
        + table([('Material', 'Material'), ('De onde vem', 'Where it comes from'), ('Detalhe', 'Detail')], [
            (same('Orichalcum Ore, Fine / Pure / Radiant Orichalcum Ore'), same('Essence Extraction: Ore'),
             ('Um nó só; o grau é sorteado a cada extração', 'A single node; the grade is rolled on each extraction')),
            (same('Odyle, Fine / Pure / Radiant Odyle'), same('Essence Extraction: Odyle'),
             ('Entra em todas as receitas', 'Goes into every recipe')),
            (same('Yggdrasil Log / Asvata Log'), same('Essence Extraction: Log'),
             ('Bow e Staff. Yggdrasil em Verteron, Asvata em Altgard', 'Bow and Staff. Yggdrasil in Verteron, Asvata in Altgard')),
            (same('Sapphire / Diamond / Ruby Gemstone'), same('Essence Extraction: Gem'),
             ('Anel e Orb, brincos, colar e Spellbook, nessa ordem', 'Ring and Orb, earrings, necklace and Spellbook, in that order')),
            (same('Raw Leather'), ('Monstros de nível 10 a 49', 'Monsters of level 10 to 49'),
             ('2 Raw Leather viram 1 Strong Leather, para a armadura', '2 Raw Leather become 1 Strong Leather, for armour')),
            (same('Spiritstone'), ('Monstros de nível 10 a 51', 'Monsters of level 10 to 51'),
             ('2 Spiritstone viram 1 Magic Crystal, para Spellbook e Orb', '2 Spiritstone become 1 Magic Crystal, for Spellbook and Orb')),
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
            (same('Orichalcum Solvent, Abrasive, Sandpaper, Catalyst (Bound)'), ('Merchant da profissão ou Shop do menu', 'Profession Merchant or the menu Shop'),
             same('400 Kina')),
            (('Hammer, Leather Softener e Scale Hardener (Bound)', 'Hammer, Leather Softener and Scale Hardener (Bound)'),
             ('Merchant da profissão ou Shop do menu', 'Profession Merchant or the menu Shop'),
             ('4.650 Kina (Thick), 5.600 (Hard), 6.550 (Durable)', '4,650 Kina (Thick), 5,600 (Hard), 6,550 (Durable)')),
        ])
        + more('Materiais que você fabrica antes', 'Materials you craft first',
               table([('Material', 'Material'), ('Receita', 'Recipe'), ('Nível', 'Level')], [
                   (same('Orichalcum Ingot'), same('2 Orichalcum Ore + 1 Orichalcum Solvent (Bound)'), same('1')),
                   (same('Strong Leather'), same('2 Raw Leather'), same('1')),
                   (same('Yggdrasil Wood / Asvata Wood'), same('2 Yggdrasil Log / Asvata Log + 1 Sandpaper (Bound)'), same('1')),
                   (same('Magic Crystal'), same('2 Spiritstone + 1 Catalyst (Bound)'), same('1')),
                   (same('Sapphire / Diamond / Ruby Decoration'), same('2 Gemstone + 1 Abrasive (Bound)'), same('1')),
                   (same('Fine Thick / Hard / Durable Balaur Horn'), same("2 Balaur's Essence + 1 Zircon / Lazuli / Moonstone Hammer (Bound)"),
                    same('51 / 65 / 80')),
                   (same('Tanned Thick / Hard / Durable Balaur Leather'),
                    same("2 Balaur's Essence + 1 Lesser / Intermediate / Superior Dragon Leather Softener (Bound)"), same('51 / 65 / 80')),
                   (same('Enhanced Thick / Hard / Durable Balaur Scale'),
                    same("2 Balaur's Essence + 1 Lesser / Intermediate / Superior Dragon Scale Hardener (Bound)"), same('51 / 65 / 80')),
               ])
               + p('A calculadora já abre esses materiais: a lista dela mostra o que você coleta, dropa ou compra.',
                   'The calculator already breaks these materials down: its list shows what you gather, loot or buy.', 'note'))
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
