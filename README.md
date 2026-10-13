# Atreia Hub - Aion 2

Site de apoio para Aion 2 (servidores Global), feito por fãs: tudo num lugar só.

- **Rotina:** entradas diárias e limites semanais por personagem, com reset automático.
- **Minha build:** editor de build para as 8 classes (skills, specs, stigmas, Daevanion, equipamento, títulos, Arcana, asas), com salvar e carregar em arquivo.
- **Progressão:** objetivos por faixa de Gear Score, com checklist.
- **Crafting:** calculadora de craft de várias peças, calculadora de aprimoramento, linha Dragon Lord e Essence Extraction.
- **Configurações:** configuração de referência, com espaço para anotar a sua.

O site é um arquivo só (`index.html`), em português e inglês. O que você marca fica salvo no seu navegador; nada é enviado para servidor.

## Créditos

- Dados do jogo (skills, tabuleiros, itens, receitas, custos, limites): [wikily.gg](https://wikily.gg/aion-2).
- Crafting: planilha [Aion 2 Content Guide](https://docs.google.com/spreadsheets/d/1bNxC1wd0S_ILGYAyWnO0aTo_G_AOrjkv7bTcOj_NRz8/), do Screamheart.
- Progressão: baseada no guia de início indicado na própria página.

Site de fãs, sem vínculo com a NCSOFT. Aion 2 e seus nomes, ícones e dados pertencem à NCSOFT.

## Como gerar

Precisa de Python 3.

```bash
py -I gerador/guide_build.py
```

Isso refaz o `index.html` a partir de `fontes/` (os DOCX das páginas de texto) e de `gerador/` (o modelo da página, as páginas escritas em Python e os dados em JSON).

Os scripts `wk_all.py`, `bld_data.py`, `craft_data.py`, `enh_fetch.py`, `enh_data.py` e `routine_data.py`, em `gerador/`, baixam os dados do wikily de novo e refazem os JSON; servem para depois de um patch do jogo.
