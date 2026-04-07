"""Replace sidebar in all docs HTML files with comprehensive 3-level menu."""
import re, glob

NEW_SIDEBAR = '''<aside class="sidebar">
  <nav>
    <div class="nav-section">Разделы</div>
    <ul>
      <li><a href="index.html">&#127968; Главная</a></li>
      <li class="has-children">
        <a href="pages/installation.html">&#128268; Установка и интеграция <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/installation.html#requirements">1. Системные требования</a></li>
          <li><a href="pages/installation.html#docker-install">2. Установка Docker Compose</a></li>
          <li><a href="pages/installation.html#demo-cleanup">3. Удаление демо-данных</a></li>
          <li><a href="pages/installation.html#equip-integration">4. Интеграция с оборудованием</a></li>
          <li><a href="pages/installation.html#tariff-setup">5. Настройка тарифов</a></li>
          <li><a href="pages/installation.html#add-subscribers">6. Добавление абонентов</a></li>
          <li><a href="pages/installation.html#final-test">7. Финальное тестирование</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="pages/billing.html">&#9881; Настройки биллинга <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/billing.html#general">1. Общие настройки</a></li>
          <li class="sub-item"><a href="pages/billing.html#admin-ip">1.1. IP администратора</a></li>
          <li class="sub-item"><a href="pages/billing.html#global-settings">1.2. Глобальные настройки</a></li>
          <li class="sub-item"><a href="pages/billing.html#user-interfaces">1.4. Интерфейсы</a></li>
          <li class="sub-item"><a href="pages/billing.html#access-control">1.6. Права доступа</a></li>
          <li><a href="pages/billing.html#subscribers">2. Работа с абонентами</a></li>
          <li class="sub-item"><a href="pages/billing.html#create-subscriber">2.1. Создание абонента</a></li>
          <li class="sub-item"><a href="pages/billing.html#search">2.2. Поиск</a></li>
          <li class="sub-item"><a href="pages/billing.html#finance-operations">2.3. Финансовые операции</a></li>
          <li class="sub-item"><a href="pages/billing.html#block-unblock">2.4. Блокировка</a></li>
          <li class="sub-item"><a href="pages/billing.html#accounts">2.5. Лицевые счета</a></li>
          <li class="sub-item"><a href="pages/billing.html#debtors">2.6. Должники</a></li>
          <li class="sub-item"><a href="pages/billing.html#send-message">2.7. Отправка сообщений</a></li>
          <li><a href="pages/billing.html#tariffs">3. Тарификация и услуги</a></li>
          <li class="sub-item"><a href="pages/billing.html#tarif-create">3.1. Тарифы</a></li>
          <li class="sub-item"><a href="pages/billing.html#services">3.6. Услуги</a></li>
          <li class="sub-item"><a href="pages/billing.html#bonus-system">3.16. Бонусы</a></li>
          <li><a href="pages/billing.html#messaging">4. Отправка сообщений</a></li>
          <li class="sub-item"><a href="pages/billing.html#telegram">4.4. Telegram</a></li>
          <li class="sub-item"><a href="pages/billing.html#smsaero">4.5. SMSAero</a></li>
          <li class="sub-item"><a href="pages/billing.html#email-smtp">4.6. Email (SMTP)</a></li>
          <li><a href="pages/billing.html#payments">5. Платежи, API, 1С</a></li>
          <li class="sub-item"><a href="pages/billing.html#payment-systems">5.2. Платёжные системы</a></li>
          <li class="sub-item"><a href="pages/billing.html#yookassa-settings">5.8. ЮKassa</a></li>
          <li class="sub-item"><a href="pages/billing.html#online-cash">5.7. Онлайн-кассы (54-ФЗ)</a></li>
          <li><a href="pages/billing.html#cabinet">6. Личный кабинет</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-auth">6.1. Авторизация</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-settings">6.2. Настройки интеграций</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-telegram">6.3. Telegram-бот уведомлений</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-payments">6.4. Оплата (ЮKassa)</a></li>
          <li class="sub-item"><a href="pages/billing.html#telegram-admin-bot">6.5. Telegram-бот оператора</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-mobile-app">6.6. Мобильное приложение</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-support">6.7. Поддержка (FreeScout)</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-ai-chat">6.8. AI-ассистент</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-profile">6.9. Профиль абонента</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-firebase">6.10. Push-уведомления</a></li>
          <li class="sub-item"><a href="pages/billing.html#lk-deploy">6.11. Развёртывание и SSL</a></li>
          <li><a href="pages/billing.html#oss-bss">7. OSS.BSS / NAS</a></li>
          <li class="sub-item"><a href="pages/billing.html#rtsh">7.1. rtsh — команды</a></li>
          <li class="sub-item"><a href="pages/billing.html#nas-deploy">7.3. NAS развёртывание</a></li>
          <li class="sub-item"><a href="pages/billing.html#helpdesk">7.7. CRM / HelpDesk</a></li>
          <li class="sub-item"><a href="pages/billing.html#shell-exec">7.9. Shell-команды</a></li>
          <li class="sub-item"><a href="pages/billing.html#nas-management-api">7.10. NAS API</a></li>
          <li><a href="pages/billing.html#freeradius">8. FreeRADIUS</a></li>
          <li class="sub-item"><a href="pages/billing.html#radius-arch">8.1. Архитектура</a></li>
          <li class="sub-item"><a href="pages/billing.html#radius-auth">8.2. Авторизация</a></li>
          <li class="sub-item"><a href="pages/billing.html#radius-clients">8.4. Клиенты (NAS)</a></li>
          <li class="sub-item"><a href="pages/billing.html#radius-test">8.5. Тестирование</a></li>
          <li><a href="pages/billing.html#backup-system">9. Резервное копирование</a></li>
          <li class="sub-item"><a href="pages/billing.html#backup-config">9.1. Настройка</a></li>
          <li class="sub-item"><a href="pages/billing.html#backup-types">9.2. Типы бекапов</a></li>
          <li class="sub-item"><a href="pages/billing.html#backup-restore">9.3. Восстановление</a></li>
          <li><a href="pages/billing.html#reports">10. Отчёты</a></li>
          <li class="sub-item"><a href="pages/billing.html#audit">10.1. Аудит</a></li>
          <li class="sub-item"><a href="pages/billing.html#payment-log">10.2. Журнал платежей</a></li>
          <li class="sub-item"><a href="pages/billing.html#report-constructor">10.3. Конструктор отчётов</a></li>
          <li class="sub-item"><a href="pages/billing.html#director-report">10.4. Панель директора</a></li>
          <li class="sub-item"><a href="pages/billing.html#dev-reports">10.6. Разработка и логи</a></li>
          <li class="sub-item"><a href="pages/billing.html#monthly-billing">10.8. Месячное списание</a></li>
          <li><a href="pages/billing.html#dictionaries">11. Справочники</a></li>
          <li class="sub-item"><a href="pages/billing.html#ip-pools">11.5. Пулы IP-адресов</a></li>
          <li class="sub-item"><a href="pages/billing.html#houses">11.7. Дома</a></li>
          <li><a href="pages/billing.html#additional">12. Дополнительные настройки</a></li>
          <li class="sub-item"><a href="pages/billing.html#sorm-access">12.4. СОРМ</a></li>
          <li class="sub-item"><a href="pages/billing.html#print-templates">12.5. Шаблоны печати</a></li>
          <li><a href="pages/billing.html#security">13. Безопасность</a></li>
          <li><a href="pages/billing.html#versioning">14. Версионность</a></li>
          <li><a href="pages/billing.html#tech-stack">15. Технологический стек</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="pages/server.html">&#128421; Управление сервером <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/server.html#server-setup">1. Настройка сервера</a></li>
          <li><a href="pages/server.html#maintenance">2. Сервисное обслуживание</a></li>
          <li class="sub-item"><a href="pages/server.html#backup">2.1. Резервное копирование</a></li>
          <li class="sub-item"><a href="pages/server.html#backup-ui">2.2. Бекапы (веб-интерфейс)</a></li>
          <li><a href="pages/server.html#modules">3. Управление модулями</a></li>
          <li><a href="pages/server.html#remote">4. Удалённое управление</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="pages/equipment.html">&#128225; Интеграция с оборудованием <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/equipment.html#internet">1. Интернет (NAS/BRAS)</a></li>
          <li class="sub-item"><a href="pages/equipment.html#switch-types">1.1. Типы коммутаторов</a></li>
          <li><a href="pages/equipment.html#voip">2. Телефония (VoIP)</a></li>
          <li><a href="pages/equipment.html#iptv">3. IPTV</a></li>
          <li class="sub-item"><a href="pages/equipment.html#iptv-tvip">3.1. TVIP Media</a></li>
          <li class="sub-item"><a href="pages/equipment.html#iptv-lfstream">3.2. LFStream</a></li>
          <li class="sub-item"><a href="pages/equipment.html#iptv-mappings">3.3. Маппинг пакетов</a></li>
          <li><a href="pages/equipment.html#cpe">4. Абонентское оборудование</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="pages/sorm.html">&#128274; Интеграция с СОРМ3 <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/sorm.html#principle">1. Принцип работы</a></li>
          <li><a href="pages/sorm.html#integrated">2. Интегрированные решения</a></li>
          <li><a href="pages/sorm.html#children">3. Схемы настройки</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="pages/api.html">&#128279; API <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/api.html#overview">1. Обзор API</a></li>
          <li><a href="pages/api.html#auth">2. Аутентификация</a></li>
          <li><a href="pages/api.html#rest-v2">3. REST API v2</a></li>
          <li><a href="pages/api.html#promise-pay">4. Обещанный платёж</a></li>
          <li><a href="pages/api.html#soap">5. SOAP API</a></li>
          <li><a href="pages/api.html#mobile-api">7. Mobile API</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="pages/troubleshooting.html">&#128295; Решение проблем <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/troubleshooting.html#general">1. Общие вопросы</a></li>
          <li><a href="pages/troubleshooting.html#auth">2. Абоненты и авторизация</a></li>
          <li><a href="pages/troubleshooting.html#billing-payments">3. Биллинг и платежи</a></li>
          <li><a href="pages/troubleshooting.html#server-perf">4. Сервер и производительность</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="pages/licensing.html">&#128196; Лицензирование <span class="arrow">&#9654;</span></a>
        <ul class="submenu">
          <li><a href="pages/licensing.html#delivery">1. Порядок поставки ПО</a></li>
          <li><a href="pages/licensing.html#payment-issues">2. Не проходит оплата</a></li>
        </ul>
      </li>
      <li><a href="pages/contacts.html">&#128222; Контакты</a></li>
    </ul>
  </nav>
</aside>'''

files = ['index.html'] + glob.glob('pages/*.html')
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()

    # For index.html: links use "pages/billing.html"
    # For pages/*.html: links use "billing.html" (same dir) and "../index.html" for home
    sidebar = NEW_SIDEBAR
    is_subpage = f.startswith('pages')
    if is_subpage:
        sidebar = sidebar.replace('href="pages/', 'href="')
        sidebar = sidebar.replace('href="index.html"', 'href="../index.html"')
        sidebar = sidebar.replace('src="../img/', 'src="../img/')  # keep as-is

    new_content = re.sub(
        r'<aside class="sidebar">.*?</aside>',
        sidebar,
        content,
        flags=re.DOTALL
    )
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        print(f'Updated: {f}')
    else:
        print(f'No change: {f}')
