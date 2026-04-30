"""Auto-generated icons module — извлечён из run_labels.py.

Содержит COMM_ICONS (имя иконки для каждого community-id) и
ICON_PATHS (SVG path-d для каждой именованной иконки Tabler).

Регенерация: запустить graphify pipeline → run_labels.py обновит
свои ICONS/ICON_PATHS, после чего скопировать словари сюда вручную
или через `extract_icons.py`.
"""
"""
Step 5: Label communities with meaningful names and regenerate report + HTML.
"""
import json
from pathlib import Path

OUT = Path('graphify-out')
BASE = Path('.')

# Community labels (Russian) + emoji icons shown inside bubbles
LABELS = {
    0:  "Карточка абонента",
    1:  "Личный кабинет",
    2:  "Финансы и деньги",
    3:  "Поиск абонентов",
    4:  "Мобильный API",
    5:  "Авторизация",
    6:  "ACL и соцсети",
    7:  "Блокировки",
    8:  "Резервные копии",
    9:  "IPTV",
    10: "Фреймворк форм",
    11: "Задачи биллинга",
    12: "Шаблоны ЛК",
    13: "Интерфейс",
    14: "Отчёты СОРМ",
    15: "Платёжные системы",
    16: "Сообщения",
    17: "Мобильная авторизация",
    18: "Push-уведомления",
    19: "Модель аккаунта",
    20: "FreeScout Webhooks",
    21: "Авторизация ЛК",
    22: "Фильтры шаблонов",
    23: "Пакет мобильного API",
    24: "Конфигурация",
    25: "Адреса",
    26: "URL мобильного API",
    28: "Миграции БД",
    29: "Учёт баланса",
    30: "Текущий баланс",
    31: "Баланс месяца",
    32: "Приоритет шаблонов",
    33: "Исправление SQL",
    34: "Аватары",
}

# SVG icon paths (Tabler Icons contour style, viewBox 0 0 24 24, stroke-based)
# Each value is the path/shape data rendered at ~40% bubble radius
ICONS = {
    0:  "user",           # Карточка абонента
    1:  "home",           # Личный кабинет
    2:  "credit-card",    # Финансы
    3:  "search",         # Поиск
    4:  "device-mobile",  # Мобильный API
    5:  "lock",           # Авторизация
    6:  "world",          # ACL / соцсети
    7:  "ban",            # Блокировки
    8:  "database",       # Резервные копии
    9:  "device-tv",      # IPTV
    10: "layout-list",    # Формы
    11: "settings",       # Задачи биллинга
    12: "file-text",      # Шаблоны ЛК
    13: "layout-dashboard",  # Интерфейс
    14: "shield-check",   # СОРМ
    15: "cash",           # Платежи
    16: "mail",           # Сообщения
    17: "key",            # Мобильная авт.
    18: "bell",           # Push
    19: "users",          # Аккаунт
    20: "ticket",         # FreeScout
    21: "shield",         # Авт. ЛК
    22: "code",           # Фильтры
    23: "package",        # Пакет
    24: "adjustments",    # Конфиг
    25: "building",       # Адреса
    26: "link",           # URL
    28: "table",          # Миграции
    29: "chart-bar",      # Учёт
    30: "trending-up",    # Баланс
    31: "calendar",       # Баланс месяца
    32: "layers-intersect",  # Приоритет
    33: "tool",           # SQL fix
    34: "photo",          # Аватары
}

