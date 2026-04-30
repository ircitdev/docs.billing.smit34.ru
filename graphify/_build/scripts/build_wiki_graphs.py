"""Извлекает RAW_NODES + RAW_EDGES из graph_c{cid}.html и пишет в JSON
для встраиваемой вкладки «Схема» в community_{cid}.html.

Запуск:
    python docs/graphify/_build/scripts/build_wiki_graphs.py

Layout:
    docs/graphify/_build/scripts/    ← здесь этот файл
    docs/graphify/_build/historical/ ← graph_c*.html (источник данных)
    docs/graphify/wiki/              ← цель: community_{cid}_graph.json

Тестовые ноды фильтруются синхронно с generate_wiki.py (is_test_node).
"""
import re
import json
import sys
import glob
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# docs/graphify/_build/scripts/ → docs/graphify/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.dirname(SCRIPT_DIR)              # _build/
HIST_DIR = os.path.join(BUILD_DIR, 'historical')     # _build/historical/
DOCS_GRAPHIFY = os.path.dirname(BUILD_DIR)           # docs/graphify/
WIKI_OUT = os.path.join(DOCS_GRAPHIFY, 'wiki')       # docs/graphify/wiki/
os.makedirs(WIKI_OUT, exist_ok=True)


def is_test_node(nd):
    """Синхронно с generate_wiki.py::is_test_node — скрываем tests/."""
    src = (nd.get('source_file') or '').replace('\\', '/').lower()
    if any(seg in src for seg in ('/tests/', '/test/', '/__tests__/', '/spec/')):
        return True
    if src.endswith('_test.py') or src.endswith('_tests.py') or src.endswith('.test.js'):
        return True
    label = nd.get('label') or ''
    if (label.startswith('test_') or label.endswith('Test')
            or label.endswith('Tests') or label.endswith('TestCase')):
        return True
    return False


def main():
    count = 0
    pattern = os.path.join(HIST_DIR, 'graph_c*.html')
    files = sorted(glob.glob(pattern))
    if not files:
        print('  WARN: no graph_c*.html in {}'.format(HIST_DIR))
        print('  → запусти run_pipeline.py + run_labels.py чтобы пересобрать.')
        return
    for f in files:
        m = re.search(r'graph_c(\d+)\.html$', f)
        if not m:
            continue
        cid = int(m.group(1))
        src = open(f, 'r', encoding='utf-8').read()
        n_m = re.search(r'const RAW_NODES = (\[.*?\]);', src, re.DOTALL)
        e_m = re.search(r'const RAW_EDGES = (\[.*?\]);', src, re.DOTALL)
        if not (n_m and e_m):
            print('  SKIP {}: no RAW_NODES/EDGES'.format(os.path.basename(f)))
            continue
        nodes = json.loads(n_m.group(1))
        edges = json.loads(e_m.group(1))
        test_ids = {n['id'] for n in nodes if is_test_node(n)}
        nodes_clean = [n for n in nodes if n['id'] not in test_ids]
        edges_clean = [e for e in edges
                       if e.get('from') not in test_ids and e.get('to') not in test_ids]
        out_path = os.path.join(WIKI_OUT, 'community_{}_graph.json'.format(cid))
        with open(out_path, 'w', encoding='utf-8') as fp:
            json.dump({
                'cid': cid,
                'nodes': nodes_clean,
                'edges': edges_clean,
                'stats': {
                    'nodes': len(nodes_clean),
                    'edges': len(edges_clean),
                    'tests_filtered': len(test_ids),
                }
            }, fp, ensure_ascii=False)
        count += 1
        print('  cid={:3d}: {} nodes, {} edges (filtered {} tests)'.format(
            cid, len(nodes_clean), len(edges_clean), len(test_ids)))
    print('Total: {} community_*_graph.json files in {}'.format(count, WIKI_OUT))


if __name__ == '__main__':
    main()
