# `_build/` — рабочие материалы для wiki архитектуры

Эта директория — **часть документации**. Содержит исходники и
данные, из которых генерируются страницы `docs/graphify/wiki/*.html`,
доступные на сайте https://docs.billing.smit34.ru/graphify/wiki/.

## Зачем эта папка существует

Wiki сообществ (`docs/graphify/wiki/`) — публикуемые HTML.
Чтобы **обновлять** их без ручной правки 21 страницы, нужны:

- скрипты-генераторы (`scripts/`),
- исходные данные графа (`data/`),
- исторические артефакты vis-network графов на сообщество (`historical/`).

Всё в этой папке версионируется в git и зеркалится в репозиторий
[ircitdev/docs.billing.smit34.ru](https://github.com/ircitdev/docs.billing.smit34.ru)
автоматически через `sync-docs.sh`.

## Структура

```
docs/graphify/_build/
├── README.md               ← этот файл
│
├── scripts/                ← Python-скрипты сборки
│   ├── generate_wiki.py    ← генератор index.html + community_N.html
│   ├── build_wiki_graphs.py ← извлекает RAW_NODES/EDGES → JSON для Schema-вкладки
│   └── icons.py            ← словари ICONS/ICON_PATHS (Tabler SVG path-d)
│
├── data/                   ← входные данные графа (источник истины)
│   ├── .graphify_extract.json    ← все ноды + edges (~5 MB)
│   ├── .graphify_analysis.json   ← communities + cohesion + gods (~100 KB)
│   ├── .graphify_labels.json     ← человеческие имена сообществ
│   └── GRAPH_REPORT.md           ← итоговый отчёт о структуре графа (~140 KB)
│
└── historical/             ← snapshot vis-network графов на каждое community
    └── graph_c{0..46}.html ← RAW_NODES/EDGES источник для build_wiki_graphs.py
```

## Что НЕ хранится в git (создаётся локально)

- `cache/` — LLM-кеш семантических чанков (37 MB)
- `converted/` — промежуточные текстовые конверсии
- `.graphify_ast.json` — AST-снапшот всего кода (~5 MB)
- `.graphify_cached.json` / `.graphify_uncached.txt` — служебные
- `graph.json` — полный граф dump (~25 MB, не нужен для wiki)

Эти артефакты лежат в `carbon_modern/graphify-out/` (за пределами `docs/`)
и пересоздаются командой `graphify` CLI.

## Как обновить wiki — типичный workflow

### Сценарий А: только мелкая правка дизайна wiki

> Например — поменял CSS, добавил новую колонку в таблицу нод,
> поменял текст подсказки — данные графа не трогал.

```bash
cd docs/graphify/_build/scripts
python generate_wiki.py        # → docs/graphify/wiki/*.html
cd ../../
bash sync-docs.sh "wiki: cosmetic update"
```

### Сценарий Б: код проекта изменился — нужен новый граф

> Когда добавил новые модули, переименовал классы, изменил
> архитектуру и хочешь чтобы граф это отразил.

Внешний инструмент — [graphify CLI](https://github.com/anthropics/graphify):

```bash
# 1. Перестроить граф из текущего кода
cd carbon_modern
graphify update .                    # обновляет AST + кеш
graphify build                       # делает .graphify_extract.json + analysis

# 2. Обновить labels (если появились новые сообщества)
cd graphify-out
python run_labels.py                 # обновит labels.json + GRAPH_REPORT.md
                                     # + перегенерит graph.html + graph_c*.html

# 3. Скопировать обновлённые data + historical в _build/
cp .graphify_extract.json   ../docs/graphify/_build/data/
cp .graphify_analysis.json  ../docs/graphify/_build/data/
cp .graphify_labels.json    ../docs/graphify/_build/data/
cp GRAPH_REPORT.md          ../docs/graphify/_build/data/
cp graph_c*.html            ../docs/graphify/_build/historical/

# 4. (если в run_labels.py добавил новые иконки) — обновить icons.py
#    Простой способ: скопировать ICONS/ICON_PATHS блок из run_labels.py
#    в _build/scripts/icons.py (заменив старые словари)

# 5. Сгенерировать wiki + вытащить графы для Schema-вкладки
cd ../docs/graphify/_build/scripts
python generate_wiki.py
python build_wiki_graphs.py

# 6. Развернуть на live + push в зеркало
cd ../../
bash sync-docs.sh "wiki: rebuild after code refactor"
```

### Сценарий В: только переименовать сообщество

> Например, cid=8 «Резервные копии» → «Бэкапы».

```bash
# 1. Открыть _build/data/.graphify_labels.json
#    Изменить значение для нужного "cid"
# 2. Регенерировать
cd docs/graphify/_build/scripts
python generate_wiki.py
# 3. Деплой
cd ../../
bash sync-docs.sh "wiki: rename community 8"
```

## Как `sync-docs.sh` зеркалит изменения в GitHub

Скрипт `docs/sync-docs.sh` выполняет 4 шага:

1. **Auto-update version.js** из `billing/version.py` + git log
2. **Rebuild search-index.json** — индекс h2/h3/h4 для глобального поиска
3. **Mirror в `2026Carbon/docs/`** — отдельный git-репо
   `ircitdev/docs.billing.smit34.ru`, push в `main`
4. **Deploy на сервер** — `tar + scp` в `/var/www/docs.billing.smit34.ru/`
   на `31.44.7.144` (DNS docs.billing.smit34.ru)

Папка `_build/` целиком включается в зеркало — пользователи на GitHub
смогут видеть исходники сборки. Размер: **~7 MB** (data 5MB + historical
~2MB) — приемлемо для git.

## Зависимости скриптов

`generate_wiki.py`:
- Python 3.7+ (использует f-strings)
- Без внешних библиотек, всё на stdlib (`json`, `pathlib`, `re`, `html`)
- Загружает локальный `icons.py` для Tabler-иконок

`build_wiki_graphs.py`:
- Python 3.7+, stdlib only
- Парсит regex-ом `RAW_NODES/RAW_EDGES` из `historical/graph_c*.html`

## Полезные ссылки

- Wiki архитектуры: https://docs.billing.smit34.ru/graphify/wiki/
- Главный граф: https://docs.billing.smit34.ru/graphify/graph.html
- Wiki по конкретному сообществу: `community_{cid}.html` (cid 0..20 — публикуются, 21..46 < 10 нод не публикуются)
- graphify CLI: https://github.com/anthropics/graphify (внешний инструмент)
