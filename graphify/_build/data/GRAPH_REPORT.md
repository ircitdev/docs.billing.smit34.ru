# Graph Report - billing/  (2026-05-06)

## Corpus Check
- 172 files · ~129,181 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2524 nodes · 9003 edges · 34 communities detected
- Extraction: 38% EXTRACTED · 62% INFERRED · 0% AMBIGUOUS · INFERRED: 5567 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Карточка абонента|Карточка абонента]]
- [[_COMMUNITY_Личный кабинет|Личный кабинет]]
- [[_COMMUNITY_Финансы и деньги|Финансы и деньги]]
- [[_COMMUNITY_Поиск абонентов|Поиск абонентов]]
- [[_COMMUNITY_Мобильный API|Мобильный API]]
- [[_COMMUNITY_Авторизация|Авторизация]]
- [[_COMMUNITY_ACL и соцсети|ACL и соцсети]]
- [[_COMMUNITY_Блокировки|Блокировки]]
- [[_COMMUNITY_Резервные копии|Резервные копии]]
- [[_COMMUNITY_IPTV|IPTV]]
- [[_COMMUNITY_Фреймворк форм|Фреймворк форм]]
- [[_COMMUNITY_Задачи биллинга|Задачи биллинга]]
- [[_COMMUNITY_Шаблоны ЛК|Шаблоны ЛК]]
- [[_COMMUNITY_Интерфейс|Интерфейс]]
- [[_COMMUNITY_Отчёты СОРМ|Отчёты СОРМ]]
- [[_COMMUNITY_Платёжные системы|Платёжные системы]]
- [[_COMMUNITY_Сообщения|Сообщения]]
- [[_COMMUNITY_Мобильная авторизация|Мобильная авторизация]]
- [[_COMMUNITY_Push-уведомления|Push-уведомления]]
- [[_COMMUNITY_Модель аккаунта|Модель аккаунта]]
- [[_COMMUNITY_FreeScout Webhooks|FreeScout Webhooks]]
- [[_COMMUNITY_Авторизация ЛК|Авторизация ЛК]]
- [[_COMMUNITY_Фильтры шаблонов|Фильтры шаблонов]]
- [[_COMMUNITY_Пакет мобильного API|Пакет мобильного API]]
- [[_COMMUNITY_Конфигурация|Конфигурация]]
- [[_COMMUNITY_Адреса|Адреса]]
- [[_COMMUNITY_URL мобильного API|URL мобильного API]]
- [[_COMMUNITY_Миграции БД|Миграции БД]]
- [[_COMMUNITY_Учёт баланса|Учёт баланса]]
- [[_COMMUNITY_Текущий баланс|Текущий баланс]]
- [[_COMMUNITY_Баланс месяца|Баланс месяца]]
- [[_COMMUNITY_Приоритет шаблонов|Приоритет шаблонов]]
- [[_COMMUNITY_Исправление SQL|Исправление SQL]]
- [[_COMMUNITY_Аватары|Аватары]]

## God Nodes (most connected - your core abstractions)
1. `BaseView` - 197 edges
2. `PaginatorFormMixin` - 166 edges
3. `SearchFormMixin` - 160 edges
4. `MsgStack` - 159 edges
5. `Homes` - 149 edges
6. `Универсальный контекст для печатных форм.` - 140 edges
7. `FreeScoutClient` - 138 edges
8. `StatusViewMixin` - 134 edges
9. `FinanceOperations` - 130 edges
10. `AdminAccounts` - 127 edges

## Surprising Connections (you probably didn't know these)
- `Convert 2026-04-15 → '15 апреля 2026'.` --uses--> `AuditOperations`  [INFERRED]
  D:\DevTools\Database\2026Carbon\carbon_modern\billing\views\audit_api.py → D:\DevTools\Database\2026Carbon\carbon_modern\billing\models\stubs.py
- `Simplify verbose audit descriptions — strip redundant info already in table colu` --uses--> `AuditOperations`  [INFERRED]
  D:\DevTools\Database\2026Carbon\carbon_modern\billing\views\audit_api.py → D:\DevTools\Database\2026Carbon\carbon_modern\billing\models\stubs.py
- `Return {pk: {'name': 'Фамилия И.О.', 'contract': '...'}} for a set of abonent ID` --uses--> `AuditOperations`  [INFERRED]
  D:\DevTools\Database\2026Carbon\carbon_modern\billing\views\audit_api.py → D:\DevTools\Database\2026Carbon\carbon_modern\billing\models\stubs.py
- `Return brief abonent info for tooltip on hover.` --uses--> `AuditOperations`  [INFERRED]
  D:\DevTools\Database\2026Carbon\carbon_modern\billing\views\audit_api.py → D:\DevTools\Database\2026Carbon\carbon_modern\billing\models\stubs.py
