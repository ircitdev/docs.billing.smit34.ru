# -*- coding: utf-8 -*-
"""Счётчик Яндекс.Метрики на страницы документации.

Ставим перед </head>: счётчик должен успеть засечь загрузку до отрисовки
содержимого. Служебные фрагменты (_nav.html — кусок навигации, а не
страница) пропускаем: он вставляется внутрь готовой страницы, и счётчик
инициализировался бы дважды.

Запуск: python tools/add_metrika.py [--dry-run]
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = '--dry-run' in sys.argv
COUNTER_ID = '112276394'
MARK = 'mc.yandex.ru/metrika/tag.js'

SNIPPET = """<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=%(id)s', 'ym');

    ym(%(id)s, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/%(id)s" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->
""" % {'id': COUNTER_ID}

# фрагменты, которые вставляются внутрь других страниц
SKIP_NAMES = {'_nav.html'}
# срезы графа знаний открываются внутри его интерфейса; как отдельные адреса
# они бессмысленны и засорили бы отчёт по страницам
SKIP_PREFIX = ('graph_c',)
SKIP_DIRS = {'node_modules', '.git', 'fonts', 'img', 'css'}

added, already, skipped = [], [], []

for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for name in sorted(files):
        if not name.endswith('.html'):
            continue
        rel = os.path.relpath(os.path.join(base, name), ROOT).replace('\\', '/')
        if name in SKIP_NAMES or name.startswith(SKIP_PREFIX):
            skipped.append(rel)
            continue

        path = os.path.join(base, name)
        s = io.open(path, encoding='utf-8', newline='').read()

        if MARK in s:
            already.append(rel)
            continue
        if '</head>' not in s:
            skipped.append(rel + ' (нет </head>)')
            continue

        nl = '\r\n' if '\r\n' in s else '\n'
        out = s.replace('</head>', SNIPPET.replace('\n', nl) + '</head>', 1)
        if not DRY:
            io.open(path, 'w', encoding='utf-8', newline='').write(out)
        added.append(rel)

print('счётчик добавлен: %d' % len(added))
for r in added[:8]:
    print('   %s' % r)
if len(added) > 8:
    print('   … и ещё %d' % (len(added) - 8))
if already:
    print('уже стоял: %d' % len(already))
if skipped:
    print('пропущено: %d (фрагменты навигации и срезы графа)' % len(skipped))
if DRY:
    print('\n(проба — файлы не изменены)')
