# docs/tools/

Скрипты для поддержки документации `docs.billing.smit34.ru`.

## audit_docs_headers.py

Аудит иерархии заголовков h1-h4 во всех `docs/pages/*.html`. Выявляет:

- **MULTIPLE_H1** / **NO_H1** — несколько h1 на странице или ни одного
- **NO_ID** — h2/h3/h4 без `id="..."` (нельзя сослаться)
- **DUPLICATE_IDS** — два разных заголовка с одинаковым id
- **EMPTY** — пустые заголовки
- **LEVEL_SKIP** — скачок уровня (h1→h3, h2→h4)
- **ORPHAN_H3 / ORPHAN_H4** — h3 без родительского h2, h4 без h3
- **BAD_ID** — id с пробелом или кириллицей

```bash
PYTHONIOENCODING=utf-8 python docs/tools/audit_docs_headers.py
```

Не модифицирует файлы.

## fix_docs_headers.py

Автоматически добавляет `id="..."` ко всем `<h2>` и `<h3>` без id (h4 не трогает).
Slug формируется транслитом русского названия: `Логин через Web (получение сессии)` → `login-cherez-web-poluchenie-sessii`. Уникальность гарантируется (при дубле добавляется `-2`, `-3`).

```bash
python docs/tools/fix_docs_headers.py --dry-run
python docs/tools/fix_docs_headers.py
```

## check_billing_doc_links.py

Сверяет все ссылки `docs.billing.smit34.ru/pages/X.html#anchor` из биллинг-кода (`billing/`, `lk/`, `mobile_api/`, `config/`) с реальными `id="..."` в `docs/pages/*.html`. Находит broken links + предлагает похожие якоря.

```bash
PYTHONIOENCODING=utf-8 python docs/tools/check_billing_doc_links.py
```

Возвращает exit code 1 если есть broken links — можно использовать в CI.

## audit_docs_toc.py

Анализирует структуру h2/h3/h4 в `docs/pages/*.html` и выявляет проблемы в блоках «Содержание раздела» (`<div class="section-toc">`):

- **NO TOC** — раздел с ≥2 дочерних, но без TOC
- **STALE** — ссылка в TOC на якорь, которого нет в документе
- **MISSING** — якорь дочернего раздела без записи в TOC
- **OK** — TOC синхронизирован

```bash
cd carbon_modern
python docs/tools/audit_docs_toc.py
```

Не модифицирует файлы.

## fix_docs_toc.py

Автоматически создаёт/обновляет/удаляет блоки `section-toc`:

1. Внутри каждого `<h2 id>` с **≥2** дочерних `<h3 id>` — TOC сразу после h2
2. Внутри каждого `<h3 id>` с **≥2** дочерних `<h4 id>` — TOC сразу после h3
3. Если разделов 0-1 — TOC удаляется (если был)
4. Существующие TOC синхронизируются с реальной структурой документа

```bash
cd carbon_modern
python docs/tools/fix_docs_toc.py --dry-run   # посмотреть что изменится
python docs/tools/fix_docs_toc.py             # применить
```

После применения — `cd docs && bash sync-docs.sh "..."` для деплоя.

## Когда запускать

- После добавления/переименования/удаления `<h2 id>`, `<h3 id>` или `<h4 id>` в любой странице
- Перед публикацией крупных изменений в docs
- В рамках периодического hygiene check
- **После `fix_docs_headers.py`** — обязательно `check_billing_doc_links.py`, чтобы убедиться что переименованные id не сломали info-иконки в биллинге

## Полный workflow для крупного редактирования docs

```bash
cd d:/DevTools/Database/2026Carbon/carbon_modern

# 1. Правим контент в docs/pages/<page>.html

# 2. Проверяем иерархию + добавляем id
PYTHONIOENCODING=utf-8 python docs/tools/audit_docs_headers.py
python docs/tools/fix_docs_headers.py

# 3. Регенерируем TOC
python docs/tools/fix_docs_toc.py

# 4. Сверяем ссылки из биллинга
PYTHONIOENCODING=utf-8 python docs/tools/check_billing_doc_links.py
# → если есть broken — править биллинг-templates

# 5. Финальный аудит (всё OK?)
PYTHONIOENCODING=utf-8 python docs/tools/audit_docs_headers.py
python docs/tools/audit_docs_toc.py

# 6. Sync (с workaround для /tmp на Windows)
cd docs && bash sync-docs.sh "docs: ..."
cd ..
scp docs/pages/*.html docs/search-index.json root@31.44.7.144:/var/www/docs.billing.smit34.ru/
# (СЕРВЕР: 31.44.7.144, НЕ testbill — см. memory/docs_site.md)
```

## Версия и дата в подвале — авто-подстановка

`docs/js/version.js` — единый источник истины для подвала docs-сайта (`Обновлено: DD.MM.YYYY`, `v1.6.0 (build NNN)`). С build 380+ файл **авто-генерируется** при каждом запуске `sync-docs.sh` (шаг `0a`):

- **VERSION / BUILD** — из `billing/version.py` (бампается при каждом деплое биллинга)
- **updated** — дата последнего git-коммита, затронувшего `carbon_modern/docs/` (`git log -1 --format=%cI -- docs/`)
- **year** — текущий год

Ручные правки `version.js` будут **затёрты** при следующем `sync-docs.sh`. Чтобы изменить версию — править только `billing/version.py`.
