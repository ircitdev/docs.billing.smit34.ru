import re, json, os, glob, html

pages = []
for f in sorted(glob.glob('index.html') + glob.glob('pages/*.html')):
    with open(f, 'r', encoding='utf-8') as fp:
        txt = fp.read()
    for m in re.finditer(r'<(h[234])\s+id="([^"]+)"[^>]*>(.*?)</\1>', txt, re.DOTALL):
        tag, hid, inner = m.groups()
        title = re.sub(r'<[^>]+>', '', inner).strip()
        title = html.unescape(title)
        if not title:
            continue
        after = txt[m.end():m.end()+2000]
        plain = re.sub(r'<[^>]+>', ' ', after)
        plain = re.sub(r'\s+', ' ', plain).strip()[:240]
        plain = html.unescape(plain)
        pages.append({'t': title, 'id': hid, 'f': f.replace('\\', '/'), 'c': plain})

print(f'Total entries: {len(pages)}')
with open('js/search_index.json', 'w', encoding='utf-8') as fp:
    json.dump(pages, fp, ensure_ascii=False, separators=(',', ':'))
print('Wrote js/search_index.json', os.path.getsize('js/search_index.json'), 'bytes')
