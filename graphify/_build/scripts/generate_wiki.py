#!/usr/bin/env python3
"""
generate_wiki.py — генератор wiki архитектуры.

Читает данные графа из ../data/.graphify_*.json, выдаёт HTML в
../../wiki/ (docs/graphify/wiki/index.html + community_{cid}.html).

Запуск (из любой директории, использует __file__):
    python docs/graphify/_build/scripts/generate_wiki.py

Полная инструкция по сборке: docs/graphify/_build/README.md
"""

import json
import os
import sys
import importlib.util
from pathlib import Path
from collections import defaultdict

# ── Paths ──────────────────────────────────────────────────────────────────────
# Layout (часть docs):
#   docs/graphify/_build/scripts/   ← здесь этот файл
#   docs/graphify/_build/data/      ← *.json + GRAPH_REPORT.md
#   docs/graphify/wiki/             ← публикуемые страницы
SCRIPT_DIR = Path(__file__).parent                  # _build/scripts/
BUILD_DIR = SCRIPT_DIR.parent                        # _build/
DOCS_GRAPHIFY = BUILD_DIR.parent                     # docs/graphify/
OUT_DIR = DOCS_GRAPHIFY / "wiki"                     # публикуемая wiki

DATA_DIR = BUILD_DIR / "data"
EXTRACT_FILE = DATA_DIR / ".graphify_extract.json"
ANALYSIS_FILE = DATA_DIR / ".graphify_analysis.json"
LABELS_FILE = DATA_DIR / ".graphify_labels.json"

# Совместимость со старыми импортами/path-helpers ниже по коду
BASE = SCRIPT_DIR

# ── Import ICONS + ICON_PATHS from icons.py (extracted from run_labels.py) ────
def _load_icons():
    """Загружает COMM_ICONS + ICON_PATHS из локального icons.py.

    Раньше брал прямо из graphify-cli's run_labels.py (внешняя зависимость),
    теперь — из соседнего модуля icons.py (часть документации, в git).
    Регенерация: graphify pipeline → run_labels.py → скопировать словари
    в icons.py (см. _build/README.md шаг 4).
    """
    try:
        sys.path.insert(0, str(BASE))
        import icons as _icons  # noqa: WPS433  # локальный модуль рядом
        return getattr(_icons, "ICONS", {}), getattr(_icons, "ICON_PATHS", {})
    except Exception as e:
        print(f"⚠ Could not load icons.py: {e}", file=sys.stderr)
        return {}, {}

COMM_ICONS, ICON_PATHS = _load_icons()

# ── Community filter: skip technical/irrelevant communities ───────────────────
# Drop communities with fewer than this many nodes (noise: tiny fragments, __init__.py)
MIN_NODE_COUNT = 10

# ── Community descriptions (shown on cards & header) ──────────────────────────
COMM_DESCRIPTIONS = {
    0:  "Views карточки абонента: открытие, редактирование, табы, быстрое добавление, карта.",
    1:  "Личный кабинет абонента: дашборд, оплата, тариф, обещанный платёж, блокировка.",
    2:  "Финансовые операции: FinanceOperations, MoneyField, счета, проводки, AtolConfig.",
    3:  "Глобальный поиск абонентов, мастер добавления, bulk-операции и массовые действия.",
    4:  "Mobile API /mobile-api/v1/: JWT, account/status, tariffs, push registration.",
    5:  "Core модели: Abonents, Users, AuthView, базовые представления и миграции.",
    6:  "ACL, права доступа, интеграции с соцсетями (VK, Telegram), ConnectionPoints.",
    7:  "Блокировки абонентов: AbonentsBlock, FirewallService, MikroTik, CoA.",
    8:  "Бэкапы: pg_dump, tar файлы, Docker backup пакеты, восстановление.",
    9:  "IPTV: интеграция с Lfstream, синхронизация, биллинг IPTV-услуг.",
    10: "Framework форм: ChangeView, formsets, вкладки, безопасные глобалы.",
    11: "Периодические Celery-задачи: billing_worker, abonent_block, sync.",
    12: "Шаблоны ЛК: базовый layout, AI-чат, уведомления, дашборд личного кабинета.",
    13: "Interface Framework: настройки отображения полей, группы, доступы.",
    14: "СОРМ-отчёты: экспорт в CSV/DBF, расписание FTP-выгрузки, форматы.",
    15: "Платёжные системы: YooKassa (HTTP+REST v3), Wallet One, универсальный webhook.",
    16: "Рассылка сообщений: email (SMTP), SMS (SMSAero), шаблоны MsgStack.",
    17: "Mobile-авторизация: JWT, Telegram OAuth, VK OAuth, login по договору.",
    18: "Firebase Cloud Messaging: регистрация токенов, push-уведомления абонентам.",
    19: "Модель финансового аккаунта: AdminAccounts, MoneyFormField, остатки.",
    20: "Webhooks от FreeScout: conversation.*, assignment, status_changed.",
    21: "OAuth-авторизация ЛК: вход через VK / Telegram, связка аккаунтов.",
    22: "Template filters для ЛК: форматирование денег, дат, адресов.",
}

# ── Colors (same as graph.html) ────────────────────────────────────────────────
COLORS = [
    '#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f',
    '#edc948','#b07aa1','#ff9da7','#9c755f','#bab0ac',
    '#d37295','#fabfd2','#8cd17d','#b6992d','#499894',
    '#86bcb6','#f1ce63','#a0cbe8','#ffbe7d','#8CD3C7',
]