- `Пример из документации Django     Return all rows from a cursor as a dict` --uses--> `BaseView`  [INFERRED]
  D:\DevTools\Database\2026Carbon\carbon_modern\billing\views\dashboard_reports.py → D:\DevTools\Database\2026Carbon\carbon_modern\billing\views\form.py

## Communities

### Community 0 - "Карточка абонента"
Cohesion: 0.01
Nodes (211): abonent_map_data(), abonent_map_view(), Return (map_provider, map_2gis_key, yandex_api_key) respecting user preference., Страница карты абонентов., JSON API: координаты абонентов и оборудования для карты., _resolve_map_provider(), abonent_egrul_sync(), abonent_quick_add() (+203 more)

### Community 1 - "Личный кабинет"
Cohesion: 0.01
Nodes (230): change_password(), Connection sessions (RADIUS) — stub., Change connection password (Users.psw)., sessions_view(), voluntary_block(), ippull_get_and_reserve_ip(), AJAX-обработчики — Python 3 / Django 4.2 Замена: admin/view/ajax_processors.py, AJAX запрос на выделение ip.      После выделения он вставляется в форму и тольк (+222 more)

### Community 2 - "Финансы и деньги"
Cohesion: 0.01
Nodes (168): MoneyField, Model field for money stored as ×10^10 in DB, shown as rubles in forms., atol_config_api(), atol_config_view(), Fiscal settings (AtolConfig) — dedicated view with AJAX API., Meta, number_is_free(), Журнал финансовых операций (платежи, списания, сторнирования, ФР-чеки).     db_t (+160 more)

### Community 3 - "Поиск абонентов"
Cohesion: 0.09
Nodes (194): AbonentExtendedSearchExportView, _AbonentResultWrapper, AbonentsCommentsView, AbonentSearchExportView, AbonentSlaveAdd, AbonentsMainSearchView, AbonentsSearchView, AbonentWizard (+186 more)

### Community 4 - "Мобильный API"
Cohesion: 0.03
Nodes (141): account_status(), change_password(), Mobile API account actions — change password, voluntary block., POST /mobile-api/v1/account/update_contacts — set email/sms if currently empty., GET /mobile-api/v1/account/telegram_link — get one-time token + deep link., POST /mobile-api/v1/account/change_password — change user password., GET  — current block status + can_block flag.     POST — action=block or action=, update_contacts() (+133 more)

