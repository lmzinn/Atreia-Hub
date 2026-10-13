"""The 'Rotina' part of the guide: daily and weekly limits with counters that reset by themselves (drawn by the page
script into #routine). The list of activities is routine_data.json, made by routine_data.py from wikily.gg's Homework
Checklist, read on 13 Oct 2026. The text lives here, in Portuguese and English."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'routine_data.json')
WIKILY = 'https://wikily.gg/aion-2/homework'


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

    link = f'<a href="{WIKILY}" target="_blank" rel="noopener">Homework Checklist</a>'
    tool = (
        el('p', 'O que dá para fazer hoje e nesta semana, por personagem. Use − e + conforme for gastando as entradas; a '
                'página recarrega e zera sozinha no reset.',
           'What can be done today and this week, per character. Use − and + as you spend the entries; the page '
           'recharges and clears by itself at the reset.')
        + '<div id="routine" class="tool"></div>')
    how = ul(
        ('<b>Entradas que acumulam:</b> recarregam todo dia e ficam guardadas até um máximo. O número é quantas você '
         'tem agora: aperte − a cada entrada usada. Na primeira vez, ajuste para o que o jogo mostra.',
         '<b>Entries that stack up:</b> they recharge every day and are kept up to a cap. The number is how many you '
         'have now: press − for each entry you use. The first time, set it to what the game shows.'),
        ('<b>“No máximo”:</b> a entrada já está no teto, então a recarga do próximo reset se perde. É a primeira a gastar.',
         '<b>“At the cap”:</b> the entry is already at its cap, so the recharge of the next reset is lost. Spend it first.'),
        ('<b>Limites da semana:</b> o número é quantas você já fez. Volta a zero no reset semanal.',
         '<b>Weekly limits:</b> the number is how many you have done. It goes back to zero at the weekly reset.'),
        ('<b>Reset:</b> todo dia às 07:00 UTC (04:00 em Brasília); o semanal é na quarta, no mesmo horário. A página '
         'mostra no horário do seu computador. No jogo, o tooltip de cada contador mostra a contagem oficial.',
         '<b>Reset:</b> every day at 07:00 UTC (04:00 in Brasília); the weekly one is on Wednesday, at the same time. The '
         'page shows it in your computer\'s time. In the game, the tooltip of each counter shows the official countdown.'),
        ('<b>Se a página ficar fechada por dias,</b> ela soma as recargas dos dias que passaram ao abrir.',
         '<b>If the page stays closed for days,</b> it adds the recharges of the days that went by when you open it.'),
        ('<b>Escolher o que aparece:</b> esconde as atividades que você não faz. Vale para todos os personagens.',
         '<b>Choose what shows:</b> hides the activities you do not do. It applies to every character.'),
        ('<b>Personagens:</b> até 6, cada um com os próprios números. O campo Nome troca o nome da aba.',
         '<b>Characters:</b> up to 6, each with its own numbers. The Name field renames the tab.'),
        ('Com membership, o Shugo Festival guarda até 21 em vez de 12; a página usa 12.',
         'With a membership, Shugo Festival stores up to 21 instead of 12; the page uses 12.'),
        (f'Lista e limites: {link} do wikily.gg, lido em 13/out/2026.',
         f'List and limits: wikily.gg\'s {link}, read on 13 Oct 2026.'),
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
