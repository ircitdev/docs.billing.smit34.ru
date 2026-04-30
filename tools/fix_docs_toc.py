# -*- coding: utf-8 -*-
"""Add/update section-toc blocks in docs/pages/*.html.

Стратегия:
  0. На уровне страницы (сразу после <h1>) — page-toc со списком всех h2-разделов,
     если их >=3.
  1. Внутри каждого <h2 id> с >=2 дочерних <h3 id> — section-toc сразу после h2,
     список ссылок на все h3.
  2. Внутри каждого <h3 id> с >=2 дочерних <h4 id> — section-toc сразу после h3,
     список ссылок на все h4.
  3. Если <h2>/<h3> имеет 0-1 дочерних — TOC удаляется (если был).
  4. Существующие TOC синхронизируются с актуальной структурой (STALE удаляются,
     MISSING добавляются, порядок = порядок в документе).

Запуск:
  python docs/tools/fix_docs_toc.py             # apply
  python docs/tools/fix_docs_toc.py --dry-run   # show changes without writing
"""
import io
import re
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
DOCS = THIS_DIR.parent / 'pages'

H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.DOTALL)
H2_RE = re.compile(r'(<h2\s+id="([^"]+)"[^>]*>(.*?)</h2>)', re.DOTALL)
H3_RE = re.compile(r'(<h3\s+id="([^"]+)"[^>]*>(.*?)</h3>)', re.DOTALL)
H4_RE = re.compile(r'(<h4\s+id="([^"]+)"[^>]*>(.*?)</h4>)', re.DOTALL)
TOC_RE = re.compile(
    r'\s*<div\s+class="section-toc">.*?</details>\s*</div>',
    re.DOTALL,
)
# Page-level TOC отличается классом "page-toc" чтобы не конфликтовать с h2/h3 TOC
PAGE_TOC_RE = re.compile(
    r'\s*<div\s+class="page-toc">.*?</details>\s*</div>',
    re.DOTALL,
)


def strip_html(s):
    s = re.sub(r'<[^>]+>', '', s)
    return ' '.join(s.split())


def build_toc_block(items, indent='  ', cls='section-toc', summary='Содержание раздела'):
    """Generate <div class='section-toc'> (or page-toc) from list of (id, title)."""
    lines = [
        f'{indent}<div class="{cls}">',
        f'{indent}<details open>',
        f'{indent}  <summary><strong>{summary}</strong></summary>',
        f'{indent}  <ul>',
    ]
    for hid, htitle in items:
        lines.append(f'{indent}  <li><a href="#{hid}">{htitle}</a></li>')
    lines.append(f'{indent}  </ul>')
    lines.append(f'{indent}</details>')
    lines.append(f'{indent}</div>')
    return '\n' + '\n'.join(lines) + '\n'


def process_h3_blocks(h2_section):
    """Process h3 blocks inside one h2 section. Returns (new_section, n_added, n_updated, n_removed)."""
    n_a = n_u = n_r = 0
    new_section = h2_section
    h3_matches = list(H3_RE.finditer(h2_section))
    # iterate from end to start (positions don't shift)
    for j in range(len(h3_matches) - 1, -1, -1):
        h3m = h3_matches[j]
        h3_end = h3m.end()
        h3_block_end = h3_matches[j + 1].start() if j + 1 < len(h3_matches) else len(h2_section)
        h3_block = h2_section[h3_end:h3_block_end]
        h4_items = [(m.group(2), strip_html(m.group(3))) for m in H4_RE.finditer(h3_block)]
        toc_match = TOC_RE.search(h3_block)
        if len(h4_items) >= 2:
            new_toc = build_toc_block(h4_items, indent='    ')
            if toc_match:
                old = toc_match.group(0)
                if old.strip() != new_toc.strip():
                    new_block = h3_block.replace(old, new_toc, 1)
                    new_section = new_section[:h3_end] + new_block + new_section[h3_end + len(h3_block):]
                    n_u += 1
            else:
                new_section = new_section[:h3_end] + new_toc + new_section[h3_end:]
                n_a += 1
        else:
            if toc_match:
                old = toc_match.group(0)
                new_block = h3_block.replace(old, '', 1)
                new_section = new_section[:h3_end] + new_block + new_section[h3_end + len(h3_block):]
                n_r += 1
    return new_section, n_a, n_u, n_r


