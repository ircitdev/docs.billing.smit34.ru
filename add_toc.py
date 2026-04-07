"""Add table of contents after each <h2> section in billing.html."""
import re

with open('pages/billing.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any existing TOC blocks first
content = re.sub(r'\n  <div class="section-toc">.*?</div>\n', '\n', content, flags=re.DOTALL)

# Find all h2 and h3 with IDs
headings = list(re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', content))

# Group h3s under their preceding h2
sections = []
current_h2 = None
for m in headings:
    level = m.group(1)
    anchor = m.group(2)
    # Strip HTML tags from title
    title = re.sub(r'<[^>]+>', '', m.group(3)).strip()
    if level == '2':
        current_h2 = {'anchor': anchor, 'title': title, 'pos': m.end(), 'children': []}
        sections.append(current_h2)
    elif level == '3' and current_h2:
        current_h2['children'].append({'anchor': anchor, 'title': title})

# Insert TOC after each h2 (reverse order to preserve positions)
insertions = 0
for sec in reversed(sections):
    if len(sec['children']) < 2:
        continue  # Skip sections with < 2 subsections

    # Build TOC HTML
    items = []
    for child in sec['children']:
        items.append(f'    <li><a href="#{child["anchor"]}">{child["title"]}</a></li>')

    toc_html = '\n  <div class="section-toc">\n  <details open>\n    <summary><strong>Содержание раздела</strong></summary>\n    <ul>\n' + '\n'.join(items) + '\n    </ul>\n  </details>\n  </div>\n'

    # Find the first <p> after the h2 and insert after it
    after_h2 = content[sec['pos']:]
    p_match = re.search(r'</p>', after_h2)
    if p_match:
        insert_pos = sec['pos'] + p_match.end()
        content = content[:insert_pos] + toc_html + content[insert_pos:]
        insertions += 1
        print(f'Added TOC for: {sec["title"]} ({len(sec["children"])} items)')

with open('pages/billing.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone: {insertions} TOCs added')
