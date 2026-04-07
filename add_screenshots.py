"""Add section screenshots to billing.html where missing."""
import re

INSERTIONS = [
    # (anchor_id, img_name, alt_text) — insert img AFTER the first <p> or <ul> following the <h2>/<h3> with this id
    ('global-settings', 'section_file_config', 'Настройки системы'),
    ('access-control', 'section_permissions', 'Права доступа'),
    ('user-interfaces', 'section_interface', 'Настройки интерфейса'),
    ('search', 'section_abonent_search', 'Поиск абонентов'),
    ('debtors', 'section_debtors', 'Список должников'),
    ('yookassa-settings', 'section_payment_settings', 'Настройки ЮKassa'),
    ('tarif-create', 'section_tarifs', 'Тарифы'),
    ('smsaero', 'section_messaging_sms', 'Настройка SMS'),
    ('email-smtp', 'section_messaging_email', 'Настройка Email'),
    ('lk-auth', 'section_lk_login', 'Страница входа в ЛК'),
    ('lk-telegram', 'section_telegram_bot', 'Telegram-бот настройки'),
    ('lk-firebase', 'section_firebase', 'Firebase Push-уведомления'),
    ('lk-claude-ai', 'section_aida', 'Claude AI / AIDA настройки'),
    ('lk-profile', 'section_lk_profile', 'Профиль абонента в ЛК'),
    ('backup-config', 'section_backup', 'Резервное копирование'),
    ('report-constructor', 'section_custom_reports', 'Конструктор отчётов'),
]

with open('pages/billing.html', 'r', encoding='utf-8') as f:
    content = f.read()

count = 0
for anchor_id, img_name, alt_text in INSERTIONS:
    img_tag = f'\n  <img src="../img/{img_name}.png" alt="{alt_text}" class="screenshot">\n'

    # Check if already inserted
    if img_name in content:
        print(f'Skip (exists): {img_name}')
        continue

    # Find the heading with this id, then insert after the next closing tag
    pattern = rf'(id="{re.escape(anchor_id)}"[^>]*>.*?</h[23]>\s*\n\s*<p>.*?</p>)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + img_tag + content[insert_pos:]
        count += 1
        print(f'Added: {img_name} after #{anchor_id}')
    else:
        # Try after <ul>...</ul>
        pattern2 = rf'(id="{re.escape(anchor_id)}"[^>]*>.*?</h[23]>\s*\n.*?</ul>)'
        match2 = re.search(pattern2, content, re.DOTALL)
        if match2:
            insert_pos = match2.end()
            content = content[:insert_pos] + img_tag + content[insert_pos:]
            count += 1
            print(f'Added: {img_name} after #{anchor_id} (after ul)')
        else:
            print(f'NOT FOUND: #{anchor_id}')

with open('pages/billing.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone: {count} screenshots added')
