# -*- coding: utf-8 -*-
"""Сверка ссылок docs.billing.smit34.ru/pages/X.html#anchor из биллинг-кода
с реальными id="..." в docs/pages/*.html.

Запуск:
  python docs/tools/check_billing_doc_links.py

Что проверяет:
  - Все ссылки вида docs.billing.smit34.ru/pages/<page>.html#<anchor> в коде
    биллинга (billing/, lk/, mobile_api/) — что <page> существует и <anchor>
    реально присутствует на этой странице
  - Считает сколько раз каждая страница docs упоминается в биллинг-UI
  - Показывает страницы которые ни разу не упоминаются (неиспользуемые в info-icons)

Когда запускать:
  - После переименования/удаления любого <h2 id> или <h3 id> в docs/pages/
  - После запуска docs/tools/fix_docs_headers.py (он генерирует новые id)
  - Перед публикацией изменений в docs
  - В рамках периодического hygiene check
"""
import io
import os
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent  # carbon_modern/
DOCS = ROOT / 'docs' / 'pages'

ID_RE = re.compile(r'\bid="([^"]+)"')
LINK_RE = re.compile(r'docs\.billing\.smit34\.ru/pages/([a-z]+\.html)#([a-zA-Z0-9_-]+)')

# Папки в которых ищем ссылки (исключаем docs/, graphify-out/, .git)
SCAN_DIRS = ['billing', 'lk', 'mobile_api', 'config']


def collect_anchors():
    """Все id из docs/pages/*.html"""
    anchors = defaultdict(set)
    for f in DOCS.glob('*.html'):
        src = io.open(f, encoding='utf-8').read()
        for m in ID_RE.finditer(src):
            anchors[f.name].add(m.group(1))
    return anchors


def collect_links():
    """Все ссылки из биллинг-кода"""
    links = defaultdict(list)  # {(page, anchor): [files]}
    for sub in SCAN_DIRS:
        sub_path = ROOT / sub
        if not sub_path.exists():
            continue
        for dirpath, _dirs, files in os.walk(sub_path):
            for fn in files:
                if not (fn.endswith('.html') or fn.endswith('.py')):
                    continue
                fp = Path(dirpath) / fn
                try:
                    src = io.open(fp, encoding='utf-8').read()
                except Exception:
                    continue
                for m in LINK_RE.finditer(src):
                    page, anchor = m.group(1), m.group(2)
                    rel = str(fp.relative_to(ROOT)).replace('\\', '/')
                    if rel not in links[(page, anchor)]:
                        links[(page, anchor)].append(rel)
    return links


def main():
    anchors = collect_anchors()
    links = collect_links()

    # === Stats ===
    print('=== Anchors per docs page ===')
    for page, ancs in sorted(anchors.items()):
        print(f'  {page:25s} {len(ancs):4d} anchors')

    page_refs = defaultdict(int)
    for (page, _), files in links.items():
        page_refs[page] += len(files)
    print(f'\n=== Pages referenced from billing code ===')
    for p, n in sorted(page_refs.items(), key=lambda x: -x[1]):
        print(f'  {p:25s} {n} refs')
    unused = set(anchors.keys()) - set(page_refs.keys())
    if unused:
        print(f'\n  Unused docs pages (no info-icons): {sorted(unused)}')

    # === Broken links ===
    broken = []
    ok = 0
    for (page, anchor), files in sorted(links.items()):
        if page not in anchors:
            broken.append((page, anchor, files, 'PAGE_NOT_FOUND'))
        elif anchor not in anchors[page]:
            # Поищем близкие варианты
            cands = [a for a in anchors[page]
                     if anchor.replace('-', '').lower() in a.replace('-', '').lower()
                     or a.replace('-', '').lower() in anchor.replace('-', '').lower()]
            broken.append((page, anchor, files, cands[:3]))
        else:
            ok += 1

    print(f'\n=== Verification: OK={ok} | BROKEN={len(broken)} ===')
    if broken:
        print()
        for page, anchor, files, hint in broken:
            print(f'[BROKEN] {page}#{anchor}')
            print(f'  used in: {files[:3]}{"..." if len(files) > 3 else ""}')
            if hint == 'PAGE_NOT_FOUND':
                print(f'  reason: page {page} does not exist')
            elif hint:
                print(f'  candidates: {hint}')
            else:
                print(f'  reason: no similar anchors on the page')
            print()
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