def process_page(path, dry_run=False):
    content = io.open(path, encoding='utf-8').read()
    new_content = content
    h2_matches = list(H2_RE.finditer(content))
    h2_a = h2_u = h2_r = 0
    h3_a = h3_u = h3_r = 0
    page_a = page_u = page_r = 0

    # === Page-level TOC: список всех h2 сразу после <h1> ===
    h1_match = H1_RE.search(content)
    if h1_match:
        h1_end = h1_match.end()
        h2_items = [(m.group(2), strip_html(m.group(3))) for m in h2_matches]
        # Ищем существующий page-toc сразу после h1 (в пределах ~3 КБ)
        search_window = content[h1_end:h1_end + 5000]
        existing = PAGE_TOC_RE.match('\n' + search_window) or PAGE_TOC_RE.search(search_window[:3000])
        if len(h2_items) >= 3:
            new_toc = build_toc_block(
                h2_items, indent='', cls='page-toc',
                summary='Содержание страницы',
            )
            if existing:
                old = existing.group(0)
                if old.strip() != new_toc.strip():
                    # позиция existing относительно content
                    abs_start = h1_end + content[h1_end:].find(old)
                    new_content = new_content[:abs_start] + new_toc + new_content[abs_start + len(old):]
                    page_u += 1
            else:
                new_content = new_content[:h1_end] + new_toc + new_content[h1_end:]
                page_a += 1
        else:
            if existing:
                old = existing.group(0)
                abs_start = h1_end + content[h1_end:].find(old)
                new_content = new_content[:abs_start] + new_content[abs_start + len(old):]
                page_r += 1
        # После page-TOC координаты h2_matches могли сдвинуться — пересчитаем
        if page_a or page_u or page_r:
            h2_matches = list(H2_RE.finditer(new_content))

    # Iterate from END to START — positions don't shift
    for i in range(len(h2_matches) - 1, -1, -1):
        h2m = h2_matches[i]
        h2_end = h2m.end()
        h2_block_end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(content)
        h2_section = new_content[h2_end:h2_block_end]

        # First — process h3 blocks inside (which may add/remove h3-level TOCs)
        new_h2_section, ha, hu, hr = process_h3_blocks(h2_section)
        h3_a += ha
        h3_u += hu
        h3_r += hr
        if new_h2_section != h2_section:
            new_content = new_content[:h2_end] + new_h2_section + new_content[h2_end + len(h2_section):]
            h2_section = new_h2_section
            h2_block_end = h2_end + len(new_h2_section)

        # Then — h2-level TOC (list of h3)
        h3_items = [(m.group(2), strip_html(m.group(3))) for m in H3_RE.finditer(h2_section)]
        toc_match = TOC_RE.search(h2_section)
        if len(h3_items) >= 2:
            new_toc = build_toc_block(h3_items, indent='  ')
            if toc_match:
                old = toc_match.group(0)
                if old.strip() != new_toc.strip():
                    new_section = h2_section.replace(old, new_toc, 1)
                    new_content = new_content[:h2_end] + new_section + new_content[h2_end + len(h2_section):]
                    h2_u += 1
            else:
                new_content = new_content[:h2_end] + new_toc + new_content[h2_end:]
                h2_a += 1
        else:
            if toc_match:
                old = toc_match.group(0)
                new_section = h2_section.replace(old, '', 1)
                new_content = new_content[:h2_end] + new_section + new_content[h2_end + len(h2_section):]
                h2_r += 1

    summary = (
        f'{path.name:30s} page: +{page_a} ~{page_u} -{page_r}    '
        f'h2: +{h2_a} ~{h2_u} -{h2_r}    h3: +{h3_a} ~{h3_u} -{h3_r}'
    )
    print(summary)
    total = page_a + page_u + page_r + h2_a + h2_u + h2_r + h3_a + h3_u + h3_r
    if not dry_run and total:
        io.open(path, 'w', encoding='utf-8', newline='\n').write(new_content)
    return total


def main():
    dry = '--dry-run' in sys.argv
    print(f'{"DRY RUN" if dry else "APPLY"}\n')
    print(f'{"file":30s} {"h2 changes":20s} {"h3 changes":20s}')
    print('-' * 80)
    total = 0
    for f in sorted(DOCS.glob('*.html')):
        total += process_page(f, dry_run=dry)
    print('-' * 80)
    print(f'Total changes: {total}')


if __name__ == '__main__':
    main()
