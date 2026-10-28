# Atreia Hub - Aion 2

Site de apoio para Aion 2 (servidores Global), feito por fãs: tudo num lugar só.

- **Rotina:** entradas diárias e limites semanais por personagem, com reset automático.
- **Minha build:** editor de build para as 8 classes (skills, specs, stigmas, barra de skills, Daevanion com zoom e os seis tabuleiros, Ariel incluído, equipamento com o bônus de aprimoramento, títulos, Arcana, asas), compartilhado por link.
- **Meu personagem:** busca o personagem pelo nome na página oficial do Aion 2 e mostra a ficha (equipamento, Arcanas, Daevanion, skills, atributos, títulos); com um clique vira uma build no editor ou um personagem da Rotina. O personagem ativo fica no canto de cima da página, com um botão que busca a ficha de novo e atualiza a build feita dela, o Crafting (classe e peças que já tem), a calculadora de aprimoramento (peça e nível atual) e os cristais de Daevanion.
- **Progressão:** objetivos por faixa de Gear Score, com checklist.
- **Crafting:** calculadora de craft organizada como no jogo, por profissão, com as cerca de 540 receitas (a linha Dragon Lord com a conta das Splendent), materiais processados abertos no que são feitos, calculadora de aprimoramento e onde pôr os pontos de Essence Extraction.
- **Database:** armas, armaduras, joias, Arcanas, pets, asas, títulos, consumíveis, materiais, pedras, skills, dungeons, monstros e receitas (mais de 5.000 entradas), com filtros, atributos, origem, onde é usado e o botão “Ir para o Crafting”.
- **Timers:** no canto de todas as páginas, os resets diário e semanal, o evento que está acontecendo e os próximos, com lembrete em cada um.
- **Configurações:** tema, nove cores de destaque, idioma, timers no canto e lembretes de evento (aviso na tela, som e notificação do navegador).

O site é um arquivo só (`index.html`), em português e inglês, mais a pasta `database/` com os dados e os ícones do Database (carregados só quando a página abre). O que você marca fica salvo no seu navegador; nada é enviado para servidor. A única consulta externa é a do “Meu personagem”, que pergunta à página oficial do Aion 2 pelo personagem buscado.

## Créditos

- Dados e ícones do jogo (skills, tabuleiros, itens, receitas, custos, limites): [wikily.gg](https://wikily.gg/aion-2).
- Bônus de aprimoramento do equipamento: armaria oficial do jogo (aion2.plaync.com). Horários dos eventos: [shugo.gg](https://shugo.gg/timers).
- Contadores da Rotina e arte de algumas dungeons: [metabot.gg](https://metabot.gg/en/aion-2). Imagem do Dimensional Invasion: [thegameswiki.com](https://thegameswiki.com/aion-2).
- Crafting: planilha [Aion 2 Content Guide](https://docs.google.com/spreadsheets/d/1bNxC1wd0S_ILGYAyWnO0aTo_G_AOrjkv7bTcOj_NRz8/), do Screamheart.
- Progressão: baseada no [documento de progressão inicial](https://docs.google.com/document/d/1Iu01j2KDeZ4ebVKifo42SaWYmp7WTBHVw5YKRjLgX1U/edit?tab=t.0) do guia de início.

Site de fãs, sem vínculo com a NCSOFT. Aion 2 e seus nomes, ícones e dados pertencem à NCSOFT.

## Como gerar

Precisa de Python 3.

```bash
py -I gerador/guide_build.py
```

Isso refaz o `index.html` a partir de `fontes/` (os DOCX das páginas de texto) e de `gerador/` (o modelo da página, as páginas escritas em Python e os dados em JSON).

Os scripts `wk_all.py`, `bld_data.py`, `craft_data.py`, `enh_fetch.py`, `enh_data.py`, `routine_data.py`, `icons_data.py` e `db_data.py`, em `gerador/`, baixam os dados do wikily de novo e refazem os JSON e as imagens; servem para depois de um patch do jogo. Os dois últimos precisam do Pillow.

O bônus de aprimoramento vem da armaria oficial: `enh_fetch_bonus.py` lê o equipamento de personagens em `enh_raw.json` (só responde para a peça que o personagem está usando) e `enh_bonus.py` monta a tabela do editor (`enh_bonus.json`, também gravada em `builder_data.json`).

## Meu personagem e a página oficial

A página oficial do Aion 2 só responde para o próprio site, então a busca passa por uma ponte:

- **No computador:** `py -I gerador/servidor_local.py` abre o site em http://127.0.0.1:5176/ e faz a ponte. Uma cópia do site aberta como arquivo também usa esse servidor enquanto ele estiver ligado.
- **No site publicado:** um Cloudflare Worker gratuito com o código de `gerador/aion2_worker.js`. O endereço dele vai em `API_REMOTE`, no `gerador/guide_template.html`. Enquanto estiver vazio, a página avisa que a busca ainda não está ligada.

As duas pontes só repassam seis endereços de leitura (busca, servidores, ficha, equipamento, peça e Daevanion).