# Tabler Icons SVG paths (stroke-based, 24x24, ready to embed)
ICON_PATHS = {
    "user": "M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z",
    "home": "M3 9.5L12 3l9 6.5V21H3V9.5z M9 21v-6h6v6",
    "credit-card": "M3 6h18a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1zm-1 5h20M7 16h2M11 16h4",
    "search": "M11 5a6 6 0 1 0 0 12A6 6 0 0 0 11 5zm9 14l-4.35-4.35",
    "device-mobile": "M7 4h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm5 14v.01",
    "lock": "M5 11V7a7 7 0 1 1 14 0v4M4 11h16a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-8a1 1 0 0 1 1-1zm8 4v2",
    "world": "M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zM2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20",
    "ban": "M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zM4.93 4.93l14.14 14.14",
    "database": "M12 3c4.97 0 9 1.12 9 2.5v13C21 19.88 17 21 12 21s-9-1.12-9-2.5v-13C3 4.12 7.03 3 12 3zm9 4.5c0 1.38-4.03 2.5-9 2.5S3 8.88 3 7.5m18 5c0 1.38-4.03 2.5-9 2.5S3 13.88 3 12.5",
    "device-tv": "M3 7h18a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1zM8 19l-2 3M16 19l2 3M12 3l-4 4M12 3l4 4",
    "layout-list": "M4 6h16M4 10h16M4 14h10M4 18h10M14 14h6v4h-6z",
    "settings": "M12 12m-2 0a2 2 0 1 0 4 0 2 2 0 1 0-4 0M12 2v3m0 14v3M4.22 4.22l2.12 2.12m11.32 11.32 2.12 2.12M2 12h3m14 0h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12",
    "file-text": "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm0 0v6h6M9 13h6M9 17h4",
    "layout-dashboard": "M4 4h6v8H4zm10 0h6v4h-6zM4 16h6v4H4zm10-4h6v8h-6z",
    "shield-check": "M12 3L4 7v5c0 4.97 3.37 9.08 8 10 4.63-.92 8-5.03 8-10V7l-8-4zm-2 9l2 2 4-4",
    "cash": "M3 6h18v12H3zM3 10h18M7 14h2M13 14h4",
    "mail": "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm18 2l-10 7L2 6",
    "key": "M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4",
    "bell": "M10 5a2 2 0 1 1 4 0 7 7 0 0 1 4 6v3l2 2H4l2-2v-3a7 7 0 0 1 4-6zM9 17v1a3 3 0 0 0 6 0v-1",
    "users": "M9 7a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm6 0a4 4 0 0 1 0 8M1 21v-2a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v2m0-14a4 4 0 0 1 0 8",
    "ticket": "M15 5v2m0 4v2m0 4v2M5 5h14a2 2 0 0 1 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3a2 2 0 0 0 0-4V7a2 2 0 0 1 2-2z",
    "shield": "M12 3L4 7v5c0 4.97 3.37 9.08 8 10 4.63-.92 8-5.03 8-10V7l-8-4z",
    "code": "M7 8l-4 4 4 4m10-8 4 4-4 4m-5-11-2 14",
    "package": "M12 3l9 4.5v9L12 21l-9-4.5v-9L12 3zm0 0v9m9-4.5L12 12m-9-4.5L12 12",
    "adjustments": "M4 8h16M6 16h12M12 4v4M8 12v4M16 12v4",
    "building": "M3 21h18M5 21V7l7-4 7 4v14M9 21v-4h6v4M9 9h1v1H9zm5 0h1v1h-1zM9 13h1v1H9zm5 0h1v1h-1z",
    "link": "M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 1 0-5.66-5.66l-1.5 1.5M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1.5-1.5",
    "table": "M3 5h18v14H3zM3 10h18M3 15h18M8 5v14M13 5v14",
    "chart-bar": "M4 20h16M8 8v12M12 4v16M16 10v10",
    "trending-up": "M3 17l6-6 4 4 8-8M17 7h4v4",
    "calendar": "M4 5h16a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM16 3v4M8 3v4M3 10h18",
    "layers-intersect": "M7 3h10v10H7zm4 4h10v10H11zm-4 4h10v10H7z",
    "tool": "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
    "photo": "M15 8a1 1 0 1 0 2 0 1 1 0 0 0-2 0zM3 6h18v13H3zM3 13l5-5 4 4 3-3 5 4",
}