# ── CSS shared across all pages ────────────────────────────────────────────────
SHARED_CSS = """
:root {
  --bg: #0f172a; --bg2: #1e293b; --bg3: #172033; --border: #334155;
  --text: #e2e8f0; --text2: #94a3b8; --text3: #64748b;
  --primary: #26a69a; --primary-l: #4db6ac;
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
}
[data-theme=light] {
  --bg: #f4f6f9; --bg2: #fff; --bg3: #f0f4f8; --border: #e2e8f0;
  --text: #1f2d3d; --text2: #475569; --text3: #94a3b8;
  --primary: #00897b; --primary-l: #26a69a;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font); background: var(--bg); color: var(--text);
  min-height: 100vh; font-size: 14px; line-height: 1.5;
}
a { color: var(--primary-l); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Header */
.site-header {
  background: var(--bg2); border-bottom: 1px solid var(--border);
  padding: 12px 24px; display: flex; align-items: center; gap: 16px;
  position: sticky; top: 0; z-index: 100;
}
.site-header h1 { font-size: 18px; font-weight: 700; color: var(--primary-l); flex: 1; }
.site-header .subtitle { color: var(--text2); font-size: 12px; }
.nav-links { display: flex; gap: 8px; }
.nav-link {
  color: var(--text2); font-size: 13px; padding: 4px 10px;
  border: 1px solid var(--border); border-radius: 6px;
  transition: all 0.15s;
}
.nav-link:hover { color: var(--primary-l); border-color: var(--primary); text-decoration: none; }

/* Theme toggle */
.theme-btn {
  background: var(--bg3); border: 1px solid var(--border); color: var(--text2);
  padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 13px;
  transition: all 0.15s;
}
.theme-btn:hover { color: var(--primary-l); border-color: var(--primary); }

/* Main layout */
.main { padding: 24px; max-width: 1400px; margin: 0 auto; }

/* Search */
.search-wrap { margin-bottom: 24px; }
.search-input {
  width: 100%; padding: 10px 16px; font-size: 15px;
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 8px; color: var(--text); outline: none;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: var(--primary); }
.search-input::placeholder { color: var(--text3); }

/* Table */
.tbl-wrap { overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 9px 14px; text-align: left; border-bottom: 1px solid var(--border); }
th {
  background: var(--bg3); color: var(--text2); font-weight: 600;
  font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em;
  cursor: pointer; user-select: none; white-space: nowrap;
}
th:hover { color: var(--primary-l); }
th .sort-icon { margin-left: 4px; opacity: 0.4; font-style: normal; }
th.sorted-asc .sort-icon::after { content: '▲'; opacity: 1; }
th.sorted-desc .sort-icon::after { content: '▼'; opacity: 1; }
th .sort-icon::after { content: '⇅'; }
tr:last-child td { border-bottom: none; }
tbody tr { transition: background 0.1s; }
tbody tr:hover { background: var(--bg3); }

/* Badges — цветовая маркировка типов нод */
.badge {
  display: inline-block; padding: 2px 9px; border-radius: 12px;
  font-size: 11px; font-weight: 600; white-space: nowrap;
  border: 1px solid transparent;
}
/* code → синий: Python/JS-исходники */
.badge-code     { background: rgba(78, 121, 167, 0.22); color: #93c5fd; border-color: rgba(78,121,167,.35); }
/* rationale → серый: архитектурные обоснования */
.badge-rationale{ background: rgba(148, 163, 184, 0.18); color: #cbd5e1; border-color: rgba(148,163,184,.3); }
/* document → зелёный: документация / readme */
.badge-document { background: rgba(89, 161, 79, 0.22);  color: #86efac; border-color: rgba(89,161,79,.35); }
/* template → фиолетовый: HTML-шаблоны */
.badge-template { background: rgba(176, 122, 161, 0.22); color: #d8b4fe; border-color: rgba(176,122,161,.35); }
/* config → оранжевый: yaml/json/ini */
.badge-config   { background: rgba(245, 158, 11, 0.18); color: #fbbf24; border-color: rgba(245,158,11,.35); }
/* test → жёлтый */
.badge-test     { background: rgba(234, 179, 8, 0.18); color: #fde047; border-color: rgba(234,179,8,.35); }
/* style → розовый */
.badge-style    { background: rgba(244, 114, 182, 0.18); color: #f9a8d4; border-color: rgba(244,114,182,.35); }
[data-theme=light] .badge-code     { color: #1e40af; }
[data-theme=light] .badge-rationale{ color: #475569; }
[data-theme=light] .badge-document { color: #166534; }
[data-theme=light] .badge-template { color: #7e22ce; }
[data-theme=light] .badge-config   { color: #b45309; }
[data-theme=light] .badge-test     { color: #a16207; }
[data-theme=light] .badge-style    { color: #be185d; }

/* Community icon (card & legend) — square with themed SVG */
.com-dot {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px;
  border-radius: 8px; flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0,0,0,.18);
}
.com-dot svg { width: 18px; height: 18px; }

/* Cards grid */
.cards-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 16px; margin-bottom: 32px;
}
@media (max-width: 1100px) { .cards-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 680px) { .cards-grid { grid-template-columns: 1fr; } }

.card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 10px; padding: 16px; display: flex; flex-direction: column;
  gap: 8px; transition: border-color 0.15s, box-shadow 0.15s;
}
.card:hover { border-color: var(--primary); box-shadow: 0 0 0 1px var(--primary) inset; }
.card-header { display: flex; align-items: center; gap: 10px; }
.card-title { font-weight: 700; font-size: 15px; color: var(--primary-l); transition: color 0.15s; }
.card:hover .card-title { text-decoration: underline; }
.card-desc { color: var(--text); font-size: 13px; line-height: 1.45; text-decoration: none; }
.card-meta { color: var(--text2); font-size: 12px; text-decoration: none; }
.card-top3 { color: var(--text3); font-size: 12px; font-family: monospace; text-decoration: none; }

/* Section heading */
.section-heading {
  font-size: 13px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text2); margin-bottom: 12px;
  padding-bottom: 8px; border-bottom: 1px solid var(--border);
}

/* Tabs (Таблица / Схема) */
.wiki-tabs {
  display: inline-flex; gap: 0; margin: 18px 0 18px;
  border-bottom: 2px solid var(--border);
  padding: 0; flex-wrap: wrap;
}
.wiki-tab-btn {
  background: none; border: none; padding: 9px 16px;
  font: inherit; font-size: 14px; color: var(--text2);
  cursor: pointer; position: relative; bottom: -2px;
  border-bottom: 2px solid transparent;
  display: inline-flex; align-items: center; gap: 7px;
  transition: color .15s, border-color .15s;
}
.wiki-tab-btn:hover { color: var(--text); }
.wiki-tab-btn.active {
  color: var(--primary-l); border-bottom-color: var(--primary);
  font-weight: 600;
}
.wiki-tab-btn .ti { font-size: 16px; line-height: 1; }
.wiki-tab-btn .tab-badge {
  font-size: 10px; padding: 1px 6px; border-radius: 8px;
  background: var(--bg3); color: var(--text3); font-weight: 500;
}
.tab-content[hidden] { display: none; }

/* Schema tab — graph layout: graph слева, sidebar справа */
.schema-layout {
  display: flex; gap: 0;
  height: 720px; max-height: calc(100vh - 200px); min-height: 540px;
  background: var(--bg2);
  border: 1px solid var(--border); border-radius: 8px;
  overflow: hidden;
}
.schema-graph-pane {
  flex: 1; min-width: 0; position: relative;
  background: var(--bg3);
}
.schema-toolbar-overlay {
  position: absolute; top: 12px; left: 12px; z-index: 10;
  display: flex; gap: 6px; flex-wrap: wrap; align-items: center;
}
.schema-toolbar-overlay button {
  background: var(--bg2); border: 1px solid var(--border); color: var(--text);
  padding: 5px 10px; border-radius: 6px; font-size: 12px;
  cursor: pointer; display: inline-flex; align-items: center; gap: 5px;
  transition: background .15s, border-color .15s;
  box-shadow: 0 1px 4px rgba(0,0,0,.15);
}
.schema-toolbar-overlay button:hover { background: var(--bg3); border-color: var(--primary); }
.schema-toolbar-overlay button.active { background: var(--primary); color: #fff; border-color: var(--primary); }

.schema-graph-stats {
  position: absolute; bottom: 10px; left: 12px; z-index: 10;
  font-size: 11px; color: var(--text3);
  background: var(--bg2); border: 1px solid var(--border);
  padding: 3px 9px; border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,.15);
}

#visGraph {
  width: 100%; height: 100%;
}
#visGraph .vis-loading {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  color: var(--text2); font-size: 13px;
}
#visGraph .vis-loading::before {
  content: ''; width: 18px; height: 18px; margin-right: 8px;
  border: 2.5px solid var(--border); border-top-color: var(--primary);
  border-radius: 50%; animation: visSpin 0.8s linear infinite;
}
@keyframes visSpin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) {
  #visGraph .vis-loading::before { animation: none; }
}

/* Right sidebar */
.schema-sidebar {
  width: 280px; flex-shrink: 0;
  background: var(--bg2); border-left: 1px solid var(--border);
  display: flex; flex-direction: column; overflow: hidden;
}
.schema-help {
  padding: 12px 14px; border-bottom: 1px solid var(--border);
  font-size: 12px; color: var(--text2); line-height: 1.5;
  background: linear-gradient(180deg, var(--bg3) 0%, transparent 100%);
}
.schema-help-title {
  font-weight: 600; color: var(--text); display: flex; align-items: center;
  gap: 6px; margin-bottom: 6px; font-size: 12.5px;
}
.schema-help-title .ti { font-size: 14px; color: var(--primary-l); }
.schema-help ul {
  list-style: none; padding: 0; margin: 4px 0 0;
}
.schema-help ul li {
  padding: 2px 0 2px 16px; position: relative; font-size: 11.5px;
}
.schema-help ul li::before {
  content: '·'; position: absolute; left: 6px; color: var(--primary-l); font-weight: 700;
}
.schema-help ul li b { color: var(--text); font-weight: 500; }
.schema-help-toggle {
  display: inline-block; margin-top: 6px; cursor: pointer;
  color: var(--primary-l); font-size: 11px; user-select: none;
}
.schema-help-toggle:hover { text-decoration: underline; }
.schema-help[data-collapsed="true"] ul,
.schema-help[data-collapsed="true"] .schema-help-intro { display: none; }

.schema-search-wrap {
  padding: 12px; border-bottom: 1px solid var(--border);
}
.schema-search {
  width: 100%; box-sizing: border-box;
  background: var(--bg3); border: 1px solid var(--border); color: var(--text);
  padding: 7px 10px; border-radius: 6px; font-size: 13px; outline: none;
}
.schema-search:focus { border-color: var(--primary); }
.schema-search-results {
  max-height: 160px; overflow-y: auto; padding: 4px 12px;
  border-bottom: 1px solid var(--border); display: none;
  font-size: 12px;
}
.schema-search-results.visible { display: block; }
.schema-search-results .ssi {
  padding: 4px 6px; cursor: pointer; border-radius: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  color: var(--text2);
}
.schema-search-results .ssi:hover { background: var(--bg3); color: var(--primary-l); }

.schema-info-panel {
  padding: 14px; border-bottom: 1px solid var(--border);
  font-size: 13px;
}
.schema-info-panel .si-empty { color: var(--text3); font-style: italic; font-size: 12px; }
.schema-info-panel .si-section-title {
  font-size: 11px; color: var(--text3); margin-bottom: 7px;
  text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;
}
.schema-info-panel .si-name { font-weight: 600; color: var(--text); margin-bottom: 4px; word-break: break-word; }
.schema-info-panel .si-alt { color: var(--text2); font-size: 12px; margin-bottom: 8px; }
.schema-info-panel .si-field { margin: 4px 0; font-size: 12px; color: var(--text2); }
.schema-info-panel .si-field b { color: var(--text); font-weight: 500; }
.schema-info-panel .si-field code {
  background: var(--bg3); padding: 1px 5px; border-radius: 3px;
  font-size: 11px; color: var(--text); word-break: break-all;
}
.schema-info-panel .si-neighbors { margin-top: 10px; max-height: 200px; overflow-y: auto; }
.schema-info-panel .si-nb-item {
  display: block; padding: 4px 7px; margin: 2px 0;
  border-radius: 4px; cursor: pointer; font-size: 12px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  border-left: 3px solid var(--border);
  color: var(--text2);
  text-decoration: none;
}
.schema-info-panel .si-nb-item:hover {
  background: var(--bg3); color: var(--primary-l);
  border-left-color: var(--primary);
}

.schema-legend {
  flex: 1; overflow-y: auto; padding: 12px;
}
.schema-legend .si-section-title { margin-bottom: 8px; }
.schema-legend .leg-item {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 0; font-size: 12px; color: var(--text2);
}
.schema-legend .leg-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}

.schema-footer-count {
  padding: 9px 12px; font-size: 11px; color: var(--text3);
  border-top: 1px solid var(--border); background: var(--bg3);
  text-align: center;
}

@media (max-width: 900px) {
  .schema-layout { flex-direction: column; height: auto; max-height: none; }
  .schema-graph-pane { height: 480px; flex: none; }
  .schema-sidebar { width: 100%; border-left: none; border-top: 1px solid var(--border); }
  .schema-legend { max-height: 200px; }
}

/* Modal */
.modal-backdrop {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,0.65); z-index: 200;
  align-items: center; justify-content: center;
}
.modal-backdrop.open { display: flex; }
.modal {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 24px; width: min(640px, 94vw);
  max-height: 80vh; overflow-y: auto; position: relative;
}
.modal-close {
  position: absolute; top: 12px; right: 16px;
  background: none; border: none; font-size: 22px; color: var(--text2);
  cursor: pointer; line-height: 1;
}
.modal-close:hover { color: var(--text); }
.modal-title { font-size: 16px; font-weight: 700; margin-bottom: 10px; padding-right: 28px; line-height: 1.35; }
.modal-title .modal-alt-name { color: var(--text2); font-weight: 400; font-size: 13px; }
.modal-desc { font-size: 13px; color: var(--text2); line-height: 1.45; margin-bottom: 14px; padding: 8px 10px; background: var(--bg3); border-left: 3px solid var(--primary); border-radius: 4px; }
.modal-meta-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.modal-meta-row .mm-chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: var(--bg3); border: 1px solid var(--border); border-radius: 14px; font-size: 11.5px; }
.modal-meta-row .mm-key { color: var(--text3); text-transform: uppercase; letter-spacing: 0.04em; font-size: 10px; font-weight: 600; }
.modal-meta-row .mm-val { color: var(--text); font-family: monospace; }
.modal-meta-row .badge { font-size: 10.5px; padding: 1px 8px; }
.modal-field { margin-bottom: 10px; font-size: 13px; }
.modal-field .mf-label { color: var(--text2); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 3px; }
.modal-field .mf-val { font-family: monospace; word-break: break-all; }
.modal-neighbors { margin-top: 12px; }
.modal-neighbors .mn-title { color: var(--text2); font-size: 12px; margin-bottom: 6px; }
.neighbor-chip {
  display: inline-block; padding: 2px 10px; margin: 2px;
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 20px; font-size: 12px; color: var(--text2);
}

/* Related communities */
.related-grid {
  display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;
}
.rel-chip {
  display: flex; align-items: center; gap: 6px;
  padding: 4px 12px; border: 1px solid var(--border);
  border-radius: 20px; background: var(--bg2); font-size: 12px;
  color: var(--text2); transition: all 0.15s;
}
.rel-chip:hover { border-color: var(--primary); color: var(--primary-l); text-decoration: none; }
.rel-chip .rel-count {
  background: var(--bg3); border-radius: 10px; padding: 1px 6px;
  font-size: 11px; font-weight: 600; color: var(--text3);
}

/* Stat row */
.stat-row { display: flex; gap: 24px; margin-bottom: 24px; flex-wrap: wrap; }
.stat-item { color: var(--text2); font-size: 13px; position: relative; }
.stat-item strong { color: var(--text); font-size: 22px; display: block; }
/* «?»-tooltip — нативный title через ::after не отрисуется на mobile, поэтому JS-tooltip */
.help-q {
  display: inline-flex; align-items: center; justify-content: center;
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--bg3); border: 1px solid var(--border);
  color: var(--text3); font-size: 9px; font-weight: 700;
  margin-left: 4px; cursor: help; vertical-align: middle;
  transition: background .15s, color .15s;
}
.help-q:hover { background: var(--primary); color: #fff; border-color: var(--primary); }
.help-tip {
  position: fixed; max-width: 280px;
  background: var(--bg2); color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 8px 11px; font-size: 12px; line-height: 1.45;
  box-shadow: 0 4px 16px rgba(0,0,0,.35); z-index: 5000; pointer-events: none;
  display: none;
}
.help-tip.visible { display: block; }
.help-tip b { color: var(--primary-l); }

/* Empty */
.empty { color: var(--text3); text-align: center; padding: 32px; font-size: 14px; }

/* File path */
.file-path { font-family: monospace; font-size: 12px; color: var(--text3); }

/* Degree number */
.degree-num { font-weight: 600; color: var(--primary-l); }

/* Search results table shown/hidden */
.search-results { display: none; margin-top: 16px; }
.search-results.visible { display: block; }

/* Фирменная шапка docs (gradient, fixed) */
:root { --header-grad-a: #43a047; --header-grad-b: #26a69a; --header-height: 56px; }
[data-theme=dark] { --header-grad-a: #0f172a; --header-grad-b: #1e293b; }
@keyframes header-gradient-shift {
  0%   { background-position:   0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position:   0% 50%; }
}
@media (prefers-reduced-motion: reduce) { .docs-topnav { animation: none !important; } }

.docs-topnav {
  position: fixed; top: 0; left: 0; right: 0; height: var(--header-height);
  background: linear-gradient(135deg, var(--header-grad-a), var(--header-grad-b), var(--header-grad-a));
  background-size: 200% 200%;
  animation: header-gradient-shift 18s ease-in-out infinite;
  color: #fff; display: flex; align-items: center; padding: 0 20px;
  z-index: 200; gap: 12px;
  box-shadow: 0 1px 3px rgba(15,23,42,.06), 0 4px 12px rgba(15,23,42,.08);
}
[data-theme=dark] .docs-topnav { border-bottom: 1px solid #334155; }
body { padding-top: var(--header-height); }

.docs-topnav .dtn-logo {
  display: flex; align-items: center; gap: 10px;
  font-weight: 700; font-size: 15px; color: #fff; text-decoration: none; white-space: nowrap;
}
.docs-topnav .dtn-logo:hover { text-decoration: none; color: #fff; }
.docs-topnav .dtn-logo-icon {
  width: 36px; height: 36px; border-radius: 8px;
  background: linear-gradient(135deg, #66bb6a, #26a69a);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 800; flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,.18);
}
.docs-topnav .dtn-sep { display: none; }
.docs-topnav .dtn-links { display: flex; gap: 6px; flex-wrap: nowrap; }
.docs-topnav .dtn-link {
  color: #fff; font-size: 13px; padding: 6px 12px;
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22);
  border-radius: 8px; transition: all 0.15s; white-space: nowrap;
  display: inline-flex; align-items: center; gap: 6px;
}
.docs-topnav .dtn-link:hover { background: rgba(255,255,255,.22); text-decoration: none; color: #fff; }
.docs-topnav .dtn-link .dtn-ico { font-size: 15px; line-height: 1; }
.docs-topnav .dtn-link .dtn-txt { display: inline; }
.docs-topnav .dtn-spacer { flex: 1; min-width: 8px; }
.docs-topnav .dtn-theme-btn {
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22); color: #fff;
  padding: 6px 12px; border-radius: 8px; cursor: pointer; font-size: 13px;
  transition: all 0.15s; white-space: nowrap; flex-shrink: 0;
  display: inline-flex; align-items: center; gap: 6px;
}
.docs-topnav .dtn-theme-btn:hover { background: rgba(255,255,255,.22); }

/* Mobile: иконки вместо текста, логотип-текст скрыть */
@media (max-width: 680px) {
  .docs-topnav { padding: 0 12px; gap: 8px; }
  .docs-topnav .dtn-logo .dtn-logo-text { display: none; }
  .docs-topnav .dtn-link .dtn-txt { display: none; }
  .docs-topnav .dtn-link { padding: 6px 10px; }
  .docs-topnav .dtn-theme-btn .dtn-theme-txt { display: none; }
  .docs-topnav .dtn-theme-btn { padding: 6px 10px; }
}

/* Community page header */
.comm-header {
  display: flex; align-items: flex-start; gap: 16px;
  margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid var(--border);
}
.comm-icon {
  width: 72px; height: 72px; border-radius: 14px;
  flex-shrink: 0; box-shadow: 0 4px 14px rgba(0,0,0,.22);
  display: flex; align-items: center; justify-content: center;
}
.comm-icon svg { width: 40px; height: 40px; }
@media (max-width: 680px) {
  .comm-icon { width: 56px; height: 56px; border-radius: 12px; }
  .comm-icon svg { width: 30px; height: 30px; }
}
.comm-name { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.comm-id { color: var(--text3); font-size: 12px; }
.comm-desc-hdr {
  margin-top: 10px; color: var(--text); font-size: 14px; line-height: 1.5;
  max-width: 760px;
}
"""

