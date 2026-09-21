"""Check source fidelity, document bytes, navigation and local resources."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def require(ok,message):
 if not ok:errors.append(message)
class Page(HTMLParser):
 def __init__(self,path):
  super().__init__(convert_charrefs=True);self.path=path;self.ids=set();self.links=[];self.h1=0;self.lang=None;self.images=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if tag=='h1':self.h1+=1
  if 'id' in a:
   require(a['id'] not in self.ids,f'{self.path.name}: duplicate id {a["id"]}');self.ids.add(a['id'])
  if tag=='img':
   self.images+=1;require('alt' in a,f'{self.path.name}: missing image alternative')
  for key in ['href','src']:
   if key in a:self.links.append(a[key])
  if 'srcset' in a:self.links.extend(x.strip().split()[0] for x in a['srcset'].split(','))
pages={}
for path in ROOT.glob('*.html'):
 p=Page(path);p.feed(path.read_text(encoding='utf-8'));pages[path.name]=p
 require(p.h1==1,f'{path.name}: expected one main heading')
 require(p.lang=='en-AU',f'{path.name}: missing Australian English language tag')
 require('\ufffd' not in path.read_text(encoding='utf-8'),f'{path.name}: replacement character')
for name,p in pages.items():
 for url in p.links:
  parsed=urlsplit(url)
  if parsed.scheme or parsed.netloc:continue
  target=(ROOT/unquote(parsed.path)) if parsed.path else ROOT/name
  require(target.is_file(),f'{name}: missing local resource {url}')
  if parsed.fragment and target.suffix=='.html' and target.name in pages:require(unquote(parsed.fragment) in pages[target.name].ids,f'{name}: missing anchor {url}')
require(len(pages)==9,'Expected eight main pages and a 404 page')
pdf=ROOT/'documents/UNGA81_Joyful_Responsible_Abundance_Refined.pdf'
require(hashlib.sha256(pdf.read_bytes()).hexdigest()=='2ef53564995743044715b30d216d1998f4a08a3652074e29e4f137555566d7c2','Original PDF bytes changed')
content=json.loads((ROOT/'data/content.json').read_text(encoding='utf-8'))
source=(ROOT/'data/source-transcript.txt').read_text(encoding='utf-8-sig')
source=re.sub(r'A fair go in the age of intelligence\s*Joyful Responsible Abundance\s*\d+\s*','',source)
body=source[source.index('The invitation'):source.index('\nReferences\n')]
rendered=' '.join(s['title']+' '+' '.join(b['text'] for b in s['blocks']) for secs in content.values() for s in secs)
norm=lambda x:re.sub(r'[^\w]+','',x).lower()
require(norm(body)==norm(rendered),'Web body differs from supplied document transcript')
refs=json.loads((ROOT/'data/references.json').read_text(encoding='utf-8'))
ids=[r['id'] for r in refs]
require(len(ids)==len(set(ids)),'Duplicate reference IDs')
require(set(range(1,30)).issubset(ids),'Missing original reference entries')
for r in refs:
 require(bool(r['title'] and r['description'] and r['category'] and r['status']),f'Incomplete reference {r["id"]}')
 for l in r['links']:
  u=urlsplit(l['url']);require(u.scheme in ['https',''] and not l['url'].startswith('//'),f'Invalid link scheme in reference {r["id"]}')
  if not u.scheme:require((ROOT/unquote(u.path)).is_file(),f'Missing document in reference {r["id"]}')
for name in ['index','invitation','capability','livelihoods','intelligence','futures','library','about']:
 require((ROOT/f'assets/images/{name}-1536.webp').is_file(),f'Missing unique hero for {name}')
if errors:
 print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(pages)} HTML pages; local links, anchors, source fidelity, original PDF checksum and {len(refs)} references.')
