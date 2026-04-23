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

echo "=== 1. Rebuild search index ==="
if command -v py >/dev/null 2>&1; then PY=py; else PY=python3; fi
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
