#!/usr/bin/env python3
"""Мобильные правки просмотрщика схем.

На телефоне панель вьюера не помещается в одну строку и разъезжается на два
ряда, отнимая высоту у самой схемы. Её кнопки прячутся, а тема и экспорт
переезжают в шапку страницы (см. `make_pages.py`): шапка переключает тему
через параметр адреса и открывает меню экспорта программно.

Правки живут в отдельном блоке стилей и применяются после `deliver`, как
локализация и фирменные цвета.

Запуск:  python src/viewer_mobile.py            (все схемы в viewer/)
         python src/viewer_mobile.py file.html  (одна схема)
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VIEWER_DIR = os.path.join(ROOT, 'viewer')
MARKER = 'id="smit-viewer-mobile"'

STYLE = """
<style id="smit-viewer-mobile">
  @media (max-width: 760px) {
    /* Выбор оформления и режим показа — приёмы для большого экрана.
       Тема и экспорт переехали в шапку страницы, поэтому кнопки панели
       прячем, но саму панель и меню экспорта оставляем в документе:
       шапка открывает это меню программно. */
    .preset-wrap,
    #btn-preset,
    #btn-present,
    #btn-theme,
    #btn-motion,
    #btn-export { display: none !important; }
    .toolbar { gap: 0; padding: 0; min-height: 0; }
  }
</style>
"""


def tweak(path):
    with io.open(path, encoding='utf-8') as fh:
        html = fh.read()
    if MARKER in html:
        return False
    html = html.replace('</head>', STYLE.strip() + '\n</head>', 1)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(html)
    return True


def main():
    targets = sys.argv[1:]
    if not targets:
        targets = [os.path.join(VIEWER_DIR, name)
                   for name in sorted(os.listdir(VIEWER_DIR)) if name.endswith('.html')]
    for path in targets:
        done = tweak(path)
        print('%-46s %s' % (os.path.basename(path), 'правка добавлена' if done else 'уже была'))


if __name__ == '__main__':
    main()
