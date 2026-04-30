# -*- coding: utf-8 -*-
"""Audit heading hierarchy h1-h4 across docs/pages/*.html.

Looking for problems:
  - Multiple <h1> per page (should be exactly 1)
  - h2 before h1 (broken structure)
  - h3 without parent h2
  - h4 without parent h3
  - Headings without id (anchor target)
  - Duplicate ids on the same page
  - Empty/whitespace-only headings
  - Скачки уровней (h2 → h4 без h3)

Запуск: python docs/tools/audit_docs_headers.py
Не модифицирует файлы.
"""
import io
import re
from pathlib import Path
from collections import Counter, defaultdict

THIS_DIR = Path(__file__).resolve().parent
DOCS = THIS_DIR.parent / 'pages'

# Любой h1-h6 c опциональным id
HEADING_RE = re.compile(
    r'<(h[1-6])(\s+[^>]*)?>(.*?)</\1>',
    re.DOTALL,
)
ID_RE = re.compile(r'\bid="([^"]*)"')


def strip_html(s):
    s = re.sub(r'<[^>]+>', '', s)
    return ' '.join(s.split())


def audit_page(path):
    content = io.open(path, encoding='utf-8').read()
    issues = []
    headings = []  # [(level:int, id:str|None, title:str, pos:int)]

    for m in HEADING_RE.finditer(content):
        tag = m.group(1)
        level = int(tag[1])
        attrs = m.group(2) or ''
        title_html = m.group(3)
        title = strip_html(title_html)
        idm = ID_RE.search(attrs)
        hid = idm.group(1) if idm else None
        headings.append((level, hid, title, m.start()))

    # 1. h1 count
    h1s = [h for h in headings if h[0] == 1]
    if len(h1s) == 0:
        issues.append('NO_H1: страница без <h1>')
    elif len(h1s) > 1:
        issues.append(f'MULTIPLE_H1: найдено {len(h1s)} h1: {[h[2][:40] for h in h1s]}')

    # 2. Headings without id (h2-h4 only — h1 не обязателен)
    no_id = [h for h in headings if h[0] in (2, 3, 4) and not h[1]]
    if no_id:
        sample = [(h[0], h[2][:50]) for h in no_id[:5]]
        issues.append(f'NO_ID: {len(no_id)} h2/h3/h4 без id, sample: {sample}')

    # 3. Empty headings
    empty = [h for h in headings if not h[2].strip()]
    if empty:
        issues.append(f'EMPTY: {len(empty)} пустых заголовков (h{",".join(str(h[0]) for h in empty)})')

    # 4. Duplicate ids
    ids = [h[1] for h in headings if h[1]]
    dup_ids = [(i, c) for i, c in Counter(ids).items() if c > 1]
    if dup_ids:
        issues.append(f'DUPLICATE_IDS: {dup_ids}')

    # 5. Иерархия — скачки уровней (h2 → h4 без h3)
    last_real_level = 0  # игнорируем h1
    skip_jumps = []
    for level, hid, title, _ in headings:
        if level == 1:
            last_real_level = 1
            continue
        if last_real_level > 0 and level > last_real_level + 1:
            skip_jumps.append((last_real_level, level, hid or '?', title[:40]))
        last_real_level = level
    if skip_jumps:
        sample = skip_jumps[:5]
        issues.append(f'LEVEL_SKIP: {len(skip_jumps)} skips (h{sample[0][0]}->h{sample[0][1]}), sample: {sample}')

    # 6. h3 без родителя h2 / h4 без родителя h3
    orphan_h3 = []
    orphan_h4 = []
    last_h2 = None
    last_h3 = None
    for level, hid, title, _ in headings:
        if level == 2:
            last_h2 = hid or title
            last_h3 = None
        elif level == 3:
            if last_h2 is None:
                orphan_h3.append(title[:40])
            last_h3 = hid or title
        elif level == 4:
            if last_h3 is None:
                orphan_h4.append(title[:40])
    if orphan_h3:
        issues.append(f'ORPHAN_H3: {len(orphan_h3)} h3 без родительского h2: {orphan_h3[:3]}')
    if orphan_h4:
        issues.append(f'ORPHAN_H4: {len(orphan_h4)} h4 без родительского h3: {orphan_h4[:3]}')

    # 7. Подозрительные id (с пробелом/кириллицей)
    bad_ids = []
    for h in headings:
        if h[1] and (re.search(r'\s', h[1]) or re.search(r'[А-Яа-яЁё]', h[1])):
            bad_ids.append(h[1])
    if bad_ids:
        issues.append(f'BAD_ID: {bad_ids[:5]}')

    # Stats
    counts = Counter(h[0] for h in headings)
    stat = ' '.join(f'h{l}={counts.get(l, 0)}' for l in (1, 2, 3, 4, 5, 6) if counts.get(l, 0))

    print(f'\n========== {path.name} ==========')
    print(f'  Headings: {stat}')
    if issues:
        for i in issues:
            print(f'  [!] {i}')
    else:
        print('  [OK] no issues')


if __name__ == '__main__':
    for f in sorted(DOCS.glob('*.html')):
        audit_page(f)