SHARED_JS = """
// Theme toggle
const html = document.documentElement;
const saved = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
html.setAttribute('data-theme', saved);
document.querySelectorAll('.dtn-theme-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });
});

// «?» help tooltip — общий handler для всех .help-q элементов
(function setupHelpTooltip() {
  const tip = document.createElement('div');
  tip.className = 'help-tip';
  document.body.appendChild(tip);
  let activeEl = null;
  function show(el) {
    activeEl = el;
    tip.innerHTML = el.dataset.help || '';
    const r = el.getBoundingClientRect();
    tip.classList.add('visible');
    // Позиционируем над элементом, если выше есть место, иначе снизу
    const tipR = tip.getBoundingClientRect();
    let top = r.top - tipR.height - 8;
    if (top < 8) top = r.bottom + 8;
    let left = r.left + r.width / 2 - tipR.width / 2;
    if (left < 8) left = 8;
    if (left + tipR.width > window.innerWidth - 8) left = window.innerWidth - tipR.width - 8;
    tip.style.left = left + 'px';
    tip.style.top  = top  + 'px';
  }
  function hide() { activeEl = null; tip.classList.remove('visible'); }
  document.addEventListener('mouseover', e => {
    const el = e.target.closest('.help-q');
    if (el && el !== activeEl) show(el);
  });
  document.addEventListener('mouseout', e => {
    const el = e.target.closest('.help-q');
    if (el && el === activeEl) hide();
  });
  // Click toggle (mobile)
  document.addEventListener('click', e => {
    const el = e.target.closest('.help-q');
    if (!el) { if (activeEl) hide(); return; }
    e.stopPropagation();
    if (el === activeEl) hide(); else show(el);
  });
})();
"""


def short_path(p: str) -> str:
    """Return last 2 parts of a Windows/Unix path, or — if empty."""
    if not p:
        return "—"
    parts = p.replace("\\", "/").rstrip("/").split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]


def is_test_node(nd: dict) -> bool:
    """Узел из tests/ — фильтруем из wiki (нерелевантно для архитектурного обзора).

    Признаки: путь содержит /tests/, /test/, /__tests__/ или label-имя имеет
    test-суффикс/префикс (TestCase, FooTest, test_bar и т.п.).
    """
    src = (nd.get("source_file") or "").replace("\\", "/").lower()
    if any(seg in src for seg in ("/tests/", "/test/", "/__tests__/", "/spec/")):
        return True
    if src.endswith("_test.py") or src.endswith("_tests.py") or src.endswith(".test.js"):
        return True
    label = (nd.get("label") or "")
    if label.startswith("test_") or label.endswith("Test") or label.endswith("Tests") or label.endswith("TestCase"):
        return True
    return False


def load_data():
    with open(EXTRACT_FILE, "rb") as f:
        extract = json.loads(f.read().decode("utf-8"))
    with open(ANALYSIS_FILE, "rb") as f:
        analysis = json.loads(f.read().decode("utf-8"))
    with open(LABELS_FILE, "rb") as f:
        labels = json.loads(f.read().decode("utf-8"))
    return extract, analysis, labels


def build_color_map(communities: dict) -> dict:
    return {cid: COLORS[i % len(COLORS)] for i, cid in enumerate(sorted(communities.keys(), key=int))}


def compute_degrees(nodes: list, edges: list) -> dict:
    """Count total edges (in + out) per node id."""
    deg = defaultdict(int)
    for e in edges:
        deg[e["source"]] += 1
        deg[e["target"]] += 1
    return deg


def compute_cross_edges(edges: list, node_to_cid: dict) -> dict:
    """
    Returns dict: cid -> {other_cid: count} of cross-community edge counts.
    """
    cross = defaultdict(lambda: defaultdict(int))
    for e in edges:
        c1 = node_to_cid.get(e["source"])
        c2 = node_to_cid.get(e["target"])
        if c1 is None or c2 is None or c1 == c2:
            continue
        cross[c1][c2] += 1
        cross[c2][c1] += 1
    # Deduplicate (already counts both directions, keep as-is for display)
    return {k: dict(v) for k, v in cross.items()}


def compute_intra_edges(edges: list, node_to_cid: dict) -> dict:
    """Count edges within each community."""
    intra = defaultdict(int)
    for e in edges:
        c1 = node_to_cid.get(e["source"])
        c2 = node_to_cid.get(e["target"])
        if c1 is not None and c1 == c2:
            intra[c1] += 1
    return dict(intra)


def build_neighbor_map(edges: list) -> dict:
    """node_id -> set of neighbor node_ids"""
    nbr = defaultdict(set)
    for e in edges:
        nbr[e["source"]].add(e["target"])
        nbr[e["target"]].add(e["source"])
    return {k: list(v) for k, v in nbr.items()}


def js_str(s: str) -> str:
    """Escape a Python string for embedding in JS single-quoted string."""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")


