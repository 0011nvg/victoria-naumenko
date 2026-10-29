"""Build a crawlable, JavaScript-independent site from editable JSON and HTML."""
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'content.json').read_text())
e = lambda value: escape(str(value), quote=True)

projects = []
for item in data['projects']:
    status = f'<span class="status">{e(item["status"])}</span>' if item['status'] else ''
    note = f'<p class="project-note">{e(item["note"])}</p>' if item['note'] else ''
    tags = ''.join(f'<li>{e(tag)}</li>' for tag in item['tags'])
    projects.append(f'''<article class="project project--{e(item['id'])} reveal" aria-labelledby="title-{e(item['id'])}">
      <div class="project-visual"><div class="preview-label"><span>{e(item['number'])} / {e(item['title'])}</span><span>Превью проекта</span></div>
        <div class="preview-image"><img src="{e(item['image'])}" alt="{e(item['alt'])}" width="1200" height="824" loading="lazy" decoding="async"></div>
      </div>
      <div class="project-copy"><div class="project-meta"><span class="overline">{e(item['category'])}</span>{status}</div>
        <h3 id="title-{e(item['id'])}">{e(item['title'])}</h3><p class="project-description">{e(item['description'])}</p>
        <p class="audience">{e(item['audience'])}</p><ul class="tags" aria-label="Возможности проекта">{tags}</ul>{note}
        <a class="project-link" href="{e(item['url'])}" target="_blank" rel="noopener noreferrer" aria-label="Открыть проект {e(item['title'])} — новая вкладка">Открыть проект <span aria-hidden="true">↗</span></a>
      </div></article>''')

directions = ''.join(f'''<article class="direction reveal"><span class="direction-number" aria-hidden="true">{e(x['number'])}</span><div><h3>{e(x['title'])}</h3><p class="direction-subtitle">{e(x['subtitle'])}</p></div><p>{e(x['text'])}</p></article>''' for x in data['directions'])
achievements = ''.join(f'''<article class="achievement reveal"><span class="overline">{e(x['label'])}</span><h3>{e(x['title'])}</h3><p>{e(x['text'])}</p></article>''' for x in data['achievements'])
principles = ''.join(f'''<article class="principle reveal"><span class="overline">0{i+1}</span><h3>{e(x['title'])}</h3><p>{e(x['text'])}</p></article>''' for i,x in enumerate(data['principles']))
html = (ROOT/'template.html').read_text()
for key,value in {'projects':'\n'.join(projects),'directions':directions,'achievements':achievements,'principles':principles,'project_count':str(len(data['projects'])).zfill(2)}.items():
    html = html.replace('{{'+key+'}}',value)
assert '{{' not in html, 'Unresolved template field'
(ROOT/'index.html').write_text(html)
print('Built index.html from template.html and content.json')