### Community 5 - "Авторизация"
Cohesion: 0.04
Nodes (91): Abonents, Основная таблица абонентов (дерево через parent/lft/rght/tree_id/level — MPTT-со, api_logout(), auth(), AuthView, diagnostic(), do_logout(), intro() (+83 more)

### Community 6 - "ACL и соцсети"
Cohesion: 0.03
Nodes (83): AclAdd, AclSocial, AclView, fill_social(), ACL (Access Control List) — Python 3 / Django 4.2 Замена: admin/view/acl.py, View-функция: запускает обновление ресурсов социального интернета., Представление для добавления ACL-записей., Строит контекст с указанием вкладки sub_select. (+75 more)

### Community 7 - "Блокировки"
Cohesion: 0.03
Nodes (105): Блокировка абонента. Упрощённая версия — создаёт записи в AbonentsBlock., telegram_link(), BaseCommand, FirewallService, get_allowed_ips(), get_blocked_ips(), get_trusted_ips(), push_address_list_to_mikrotik() (+97 more)

### Community 8 - "Резервные копии"
Cohesion: 0.03
Nodes (91): backup_create_config(), backup_delete_config(), backup_delete_record(), backup_download(), backup_list(), backup_update_config(), _ctx(), Stream backup file as download. (+83 more)

### Community 9 - "IPTV"
Cohesion: 0.04
Nodes (62): IptvClient, Абстрактный клиент для IPTV-провайдеров., Разблокировать аккаунт. Возвращает bool., Подписать на пакет. Возвращает bool., Отписать от пакета. Возвращает bool., Базовый класс API-клиента IPTV-провайдера.      Подклассы реализуют конкретные м, Получить список доступных пакетов. Возвращает list[dict]., Получить данные аккаунта. Возвращает dict. (+54 more)

### Community 10 - "Фреймворк форм"
Cohesion: 0.04
Nodes (24): Form, create_select2_object(), form_save(), formset_save(), get_virtualbook(), need_search(), prePrintObject(), process_item_get() (+16 more)

### Community 11 - "Задачи биллинга"
Cohesion: 0.03
Nodes (63): _block_negative_balance(), process_blocks(), _process_own_disabled(), billing/tasks/abonent_block.py — Блокировка/разблокировка абонентов.  Замена: da, Обработка добровольной блокировки — снятие по истечении срока., Основной цикл обработки блокировок.      1. Блокировка абонентов с отрицательным, Блокировка абонентов с отрицательным балансом., Разблокировка абонентов с восстановленным балансом. (+55 more)

### Community 12 - "Шаблоны ЛК"
Cohesion: 0.05
Nodes (61): LK Base Layout Template, LK Dark Theme Toggle, POST /lk/notifications/dismiss/{id}/, LK Navbar Component, LK Sidebar Navigation, LK Notifications Banner, LK AI Chat Screen, Chat Escalated-to-Operator Banner (+53 more)

### Community 13 - "Интерфейс"
Cohesion: 0.05
Nodes (40): FrameworkFormGroupFields, FrameworkFormGroups, Interface, Meta, billing/models/framework.py — модели фреймворка интерфейса Оригинал: admin/model, Группы полей (вкладки) для форм., _build_field_labels(), _filter_menu_for_interface() (+32 more)

### Community 14 - "Отчёты СОРМ"
Cohesion: 0.08
Nodes (52): add_report_view(), _base_context(), create_attrs_view(), export_sorm_report(), _generate_filename(), SORM export tasks — execute SQL, write CSV, upload via FTP., Core export logic (sync). Returns dict:     {'ok': bool, 'filename': str, 'rows', Celery task: export single SORM report to FTP. (+44 more)

### Community 15 - "Платёжные системы"
Cohesion: 0.07
Nodes (46): calculate_commission(), create_payment(), _create_w1_payment(), _create_yookassa_http_form(), _create_yookassa_payment(), _create_yookassa_rest(), _credit_abonent(), get_active_system() (+38 more)

### Community 16 - "Сообщения"
Cohesion: 0.11
Nodes (31): _create_felicitation_message(), _dispatch_message(), _get_felicitation_abonents(), _increment_count_try(), process_message_queue(), billing/tasks/messaging.py — Отправка сообщений.  Обрабатывает очередь MsgStack:, Увеличивает счётчик попыток. После MAX_TRIES помечает sent_at чтобы не зациклива, Отправка email через Django mail backend. (+23 more)

### Community 17 - "Мобильная авторизация"
Cohesion: 0.18
Nodes (14): AnonRateThrottle, authenticate_subscriber(), _find_billing_user(), login_view(), Mobile API authentication views., Authenticate subscriber by Users.login + Users.psw (plaintext)., Find billing Users by contract_number or login (with/without leading zero)., Verify Telegram Login Widget data using bot token. (+6 more)

### Community 18 - "Push-уведомления"
Cohesion: 0.17
Nodes (15): _get_firebase_app(), Push notifications — send FCM messages to abonents via Firebase Admin SDK., Alert abonents whose promise pay expires tomorrow., Alert abonents whose promise pay expired today., Lazy-init Firebase Admin SDK., Send a single FCM message., Send push notification to a single abonent., Send push to abonents with balance below threshold (in rubles). (+7 more)

### Community 19 - "Модель аккаунта"
Cohesion: 0.17
Nodes (9): credit_adjust_rub(), credit_rub(), debit_rub(), Meta, _money(), MoneyFormField, ostatok_rub(), Модель лицевых счётов — конвертирована из admin/abstract_models.py (AdminAccount (+1 more)

### Community 20 - "FreeScout Webhooks"
Cohesion: 0.27
Nodes (9): freescout_webhook(), _log_ticket_closed(), _notify_agent_assigned(), Webhook handlers for external service callbacks., Log ticket closure to abonent activity (AuditOperations)., FreeScout webhook — handles various conversation events.      Configure in FreeS, Send push notification to abonent when support replies., Notify operator via Telegram when ticket is assigned to them. (+1 more)

### Community 21 - "Авторизация ЛК"
Cohesion: 0.25
Nodes (9): POST /lk/login/ (auth endpoint), Login Form (contract/password), LK Login Screen, Login Telegram OAuth Widget, GET /lk/auth/vk/ (VK OAuth start), Login VK OAuth Button, VK OAuth Popup Window (oauth.vk.com), LK VK Auth Popup Screen (+1 more)

### Community 22 - "Фильтры шаблонов"
Cohesion: 0.29
Nodes (6): money(), money_sign(), Convert ISO datetime string (from FreeScout API) to human-readable relative time, Convert DB money (×10^10) to rubles with 2 decimal places., Convert DB money with + or - sign., timeago()

### Community 23 - "Пакет мобильного API"
Cohesion: 0.5
Nodes (1): Mobile API views package.

### Community 24 - "Конфигурация"
Cohesion: 0.67
Nodes (2): AppConfig, LkConfig

### Community 25 - "Адреса"
Cohesion: 1.0
Nodes (1): billing/models/homes.py — переэкспорт из lookups

### Community 26 - "URL мобильного API"
Cohesion: 1.0
Nodes (1): Mobile API URL routing — /mobile-api/v1/...

### Community 28 - "Миграции БД"
Cohesion: 1.0
Nodes (1): Migration

### Community 29 - "Учёт баланса"
Cohesion: 1.0
Nodes (1): Баланс бухгалтерский = остаток + дебит.

### Community 30 - "Текущий баланс"
Cohesion: 1.0
Nodes (1): Баланс текущий = остаток + дебит - кредит.

### Community 31 - "Баланс месяца"
Cohesion: 1.0
Nodes (1): Баланс на конец месяца = остаток + дебит - кредит - стоплата.

### Community 32 - "Приоритет шаблонов"
Cohesion: 1.0
Nodes (1): Get the highest-priority active template for an event.

### Community 33 - "Исправление SQL"
Cohesion: 1.0
Nodes (1): Fix quoted column references for PostgreSQL mixed-case tables.          Problem:

### Community 34 - "Аватары"
Cohesion: 1.0
Nodes (1): Get initials for default avatar.

## Knowledge Gaps
- **264 isolated node(s):** `ACL (Access Control List) — Python 3 / Django 4.2 Замена: admin/view/acl.py`, `AJAX-обработчики — Python 3 / Django 4.2 Замена: admin/view/ajax_processors.py`, `AJAX запрос на выделение ip.      После выделения он вставляется в форму и тольк`, `Запросить информацию для формы учетной записи через внешние скрипты.`, `Возвращает список портов для коммутатора.` (+259 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Пакет мобильного API`** (4 nodes): `__init__.py`, `__init__.py`, `Mobile API views package.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Конфигурация`** (3 nodes): `AppConfig`, `LkConfig`, `apps.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Адреса`** (2 nodes): `homes.py`, `billing/models/homes.py — переэкспорт из lookups`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `URL мобильного API`** (2 nodes): `urls.py`, `Mobile API URL routing — /mobile-api/v1/...`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Миграции БД`** (2 nodes): `Migration`, `0001_support_attachment.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Учёт баланса`** (1 nodes): `Баланс бухгалтерский = остаток + дебит.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Текущий баланс`** (1 nodes): `Баланс текущий = остаток + дебит - кредит.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Баланс месяца`** (1 nodes): `Баланс на конец месяца = остаток + дебит - кредит - стоплата.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Приоритет шаблонов`** (1 nodes): `Get the highest-priority active template for an event.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Исправление SQL`** (1 nodes): `Fix quoted column references for PostgreSQL mixed-case tables.          Problem:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Аватары`** (1 nodes): `Get initials for default avatar.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Универсальный контекст для печатных форм.` connect `Финансы и деньги` to `Карточка абонента`, `Личный кабинет`, `Поиск абонентов`, `Авторизация`, `ACL и соцсети`, `Резервные копии`, `IPTV`, `Задачи биллинга`, `Интерфейс`, `Отчёты СОРМ`, `Сообщения`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `BaseView` connect `Поиск абонентов` to `Карточка абонента`, `Личный кабинет`, `Финансы и деньги`, `Авторизация`, `ACL и соцсети`, `Фреймворк форм`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `Abonents` connect `Авторизация` to `Карточка абонента`, `Финансы и деньги`, `Поиск абонентов`, `ACL и соцсети`, `Блокировки`, `Задачи биллинга`, `Мобильная авторизация`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 166 inferred relationships involving `BaseView` (e.g. with `DeleteAbonentFormMixin` and `AbonentViewMixin`) actually correct?**
  _`BaseView` has 166 INFERRED edges - model-reasoned connections that need verification._
- **Are the 156 inferred relationships involving `PaginatorFormMixin` (e.g. with `DeleteAbonentFormMixin` and `AbonentViewMixin`) actually correct?**
  _`PaginatorFormMixin` has 156 INFERRED edges - model-reasoned connections that need verification._
- **Are the 147 inferred relationships involving `SearchFormMixin` (e.g. with `DeleteAbonentFormMixin` and `AbonentViewMixin`) actually correct?**
  _`SearchFormMixin` has 147 INFERRED edges - model-reasoned connections that need verification._
- **Are the 157 inferred relationships involving `MsgStack` (e.g. with `DeleteAbonentFormMixin` and `AbonentViewMixin`) actually correct?**
  _`MsgStack` has 157 INFERRED edges - model-reasoned connections that need verification._