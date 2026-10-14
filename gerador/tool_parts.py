"""Small parts drawn by the page script: 'Onde consigo?' (#finder: where a material or item comes from; data in
finder_data.json, made by finder_data.py from wikily.gg) and the site settings (#settings). The text lives here, in
Portuguese and English."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FINDER = os.path.join(HERE, 'finder_data.json')
NEWS = os.path.join(HERE, 'novidades.json')


def finder_data():
    return json.load(open(FINDER, encoding='utf8')) if os.path.exists(FINDER) else []


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
    tool = (
        el('p', 'Digite o nome de um material, item, Arcana, asa ou título para ver de onde ele vem.',
           'Type the name of a material, item, Arcana, wings or title to see where it comes from.')
        + '<div id="finder" class="tool"></div>'
        + el('p', 'Origens segundo o <a href="https://wikily.gg/aion-2/items" target="_blank" rel="noopener">wikily.gg</a>, lido em '
                  '13/out/2026. Mostra até seis origens por item.',
             'Sources according to <a href="https://wikily.gg/aion-2/items" target="_blank" rel="noopener">wikily.gg</a>, read on '
             '13 Oct 2026. It shows up to six sources per item.', 'note'))
    english.update({'Onde consigo?': 'Where do I get it?', 'De onde vem cada material, item e título': 'Where each material, item and title comes from',
                    'Busca de origem': 'Source search'})
    return {'title': 'Onde consigo?', 'subtitle': 'De onde vem cada material, item e título',
            'sections': [{'id': 'find-busca', 'title': 'Busca de origem', 'meta': '', 'html': tool}]}


def settings_part(strings, english):
    el = _writer(strings, english)
    tool = (el('p', 'Como o site aparece e avisa. Vale só para este navegador.', 'How the site looks and reminds you. It applies to this browser only.')
            + '<div id="settings" class="tool"></div>')
    english.update({'Configurações': 'Settings', 'Aparência, lembretes e dados do site': 'Look, reminders and data of the site',
                    'Configurações do site': 'Site settings'})
    return {'title': 'Configurações', 'subtitle': 'Aparência, lembretes e dados do site',
            'sections': [{'id': 'set-site', 'title': 'Configurações do site', 'meta': '', 'html': tool}]}
