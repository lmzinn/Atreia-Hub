"""The 'Minha build' part: the build editor (drawn by the page script into #builder). Its data is builder_data.json
and builder_icons.json, made by bld_data.py from wikily.gg, read on 13 Oct 2026. The text lives here, in Portuguese
and English."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'builder_data.json')
ICONS = os.path.join(HERE, 'builder_icons.json')
WIKILY = 'https://wikily.gg/aion-2/'


def builder_data():
    return json.load(open(DATA, encoding='utf8'))


def builder_icons():
    return json.load(open(ICONS, encoding='utf8')) if os.path.exists(ICONS) else {}


def builder_part(strings, english):
    """Same shape as guide_convert.convert(); every text goes to `strings` and its English version to `english`."""
    def el(tag, pt, en, cls=''):
        strings.append(pt)
        english[pt] = en
        c = f' class="{cls}"' if cls else ''
        return f'<{tag}{c} data-t="{len(strings) - 1}">{pt}</{tag}>'

    def ul(*items):
        return '<ul>' + ''.join(el('li', pt, en) for pt, en in items) + '</ul>'

    link = f'<a href="{WIKILY}" target="_blank" rel="noopener">wikily.gg</a>'
    tool = (
        el('p', 'Monte a build de qualquer classe: skills, specs, stigmas, Daevanion, equipamento, títulos, Arcana, asas e '
                'notas. Fica salva neste navegador; use “Copiar link” para mandar para alguém.',
           'Put together the build of any class: skills, specs, stigmas, Daevanion, gear, titles, Arcana, wings and notes. '
           'It is saved in this browser; use “Copy link” to send it to someone.')
        + '<div id="builder" class="tool"></div>')
    how = ul(
        ('<b>Várias builds:</b> “Nova” cria outra, “Duplicar” copia a atual (útil para PvE e PvP). Os botões no alto trocam '
         'entre elas.',
         '<b>Several builds:</b> “New” creates another one, “Duplicate” copies the current one (handy for PvE and PvP). '
         'The buttons at the top switch between them.'),
        ('<b>Copiar link:</b> gera um endereço com a build aberta; quem abrir recebe uma cópia dela, sem apagar as suas.',
         '<b>Copy link:</b> makes an address with the open build; whoever opens it gets a copy of it, without losing theirs.'),
        ('<b>Nível treinado:</b> o que você comprou com Skill Points (até 10) ou Stigma Shards (até 20). A página soma o '
         'que foi gasto; ela não sabe quantos pontos o seu personagem tem.',
         '<b>Trained level:</b> what you bought with Skill Points (up to 10) or Stigma Shards (up to 20). The page adds up '
         'what was spent; it does not know how many points your character has.'),
        ('<b>Nível final:</b> treinado + Daevanion + equipamento. O “+ Daevanion” vem sozinho dos nós pegos na aba '
         'Daevanion; o “+ equipamento” você digita.',
         '<b>Final level:</b> trained + Daevanion + gear. “+ Daevanion” comes by itself from the nodes taken on the '
         'Daevanion tab; “+ gear” you type in.'),
        ('<b>Specs:</b> cabe 1 a partir do nível final 8, 2 a partir do 12 e 3 a partir do 20. Cada spec só pode ser '
         'escolhida quando a skill chega ao nível em que ela abre (passe o mouse para ver).',
         '<b>Specs:</b> 1 fits from final level 8, 2 from 12 and 3 from 20. A spec can only be picked once the skill '
         'reaches the level at which it opens (hover to see it).'),
        ('<b>Stigmas:</b> marque “Equipado” em até 4.', '<b>Stigmas:</b> tick “Equipped” on up to 4.'),
        ('<b>Daevanion:</b> clicar num nó distante pega também o caminho mais barato até ele. Os quatro primeiros '
         'tabuleiros somam nos Daevanion Crystals; o Azphel tem cristais próprios.',
         '<b>Daevanion:</b> clicking a far node also takes the cheapest path to it. The first four boards add up under '
         'Daevanion Crystals; Azphel has crystals of its own.'),
        ('<b>Equipamento:</b> a lista de cada slot já vem filtrada pela arma da classe e pela facção.',
         '<b>Gear:</b> the list of each slot is already filtered by the class weapon and by the faction.'),
        ('<b>O que não tem campo próprio</b> (Manastones, Soul Binding, rotação, barra de skills) vai na aba Notas.',
         '<b>What has no field of its own</b> (Manastones, Soul Binding, rotation, skill bar) goes on the Notes tab.'),
        (f'Dados de skills, tabuleiros, itens, títulos, Arcana, asas e pets: {link}, lido em 13/out/2026. Depois de um '
         'patch do jogo os números podem mudar.',
         f'Skill, board, item, title, Arcana, wing and pet data: {link}, read on 13 Oct 2026. After a game patch the '
         'numbers may change.'),
    )
    english.update({'Minha build': 'My build', 'Monte, salve e compartilhe a build de qualquer classe': 'Create, save and share the build of any class',
                    'Editor de build': 'Build editor', 'Como funciona o editor': 'How the editor works'})
    return {
        'title': 'Minha build', 'subtitle': 'Monte, salve e compartilhe a build de qualquer classe',
        'sections': [
            {'id': 'bld-editor', 'title': 'Editor de build', 'meta': '', 'html': tool},
            {'id': 'bld-como-funciona', 'title': 'Como funciona o editor', 'meta': '', 'html': how},
        ],
    }
