# -*- coding: utf-8 -*-
"""Add missing id="..." to <h2>/<h3> headings + fix orphan headings.

Стратегия:
  1. Транслитерация русского заголовка в slug (lowercase ascii a-z, 0-9, -)
  2. Если slug пустой или дубль — добавить -2/-3...
  3. h4 НЕ трогаем (по решению пользователя)
  4. Орфан-заголовки (h1->h3, h2->h4) — точечные ручные правки

Запуск:
  python docs/tools/fix_docs_headers.py             # apply
  python docs/tools/fix_docs_headers.py --dry-run   # show changes
"""
import io
import re
import sys
from pathlib import Path
from collections import Counter

THIS_DIR = Path(__file__).resolve().parent
DOCS = THIS_DIR.parent / 'pages'

# Транслит ru→en (упрощённый GOST)
TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def slugify(text):
    """Russian title -> ASCII slug."""
    text = text.lower().strip()
    out = []
    for ch in text:
        if ch in TRANSLIT:
            out.append(TRANSLIT[ch])
        elif ch.isascii() and (ch.isalnum() or ch == '-'):
            out.append(ch)
        elif ch in (' ', '\t', '\n', '_', '/', '.', ',', ':', ';', '(', ')', '"', "'"):
            out.append('-')
        # else skip (punctuation etc)
    s = ''.join(out)
    # collapse multiple dashes
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    # truncate to reasonable length
    if len(s) > 60:
        s = s[:60].rstrip('-')
    return s


def strip_html(s):
    s = re.sub(r'<[^>]+>', '', s)
    return ' '.join(s.split())


HEADING_RE = re.compile(
    r'<(h[23])(\s*[^>]*)>(.*?)</\1>',
    re.DOTALL,
)
ID_RE = re.compile(r'\bid="([^"]*)"')


def process_page(path, dry_run=False):
    content = io.open(path, encoding='utf-8').read()
    new_content = content

    # 1. Сначала собираем все existing ids (любого тега) для проверки уникальности
    existing_ids = set(re.findall(r'\bid="([^"]*)"', content))

    # 2. Идём по h2/h3 от КОНЦА к НАЧАЛУ (чтобы позиции не смещались)
    matches = list(HEADING_RE.finditer(content))
    n_added = 0
    edits = []  # [(position, old_text, new_text)]

    for m in reversed(matches):
        attrs = m.group(2) or ''
        if ID_RE.search(attrs):
            continue  # already has id
        title = strip_html(m.group(3))
        if not title:
            continue
        base_slug = slugify(title)
        if not base_slug:
            continue
        slug = base_slug
        i = 2
        while slug in existing_ids:
            slug = f'{base_slug}-{i}'
            i += 1
        existing_ids.add(slug)
        # Insert id="..." into the heading tag
        old_tag = m.group(0)
        # Insert as first attribute
        new_attrs = f' id="{slug}"' + attrs
        new_tag = f'<{m.group(1)}{new_attrs}>{m.group(3)}</{m.group(1)}>'
        new_content = new_content[:m.start()] + new_tag + new_content[m.end():]
        n_added += 1

    print(f'{path.name:30s} added id: {n_added}')
    if not dry_run and n_added:
        io.open(path, 'w', encoding='utf-8', newline='\n').write(new_content)
    return n_added


def main():
    dry = '--dry-run' in sys.argv
    print(f'{"DRY RUN" if dry else "APPLY"}\n')
    total = 0
    for f in sorted(DOCS.glob('*.html')):
        total += process_page(f, dry_run=dry)
    print(f'\nTotal new ids: {total}')


if __name__ == '__main__':
    main()
