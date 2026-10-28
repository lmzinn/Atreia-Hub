"""Small parts drawn by the page script: the Database (#db: data in ../database, made by db_data.py from wikily.gg),
Meu personagem (#me) and the site settings (#settings). The text lives here, in Portuguese and English."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NEWS = os.path.join(HERE, 'novidades.json')


def news_data():
    return json.load(open(NEWS, encoding='utf8')) if os.path.exists(NEWS) else []


def _writer(strings, english):
    def el(tag, pt, en, cls=''):
        strings.append(pt)
        english[pt] = en
        c = f' class="{cls}"' if cls else ''
        return f'<{tag}{c} data-t="{len(strings) - 1}">{pt}</{tag}>'
    return el


def finder_part(strings, english):
    el = _writer(strings, english)
    tool = (el('p', 'Itens, monstros, dungeons, skills e títulos do jogo: busque pelo nome ou abra uma categoria. No item com '
                    'receita, “Ir para o Crafting” leva ele para a calculadora.',
               'Items, monsters, dungeons, skills and titles of the game: search by name or open a category. On an item with a '
               'recipe, “Go to Crafting” takes it to the calculator.')
            + '<div id="db" class="tool"></div>')
    english.update({'Database': 'Database', 'Itens, monstros, dungeons, skills e títulos do jogo': 'Items, monsters, dungeons, skills and titles of the game'})
    return {'title': 'Database', 'subtitle': 'Itens, monstros, dungeons, skills e títulos do jogo',
            'sections': [{'id': 'find-db', 'title': 'Database', 'meta': '', 'html': tool}]}


def me_part(strings, english):
    el = _writer(strings, english)
    tool = (el('p', 'Busque o seu personagem pelo nome para ver a ficha do jogo e levar equipamento, skills e Daevanion '
                    'para o editor de build.',
               'Look up your character by name to see its in-game sheet and take its gear, skills and Daevanion to the '
               'build editor.')
            + '<div id="me" class="tool"></div>'
            + el('p', 'Os dados vêm da página oficial de personagens do Aion 2 (aion2.plaync.com), na hora em que você busca. '
                      'Ficam salvos só neste navegador.',
                 'The data comes from the official Aion 2 character page (aion2.plaync.com) at the moment you look it up. '
                 'It is saved in this browser only.', 'note'))
    english.update({'Meu personagem': 'My character', 'A ficha do jogo e a importação para o editor de build': 'The in-game sheet and the import to the build editor',
                    'Ficha do personagem': 'Character sheet'})
    return {'title': 'Meu personagem', 'subtitle': 'A ficha do jogo e a importação para o editor de build',
            'sections': [{'id': 'me-ficha', 'title': 'Ficha do personagem', 'meta': '', 'html': tool}]}


def settings_part(strings, english):
    el = _writer(strings, english)
    tool = (el('p', 'Como o site aparece e avisa. Vale só para este navegador.', 'How the site looks and reminds you. It applies to this browser only.')
            + '<div id="settings" class="tool"></div>')
    english.update({'Configurações': 'Settings', 'Aparência, lembretes e dados do site': 'Look, reminders and data of the site',
                    'Configurações do site': 'Site settings'})
    return {'title': 'Configurações', 'subtitle': 'Aparência, lembretes e dados do site',
            'sections': [{'id': 'set-site', 'title': 'Configurações do site', 'meta': '', 'html': tool}]}
