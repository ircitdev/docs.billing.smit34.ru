#!/usr/bin/env bash
# sync-docs.sh — sync master (carbon_modern/docs/) to mirror (docs/),
# commit+push to docs.billing.smit34.ru, deploy to production server.
#
# Usage: from carbon_modern/docs/ dir, run:  ./sync-docs.sh "commit message"
#
# What it does:
#   1. Rebuild search index (search-index.json)
#   2. Mirror carbon_modern/docs/* -> ../../docs/  (excluding .git)
#   3. Commit + push in docs/ (separate docs.billing.smit34.ru repo)
#   4. Deploy same files to root@31.44.7.144:/var/www/docs.billing.smit34.ru/
#
# Master stays in carbon_modern/docs/ — always edit here.

set -euo pipefail

MSG="${1:-docs: sync from master}"
HERE="$(cd "$(dirname "$0")" && pwd)"
MIRROR="$(cd "$HERE/../../docs" && pwd)"
SERVER_PATH="/var/www/docs.billing.smit34.ru"

if command -v py >/dev/null 2>&1; then PY=py; else PY=python3; fi

echo "=== 0. Sync version.js fallback values into HTML ==="
(cd "$HERE" && $PY - <<'PYEOF'
"""Подменяет fallback-значения в HTML на актуальные из js/version.js.

Источник истины — js/version.js. После запуска все вхождения <span data-smit="full">…</span>,
<span data-smit="build">…</span>, <span data-smit="updated">…</span> и заголовков с
"v1.6.0 (build NNN)" / "build NNN" в title/meta синхронизируются с переменными.
"""
import re, glob, os
js = open('js/version.js', 'r', encoding='utf-8').read()
def get(name):
    m = re.search(r"%s:\s*'([^']+)'" % name, js)
    return m.group(1) if m else None
v = {
    'version': get('version'),
    'build':   get('build'),
    'updated': get('updated'),
    'year':    get('year'),
    'company': get('company'),
}
if not all(v.values()):
    print('  WARN: cannot parse js/version.js — skip')
    raise SystemExit(0)
full = 'v%s (build %s)' % (v['version'], v['build'])
brand = 'СмИТ Биллинг %s' % v['version']
patterns = [
    # data-smit text fallback: capture the value tag and replace inner text
    (r'(<span data-smit="full"[^>]*>)v[\d.]+\s*\(build\s+\d+\)(</span>)',     r'\g<1>%s\g<2>' % full),
    (r'(<span data-smit="vversion"[^>]*>)v[\d.]+(</span>)',                    r'\g<1>v%s\g<2>' % v['version']),
    (r'(<span data-smit="version"[^>]*>)[\d.]+(</span>)',                      r'\g<1>%s\g<2>' % v['version']),
    (r'(<span data-smit="build"[^>]*>)\d+(</span>)',                           r'\g<1>%s\g<2>' % v['build']),
    (r'(<span data-smit="vbuild"[^>]*>)build\s+\d+(</span>)',                  r'\g<1>build %s\g<2>' % v['build']),
    (r'(<span data-smit="updated"[^>]*>)\d{2}\.\d{2}\.\d{4}(</span>)',         r'\g<1>%s\g<2>' % v['updated']),
    (r'(<span data-smit="year"[^>]*>)\d{4}(</span>)',                          r'\g<1>%s\g<2>' % v['year']),
    (r'(<span data-smit="brand"[^>]*>)[^<]*(</span>)',                         r'\g<1>%s\g<2>' % brand),
    # <title>API — СмИТ Биллинг v1.6.0 (build NNN)</title>
    (r'(СмИТ Биллинг\s+)v[\d.]+\s*\(build\s+\d+\)',                            r'\g<1>%s' % full),
    # SVG/text inside index.html: "v1.6.0 · build 214"
    (r'v[\d.]+\s*·\s*build\s+\d+',                                              'v%s · build %s' % (v['version'], v['build'])),
]
total = 0
for f in glob.glob('index.html') + glob.glob('pages/*.html'):
    src = open(f, 'r', encoding='utf-8').read()
    new = src
    for pat, repl in patterns:
        new = re.sub(pat, repl, new)
    if new != src:
        open(f, 'w', encoding='utf-8').write(new)
        total += 1
print('  updated %d files (version=%s build=%s updated=%s)' % (total, v['version'], v['build'], v['updated']))
PYEOF
)

echo "=== 1. Rebuild search index ==="
(cd "$HERE" && $PY - <<'PYEOF'
import re, json, os, glob, html
pages = []
for f in sorted(glob.glob('index.html') + glob.glob('pages/*.html')):
    with open(f, 'r', encoding='utf-8') as fp:
        txt = fp.read()
    for m in re.finditer(r'<(h[234])\s+id="([^"]+)"[^>]*>(.*?)</\1>', txt, re.DOTALL):
        tag, hid, inner = m.groups()
        title = html.unescape(re.sub(r'<[^>]+>', '', inner).strip())
        if not title: continue
        after = txt[m.end():m.end()+2000]
        plain = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', after)).strip()[:240])
        pages.append({'t': title, 'id': hid, 'f': f.replace('\\','/'), 'c': plain})
with open('search-index.json', 'w', encoding='utf-8') as fp:
    json.dump(pages, fp, ensure_ascii=False, separators=(',',':'))
print(f"  wrote search-index.json — {len(pages)} entries, {os.path.getsize('search-index.json')} bytes")
PYEOF
)

echo "=== 2. Mirror to $MIRROR ==="
# Clear mirror (keep .git), then copy master content
find "$MIRROR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
cp -r "$HERE"/. "$MIRROR"/
if [ -d "$HERE/graphify" ]; then
  GRAPHIFY_FILES=$(find "$HERE/graphify" -type f | wc -l)
  echo "  synced (incl. graphify: $GRAPHIFY_FILES files)"
else
  echo "  synced"
fi

echo "=== 3. Commit + push in mirror repo ==="
cd "$MIRROR"
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "$MSG"
  git push origin main
  echo "  pushed to github.com/ircitdev/docs.billing.smit34.ru"
else
  echo "  no changes to commit"
fi

echo "=== 4. Deploy to server ==="
cd "$HERE"
tar -czf /tmp/docs-deploy.tar.gz --exclude=sync-docs.sh --exclude=build_search_index.py .
scp /tmp/docs-deploy.tar.gz root@31.44.7.144:/tmp/
ssh root@31.44.7.144 "cd $SERVER_PATH && tar -xzf /tmp/docs-deploy.tar.gz && rm /tmp/docs-deploy.tar.gz && echo '  deploy OK'"
rm /tmp/docs-deploy.tar.gz

echo "=== DONE ==="
