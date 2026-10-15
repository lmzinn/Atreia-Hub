"""The 'Rotina' part of the guide: daily and weekly limits with counters that reset by themselves (drawn by the page
script into #routine). The list of counters is routine_data.json, made by routine_data.py. The text lives here, in
Portuguese and English."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'routine_data.json')
METABOT = 'https://metabot.gg/en/aion-2/guides/daily-weekly-checklist'


def routine_data():
    return json.load(open(DATA, encoding='utf8'))


def routine_part(strings, english):
    """Same shape as guide_convert.convert(); every text goes to `strings` and its English version to `english`."""
    def el(tag, pt, en, cls=''):
        strings.append(pt)
        english[pt] = en
        c = f' class="{cls}"' if cls else ''
        return f'<{tag}{c} data-t="{len(strings) - 1}">{pt}</{tag}>'

    def ul(*items):
        return '<ul>' + ''.join(el('li', pt, en) for pt, en in items) + '</ul>'

    link = f'<a href="{METABOT}" target="_blank" rel="noopener">metabot.gg</a>'
    tool = (
        el('p', 'O que vence sozinho: o que zera todo dia e o que zera na quarta. Marque cada linha quando fizer; a página '
                'desmarca sozinha no reset.',
           'What runs out by itself: what clears every day and what clears on Wednesday. Tick each row when you do it; the '
           'page unticks by itself at the reset.')
        + '<div id="routine" class="tool"></div>')
    how = ul(
        ('<b>Marcar:</b> clique na linha quando terminar aquilo. O nome fica riscado e a linha conta em “feitos”, no '
         'alto da coluna. Clique de novo para desmarcar.',
         '<b>Ticking:</b> click the row when you finish it. The name is struck through and the row counts as “done”, at the '
         'top of the column. Click again to untick.'),
        ('<b>Diário:</b> desmarca sozinho todo dia no reset. <b>Semanal:</b> desmarca sozinho na quarta.',
         '<b>Daily:</b> unticks by itself every day at the reset. <b>Weekly:</b> unticks by itself on Wednesday.'),
        ('<b>⚠ na linha:</b> aparece em Nightmare e Festival Shugo, que acumulam até um máximo. Se a linha fica sem marcar '
         'por dias seguidos (7 no Nightmare, 4 no Festival Shugo), a página avisa que as entradas devem estar no máximo e a '
         'próxima recarga se perde.',
         '<b>⚠ on the row:</b> shows on Nightmare and Shugo Festival, which stack up to a cap. If the row goes unticked for '
         'days in a row (7 on Nightmare, 4 on Shugo Festival), the page warns that the entries should be at the cap and the '
         'next recharge is lost.'),
        ('<b>Por que não tem as dungeons de Conquest e Transcendence:</b> elas gastam Odyle Energy, que é uma reserva '
         'só para todas as dungeons e depende da assinatura. Não é um contador por dungeon.',
         '<b>Why Conquest and Transcendence dungeons are not here:</b> they spend Odyle Energy, which is one pool for '
         'every dungeon and depends on the subscription. It is not a counter per dungeon.'),
        ('<b>Membership:</b> com a assinatura, o Festival Shugo guarda até 21 em vez de 12, e o tempo no Abyss '
         'passa de 7 para 14 horas. Também aparece a compra semanal de Odyle Energy no Wind Breeze Merchant.',
         '<b>Membership:</b> with the subscription, Shugo Festival stores up to 21 instead of 12, and Abyss '
         'time goes from 7 to 14 hours. The weekly Odyle Energy purchase at the Wind Breeze Merchant shows up too.'),
        ('<b>Etiqueta SERVIDOR:</b> o contador vale para todos os seus personagens do servidor, então o número é o mesmo em '
         'todas as abas. Com PERSONAGEM, cada aba tem o seu.',
         '<b>SERVER tag:</b> the counter is for all your characters on the server, so the number is the same on every tab. '
         'With CHAR, each tab has its own.'),
        ('<b>Escolher o que aparece:</b> liga e desliga cada contador. O que aparece de início é a lista do app do Shugo.GG, mais '
         'Nightmare e Festival Shugo. Invasão Dimensional, Corredores do Abyss, Subjugação, Silent Graveyard, Fafnite '
         'Amphitheater, chefes finais e Exploração por dungeon vêm desligados. Passe o mouse no nome para ver como ele aparece no jogo.',
         '<b>Choose what shows:</b> turns each counter on and off. What shows at first is the list of the Shugo.GG app, plus '
         'Nightmare and Shugo Festival. Dimensional Invasion, Abyss Corridors, Subjugation, Silent Graveyard, Fafnite '
         'Amphitheater, final bosses and Exploration per dungeon start turned off.'),
        ('<b>Sanctuary:</b> os três raids vêm desligados, porque em 13/out/2026 nenhum estava aberto no Global. O Abyssal '
         'Forge: Ludra saiu do ar no lançamento e a NCSOFT ainda vai anunciar a volta; ligue em “Escolher o que aparece” quando abrir.',
         '<b>Sanctuary:</b> the three raids start turned off, because on 13 Oct 2026 none was open on Global. Abyssal Forge: '
         'Ludra was taken down at launch and NCSOFT has yet to announce its return; turn them on under “Choose what shows” when '
         'they open.'),
        ('<b>Reset:</b> todo dia às 07:00 UTC (04:00 em Brasília); o semanal é na quarta, no mesmo horário. No jogo, o '
         'tooltip de cada contador mostra a contagem oficial.',
         '<b>Reset:</b> every day at 07:00 UTC (04:00 in Brasília); the weekly one is on Wednesday, at the same time. In '
         'the game, the tooltip of each counter shows the official countdown.'),
        ('<b>Se a página ficar fechada por dias,</b> ela aplica ao abrir os resets que passaram.',
         '<b>If the page stays closed for days,</b> it applies the resets that went by when you open it.'),
        (f'Lista e limites do que aparece de início: app do Shugo.GG, em 13/out/2026. Nightmare, Festival Shugo, o que muda com '
         f'a assinatura e os contadores desligados: tabela do cliente Global publicada pelo {link}, lida no mesmo dia.',
         f'List and limits of what shows at first: the Shugo.GG app, on 13 Oct 2026. Nightmare, Shugo Festival, what the '
         f'subscription changes and the counters that start off: the Global client table published by {link}, read the same day.'),
    )
    english.update({'Rotina': 'Routine', 'Diário e semanal, com reset automático': 'Daily and weekly, with automatic reset',
                    'Rotina diária e semanal': 'Daily and weekly routine', 'Como funciona': 'How it works'})
    return {
        'title': 'Rotina', 'subtitle': 'Diário e semanal, com reset automático',
        'sections': [
            {'id': 'rot-rotina', 'title': 'Rotina diária e semanal', 'meta': '', 'html': tool},
            {'id': 'rot-como-funciona', 'title': 'Como funciona', 'meta': '', 'html': how},
        ],
    }
