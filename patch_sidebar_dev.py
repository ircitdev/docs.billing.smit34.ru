#!/usr/bin/env python3
"""
Add "Разработчикам" section to sidebar of all docs/pages/*.html and docs/index.html.

The block is inserted right before <button class="sidebar-theme-toggle".
"""

import os
import re

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(DOCS_DIR, 'pages')

# ── Block for docs/pages/*.html (relative paths from pages/) ──
DEV_BLOCK_PAGES = """
      <div class="nav-section">Разработчикам</div>
      <ul>
        <li class="has-children">
          <a href="../graphify/graph.html"><i class="ti ti-topology-star-3"></i> Архитектура кода <span class="arrow"><i class="bi bi-chevron-right"></i></span></a>
          <ul class="submenu">
            <li><a href="../graphify/graph.html">Граф сообществ</a></li>
            <li><a href="../graphify/wiki/index.html">Wiki модулей</a></li>
            <li><a href="dev/index.html">Портал разработчика</a></li>
            <li><a href="../graphify/help.html">graphify CLI</a></li>
          </ul>
        </li>
      </ul>
"""

# ── Block for docs/index.html (relative paths from docs/) ──
DEV_BLOCK_INDEX = """
      <div class="nav-section">Разработчикам</div>
      <ul>
        <li class="has-children">
          <a href="graphify/graph.html"><i class="ti ti-topology-star-3"></i> Архитектура кода <span class="arrow"><i class="ti ti-chevron-right"></i></span></a>
          <ul class="submenu">
            <li><a href="graphify/graph.html">Граф сообществ</a></li>
            <li><a href="graphify/wiki/index.html">Wiki модулей</a></li>
            <li><a href="pages/dev/index.html">Портал разработчика</a></li>
            <li><a href="graphify/help.html">graphify CLI</a></li>
          </ul>
        </li>
      </ul>
"""

MARKER = '<button class="sidebar-theme-toggle"'


def patch_file(filepath: str, dev_block: str) -> bool:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'Разработчикам' in content:
        print(f'  SKIP (already has dev section): {os.path.basename(filepath)}')
        return False

    if MARKER not in content:
        print(f'  SKIP (marker not found): {os.path.basename(filepath)}')
        return False

    new_content = content.replace(MARKER, dev_block + '  ' + MARKER, 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'  PATCHED: {os.path.basename(filepath)}')
    return True


def main():
    patched = 0
    skipped = 0

    # docs/pages/*.html
    page_files = [f for f in os.listdir(PAGES_DIR) if f.endswith('.html')]
    for fname in sorted(page_files):
        fpath = os.path.join(PAGES_DIR, fname)
        ok = patch_file(fpath, DEV_BLOCK_PAGES)
        if ok:
            patched += 1
        else:
            skipped += 1

    # docs/index.html
    index_path = os.path.join(DOCS_DIR, 'index.html')
    ok = patch_file(index_path, DEV_BLOCK_INDEX)
    if ok:
        patched += 1
    else:
        skipped += 1

    print(f'\nDone: {patched} patched, {skipped} skipped.')


if __name__ == '__main__':
    main()
