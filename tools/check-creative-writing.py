"""Verify exact poem rendering, stable links and optional source/HTTP reconciliation.

python tools/check-creative-writing.py --base-url http://127.0.0.1:8973
--source-text may point to a private readable Drive snapshot; never commit it.
"""
import argparse
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import urlopen
import creativewriting as cw

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=set(); self.links=[]; self.poems={}; self.poem=None; self.stanza=None
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate HTML id: {a["id"]}'
            self.ids.add(a['id'])
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag=='article' and 'data-cw-poem' in a:
            self.poem=a['id']; self.poems[self.poem]=[]
        if tag=='p' and {'cw-stanza','cw-poem__stanza'} & set(a.get('class','').split()): self.stanza=''
        if tag=='br' and self.stanza is not None: self.stanza+='\n'
    def handle_data(self,value):
        if self.stanza is not None: self.stanza+=value
    def handle_endtag(self,tag):
        if tag=='p' and self.stanza is not None:
            self.poems[self.poem].append(self.stanza); self.stanza=None
        if tag=='article': self.poem=None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url')
    parser.add_argument('--source-text',type=Path)
    args=parser.parse_args()
    root=cw.ROOT
    entries={'creative-writing':{'cw':{'kind':'main','collection':'all'}},**cw.page_entries()}
    docs={}; aliases=0; checked_links=0
    for path in entries:
        text=(root/(path+'.html')).read_text(encoding='utf-8')
        assert 'Poems to be supplied' not in text
        assert 'School level to be confirmed' not in text
        assert 'cw-wave' not in text and 'cw-split' not in text
        docs[path]=Document(text)
        if args.base_url:
            for suffix in ('','.html'):
                with urlopen(args.base_url+'/'+path+suffix,timeout=15) as response:
                    payload=response.read().decode('utf-8').replace('\r\n','\n')
                    assert response.status==200 and payload==text,(path,suffix)
                    aliases+=1
    old=json.loads(subprocess.check_output(['git','show','HEAD:tools/creative-writing-content.json'],cwd=root).decode())
    old_ids={p['id'] for e in old['editions'] for p in e.get('poems',[])}
    ids={p['id'] for _,_,p in cw.published_poems()}
    assert old_ids<=ids,'An established poem anchor was removed'
    source=args.source_text.read_text(encoding='utf-8-sig').splitlines() if args.source_text else None
    for e in cw.editions():
        rendered=docs[e['path']].poems
        assert len(rendered)==len(e['poems'])
        for p in e['poems']:
            assert rendered['poem-'+p['id']]==p['stanzas'],p['id']
            expected_landing=['\n'.join(s.splitlines()) for s in p['stanzas']]
            assert docs['creative-writing'].poems['poem-'+p['id']]==expected_landing,p['id']
            if source:
                start,end=p['source']['bodyLines']
                expected=re.split(r'\n(?:[ \t]*\n)+','\n'.join(source[start-1:end]))
                assert expected==p['stanzas'],f'Source mismatch: {p["id"]}'
                if p.get('author'):
                    assert p['author'] in source[p['source']['bylineLine']-1]
                if p.get('title'):
                    assert p['title']==source[p['source']['titleLine']-1]
    for path,doc in docs.items():
        base='http://local/'+path+'.html'
        for href in doc.links:
            u=urlsplit(urljoin(base,href)); target=unquote(u.path).strip('/').removesuffix('.html')
            if target not in docs: continue
            if u.fragment: assert unquote(u.fragment) in docs[target].ids,(path,href)
            checked_links+=1
    for key in cw.SCHOOLS:
        for e in cw.in_collection(key):
            for p in cw.poems_for(e,key): assert p.get('school')==key and p.get('grade')
    redirects={r['source']:r for r in json.loads((root/'vercel.json').read_text(encoding='utf-8'))['redirects']}
    retired_aliases=0
    for route in cw.data()['retiredRoutes']:
        path=route['path']; target='creative-writing/'+route['collection']
        assert path not in entries and not (root/(path+'.html')).exists(),f'Retired page still exists: {path}'
        assert target in entries,'Retired address needs a published destination'
        for suffix in ('','.html'):
            redirect=redirects['/'+path+suffix]
            assert redirect['destination']=='/'+target and redirect['permanent'] is True
            if args.base_url:
                with urlopen(args.base_url+'/'+path+suffix,timeout=15) as response:
                    assert urlsplit(response.url).path.removesuffix('.html')=='/'+target
                    payload=response.read().decode('utf-8').replace('\r\n','\n')
                    assert response.status==200 and payload==(root/(target+'.html')).read_text(encoding='utf-8')
                    retired_aliases+=1
    report={'routes':len(entries),'http_aliases_checked':aliases,'section_links_checked':checked_links,
            'retired_pages_removed':len(cw.data()['retiredRoutes']),'retired_redirect_aliases_checked':retired_aliases,
            'all_counts':cw.counts(),'senior_counts':cw.counts('senior'),'junior_counts':cw.counts('junior'),
            'established_anchors_preserved':len(old_ids),'exact_source_comparison':source is not None}
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
