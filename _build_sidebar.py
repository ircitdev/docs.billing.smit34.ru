"""Update sidebar block in all docs/pages/*.html — single source of truth.

Replaces existing <aside class="sidebar">...</aside> block with the new structure
that includes "ЛК и мобильные" as a separate top-level menu item
right after "Настройки биллинга".

Usage: python _build_sidebar.py
"""
import os
import re

SIDEBAR_BLOCK = '''<aside class="sidebar">
  <nav>
    <div class="nav-section">Разделы</div>
    <ul>
      <li><a href="../index.html"><i class="ti ti-home"></i> Главная</a></li>
      <li class="has-children">
        <a href="installation.html"><i class="ti ti-box"></i> Установка и интеграция <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="installation.html#requirements">1. Системные требования</a></li>
          <li><a href="installation.html#docker-install">2. Установка Docker Compose</a></li>
          <li><a href="installation.html#demo-cleanup">3. Удаление демо-данных</a></li>
          <li><a href="installation.html#equip-integration">4. Интеграция с оборудованием</a></li>
          <li><a href="installation.html#tariff-setup">5. Настройка тарифов</a></li>
          <li><a href="installation.html#add-subscribers">6. Добавление абонентов</a></li>
          <li><a href="installation.html#final-test">7. Финальное тестирование</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="billing.html"><i class="ti ti-settings"></i> Настройки биллинга <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="billing.html#general">1. Общие настройки</a></li>
          <li class="sub-item"><a href="billing.html#admin-ip">1.1. IP администратора</a></li>
          <li class="sub-item"><a href="billing.html#system-settings">1.2. Настройки системы</a></li>
          <li class="sub-item"><a href="billing.html#user-interfaces">1.4. Интерфейсы</a></li>
          <li class="sub-item"><a href="billing.html#access-control">1.7. Права доступа</a></li>
          <li><a href="billing.html#subscribers">2. Работа с абонентами</a></li>
          <li class="sub-item"><a href="billing.html#create-subscriber">2.1. Создание абонента</a></li>
          <li class="sub-item"><a href="billing.html#search">2.6. Поиск</a></li>
          <li class="sub-item"><a href="billing.html#finance-operations">2.7. Финансовые операции</a></li>
          <li class="sub-item"><a href="billing.html#block-unblock">2.13. Блокировка</a></li>
          <li class="sub-item"><a href="billing.html#accounts">2.14. Лицевые счета</a></li>
          <li class="sub-item"><a href="billing.html#debtors">2.15. Должники</a></li>
          <li><a href="billing.html#tariffs">3. Тарификация и услуги</a></li>
          <li class="sub-item"><a href="billing.html#tarif-create">3.1. Тарифы</a></li>
          <li class="sub-item"><a href="billing.html#services">3.6. Услуги</a></li>
          <li class="sub-item"><a href="billing.html#loyalty">3.16. Лояльность</a></li>
          <li><a href="billing.html#messaging">4. Отправка сообщений</a></li>
          <li class="sub-item"><a href="billing.html#email-smtp">4.2. Email (SMTP)</a></li>
          <li class="sub-item"><a href="billing.html#smsaero">4.3. SMS</a></li>
          <li class="sub-item"><a href="billing.html#telegram-messaging">4.5. Telegram</a></li>
          <li class="sub-item"><a href="billing.html#vk-messaging">4.6. VK</a></li>
          <li><a href="billing.html#payments">5. Платежи, API, 1С</a></li>
          <li class="sub-item"><a href="billing.html#payment-systems">5.2. Платёжные системы</a></li>
          <li class="sub-item"><a href="billing.html#yookassa-settings">5.10. ЮKassa</a></li>
          <li><a href="billing.html#oss-bss">6. OSS.BSS / NAS</a></li>
          <li class="sub-item"><a href="billing.html#nas-management-api">6.10. NAS API</a></li>
          <li><a href="billing.html#freeradius">7. FreeRADIUS</a></li>
          <li><a href="billing.html#backup-system">8. Резервное копирование</a></li>
          <li><a href="billing.html#reports">9. Отчёты</a></li>
          <li class="sub-item"><a href="billing.html#audit">9.1. Аудит</a></li>
          <li class="sub-item"><a href="billing.html#payment-log">9.2. Журнал платежей</a></li>
          <li class="sub-item"><a href="billing.html#dev-reports">9.6. Разработка и логи</a></li>
          <li><a href="billing.html#dictionaries">10. Справочники</a></li>
          <li><a href="billing.html#additional">11. Дополнительные настройки</a></li>
          <li><a href="billing.html#modal-dialogs">12. Модальные окна</a></li>
          <li><a href="billing.html#security">13. Обзор безопасности</a></li>
          <li><a href="billing.html#tech-stack">17. Технологический стек</a></li>
          <li><a href="billing.html#design-system">20. Дизайн-система</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="lk.html"><i class="ti ti-mobile"></i> ЛК и мобильные <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="lk.html#lk-overview">Обзор и возможности</a></li>
          <li><a href="lk.html#lk-admin-settings">Раздел «ЛК и мобильные» в админке</a></li>
          <li class="sub-item"><a href="lk.html#lk-admin-branding">— Брендинг</a></li>
          <li class="sub-item"><a href="lk.html#lk-admin-features">— Функции (12 toggle)</a></li>
          <li class="sub-item"><a href="lk.html#lk-admin-security">— Безопасность</a></li>
          <li class="sub-item"><a href="lk.html#lk-admin-mobile">— Мобильное (Android+iOS)</a></li>
          <li><a href="lk.html#lk-auth">Авторизация</a></li>
          <li><a href="lk.html#lk-settings">Настройки интеграций</a></li>
          <li><a href="lk.html#lk-telegram">Telegram-бот</a></li>
          <li><a href="lk.html#lk-payments">Оплата (ЮKassa)</a></li>
          <li><a href="lk.html#lk-mobile-app">Мобильное приложение</a></li>
          <li class="sub-item"><a href="lk.html#mobile-api-public">— Public Mobile API</a></li>
          <li class="sub-item"><a href="lk.html#mobile-force-update">— Force-update</a></li>
          <li class="sub-item"><a href="lk.html#mobile-ios-distribution">— iOS TestFlight ↔ AppStore</a></li>
          <li><a href="lk.html#lk-support">FreeScout</a></li>
          <li><a href="lk.html#lk-ai-chat">AI-ассистент</a></li>
          <li><a href="lk.html#lk-profile">Профиль</a></li>
          <li><a href="lk.html#lk-firebase">Push (Firebase)</a></li>
          <li><a href="lk.html#lk-claude-ai">Claude AI</a></li>
          <li><a href="lk.html#telegram-admin-bot">TG бот оператора</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="server.html"><i class="ti ti-server"></i> Управление сервером <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="server.html#server-setup">1. Настройка сервера</a></li>
          <li><a href="server.html#maintenance">2. Сервисное обслуживание</a></li>
          <li class="sub-item"><a href="server.html#backup">2.1. Резервное копирование</a></li>
          <li class="sub-item"><a href="server.html#backup-ui">2.2. Бекапы (веб-интерфейс)</a></li>
          <li><a href="server.html#modules">3. Управление модулями</a></li>
          <li><a href="server.html#remote">4. Удалённое управление</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="equipment.html"><i class="ti ti-broadcast"></i> Интеграция с оборудованием <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="equipment.html#internet">1. Интернет (NAS/BRAS)</a></li>
          <li class="sub-item"><a href="equipment.html#switch-types">1.1. Типы коммутаторов</a></li>
          <li><a href="equipment.html#voip">2. Телефония (VoIP)</a></li>
          <li><a href="equipment.html#iptv">3. IPTV</a></li>
          <li class="sub-item"><a href="equipment.html#iptv-tvip">3.1. TVIP Media</a></li>
          <li class="sub-item"><a href="equipment.html#iptv-lfstream">3.2. LFStream</a></li>
          <li class="sub-item"><a href="equipment.html#iptv-mappings">3.3. Маппинг пакетов</a></li>
          <li><a href="equipment.html#cpe">4. Абонентское оборудование</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="sorm.html"><i class="ti ti-shield-lock"></i> Интеграция с СОРМ3 <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="sorm.html#principle">Принцип работы</a></li>
          <li><a href="sorm.html#integrated">Интегрированные решения</a></li>
          <li><a href="sorm.html#pending">Ожидающие интеграции</a></li>
          <li><a href="sorm.html#setup">Настройка подключения</a></li>
          <li class="sub-item"><a href="sorm.html#sorm-add-modal">— Модальное окно «Добавить»</a></li>
          <li><a href="sorm.html#reports">Отчёты и SQL</a></li>
          <li><a href="sorm.html#schedule">Расписание выгрузки</a></li>
          <li><a href="sorm.html#sorm-admin">Админ-UI: список и FTP</a></li>
          <li class="sub-item"><a href="sorm.html#sorm-list">— Список конфигураций</a></li>
          <li class="sub-item"><a href="sorm.html#sorm-readiness">— Проверка готовности</a></li>
          <li class="sub-item"><a href="sorm.html#sorm-ftp">— FTP-сервер РКН</a></li>
          <li class="sub-item"><a href="sorm.html#sorm-telegram">— Telegram-уведомления</a></li>
          <li class="sub-item"><a href="sorm.html#sorm-history">— История выгрузок</a></li>
          <li class="sub-item"><a href="sorm.html#sorm-schedule">— Авторасписание</a></li>
          <li><a href="sorm.html#manual-run">Управление отчётами</a></li>
          <li><a href="sorm.html#metadata">СОРМ-метаданные</a></li>
          <li><a href="sorm.html#preflight">Pre-flight валидация</a></li>
          <li><a href="sorm.html#dedup">Дубликаты атрибутов</a></li>
          <li><a href="sorm.html#api">REST API готовности</a></li>
          <li><a href="sorm.html#children">Схемы настройки</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="api.html"><i class="ti ti-link"></i> API <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="api.html#overview">1. Обзор API</a></li>
          <li><a href="api.html#auth">2. Аутентификация</a></li>
          <li><a href="api.html#rest-v2">3. REST API v2</a></li>
          <li><a href="api.html#promise-pay">4. Обещанный платёж</a></li>
          <li><a href="api.html#payments-api">5. Платёжные API (ЮKassa, W1)</a></li>
          <li class="sub-item"><a href="api.html#payments-endpoints">5.0. Список endpoint</a></li>
          <li class="sub-item"><a href="api.html#payments-flow">5.1. Схема платежа</a></li>
          <li class="sub-item"><a href="api.html#yookassa-rest">5.2. ЮKassa REST v3</a></li>
          <li class="sub-item"><a href="api.html#yookassa-http">5.3. ЮKassa HTTP</a></li>
          <li class="sub-item"><a href="api.html#w1-api">5.4. Wallet One</a></li>
          <li class="sub-item"><a href="api.html#payments-settings">5.5. Настройки</a></li>
          <li><a href="api.html#soap">6. SOAP API</a></li>
          <li><a href="api.html#mobile-api">7. Mobile API</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="troubleshooting.html"><i class="ti ti-tool"></i> Решение проблем <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="troubleshooting.html#general">1. Общие вопросы</a></li>
          <li><a href="troubleshooting.html#auth">2. Абоненты и авторизация</a></li>
          <li><a href="troubleshooting.html#billing-payments">3. Биллинг и платежи</a></li>
          <li><a href="troubleshooting.html#server-perf">4. Сервер и производительность</a></li>
        </ul>
      </li>
      <li class="has-children">
        <a href="licensing.html"><i class="ti ti-file-description"></i> Лицензирование <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
        <ul class="submenu">
          <li><a href="licensing.html#delivery">1. Порядок поставки ПО</a></li>
          <li><a href="licensing.html#payment-issues">2. Не проходит оплата</a></li>
        </ul>
      </li>
      <li><a href="contacts.html"><i class="ti ti-phone"></i> Контакты</a></li>
    </ul>

      <div class="nav-section">Разработчикам</div>
      <ul>
        <li class="has-children">
          <a href="../graphify/graph.html"><i class="ti ti-topology-star-3"></i> Архитектура кода <span class="arrow"><i class="bi bi-chevron-right"></i></span></a>
          <ul class="submenu">
            <li><a href="../graphify/graph.html">Граф сообществ</a></li>
            <li><a href="../graphify/wiki/index.html">Wiki модулей</a></li>
            <li><a href="dev/index.html">Портал разработчика</a></li>
            <li><a href="../graphify/help.html">graphify CLI</a></li>
          </ul>
        </li>
      </ul>
  <button class="sidebar-theme-toggle" aria-label="Тема"><span class="icon-sun"><i class="ti ti-sun"></i></span><span class="icon-moon"><i class="ti ti-moon"></i></span><span class="sidebar-theme-label">Сменить тему</span></button>
</nav>
</aside>'''


def main():
    pages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages')
    files = sorted(f for f in os.listdir(pages_dir) if f.endswith('.html'))
    print(f'Found {len(files)} html files in {pages_dir}')
    for fname in files:
        fpath = os.path.join(pages_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        new_text, count = re.subn(
            r'<aside class="sidebar">.*?</aside>',
            SIDEBAR_BLOCK,
            text,
            count=1,
            flags=re.DOTALL,
        )
        if count == 0:
            print(f'  SKIP {fname}: sidebar not found')
            continue
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print(f'  OK   {fname}')
    print('done')


if __name__ == '__main__':
    main()
