# -*- coding: utf-8 -*-
"""Audit TOC blocks in docs/pages/*.html — find stale/missing links.

Анализирует структуру h2/h3/h4 в каждой странице и сравнивает с существующими
блоками <div class="section-toc">. Выявляет:
  - NO TOC: h2/h3 с >=2 дочерних, но без TOC
  - STALE: ссылка в TOC на несуществующий якорь
  - MISSING: якорь дочернего раздела без записи в TOC

Запуск: python docs/tools/audit_docs_toc.py
Не модифицирует файлы.
"""
import io
import re
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
DOCS = THIS_DIR.parent / 'pages'

H2_RE = re.compile(r'(<h2\s+id="([^"]+)"[^>]*>(.*?)</h2>)', re.DOTALL)
H3_RE = re.compile(r'(<h3\s+id="([^"]+)"[^>]*>(.*?)</h3>)', re.DOTALL)
H4_RE = re.compile(r'<h4\s+id="([^"]+)"[^>]*>(.*?)</h4>', re.DOTALL)
TOC_RE = re.compile(
    r'<div\s+class="section-toc">.*?</details>\s*</div>',
    re.DOTALL,
)
TOC_LI_RE = re.compile(r'<li><a\s+href="#([^"]+)"[^>]*>(.*?)</a></li>')


def strip_html(s):
    s = re.sub(r'<[^>]+>', '', s)
    return ' '.join(s.split())


def report_block(label, parent_id, children_ids, toc_ids, indent=2):
    pad = ' ' * indent
    if not children_ids and not toc_ids:
        return  # nothing to report
    if not toc_ids and len(children_ids) >= 2:
        print(f'{pad}[NO TOC] {label} {parent_id:32s} children={len(children_ids)} sample={list(children_ids)[:3]}')
        return
    if not toc_ids:
        return
    real = set(children_ids)
    toc = set(toc_ids)
    stale = toc - real
    missing = real - toc
    extras = []
    if stale:
        extras.append(f'STALE={sorted(stale)}')
    if missing:
        m = sorted(missing)
        extras.append(f'MISSING={m[:5]}{"..." if len(m) > 5 else ""}')
    status = 'OK' if not extras else 'FIX'
    extra_s = ' ' + '; '.join(extras) if extras else ''
    print(f'{pad}[{status}] {label} {parent_id:32s} ch={len(real)} toc={len(toc)}{extra_s}')


def audit_page(path):
    content = io.open(path, encoding='utf-8').read()
    print(f'\n========== {path.name} ==========')

    h2_matches = list(H2_RE.finditer(content))
    print(f'h2 sections: {len(h2_matches)}')

    for i, h2m in enumerate(h2_matches):
        h2_id = h2m.group(2)
        h2_end = h2m.end()
        h2_block_end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(content)
        h2_section = content[h2_end:h2_block_end]

        # h3-список и его TOC
        h3_matches = list(H3_RE.finditer(h2_section))
        h3_ids = [h3m.group(2) for h3m in h3_matches]
        h2_toc_match = TOC_RE.search(h2_section)
        h2_toc_ids = []
        if h2_toc_match:
            h2_toc_ids = [li.group(1) for li in TOC_LI_RE.finditer(h2_toc_match.group(0))]

        report_block('H2', h2_id, h3_ids, h2_toc_ids, indent=2)

        # Внутри каждого h3 — h4-список и его TOC
        for j, h3m in enumerate(h3_matches):
            h3_id = h3m.group(2)
            h3_end = h3m.end()
            h3_block_end = h3_matches[j + 1].start() if j + 1 < len(h3_matches) else len(h2_section)
            h3_section = h2_section[h3_end:h3_block_end]
            h4_ids = [h4m.group(1) for h4m in H4_RE.finditer(h3_section)]
            h3_toc_match = TOC_RE.search(h3_section)
            h3_toc_ids = []
            if h3_toc_match:
                h3_toc_ids = [li.group(1) for li in TOC_LI_RE.finditer(h3_toc_match.group(0))]
            report_block('  H3', h3_id, h4_ids, h3_toc_ids, indent=4)


if __name__ == '__main__':
    for f in sorted(DOCS.glob('*.html')):
        audit_page(f)
