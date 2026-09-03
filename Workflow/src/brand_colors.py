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
# (светлая тема / тёмная тема)
COLORS = {
    '#0891b2': '#28c38c',
    '#22d3ee': '#059669',
}
SCRIPT_RE = re.compile(r'<script.*?</script>', re.S)


def recolor(path):
    """Меняет цвета в стилях, разметке и запасных значениях вьюера.

    Те же цвета встречаются в скриптах как запасной вариант на случай пустой
    CSS-переменной, поэтому приводятся к новому оттенку вместе с палитрой —
    иначе при сбросе стиля вьюер вернул бы старый бирюзовый.
    """
    with io.open(path, encoding='utf-8') as fh:
        html = fh.read()

    chunks, scripts, last = [], [], 0
    for match in SCRIPT_RE.finditer(html):
        chunks.append(html[last:match.start()])
        scripts.append(match.group(0))
        last = match.end()
    chunks.append(html[last:])

    total = 0
    for index, chunk in enumerate(chunks):
        for old, new in COLORS.items():
            chunk, count = re.compile(re.escape(old), re.IGNORECASE).subn(new, chunk)
            total += count
        chunks[index] = chunk

    out = []
    for index, chunk in enumerate(chunks):
        out.append(chunk)
        if index < len(scripts):
            out.append(scripts[index])
    html = ''.join(out)

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
