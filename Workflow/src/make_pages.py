#!/usr/bin/env python3
"""Брендовые страницы для схем СмИТ Биллинг.

Вьюер archify сам подбирает раскладку под высоту окна и о внешней шапке
ничего не знает: любая полоса поверх артефакта отнимает высоту и даёт
вертикальную прокрутку. Поэтому схема и оформление разделены:

* `viewer/<имя>.html` — артефакт archify как есть (проверки 9/9 и
  visual-check остаются честными);
* `<имя>.html` — страница в стиле витрины: шапка с логотипом, названием
  и ссылками, а под ней схема во весь оставшийся экран.

Внутри рамки вьюер видит собственную высоту и укладывается в неё целиком.
Якорь страницы (`#focus=…`, `#view=…`) прокидывается в схему, поэтому
ссылки на конкретный узел продолжают работать.

Запуск: python src/make_pages.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VIEWER_DIR = os.path.join(ROOT, 'viewer')
GRAPH_URL = 'https://docs.billing.smit34.ru/understand/'
SITE_URL = 'https://docs.billing.smit34.ru/Workflow/'
# картинки и медиа хранятся в облаке, на сервере документации их нет
COVERS_URL = 'https://storage.googleapis.com/uspeshnyy-projects/smit/billing/workflow/'
DESCRIPTIONS = {'smitbilling-runtime.architecture.html': 'Каналы, ядро в Docker Compose и внешние сервисы биллинга.',
    'smitbilling-charges.workflow.html': 'Как выбираются услуги, считается сумма и когда списание пропускается.',
    'smitbilling-payment.sequence.html': 'От создания платежа до зачисления, чека и снятия блокировки.',
    'smitbilling-abonent.lifecycle.html': 'Минус на счёте, блокировка, отсрочка, обещанный платёж и возврат доступа.',
    'smitbilling-sorm.dataflow.html': 'От данных биллинга до файла на FTP пункта управления.',
    'smitbilling-radius.sequence.html': 'Авторизация через кэш, учёт сессии через очередь и природа таймаутов.',
    'smitbilling-block.sequence.html': 'Порог по лимиту счёта, разрыв сессии на узлах и включение после оплаты.',
    'smitbilling-finblock.architecture.html': 'Адрес из отдельного пула и страница оплаты вместо отказа в доступе.',
    'smitbilling-support.workflow.html': 'Путь обращения от канала до тикета, ответа ассистента и оператора.',
    'smitbilling-ai.sequence.html': 'Организация, вызов модели через шлюз лицензий и инструменты с данными клиента.',
    'smitbilling-deal.lifecycle.html': 'Стадии воронки, причина отказа и создание абонента из сделки.',
    'smitbilling-bank.dataflow.html': 'Письмо банка, поиск клиента по реквизитам, зачисление и документы.',
    'smitbilling-fiscal.lifecycle.html': 'Когда чек пробивается, когда нет и что происходит при сбое кассы.',
    'smitbilling-deploy.workflow.html': 'Порядок шагов на боевом сервере и места, где теряются чужие правки.',
    'smitbilling-queues.architecture.html': 'Три очереди с отдельными воркерами и что по какой идёт.',
    'smitbilling-org.dataflow.html': 'Как право доступа и ключ кэша определяют, чьи данные видит сотрудник.'}

PAGES = [
    # базовые
    ('smitbilling-runtime.architecture.html', 'Runtime-архитектура', 'Архитектура'),
    ('smitbilling-charges.workflow.html', 'Прогон абонплаты', 'Процесс'),
    ('smitbilling-payment.sequence.html', 'Оплата через ЮKassa', 'Последовательность'),
    ('smitbilling-abonent.lifecycle.html', 'Абонент по балансу', 'Состояния'),
    ('smitbilling-sorm.dataflow.html', 'Выгрузка СОРМ', 'Поток данных'),
    # сеть и эксплуатация
    ('smitbilling-radius.sequence.html', 'Путь RADIUS-пакета', 'Последовательность'),
    ('smitbilling-block.sequence.html', 'Блокировка и возврат доступа', 'Последовательность'),
    ('smitbilling-finblock.architecture.html', 'Финблокировка и заглушка', 'Архитектура'),
    # поддержка и продажи
    ('smitbilling-support.workflow.html', 'Путь обращения', 'Процесс'),
    ('smitbilling-ai.sequence.html', 'Запрос к ассистенту', 'Последовательность'),
    ('smitbilling-deal.lifecycle.html', 'Жизненный цикл сделки', 'Состояния'),
    # деньги
    ('smitbilling-bank.dataflow.html', 'Банковская выписка', 'Поток данных'),
    ('smitbilling-fiscal.lifecycle.html', 'Путь чека до ОФД', 'Состояния'),
    # разработчикам
    ('smitbilling-deploy.workflow.html', 'Безопасный деплой', 'Процесс'),
    ('smitbilling-queues.architecture.html', 'Очереди и фоновые задачи', 'Архитектура'),
    ('smitbilling-org.dataflow.html', 'Разделение по организациям', 'Поток данных'),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title} — СмИТ Биллинг</title>
<link rel="icon" href="../favicon.svg">
<meta property="og:type" content="article">
<meta property="og:site_name" content="СмИТ Биллинг">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{site}{file}">
<meta property="og:image" content="{covers}{base}.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="675">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{covers}{base}.jpg">
<style>
  :root{{
    --em-400:#34d399; --em-500:#10b981; --em-600:#059669; --em-700:#047857;
    --bg:#f4f6f8; --card:#ffffff; --border:rgba(0,0,0,.08);
    --text:#0f172a; --mute:#5a6a7d;
  }}
  @media (prefers-color-scheme: dark){{
    :root:not([data-theme="light"]){{
      --bg:#0b1220; --card:rgba(30,41,59,.55); --border:rgba(255,255,255,.08);
      --text:#e9ecef; --mute:#94a3b8; --em-700:#34d399; --em-600:#10b981;
    }}
  }}
  /* выбор темы с витрины перебивает системную настройку */
  :root[data-theme="dark"]{{
    --bg:#0b1220; --card:rgba(30,41,59,.55); --border:rgba(255,255,255,.08);
    --text:#e9ecef; --mute:#94a3b8; --em-700:#34d399; --em-600:#10b981;
  }}
  *{{box-sizing:border-box}}
  html,body{{height:100%}}
  body{{
    margin:0; display:flex; flex-direction:column;
    background:var(--bg); color:var(--text);
    font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  }}
  .topbar{{
    flex:0 0 auto;
    display:flex; align-items:center; gap:10px; flex-wrap:wrap;
    padding:6px 18px;
    background:var(--card); border-bottom:1px solid var(--border);
  }}
  .logo{{
    width:28px; height:28px; flex:0 0 28px; border-radius:9px;
    background:linear-gradient(135deg,var(--em-400),var(--em-600));
    color:#fff; font-weight:800; font-size:14px;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 4px 12px rgba(16,185,129,.35);
  }}
  .brand{{display:flex; align-items:baseline; gap:9px; min-width:0}}
  .brand-name{{font-weight:700; font-size:15px; letter-spacing:-.01em; white-space:nowrap}}
  .brand-title{{font-size:14px; color:var(--mute); white-space:nowrap;
    overflow:hidden; text-overflow:ellipsis}}
  .badge{{
    flex:0 0 auto; padding:2px 10px; border-radius:100px;
    background:rgba(16,185,129,.15); border:1px solid rgba(16,185,129,.25);
    color:var(--em-700); font-size:10.5px; font-weight:600;
    text-transform:uppercase; letter-spacing:1.3px; white-space:nowrap;
  }}
  .spacer{{flex:1 1 auto}}
  .topbar a{{
    display:inline-flex; align-items:center; gap:7px; padding:5px 12px;
    border-radius:9px; border:1px solid var(--border);
    color:var(--text); text-decoration:none;
    font-size:13px; font-weight:500; white-space:nowrap;
    transition:border-color .16s ease, color .16s ease;
  }}
  .topbar a svg{{width:15px; height:15px; flex:0 0 15px}}
  .topbar a:hover{{border-color:var(--em-600); color:var(--em-700)}}
  .topbar a:focus-visible{{outline:2px solid var(--em-600); outline-offset:2px}}
  .stage{{flex:1 1 auto; min-height:0}}
  .stage iframe{{display:block; width:100%; height:100%; border:0}}
  /* тема и экспорт на телефоне переезжают сюда из панели просмотрщика */
  .icon-btn{{
    display:none; align-items:center; justify-content:center;
    width:34px; height:34px; padding:0; flex:0 0 34px;
    border-radius:9px; border:1px solid var(--border);
    background:var(--card); color:var(--text); cursor:pointer;
  }}
  .icon-btn svg{{width:17px; height:17px}}
  .icon-btn:focus-visible{{outline:2px solid var(--em-600); outline-offset:2px}}
  .ic-sun{{display:none}}
  @media (prefers-color-scheme: dark){{
    :root:not([data-theme="light"]) .ic-moon{{display:none}}
    :root:not([data-theme="light"]) .ic-sun{{display:block}}
  }}
  :root[data-theme="dark"] .ic-moon{{display:none}}
  :root[data-theme="dark"] .ic-sun{{display:block}}
  :root[data-theme="light"] .ic-moon{{display:block}}
  :root[data-theme="light"] .ic-sun{{display:none}}
  @media (max-width:760px){{
    .topbar{{padding:8px 12px; gap:8px}}
    .brand-title, .badge{{display:none}}
    /* из ссылок на телефоне нужен только возврат к списку схем */
    .topbar a + a{{display:none}}
    .icon-btn{{display:inline-flex}}
  }}
</style>
</head>
<body>

<header class="topbar">
  <div class="logo" aria-hidden="true">С</div>
  <div class="brand">
    <span class="brand-name">СмИТ Биллинг</span>
    <span class="brand-title">{title}</span>
  </div>
  <span class="badge">{kind}</span>
  <div class="spacer"></div>
  <button class="icon-btn" id="m-theme" type="button" aria-label="Переключить тему"><svg class="ic-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 14.3A8.6 8.6 0 0 1 9.7 3.5a8.6 8.6 0 1 0 10.8 10.8z"/></svg><svg class="ic-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/></svg></button>
  <button class="icon-btn" id="m-export" type="button" aria-label="Экспорт схемы"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.5v11"/><path d="m7.5 10.5 4.5 4.5 4.5-4.5"/><path d="M4.5 19.5h15"/></svg></button>
  <a href="index.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7.5" height="7.5" rx="1.6"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6"/></svg>Все схемы</a>
  <a href="viewer/{file}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6"/><path d="M20 4 11 13"/><path d="M19 14.5V19a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 19V6.5A1.5 1.5 0 0 1 5 5h4.5"/></svg>Открыть отдельно</a>
  <a href="../index.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v14.5H6.5A2.5 2.5 0 0 0 4 20z"/><path d="M4 20a2.5 2.5 0 0 1 2.5-2.5H20V21H6.5A2.5 2.5 0 0 1 4 20z"/><path d="M8 7.5h8"/></svg>Документация</a>

  <a href="{graph}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="5.2" r="2.4"/><circle cx="5.5" cy="18" r="2.4"/><circle cx="18.5" cy="18" r="2.4"/><path d="M10.6 7.2 6.9 15.9M13.4 7.2l3.7 8.7M7.9 18h8.2"/></svg>Граф знаний</a>
  <a href="https://billing.smit34.ru/"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2.2"/><path d="M3 9.5h18M7.5 14h4M7.5 17h6"/></svg>Биллинг</a>
</header>

<main class="stage">
  <iframe id="stage" title="{title}" src="viewer/{file}"></iframe>
</main>

<script>
  // Тема выбирается на витрине и запоминается; здесь её подхватывают шапка
  // и сам просмотрщик. Без сохранённого выбора остаётся системная.
  // Якорь страницы прокидываем в схему: ссылки вида #focus=… продолжают работать.
  (function () {{
    var frame = document.getElementById('stage');
    var base = 'viewer/{file}';
    var theme = null;
    try {{ theme = localStorage.getItem('smit-workflow-theme'); }} catch (e) {{}}
    if (theme !== 'dark' && theme !== 'light') theme = null;
    if (theme) document.documentElement.setAttribute('data-theme', theme);
    function sync() {{
      var hash = window.location.hash || '';
      var next = base + (theme ? '?theme=' + theme : '') + hash;
      if (frame.getAttribute('src') !== next) frame.setAttribute('src', next);
    }}
    sync();
    window.addEventListener('hashchange', sync);

    // Телефон: тема и экспорт живут в шапке, панель просмотрщика там скрыта.
    var KEY = 'smit-workflow-theme';
    var themeBtn = document.getElementById('m-theme');
    if (themeBtn) themeBtn.addEventListener('click', function () {{
      var systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var current = theme || (systemDark ? 'dark' : 'light');
      theme = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', theme);
      try {{ localStorage.setItem(KEY, theme); }} catch (e) {{}}
      sync();
    }});

    var exportBtn = document.getElementById('m-export');
    if (exportBtn) exportBtn.addEventListener('click', function () {{
      try {{
        var doc = frame.contentDocument;
        var inner = doc && doc.getElementById('btn-export');
        if (inner) inner.click();
      }} catch (e) {{ /* схема ещё грузится */ }}
    }});
  }})();
</script>

</body>
</html>
"""


def main():
    if not os.path.isdir(VIEWER_DIR):
        os.makedirs(VIEWER_DIR)
    for file_name, title, kind in PAGES:
        base = file_name[:-5]  # имя без .html — так же названы обложки
        page = TEMPLATE.format(title=title, kind=kind, file=file_name, graph=GRAPH_URL,
                               site=SITE_URL, covers=COVERS_URL, base=base,
                               description=DESCRIPTIONS.get(file_name, title))
        path = os.path.join(ROOT, file_name)
        with io.open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(page)
        print('%-46s страница собрана' % file_name)


if __name__ == '__main__':
    main()