def generate_index(
    communities: dict,
    nodes_by_id: dict,
    degrees: dict,
    cross_edges: dict,
    color_map: dict,
    labels: dict,
    intra_edges: dict,
):
    # Build community summaries for JS — filter out tiny/irrelevant ones
    comm_data = []
    for cid in sorted(communities.keys(), key=int):
        nids = communities[cid]
        node_count = len(nids)
        # Skip technical/tiny communities (below MIN_NODE_COUNT)
        if node_count < MIN_NODE_COUNT:
            continue
        label = labels.get(cid, labels.get(str(cid), f"Модуль {cid}"))
        color = color_map[cid]
        # top-3 by degree
        sorted_nids = sorted(nids, key=lambda n: degrees.get(n, 0), reverse=True)
        top3 = []
        for nid in sorted_nids[:3]:
            nd = nodes_by_id.get(nid, {})
            top3.append(nd.get("label", nid))
        intra = intra_edges.get(cid, 0)
        cross_total = sum(cross_edges.get(cid, {}).values()) // 2  # each edge counted twice
        # Try both int and str keys (ICONS dict uses ints)
        try:
            cid_int = int(cid)
        except (ValueError, TypeError):
            cid_int = cid
        icon_name = COMM_ICONS.get(cid_int, COMM_ICONS.get(cid, "settings"))
        description = COMM_DESCRIPTIONS.get(cid_int, COMM_DESCRIPTIONS.get(cid, ""))
        comm_data.append({
            "cid": cid,
            "label": label,
            "color": color,
            "node_count": node_count,
            "top3": top3,
            "intra_edges": intra,
            "cross_edges_total": cross_total,
            "icon": icon_name,
            "description": description,
        })

    # Build all-nodes data for global search
    all_nodes = []
    for nid, nd in nodes_by_id.items():
        cid = None
        # Find cid from communities
        for c, nids in communities.items():
            if nid in nids:
                cid = c
                break
        all_nodes.append({
            "id": nid,
            "label": nd.get("label", nid),
            "file_type": nd.get("file_type", "code"),
            "source_file": short_path(nd.get("source_file", "")),
            "cid": cid or "",
            "cid_label": labels.get(cid, labels.get(str(cid), f"Модуль {cid}")) if cid else "",
        })

    comm_json = json.dumps(comm_data, ensure_ascii=False)
    nodes_json = json.dumps(all_nodes, ensure_ascii=False)
    icon_paths_json = json.dumps(ICON_PATHS, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ru" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>graphify — Архитектурная документация</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.26.0/dist/tabler-icons.min.css">
<style>
{SHARED_CSS}
</style>
</head>
<body>

<div class="docs-topnav">
  <a href="../../index.html" class="dtn-logo" title="СмИТ Биллинг — Документация">
    <div class="dtn-logo-icon">С</div>
    <span class="dtn-logo-text">СмИТ Биллинг</span>
  </a>
  <div class="dtn-links">
    <a href="../../index.html" class="dtn-link" title="Документация">
      <i class="ti ti-book dtn-ico"></i><span class="dtn-txt">Документация</span>
    </a>
    <a href="../../pages/dev/index.html" class="dtn-link" title="Разработчикам">
      <i class="ti ti-code dtn-ico"></i><span class="dtn-txt">Разработчикам</span>
    </a>
    <a href="../graph.html" class="dtn-link" title="Граф зависимостей">
      <i class="ti ti-topology-star-3 dtn-ico"></i><span class="dtn-txt">Граф</span>
    </a>
    <a href="../help.html" class="dtn-link" title="graphify CLI">
      <i class="ti ti-terminal-2 dtn-ico"></i><span class="dtn-txt">CLI</span>
    </a>
  </div>
  <div class="dtn-spacer"></div>
  <button class="dtn-theme-btn" id="themeToggle" title="Переключить тему">
    <span class="dtn-ico">◑</span><span class="dtn-theme-txt">Тема</span>
  </button>
</div>

<div class="main">
  <!-- Search -->
  <div class="search-wrap">
    <input type="text" class="search-input" id="globalSearch"
           placeholder="Поиск по всем нодам... (название, файл, модуль)">
    <div class="search-results" id="searchResults">
      <div class="tbl-wrap">
        <table id="searchTable">
          <thead><tr>
            <th>Нода</th>
            <th>Тип</th>
            <th>Файл</th>
            <th>Модуль</th>
          </tr></thead>
          <tbody id="searchTbody"></tbody>
        </table>
      </div>
      <p id="searchCount" style="color:var(--text3);font-size:12px;margin-top:8px;"></p>
    </div>
  </div>

  <!-- Communities grid -->
  <div class="section-heading">Модули</div>
  <div class="cards-grid" id="commGrid"></div>
</div>

<script>
{SHARED_JS}

const COMMUNITIES = {comm_json};
const ALL_NODES = {nodes_json};
const ICON_PATHS = {icon_paths_json};

function iconSvg(iconName, size, color) {{
  const p = ICON_PATHS[iconName] || ICON_PATHS['settings'];
  return `<svg width="${{size}}" height="${{size}}" viewBox="0 0 24 24" fill="none" stroke="${{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${{p}}"/></svg>`;
}}

// Build node index for search
const nodeIndex = ALL_NODES.map(n => ({{
  ...n,
  _search: (n.label + ' ' + n.source_file + ' ' + n.cid_label).toLowerCase()
}}));

// Render community cards
const grid = document.getElementById('commGrid');
COMMUNITIES.forEach(c => {{
  const top3text = c.top3.length
    ? c.top3.map(t => {{ const a = humanizeName(t) || t; return a.length > 35 ? a.slice(0,35)+'…' : a; }}).join(', ')
    : '';
  const card = document.createElement('a');
  card.href = `community_${{c.cid}}.html`;
  card.className = 'card';
  card.style.textDecoration = 'none';
  const descHtml = c.description
    ? `<div class="card-desc">${{escHtml(c.description)}}</div>`
    : '';
  card.innerHTML = `
    <div class="card-header">
      <span class="com-dot" style="background:${{c.color}};">
        ${{iconSvg(c.icon || 'settings', 18, '#fff')}}
      </span>
      <span class="card-title">${{escHtml(c.label)}}</span>
    </div>
    ${{descHtml}}
    <div class="card-meta">${{c.node_count}} нод · ${{c.intra_edges}} внутр. связей · ${{c.cross_edges_total}} внешн.</div>
    <div class="card-top3" title="Топ по степени">${{escHtml(top3text)}}</div>
  `;
  grid.appendChild(card);
}});

// Global search
const searchInput = document.getElementById('globalSearch');
const searchResults = document.getElementById('searchResults');
const searchTbody = document.getElementById('searchTbody');
const searchCount = document.getElementById('searchCount');

function getCidColor(cid) {{
  const c = COMMUNITIES.find(x => x.cid === cid);
  return c ? c.color : '#888';
}}
function getCidLabel(cid) {{
  const c = COMMUNITIES.find(x => x.cid === cid);
  return c ? c.label : ('Модуль ' + cid);
}}

function badgeHtml(ft) {{
  // Русские названия + цветовая маркировка
  const map = {{
    code:      ['Код',         'badge-code'],
    rationale: ['Обоснование', 'badge-rationale'],
    document:  ['Документ',    'badge-document'],
    template:  ['Шаблон',      'badge-template'],
    config:    ['Конфиг',      'badge-config'],
    test:      ['Тест',        'badge-test'],
    tests:     ['Тест',        'badge-test'],
    style:     ['Стиль',       'badge-style'],
  }};
  const m = map[ft];
  if (m) return '<span class="badge ' + m[1] + '">' + m[0] + '</span>';
  return '<span class="badge">' + escHtml(ft) + '</span>';
}}

// Переводит длинные английские label-ы (сгенерённые семантическим extract-ом)
// на русский по словарю-эвристике. Возвращает альтернативное имя или '' если перевод не найден.
function humanizeName(label) {{
  if (!label) return '';
  const lbl = String(label);
  // Если название уже на кириллице — пропускаем
  if (/[А-Яа-яЁё]/.test(lbl)) return '';
  // Слишком короткое (имя класса/функции) — без перевода
  if (lbl.length < 25) return '';
  // Словарь популярных шаблонов «Английский → Русский»
  const dict = [
    [/^Send notification about[^.]+/i,      'Отправка уведомления о событии'],
    [/^Send Telegram[^.]+/i,                'Отправка сообщения в Telegram'],
    [/^Send email[^.]+/i,                   'Отправка email-уведомления'],
    [/^Send SMS[^.]+/i,                     'Отправка SMS-уведомления'],
    [/^Generate (PDF|export|report|invoice)[^.]+/i, 'Генерация отчёта/документа'],
    [/^Render (template|form|page)[^.]+/i,  'Рендер шаблона/страницы'],
    [/^Get list of[^.]+/i,                  'Получить список'],
    [/^List of[^.]+/i,                      'Список'],
    [/^Return (list|set|dict|json)[^.]+/i,  'Возврат структурированных данных'],
    [/^Returns? (json|response|html|csv)[^.]+/i, 'Возврат данных API'],
    [/^Build (context|payload|request)[^.]+/i, 'Сборка запроса/контекста'],
    [/^Common context[^.]+/i,               'Общий контекст шаблона'],
    [/^Universal context[^.]+/i,            'Универсальный контекст'],
    [/^Creates?\s/i,                        'Создание сущности'],
    [/^Updates?\s/i,                        'Обновление сущности'],
    [/^Deletes?\s/i,                        'Удаление сущности'],
    [/^Imports?\s/i,                        'Импорт данных'],
    [/^Exports?\s/i,                        'Экспорт данных'],
    [/^Sync(s|hronize)?\s/i,                'Синхронизация'],
    [/^Validate[^.]+/i,                     'Валидация данных'],
    [/^Process (payment|webhook|request)[^.]+/i, 'Обработка платежа/webhook'],
    [/^Handle (webhook|event|signal)[^.]+/i,'Обработчик события'],
    [/^Celery beat task[^.]+/i,             'Периодическая Celery-задача'],
    [/^Celery (task|worker)[^.]+/i,         'Celery-задача (фоновая)'],
    [/^POST\s/i,                            'POST-обработчик'],
    [/^GET\s/i,                             'GET-обработчик'],
    [/^Redirect to[^.]+/i,                  'Редирект на другой URL'],
    [/^Redirect[^.]*/i,                     'Редирект'],
    [/^Test (connection|FTP|SSH|API)[^.]+/i,'Проверка соединения'],
    [/^Run (script|command|task)[^.]+/i,    'Запуск скрипта/команды'],
    [/^Show (form|page|dialog)[^.]+/i,      'Отображение формы/страницы'],
    [/^Save\s/i,                            'Сохранение'],
    [/^Load\s/i,                            'Загрузка'],
    [/^Apply (filter|migration|settings)[^.]+/i, 'Применение настроек/миграции'],
    [/^Migrate[^.]+/i,                      'Миграция данных/схемы'],
    [/^Build (config|payload|context)[^.]+/i, 'Сборка структуры'],
    [/^Compute[^.]+/i,                      'Вычисление'],
    [/^Calculate[^.]+/i,                    'Расчёт'],
    [/^Check[^.]+/i,                        'Проверка'],
    [/^Init[^.]+/i,                         'Инициализация'],
    [/^TODO:?\s/i,                          'TODO: задача в коде'],
    [/^FIXME:?\s/i,                         'FIXME: исправить'],
    [/^Helper[^.]+/i,                       'Вспомогательная функция'],
    [/^Universal\s/i,                       'Универсальный обработчик'],
    [/^Write (CSV|JSON|XML)[^.]+/i,         'Запись в CSV/JSON/XML'],
    [/^Core (export|import|logic)[^.]+/i,   'Основная логика модуля'],
  ];
  for (const [re, ru] of dict) {{
    if (re.test(lbl)) return ru;
  }}
  return '';
}}

function escHtml(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

let searchTimer;
searchInput.addEventListener('input', () => {{
  clearTimeout(searchTimer);
  searchTimer = setTimeout(doSearch, 120);
}});

function doSearch() {{
  const q = searchInput.value.trim().toLowerCase();
  if (!q) {{
    searchResults.classList.remove('visible');
    return;
  }}
  const results = nodeIndex.filter(n => n._search.includes(q)).slice(0, 200);
  searchTbody.innerHTML = results.map(n => {{
    const cLabel = n.cid ? getCidLabel(n.cid) : '—';
    const cColor = n.cid ? getCidColor(n.cid) : '#888';
    const commLink = n.cid
      ? `<a href="community_${{n.cid}}.html" style="display:flex;align-items:center;gap:6px;">
          <span style="width:8px;height:8px;border-radius:50%;background:${{cColor}};flex-shrink:0;display:inline-block;"></span>
          ${{escHtml(cLabel)}}
        </a>`
      : '—';
    return `<tr>
      <td style="font-size:12px;font-family:monospace;">${{escHtml(n.label.length > 60 ? n.label.slice(0,60)+'…' : n.label)}}</td>
      <td>${{badgeHtml(n.file_type)}}</td>
      <td class="file-path">${{escHtml(n.source_file)}}</td>
      <td>${{commLink}}</td>
    </tr>`;
  }}).join('');
  searchCount.textContent = results.length < nodeIndex.filter(n => n._search.includes(q)).length
    ? `Показано 200 из ${{nodeIndex.filter(n=>n._search.includes(q)).length}} результатов`
    : `Найдено: ${{results.length}}`;
  searchResults.classList.add('visible');
}}
</script>
</body>
</html>"""
    return html


def generate_community_page(
    cid: str,
    communities: dict,
    nodes_by_id: dict,
    degrees: dict,
    cross_edges: dict,
    intra_edges: dict,
    color_map: dict,
    labels: dict,
    neighbor_map: dict,
    node_to_cid: dict,
    all_communities_sorted: list,
):
    nids = communities[cid]
    label = labels.get(cid, labels.get(str(cid), f"Модуль {cid}"))
    color = color_map[cid]
    intra = intra_edges.get(cid, 0)

    # Build nodes list for this community (фильтруем тестовые ноды)
    comm_nodes = []
    skipped_tests = 0
    for nid in nids:
        nd = nodes_by_id.get(nid, {})
        if is_test_node(nd):
            skipped_tests += 1
            continue
        deg = degrees.get(nid, 0)
        comm_nodes.append({
            "id": nid,
            "label": nd.get("label", nid),
            "file_type": nd.get("file_type", "code"),
            "source_file": nd.get("source_file", ""),
            "source_location": nd.get("source_location", ""),
            "degree": deg,
            "short_path": short_path(nd.get("source_file", "")),
        })

    # Related communities sorted by cross-edge count
    cross = cross_edges.get(cid, {})
    related = sorted(cross.items(), key=lambda x: -x[1])[:15]

    # Build neighbor map for this community's nodes (for modal). Тесты не показываем.
    node_data_for_js = []
    for n in comm_nodes:
        nbrs_raw = neighbor_map.get(n["id"], [])
        nbrs = []
        for nb_id in nbrs_raw[:30]:
            nb_nd = nodes_by_id.get(nb_id, {})
            if is_test_node(nb_nd):
                continue
            nbrs.append({
                "id": nb_id,
                "label": nb_nd.get("label", nb_id),
                "cid": node_to_cid.get(nb_id, ""),
            })
            if len(nbrs) >= 15:
                break
        node_data_for_js.append({
            "id": n["id"],
            "label": n["label"],
            "file_type": n["file_type"],
            "source_file": n["source_file"],
            "short_path": n["short_path"],
            "source_location": n["source_location"] or "",
            "degree": n["degree"],
            "neighbors": nbrs,
        })

    nodes_json = json.dumps(node_data_for_js, ensure_ascii=False)
    icon_paths_json = json.dumps(ICON_PATHS, ensure_ascii=False)
    # icon name for this community
    try:
        cid_int = int(cid)
    except (ValueError, TypeError):
        cid_int = cid
    comm_icon_name = COMM_ICONS.get(cid_int, COMM_ICONS.get(cid, "settings"))
    comm_icon_path = ICON_PATHS.get(comm_icon_name, ICON_PATHS.get("settings", ""))
    comm_icon_svg = (
        f'<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"><path d="{comm_icon_path}"/></svg>'
    )
    community_description = COMM_DESCRIPTIONS.get(cid_int, COMM_DESCRIPTIONS.get(cid, ""))
    description_html = (
        f'<div class="comm-desc-hdr">{community_description}</div>' if community_description else ''
    )
    related_json = json.dumps([
        {
            "cid": rc,
            "label": labels.get(rc, labels.get(str(rc), f"Модуль {rc}")),
            "color": color_map.get(rc, "#888"),
            "count": cnt,
            "icon": COMM_ICONS.get(int(rc) if isinstance(rc, (int, str)) and str(rc).lstrip('-').isdigit() else rc, "settings"),
        }
        for rc, cnt in related
    ], ensure_ascii=False)

    # Prev / Next community navigation
    cidx = all_communities_sorted.index(cid)
    prev_cid = all_communities_sorted[cidx - 1] if cidx > 0 else None
    next_cid = all_communities_sorted[cidx + 1] if cidx < len(all_communities_sorted) - 1 else None
    prev_link = f'<a href="community_{prev_cid}.html" class="dtn-link">← {labels.get(prev_cid, "Пред.")}</a>' if prev_cid else ''
    next_link = f'<a href="community_{next_cid}.html" class="dtn-link">{labels.get(next_cid, "След.")} →</a>' if next_cid else ''

    # Link to docs chapter if this community has one
    # Map: community label → docs anchor on billing.html
    # label -> (page, anchor) where page is relative to docs/
    docs_mapping = {
        "Карточка абонента":       ("billing.html",   "subscribers"),
        "Личный кабинет":          ("billing.html",   "cabinet"),
        "Финансы и деньги":        ("billing.html",   "finance-operations"),
        "Поиск абонентов":         ("billing.html",   "search"),
        "Мобильный API":           ("billing.html",   "lk-mobile-app"),
        "Авторизация":             ("billing.html",   "lk-auth"),
        "Блокировки":              ("billing.html",   "block-unblock"),
        "Резервные копии":         ("billing.html",   "backup-system"),
        "IPTV":                    ("equipment.html", "iptv"),
        "Задачи биллинга":         ("billing.html",   "celery-zadachi-fonovye-protsessy"),
        "Отчёты СОРМ":             ("billing.html",   "sorm-reports"),
        "Платёжные системы":       ("billing.html",   "payment-systems"),
        "Сообщения":               ("billing.html",   "messaging"),
        "Push-уведомления":        ("billing.html",   "lk-firebase"),
        "FreeScout Webhooks":      ("billing.html",   "lk-support"),
        "Авторизация ЛК":          ("billing.html",   "lk-auth"),
    }
    docs_anchor = docs_mapping.get(label)
    if docs_anchor:
        page, anchor = docs_anchor
        docs_link_html = (
            f' · <a href="../../pages/{page}#{anchor}" '
            f'style="color:var(--primary-l);font-size:12px;" '
            f'title="Раздел в документации">📖 Документация</a>'
        )
    else:
        docs_link_html = ''

    html = f"""<!DOCTYPE html>
<html lang="ru" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Модуль {cid} — {label} | graphify</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.26.0/dist/tabler-icons.min.css">
<!-- vis-network подгружается lazily при открытии вкладки «Схема» -->
<style>
{SHARED_CSS}
</style>
</head>
<body>

<div class="docs-topnav">
  <a href="../../index.html" class="dtn-logo" title="СмИТ Биллинг — Документация">
    <div class="dtn-logo-icon">С</div>
    <span class="dtn-logo-text">СмИТ Биллинг</span>
  </a>
  <div class="dtn-links">
    <a href="../../index.html" class="dtn-link" title="Документация">
      <i class="ti ti-book dtn-ico"></i><span class="dtn-txt">Документация</span>
    </a>
    <a href="../../pages/dev/index.html" class="dtn-link" title="Разработчикам">
      <i class="ti ti-code dtn-ico"></i><span class="dtn-txt">Разработчикам</span>
    </a>
    <a href="../graph.html" class="dtn-link" title="Граф зависимостей">
      <i class="ti ti-topology-star-3 dtn-ico"></i><span class="dtn-txt">Граф</span>
    </a>
    <a href="index.html" class="dtn-link" title="Wiki модулей">
      <i class="ti ti-notebook dtn-ico"></i><span class="dtn-txt">Wiki</span>
    </a>
    <a href="../help.html" class="dtn-link" title="graphify CLI">
      <i class="ti ti-terminal-2 dtn-ico"></i><span class="dtn-txt">CLI</span>
    </a>
    {prev_link}
    {next_link}
  </div>
  <div class="dtn-spacer"></div>
  <button class="dtn-theme-btn" id="themeToggle" title="Переключить тему">
    <span class="dtn-ico">◑</span><span class="dtn-theme-txt">Тема</span>
  </button>
</div>

<div class="main">
  <!-- Community header -->
  <div class="comm-header">
    <div class="comm-icon" style="background:{color};">{comm_icon_svg}</div>
    <div style="flex:1;min-width:0;">
      <div class="comm-name">{label}</div>
      <div class="comm-id">Модуль #{cid}{docs_link_html}</div>
      {description_html}
      <div style="margin-top:10px;">
        <a href="index.html" class="dtn-link" style="font-size:12px;padding:4px 10px;">← Все модули</a>
      </div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="wiki-tabs" role="tablist">
    <button class="wiki-tab-btn active" data-tab="table" role="tab" aria-selected="true">
      <i class="ti ti-table"></i> Таблица
      <span class="tab-badge">{len(comm_nodes)}</span>
    </button>
    <button class="wiki-tab-btn" data-tab="schema" role="tab" aria-selected="false">
      <i class="ti ti-affiliate"></i> Схема
    </button>
  </div>

  <!-- TAB: Таблица -->
  <div class="tab-content" data-content="table">
    <!-- Stats -->
    <div class="stat-row">
      <div class="stat-item"><strong>{len(comm_nodes)}</strong> нод <span class="help-q" data-help="<b>Ноды</b> — модули, файлы и классы внутри одного модуля архитектуры. Один узел графа = один Python-файл, класс или функция. Тестовые ноды (из tests/) скрыты.">?</span></div>
      <div class="stat-item"><strong>{intra}</strong> внутренних связей <span class="help-q" data-help="<b>Внутренние связи</b> — import-зависимости между нодами одного модуля. Чем больше — тем плотнее кластер «варится в собственном соку».">?</span></div>
      <div class="stat-item"><strong>{sum(v for v in cross.values())}</strong> внешних связей <span class="help-q" data-help="<b>Внешние связи</b> — import-зависимости к нодам других модулей. Показывают, где модуль контактирует с остальной системой.">?</span></div>
    </div>

    <!-- Related communities -->
    <div class="section-heading">Связанные модули <span class="help-q" data-help="<b>Связанные модули</b> — другие модули графа, к которым ведут внешние связи. Чипы отсортированы по количеству общих связей. Клик — перейти на их wiki-страницу.">?</span></div>
    <div class="related-grid" id="relatedGrid"></div>

    <!-- Node search -->
    <div class="search-wrap" style="margin-bottom:16px;">
      <input type="text" class="search-input" id="nodeSearch"
             placeholder="Фильтр нод по названию или файлу...">
    </div>

    <!-- Nodes table -->
    <div class="section-heading">Ноды <span id="nodeCount" style="font-weight:400;color:var(--text3)"></span></div>
    <div class="tbl-wrap">
      <table id="nodesTable">
        <thead><tr>
          <th data-col="label">Название <i class="sort-icon"></i></th>
          <th data-col="file_type">Тип <i class="sort-icon"></i></th>
          <th data-col="short_path">Файл <i class="sort-icon"></i></th>
          <th data-col="degree">Связей <span class="help-q" data-help="<b>Связей</b> — сколько других нод связано с этим узлом через import (вход + выход). Чем выше, тем чаще используется. ≥ 50 — «god-объект».">?</span> <i class="sort-icon"></i></th>
        </tr></thead>
        <tbody id="nodesTbody"></tbody>
      </table>
    </div>
    <div id="nodesEmpty" class="empty" style="display:none;">Ноды не найдены</div>
  </div>

  <!-- TAB: Схема (lazy-loaded) -->
  <div class="tab-content" data-content="schema" hidden>
    <div class="schema-layout">
      <!-- Graph pane слева -->
      <div class="schema-graph-pane">
        <div class="schema-toolbar-overlay">
          <button id="schemaResetBtn" title="Сбросить позиции и зум"><i class="ti ti-refresh"></i> Сброс</button>
          <button id="schemaPhysicsBtn" class="active" title="Включить/выключить физику"><i class="ti ti-atom-2"></i> Физика</button>
          <button id="schemaLabelsBtn" class="active" title="Показать/скрыть подписи"><i class="ti ti-text-recognition"></i> Подписи</button>
        </div>
        <div id="visGraph"><div class="vis-loading">Загрузка схемы…</div></div>
        <div class="schema-graph-stats" id="schemaStatsBadge">— нод · — связей</div>
      </div>

      <!-- Sidebar справа -->
      <aside class="schema-sidebar">
        <div class="schema-help" id="schemaHelp">
          <div class="schema-help-title">
            <i class="ti ti-info-circle"></i>
            <span>Карта зависимостей модуля</span>
          </div>
          <div class="schema-help-intro">Узлы — классы, функции и файлы; рёбра — import-связи между ними. Размер узла растёт с числом связей.</div>
          <ul>
            <li><b>Клик</b> по узлу — детали, путь и соседи в этой панели</li>
            <li><b>Колесо</b> — зум, <b>drag</b> — перемещать всю карту</li>
            <li><b>Поиск</b> ниже — список совпадений, клик переносит к узлу</li>
            <li><b>Сброс</b> — в исходный масштаб; <b>Физика</b> — оживить раскладку; <b>Подписи</b> — скрыть/показать имена</li>
          </ul>
          <span class="schema-help-toggle" id="schemaHelpToggle">Скрыть подсказку</span>
        </div>
        <div class="schema-search-wrap">
          <input type="search" class="schema-search" id="schemaSearch" placeholder="Поиск ноды...">
        </div>
        <div class="schema-search-results" id="schemaSearchResults"></div>

        <div class="schema-info-panel" id="schemaInfoPanel">
          <div class="si-section-title">О ноде</div>
          <div class="si-empty">Кликните по узлу графа, чтобы увидеть детали.</div>
        </div>

        <div class="schema-legend" id="schemaLegend">
          <div class="si-section-title">Связанные модули</div>
          <div id="schemaLegendList" class="si-empty" style="font-style:italic">Загружается…</div>
        </div>

        <div class="schema-footer-count" id="schemaFooterCount">— нод · — связей</div>
      </aside>
    </div>
  </div>
</div>

<!-- Node detail modal -->
<div class="modal-backdrop" id="nodeModal">
  <div class="modal">
    <button class="modal-close" id="modalClose">×</button>
    <div class="modal-title" id="modalTitle"></div>
    <div id="modalBody"></div>
    <div class="modal-neighbors" id="modalNeighbors"></div>
  </div>
</div>

<script>
{SHARED_JS}

const NODES = {nodes_json};
const RELATED = {related_json};

// Render related communities. Ссылки чистые — без хеша, чтобы открывалась
// вкладка «Таблица» по умолчанию даже если на текущей странице активна Схема.
function navToCommunity(cid) {{
  // Используем location.assign + явно прописываем pathname без hash
  const targetPath = window.location.pathname.replace(/community_\d+\.html$/, 'community_' + cid + '.html');
  window.location.assign(targetPath);
}}

const relGrid = document.getElementById('relatedGrid');
if (RELATED.length === 0) {{
  relGrid.innerHTML = '<span style="color:var(--text3);font-size:13px;">Нет связей с другими модулями</span>';
}} else {{
  RELATED.forEach(r => {{
    const a = document.createElement('a');
    a.href = `community_${{r.cid}}.html`;
    a.className = 'rel-chip';
    a.addEventListener('click', e => {{ e.preventDefault(); navToCommunity(r.cid); }});
    a.innerHTML = `<span style="width:8px;height:8px;border-radius:50%;background:${{r.color}};flex-shrink:0;display:inline-block;"></span>
      ${{escHtml(r.label)}}
      <span class="rel-count">${{r.count}}</span>`;
    relGrid.appendChild(a);
  }});
}}

function escHtml(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}
function badgeHtml(ft) {{
  // Русские названия + цветовая маркировка
  const map = {{
    code:      ['Код',         'badge-code'],
    rationale: ['Обоснование', 'badge-rationale'],
    document:  ['Документ',    'badge-document'],
    template:  ['Шаблон',      'badge-template'],
    config:    ['Конфиг',      'badge-config'],
    test:      ['Тест',        'badge-test'],
    tests:     ['Тест',        'badge-test'],
    style:     ['Стиль',       'badge-style'],
  }};
  const m = map[ft];
  if (m) return '<span class="badge ' + m[1] + '">' + m[0] + '</span>';
  return '<span class="badge">' + escHtml(ft) + '</span>';
}}

// Переводит длинные английские label-ы (сгенерённые семантическим extract-ом)
// на русский по словарю-эвристике. Возвращает альтернативное имя или '' если перевод не найден.
function humanizeName(label) {{
  if (!label) return '';
  const lbl = String(label);
  // Если название уже на кириллице — пропускаем
  if (/[А-Яа-яЁё]/.test(lbl)) return '';
  // Слишком короткое (имя класса/функции) — без перевода
  if (lbl.length < 25) return '';
  // Словарь популярных шаблонов «Английский → Русский»
  const dict = [
    [/^Send notification about[^.]+/i,      'Отправка уведомления о событии'],
    [/^Send Telegram[^.]+/i,                'Отправка сообщения в Telegram'],
    [/^Send email[^.]+/i,                   'Отправка email-уведомления'],
    [/^Send SMS[^.]+/i,                     'Отправка SMS-уведомления'],
    [/^Generate (PDF|export|report|invoice)[^.]+/i, 'Генерация отчёта/документа'],
    [/^Render (template|form|page)[^.]+/i,  'Рендер шаблона/страницы'],
    [/^Get list of[^.]+/i,                  'Получить список'],
    [/^List of[^.]+/i,                      'Список'],
    [/^Return (list|set|dict|json)[^.]+/i,  'Возврат структурированных данных'],
    [/^Returns? (json|response|html|csv)[^.]+/i, 'Возврат данных API'],
    [/^Build (context|payload|request)[^.]+/i, 'Сборка запроса/контекста'],
    [/^Common context[^.]+/i,               'Общий контекст шаблона'],
    [/^Universal context[^.]+/i,            'Универсальный контекст'],
    [/^Creates?\s/i,                        'Создание сущности'],
    [/^Updates?\s/i,                        'Обновление сущности'],
    [/^Deletes?\s/i,                        'Удаление сущности'],
    [/^Imports?\s/i,                        'Импорт данных'],
    [/^Exports?\s/i,                        'Экспорт данных'],
    [/^Sync(s|hronize)?\s/i,                'Синхронизация'],
    [/^Validate[^.]+/i,                     'Валидация данных'],
    [/^Process (payment|webhook|request)[^.]+/i, 'Обработка платежа/webhook'],
    [/^Handle (webhook|event|signal)[^.]+/i,'Обработчик события'],
    [/^Celery beat task[^.]+/i,             'Периодическая Celery-задача'],
    [/^Celery (task|worker)[^.]+/i,         'Celery-задача (фоновая)'],
    [/^POST\s/i,                            'POST-обработчик'],
    [/^GET\s/i,                             'GET-обработчик'],
    [/^Redirect to[^.]+/i,                  'Редирект на другой URL'],
    [/^Redirect[^.]*/i,                     'Редирект'],
    [/^Test (connection|FTP|SSH|API)[^.]+/i,'Проверка соединения'],
    [/^Run (script|command|task)[^.]+/i,    'Запуск скрипта/команды'],
    [/^Show (form|page|dialog)[^.]+/i,      'Отображение формы/страницы'],
    [/^Save\s/i,                            'Сохранение'],
    [/^Load\s/i,                            'Загрузка'],
    [/^Apply (filter|migration|settings)[^.]+/i, 'Применение настроек/миграции'],
    [/^Migrate[^.]+/i,                      'Миграция данных/схемы'],
    [/^Build (config|payload|context)[^.]+/i, 'Сборка структуры'],
    [/^Compute[^.]+/i,                      'Вычисление'],
    [/^Calculate[^.]+/i,                    'Расчёт'],
    [/^Check[^.]+/i,                        'Проверка'],
    [/^Init[^.]+/i,                         'Инициализация'],
    [/^TODO:?\s/i,                          'TODO: задача в коде'],
    [/^FIXME:?\s/i,                         'FIXME: исправить'],
    [/^Helper[^.]+/i,                       'Вспомогательная функция'],
    [/^Universal\s/i,                       'Универсальный обработчик'],
    [/^Write (CSV|JSON|XML)[^.]+/i,         'Запись в CSV/JSON/XML'],
    [/^Core (export|import|logic)[^.]+/i,   'Основная логика модуля'],
  ];
  for (const [re, ru] of dict) {{
    if (re.test(lbl)) return ru;
  }}
  return '';
}}

// Table state
let sortCol = 'degree';
let sortDir = -1; // -1 = desc
let filterQ = '';
let filteredNodes = [...NODES];

function getVal(n, col) {{
  return n[col] !== undefined ? n[col] : '';
}}

function sort() {{
  filteredNodes.sort((a, b) => {{
    let va = getVal(a, sortCol), vb = getVal(b, sortCol);
    if (sortCol === 'degree') {{ va = +va; vb = +vb; }}
    else {{ va = String(va).toLowerCase(); vb = String(vb).toLowerCase(); }}
    if (va < vb) return -sortDir;
    if (va > vb) return sortDir;
    return 0;
  }});
}}

function filter() {{
  const q = filterQ.toLowerCase();
  filteredNodes = q
    ? NODES.filter(n => (n.label + ' ' + n.short_path).toLowerCase().includes(q))
    : [...NODES];
}}

function render() {{
  filter(); sort();
  const tbody = document.getElementById('nodesTbody');
  const empty = document.getElementById('nodesEmpty');
  const count = document.getElementById('nodeCount');
  count.textContent = `(${{filteredNodes.length}} / ${{NODES.length}})`;
  if (filteredNodes.length === 0) {{
    tbody.innerHTML = '';
    empty.style.display = '';
    return;
  }}
  empty.style.display = 'none';
  tbody.innerHTML = filteredNodes.map((n, i) => {{
    // Если есть человеческий перевод — показываем его как label, оригинал в title для tooltip
    const altName = humanizeName(n.label);
    const baseLbl = altName || n.label;
    const lbl = baseLbl.length > 70 ? baseLbl.slice(0,70)+'…' : baseLbl;
    const titleAttr = altName ? `title="${{escHtml(n.label)}}"` : '';
    return `<tr data-idx="${{i}}" style="cursor:pointer;" ${{titleAttr || 'title="Кликните для деталей"'}}>
      <td style="font-size:12px;font-family:monospace;">${{escHtml(lbl)}}</td>
      <td>${{badgeHtml(n.file_type)}}</td>
      <td class="file-path">${{escHtml(n.short_path || '—')}}</td>
      <td class="degree-num">${{n.degree}}</td>
    </tr>`;
  }}).join('');
  // Row click -> modal
  tbody.querySelectorAll('tr').forEach(tr => {{
    tr.addEventListener('click', () => {{
      const idx = +tr.dataset.idx;
      openModal(filteredNodes[idx]);
    }});
  }});
}}

// Sort on header click
document.querySelectorAll('#nodesTable th[data-col]').forEach(th => {{
  th.addEventListener('click', () => {{
    const col = th.dataset.col;
    if (sortCol === col) sortDir *= -1;
    else {{ sortCol = col; sortDir = (col === 'degree') ? -1 : 1; }}
    document.querySelectorAll('#nodesTable th').forEach(t => {{
      t.classList.remove('sorted-asc', 'sorted-desc');
    }});
    th.classList.add(sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
    render();
  }});
}});

// Search filter
let searchTimer2;
document.getElementById('nodeSearch').addEventListener('input', e => {{
  clearTimeout(searchTimer2);
  filterQ = e.target.value.trim();
  searchTimer2 = setTimeout(render, 100);
}});

// ── Helpers: укоротить путь файла + сгенерить чел.-понятное описание ────
function trimPath(p) {{
  if (!p) return '—';
  // Нормализуем к /
  const u = String(p).replace(/\\\\/g, '/');
  // Срезаем общий префикс до /carbon_modern/ или /app/
  let i = u.lastIndexOf('/carbon_modern/');
  if (i >= 0) return u.slice(i + '/carbon_modern/'.length);
  i = u.lastIndexOf('/app/');
  if (i >= 0) return u.slice(i + '/app/'.length);
  return u;
}}
function describeNode(n) {{
  // По file_type + label / suffix даём короткое чел.-описание на русском
  const ft = n.file_type || 'code';
  const lbl = n.label || '';
  if (ft === 'rationale') return 'Архитектурное решение или обоснование подхода.';
  if (ft === 'document')  return 'Документ или комментарий к коду.';
  // Для code — пытаемся определить тип сущности по имени
  // Длинные подписи (>=40 симв) выглядят как уже сгенерённые описания — возвращаем как есть
  if (lbl.length >= 40 && /[\.,—:!?]/.test(lbl)) return lbl;
  // Файлы (расширение)
  if (/\.py$/.test(lbl)) return 'Python-модуль (исходный файл).';
  if (/\.html$/.test(lbl)) return 'Django-шаблон HTML.';
  if (/\.(js|ts)$/.test(lbl)) return 'Скрипт фронтенда.';
  if (/\.(css|scss)$/.test(lbl)) return 'Стили оформления.';
  if (/\.(md|rst|txt)$/.test(lbl)) return 'Текстовая документация.';
  // Классы по суффиксу
  const suffix = (re) => re.test(lbl);
  const base = lbl.replace(/^_+|_+$/g, '');
  if (suffix(/View$/))         return 'Представление Django (обработчик HTTP-запроса).';
  if (suffix(/Form$/))         return 'Форма ввода / валидации данных.';
  if (suffix(/Serializer$/))   return 'DRF-сериализатор для REST API.';
  if (suffix(/Mixin$/))        return 'Миксин — переиспользуемый набор полей/методов.';
  if (suffix(/Manager$/))      return 'Менеджер модели Django (custom QuerySet).';
  if (suffix(/Queryset$|QuerySet$/)) return 'Кастомный QuerySet модели.';
  if (suffix(/Service$/))      return 'Сервисный слой бизнес-логики.';
  if (suffix(/Task$/))         return 'Celery-задача (фоновое выполнение).';
  if (suffix(/Handler$/))      return 'Обработчик события или сигнала.';
  if (suffix(/Backend$/))      return 'Бэкенд-адаптер (auth, storage и т.п.).';
  if (suffix(/Widget$/))       return 'UI-виджет формы или шаблона.';
  if (suffix(/Field$/))        return 'Кастомное поле модели или формы.';
  if (suffix(/Filter$/))       return 'Фильтр (django-filter / queryset filter).';
  if (suffix(/Adapter$/))      return 'Адаптер интеграции со сторонним сервисом.';
  if (suffix(/Client$/))       return 'HTTP-клиент к внешнему API.';
  if (suffix(/Helper$|Utils?$/)) return 'Утилиты — вспомогательные функции.';
  if (suffix(/Config$/))       return 'Конфигурация приложения / модуля.';
  if (suffix(/Middleware$/))   return 'Django middleware (обработка request/response).';
  if (suffix(/Command$/))      return 'Management-команда manage.py.';
  if (suffix(/Test|Tests$/))   return 'Юнит-тесты или тестовые сценарии.';
  if (suffix(/Migration$/))    return 'Миграция схемы БД.';
  if (suffix(/Webhook$/))      return 'Обработчик входящего webhook.';
  if (suffix(/Modal$|Dialog$/)) return 'Модальное окно UI.';
  if (suffix(/^[A-Z][a-z]+[A-Z]/) && /^[A-Z]/.test(lbl)) {{
    return 'Класс модели или сущность Django ORM.';
  }}
  if (/^[a-z_]+$/.test(lbl) && lbl.includes('_')) return 'Функция или модуль (snake_case).';
  return '—';
}}

// Modal
function openModal(n) {{
  // Заголовок: оригинальное имя + (если есть) альтернативный перевод серым шрифтом
  const altName = humanizeName(n.label);
  const titleEl = document.getElementById('modalTitle');
  titleEl.innerHTML = escHtml(n.label) +
    (altName ? ' <span class="modal-alt-name">— ' + escHtml(altName) + '</span>' : '');
  const desc = describeNode(n);
  const path = trimPath(n.source_file || '');
  document.getElementById('modalBody').innerHTML = `
    ${{desc && desc !== '—' ? `<div class="modal-desc">${{escHtml(desc)}}</div>` : ''}}
    <div class="modal-meta-row">
      <div class="mm-chip"><span class="mm-key" title="Уникальный идентификатор ноды в графе (соответствует Python-объекту в коде)">ID</span><span class="mm-val">${{escHtml(n.id)}}</span></div>
      <div class="mm-chip"><span class="mm-key" title="Тип содержимого ноды: код, шаблон, документ, конфиг и т.д.">Тип</span>${{badgeHtml(n.file_type)}}</div>
      <div class="mm-chip"><span class="mm-key">Позиция <span class="help-q" data-help="<b>Позиция</b> — номер строки в файле, где начинается класс или функция (Lxx). Удобно для быстрого перехода в IDE.">?</span></span><span class="mm-val">${{escHtml(n.source_location || '—')}}</span></div>
      <div class="mm-chip"><span class="mm-key">Связей <span class="help-q" data-help="<b>Связей</b> — сколько других нод связано с этим узлом через import (вход + выход). Чем выше, тем чаще используется.">?</span></span><span class="mm-val degree-num">${{n.degree}}</span></div>
    </div>
    <div class="modal-field">
      <div class="mf-label">Файл</div>
      <div class="mf-val">${{escHtml(path)}}</div>
    </div>
  `;
  const nbrs = n.neighbors || [];
  const nbrsHtml = nbrs.length
    ? `<div class="mn-title">Соседние ноды (${{nbrs.length}}):</div>` +
      nbrs.map(nb => {{
        const alt = humanizeName(nb.label);
        const text = alt || nb.label;
        const display = text.length > 40 ? text.slice(0,40)+'…' : text;
        return `<span class="neighbor-chip" title="${{escHtml(nb.id + (alt ? '  —  ' + nb.label : ''))}}">${{escHtml(display)}}</span>`;
      }}).join('')
    : '<div class="mn-title" style="color:var(--text3);">Нет соседних нод</div>';
  document.getElementById('modalNeighbors').innerHTML = nbrsHtml;
  document.getElementById('nodeModal').classList.add('open');
}}

document.getElementById('modalClose').addEventListener('click', () => {{
  document.getElementById('nodeModal').classList.remove('open');
}});
document.getElementById('nodeModal').addEventListener('click', e => {{
  if (e.target === document.getElementById('nodeModal'))
    document.getElementById('nodeModal').classList.remove('open');
}});
document.addEventListener('keydown', e => {{
  if (e.key === 'Escape') document.getElementById('nodeModal').classList.remove('open');
}});

// Initial render with degree desc sorted
const degTh = document.querySelector('#nodesTable th[data-col="degree"]');
if (degTh) degTh.classList.add('sorted-desc');
render();

// ── Tabs (Таблица / Схема) — lazy-load schema only on first activation ────
(function setupTabs() {{
  const buttons = document.querySelectorAll('.wiki-tab-btn');
  const contents = document.querySelectorAll('.tab-content');
  let schemaLoaded = false;
  function activate(tabName) {{
    buttons.forEach(b => {{
      const isActive = b.dataset.tab === tabName;
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-selected', isActive ? 'true' : 'false');
    }});
    contents.forEach(c => {{
      if (c.dataset.content === tabName) c.removeAttribute('hidden');
      else c.setAttribute('hidden', '');
    }});
    if (tabName === 'schema' && !schemaLoaded) {{
      schemaLoaded = true;
      loadSchema();
    }}
    // Сохраняем выбор в URL hash для шаринга — но только если активна Схема.
    // На Таблице чистим хеш (без оставшегося '#'), чтобы навигация на другие
    // community_*.html не подхватывала старый #schema.
    if (history.replaceState) {{
      if (tabName === 'schema') {{
        history.replaceState(null, '', '#schema');
      }} else {{
        // Удаляем хеш полностью — без концевого '#'
        history.replaceState(null, '', window.location.pathname + window.location.search);
      }}
    }}
  }}
  buttons.forEach(b => b.addEventListener('click', () => activate(b.dataset.tab)));
  // Инициализация — поддерживаем #schema в URL
  if (window.location.hash === '#schema') activate('schema');
}})();

// ── vis-network: lazy CDN load + render ────────────────────────────────────
const COMMUNITY_CID = {cid};
let visLib = null;
let visNetwork = null;
let visNodes = null;
let visEdges = null;
let visGraphData = null;

function loadVisCDN() {{
  return new Promise((resolve, reject) => {{
    if (window.vis) {{ visLib = window.vis; resolve(window.vis); return; }}
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js';
    s.async = true;
    s.onload = () => {{ visLib = window.vis; resolve(window.vis); }};
    s.onerror = () => reject(new Error('vis-network CDN load failed'));
    document.head.appendChild(s);
  }});
}}

async function loadSchema() {{
  const cont = document.getElementById('visGraph');
  try {{
    await loadVisCDN();
    const resp = await fetch('community_' + COMMUNITY_CID + '_graph.json');
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    visGraphData = await resp.json();
    cont.innerHTML = '';
    renderSchema();
    initSchemaControls();
    populateSidebar();
  }} catch (e) {{
    cont.innerHTML = '<div class="vis-loading" style="color:#dc3545">Ошибка загрузки схемы: ' + escHtml(e.message) + '</div>';
    console.error(e);
  }}
}}

function initSchemaHelpToggle() {{
  const help = document.getElementById('schemaHelp');
  const toggle = document.getElementById('schemaHelpToggle');
  if (!help || !toggle) return;
  const STORAGE_KEY = 'schemaHelpCollapsed';
  const collapsed = localStorage.getItem(STORAGE_KEY) === '1';
  function apply(v) {{
    help.dataset.collapsed = v ? 'true' : 'false';
    toggle.textContent = v ? 'Показать подсказку' : 'Скрыть подсказку';
  }}
  apply(collapsed);
  toggle.addEventListener('click', () => {{
    const next = help.dataset.collapsed !== 'true';
    apply(next);
    localStorage.setItem(STORAGE_KEY, next ? '1' : '0');
  }});
}}

function populateSidebar() {{
  initSchemaHelpToggle();
  const stats = visGraphData.stats || {{}};
  const nodesN = stats.nodes || visGraphData.nodes.length;
  const edgesN = stats.edges || visGraphData.edges.length;
  // Footer + overlay-badge
  const footerEl = document.getElementById('schemaFooterCount');
  if (footerEl) footerEl.textContent = nodesN + ' нод · ' + edgesN + ' связей';
  const badgeEl = document.getElementById('schemaStatsBadge');
  if (badgeEl) badgeEl.textContent = nodesN + ' нод · ' + edgesN + ' связей';
  // Связанные модули — берём из RELATED, который уже есть в JS-окружении
  const legendEl = document.getElementById('schemaLegendList');
  if (legendEl) {{
    if (Array.isArray(RELATED) && RELATED.length) {{
      legendEl.innerHTML = '';
      legendEl.classList.remove('si-empty');
      legendEl.removeAttribute('style');
      RELATED.slice(0, 12).forEach(r => {{
        const a = document.createElement('a');
        a.href = 'community_' + r.cid + '.html';
        a.className = 'leg-item';
        a.style.color = 'var(--text2)';
        a.style.textDecoration = 'none';
        // Принудительно открываем целевую страницу без хеша → активна Таблица
        a.addEventListener('click', e => {{ e.preventDefault(); navToCommunity(r.cid); }});
        a.innerHTML = '<span class="leg-dot" style="background:' + r.color + '"></span>' +
                      '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + escHtml(r.label) + '</span>' +
                      '<span style="color:var(--text3);font-size:11px">' + r.count + '</span>';
        legendEl.appendChild(a);
      }});
    }} else {{
      legendEl.textContent = 'Нет связей с другими модулями';
    }}
  }}
}}

function getThemeColors() {{
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  return {{
    edge: isDark ? '#475569' : '#94a3b8',
    edgeHover: isDark ? '#26a69a' : '#00897b',
    label: isDark ? '#e2e8f0' : '#1f2d3d',
    nodeBorderHL: isDark ? '#fff' : '#0f172a',
    bg: isDark ? '#172033' : '#f0f4f8',
  }};
}}

function renderSchema() {{
  const cont = document.getElementById('visGraph');
  const tc = getThemeColors();
  // Enrich nodes with theme-aware label colors
  const nodesArr = visGraphData.nodes.map(n => Object.assign({{}}, n, {{
    font: Object.assign({{}}, n.font || {{}}, {{ color: tc.label }}),
  }}));
  const edgesArr = visGraphData.edges.map(e => Object.assign({{}}, e, {{
    color: {{ color: tc.edge, highlight: tc.edgeHover, hover: tc.edgeHover, opacity: 0.55 }},
    smooth: {{ type: 'continuous', roundness: 0.4 }},
    width: 1,
  }}));
  visNodes = new visLib.DataSet(nodesArr);
  visEdges = new visLib.DataSet(edgesArr);
  visNetwork = new visLib.Network(cont, {{ nodes: visNodes, edges: visEdges }}, {{
    nodes: {{
      shape: 'dot', borderWidth: 2,
      font: {{ size: 11, face: 'Segoe UI, Arial', color: tc.label, strokeWidth: 0 }},
    }},
    edges: {{ arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }} }},
    physics: {{
      barnesHut: {{ gravitationalConstant: -3000, springLength: 90, springConstant: 0.04, damping: 0.4 }},
      stabilization: {{ iterations: 250, updateInterval: 25 }},
    }},
    interaction: {{ hover: true, tooltipDelay: 220, multiselect: false, navigationButtons: false, keyboard: false }},
    layout: {{ improvedLayout: visGraphData.nodes.length < 250 }},
  }});
  // После стабилизации физика выключается чтобы не дёргалось
  visNetwork.once('stabilizationIterationsDone', () => {{
    visNetwork.setOptions({{ physics: {{ enabled: false }} }});
    const btn = document.getElementById('schemaPhysicsBtn');
    if (btn) btn.classList.remove('active');
  }});
  visNetwork.on('click', e => {{
    if (e.nodes.length) showNodeInfo(e.nodes[0]);
    else clearNodeInfo();
  }});
}}

function showNodeInfo(nodeId) {{
  const n = visGraphData.nodes.find(x => x.id === nodeId);
  if (!n) return;
  const conns = visGraphData.edges.filter(e => e.from === nodeId || e.to === nodeId);
  const neighbors = conns.map(e => e.from === nodeId ? e.to : e.from);
  const neighborSet = [...new Set(neighbors)];
  const path = trimPath(n.source_file || '');
  const altName = humanizeName(n.label);
  const panel = document.getElementById('schemaInfoPanel');
  let html = '<div class="si-section-title">О ноде</div>';
  html += '<div class="si-name">' + escHtml(n.label) + '</div>';
  if (altName) html += '<div class="si-alt">— ' + escHtml(altName) + '</div>';
  html += '<div class="si-field">Тип: ' + badgeHtml(n.file_type || 'code') + '</div>';
  html += '<div class="si-field">Связей: <b>' + (n.degree || conns.length) + '</b></div>';
  if (n.source_location) html += '<div class="si-field">Позиция: <b>' + escHtml(n.source_location) + '</b></div>';
  if (path && path !== '—') html += '<div class="si-field"><code>' + escHtml(path) + '</code></div>';
  if (neighborSet.length) {{
    html += '<div class="si-section-title" style="margin-top:14px">Соседи (' + neighborSet.length + ')</div>';
    html += '<div class="si-neighbors">';
    neighborSet.forEach(nbId => {{
      const nb = visGraphData.nodes.find(x => x.id === nbId);
      const lbl = nb ? (humanizeName(nb.label) || nb.label) : nbId;
      const display = lbl.length > 38 ? lbl.slice(0,38)+'…' : lbl;
      const color = nb && nb.color && nb.color.background ? nb.color.background : 'var(--border)';
      html += '<span class="si-nb-item" data-jump="' + escHtml(nbId) +
              '" style="border-left-color:' + color + '" title="' + escHtml(nb ? nb.label : nbId) + '">' +
              escHtml(display) + '</span>';
    }});
    html += '</div>';
  }}
  panel.innerHTML = html;
  panel.querySelectorAll('[data-jump]').forEach(el => {{
    el.addEventListener('click', () => {{
      const id = el.dataset.jump;
      visNetwork.selectNodes([id]);
      visNetwork.focus(id, {{ animation: {{ duration: 400, easingFunction: 'easeInOutQuad' }}, scale: 1.2 }});
      showNodeInfo(id);
    }});
  }});
}}

function clearNodeInfo() {{
  document.getElementById('schemaInfoPanel').innerHTML =
    '<div class="si-section-title">О ноде</div>' +
    '<div class="si-empty">Кликните по узлу графа, чтобы увидеть детали.</div>';
}}

function initSchemaControls() {{
  // Search with dropdown results
  const search = document.getElementById('schemaSearch');
  const results = document.getElementById('schemaSearchResults');
  if (search && results) {{
    search.addEventListener('input', () => {{
      const q = search.value.trim().toLowerCase();
      if (!q) {{
        results.classList.remove('visible');
        results.innerHTML = '';
        visNetwork.unselectAll();
        return;
      }}
      const matches = visGraphData.nodes.filter(n =>
        (n.label || '').toLowerCase().includes(q) ||
        (n.id || '').toLowerCase().includes(q)
      ).slice(0, 30);
      if (!matches.length) {{
        results.innerHTML = '<div class="ssi" style="color:var(--text3)">Ничего не найдено</div>';
        results.classList.add('visible');
        return;
      }}
      results.innerHTML = matches.map(n => {{
        const alt = humanizeName(n.label);
        const lbl = alt || n.label;
        const display = lbl.length > 32 ? lbl.slice(0,32)+'…' : lbl;
        return '<div class="ssi" data-jump="' + escHtml(n.id) +
               '" title="' + escHtml(n.label) + '">' + escHtml(display) + '</div>';
      }}).join('');
      results.classList.add('visible');
      results.querySelectorAll('[data-jump]').forEach(el => {{
        el.addEventListener('click', () => {{
          const id = el.dataset.jump;
          visNetwork.selectNodes([id]);
          visNetwork.focus(id, {{ animation: true, scale: 1.4 }});
          showNodeInfo(id);
          search.value = '';
          results.classList.remove('visible');
        }});
      }});
      visNetwork.selectNodes(matches.map(m => m.id));
    }});
    // Close dropdown on outside click
    document.addEventListener('click', e => {{
      if (!search.contains(e.target) && !results.contains(e.target)) {{
        results.classList.remove('visible');
      }}
    }});
  }}
  // Reset
  document.getElementById('schemaResetBtn').addEventListener('click', () => {{
    visNetwork.fit({{ animation: {{ duration: 600, easingFunction: 'easeInOutQuad' }} }});
    visNetwork.unselectAll();
    clearNodeInfo();
  }});
  // Physics toggle
  const physBtn = document.getElementById('schemaPhysicsBtn');
  physBtn.addEventListener('click', () => {{
    const on = !physBtn.classList.contains('active');
    physBtn.classList.toggle('active', on);
    visNetwork.setOptions({{ physics: {{ enabled: on }} }});
  }});
  // Labels toggle (active = подписи видны)
  let labelsOn = true;
  document.getElementById('schemaLabelsBtn').addEventListener('click', () => {{
    labelsOn = !labelsOn;
    document.getElementById('schemaLabelsBtn').classList.toggle('active', labelsOn);
    const updates = visGraphData.nodes.map(n => ({{
      id: n.id,
      font: {{ size: labelsOn ? 11 : 0, color: getThemeColors().label }}
    }}));
    visNodes.update(updates);
  }});
  // Re-theme on theme change
  const themeObserver = new MutationObserver(() => {{
    if (!visNetwork) return;
    const tc = getThemeColors();
    const labelUpdates = visGraphData.nodes.map(n => ({{ id: n.id, font: {{ color: tc.label }} }}));
    const edgeUpdates = visGraphData.edges.map(e => ({{
      id: e.id || (e.from + '-' + e.to),
      color: {{ color: tc.edge, highlight: tc.edgeHover, hover: tc.edgeHover, opacity: 0.55 }}
    }}));
    visNodes.update(labelUpdates);
    // Note: edges не имеют id по умолчанию; edges.update требует id, поэтому пересоздаём dataset
    const edgesArr = visGraphData.edges.map(e => Object.assign({{}}, e, {{
      color: {{ color: tc.edge, highlight: tc.edgeHover, hover: tc.edgeHover, opacity: 0.55 }},
    }}));
    visEdges.clear();
    visEdges.add(edgesArr.map((e, i) => Object.assign({{ id: 'e' + i }}, e)));
  }});
  themeObserver.observe(document.documentElement, {{ attributes: true, attributeFilter: ['data-theme'] }});
}}
</script>
</body>
</html>"""
    return html


def main():
    print("Loading data files...")
    extract, analysis, labels = load_data()

    nodes: list = extract["nodes"]
    edges: list = extract["edges"]
    communities: dict = analysis["communities"]

    # Build lookup structures
    nodes_by_id = {n["id"]: n for n in nodes}
    node_to_cid: dict = {}
    for cid, nids in communities.items():
        for nid in nids:
            node_to_cid[nid] = cid

    print(f"  Nodes: {len(nodes)}, Edges: {len(edges)}, Communities: {len(communities)}")

    color_map = build_color_map(communities)
    degrees = compute_degrees(nodes, edges)
    cross_edges = compute_cross_edges(edges, node_to_cid)
    intra_edges = compute_intra_edges(edges, node_to_cid)
    neighbor_map = build_neighbor_map(edges)

    # Filter out tiny/technical communities below threshold
    all_communities_sorted = sorted(
        [cid for cid in communities.keys() if len(communities[cid]) >= MIN_NODE_COUNT],
        key=int
    )

    # Create output directory
    OUT_DIR.mkdir(exist_ok=True)
    print(f"Output directory: {OUT_DIR}")

    # Generate index.html
    print("Generating index.html...")
    index_html = generate_index(
        communities, nodes_by_id, degrees, cross_edges, color_map, labels, intra_edges
    )
    with open(OUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"  Written: {OUT_DIR / 'index.html'} ({len(index_html):,} bytes)")

    # Generate community pages
    print(f"Generating {len(communities)} community pages...")
    for cid in all_communities_sorted:
        html = generate_community_page(
            cid=cid,
            communities=communities,
            nodes_by_id=nodes_by_id,
            degrees=degrees,
            cross_edges=cross_edges,
            intra_edges=intra_edges,
            color_map=color_map,
            labels=labels,
            neighbor_map=neighbor_map,
            node_to_cid=node_to_cid,
            all_communities_sorted=all_communities_sorted,
        )
        out_file = OUT_DIR / f"community_{cid}.html"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)

    print(f"\nDone! Generated:")
    print(f"  {OUT_DIR / 'index.html'}")
    for cid in all_communities_sorted:
        print(f"  {OUT_DIR / f'community_{cid}.html'}")
    print(f"\nTotal: 1 index + {len(communities)} community pages")


if __name__ == "__main__":
    main()
