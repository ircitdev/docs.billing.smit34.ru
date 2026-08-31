#!/usr/bin/env python3
"""Подгонка палитры вьюера archify под фирменные цвета СмИТ Биллинг.

Артефакт собирается с палитрой archify, поэтому фирменные оттенки
подставляются постобработкой — как и русский интерфейс.

Заменяются только точные значения цветов, найденные в файле; структура
и логика вьюера не затрагиваются.

Запуск:  python src/brand_colors.py            (все схемы в viewer/)
         python src/brand_colors.py file.html  (одна схема)
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VIEWER_DIR = os.path.join(ROOT, 'viewer')

# бирюзовый акцент archify → фирменный зелёный
COLORS = {
    '#0891b2': '#28c38c',
}


def recolor(path):
    with io.open(path, encoding='utf-8') as fh:
        html = fh.read()
    total = 0
    for old, new in COLORS.items():
        pattern = re.compile(re.escape(old), re.IGNORECASE)
        html, count = pattern.subn(new, html)
        total += count
    if total:
        with io.open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(html)
    return total


def main():
    targets = sys.argv[1:]
    if not targets:
        targets = [os.path.join(VIEWER_DIR, name)
                   for name in sorted(os.listdir(VIEWER_DIR)) if name.endswith('.html')]
    for path in targets:
        count = recolor(path)
        print('%-46s заменено значений цвета: %d' % (os.path.basename(path), count))


if __name__ == '__main__':
    main()
