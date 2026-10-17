from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json, re, subprocess
from cli import v1
root=Path.cwd(); source='f6a314c0f862a921ed333688362b35f32493ae09'; main='ff9091cc2f3bdb54c679ea2cd27f4d5280d83603'; base='d47291d5d9030de5ebef713da95efa978c4d8c6e'
G=lambda *a: subprocess.check_output(['git',*a])
assert v1.runtime()['sha256']=='bb3108ae8ea0d03190291b2104e4f9e3aab2ac1690b4da9d226a09f6afa2bba0'
for p in v1.runtime_files(): assert (root/p).read_bytes()==G('show',source+':'+p),p
preserved=['README.md','docs/reviews/FPR-5-MANUAL-ACCEPTANCE.md','docs/releases/FPR-5-MANUAL-LOCAL-RELEASE.md']
for p in preserved: assert (root/p).read_bytes()==G('show',source+':'+p),p
assets=G('ls-tree','-r','--name-only',main,'docs/landing/assets').decode().splitlines()
for p in assets: assert (root/p).read_bytes()==G('show',main+':'+p),p
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=set();self.links=[];self.tags=[];self.stack=[];self.errors=[];self.feed(text);assert not self.stack,self.stack
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append(tag)
  if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(tag)
  if 'id' in a: assert a['id'] not in self.ids,a['id'];self.ids.add(a['id'])
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
  if tag=='img':assert 'alt' in a
 def handle_endtag(self,tag):
  assert self.stack and self.stack[-1]==tag,(tag,self.stack[-3:]);self.stack.pop()
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  if self.stack and self.stack[-1]==tag:self.handle_endtag(tag)
landing=root/'docs/landing';pages={p:Page(p.read_text()) for p in landing.rglob('*.html')}; links=0
for p,page in pages.items():
 for link in page.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:
   assert u.scheme in ['https','mailto'],link
   prefix='https://github.com/aaronrene/overseer-kit/blob/main/'
   if link.startswith(prefix):
    target=root/unquote(u.path.split('/blob/main/',1)[1]); assert target.is_file(),link
    if u.fragment:
     headings=re.findall(r'^#+\s+(.+?)\s*#*$',target.read_text(),re.M)
     slugs={re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-') for h in headings}
     assert u.fragment in slugs,(link,slugs)
   continue
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  if target.is_dir():target=target/'index.html'
  assert target.is_relative_to(root) and target.is_file(),(p,link)
  if u.fragment:assert target in pages and unquote(u.fragment) in pages[target].ids,(p,link)
  links+=1
# Class/style/layout attributes for the three main pages are retained.
class Layout(HTMLParser):
 def __init__(self,text):super().__init__();self.attrs=[];self.feed(text)
 def handle_starttag(self,t,attrs):
  selected={k:v for k,v in attrs if k in ['class','style','width','height']}
  if selected:self.attrs.append((t,selected))
for p in ['docs/landing/index.html','docs/landing/docs.html','docs/landing/scenarios/index.html']:
 assert Layout(Path(p).read_text()).attrs==Layout(G('show',main+':'+p).decode()).attrs,p
changed_main=G('diff','--name-only',base,main).decode().splitlines()
dispositions=[]
for p in changed_main:
 current=Path(p).read_bytes() if Path(p).is_file() else None
 def blob(ref):
  r=subprocess.run(['git','show',ref+':'+p],capture_output=True);return r.stdout if r.returncode==0 else None
 a,b=blob(source),blob(main)
 resolution='identical_both' if current==a==b else 'current_main' if current==b else 'completed_source' if current==a else 'reconciled'
 dispositions.append({'path':p,'resolution':resolution})
Path('docs/validation/publication-20261017/main-change-dispositions.json').write_text(json.dumps({'source':source,'main':main,'merge_base':base,'paths':dispositions},indent=2)+'\n')
result={'source':source,'main':main,'runtime_paths_identical_to_source':len(v1.runtime_files()),'runtime_sha256':v1.runtime()['sha256'],'preserved_source_documents':preserved,'main_site_asset_files_identical':len(assets),'main_page_layout_attributes_preserved':True,'html_pages_checked':len(pages),'local_links_checked':links,'repository_document_links_and_fragments':'pass','acceptance_scope':'97f0529 only; no new acceptance','source_changes_after_acceptance':G('diff','--name-only','97f0529',source).decode().splitlines()}
Path('docs/validation/publication-20261017/integration-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='source_changes_after_acceptance'},indent=2))
