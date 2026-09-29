"""Creative Writing pages rendered from one reconciled source, with progressive UI."""
from __future__ import annotations
import hashlib
import html
import json
import re
import zipfile
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTENT_PATH = HERE / 'creative-writing-content.json'
TEMPLATE_PATH = HERE / 'pages/creative-writing.html'
MONTHS = ('January','February','March','April','May','June','July','August','September','October','November','December')
SCHOOLS = ('junior','senior')

def esc(value):
    return html.escape(str(value), quote=True)

def contrast(a,b):
    def lum(c):
        channels=[int(c[i:i+2],16)/255 for i in (1,3,5)]
        linear=[v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in channels]
        return sum(x*y for x,y in zip(linear,(.2126,.7152,.0722)))
    hi,lo=sorted((lum(a),lum(b)),reverse=True)
    return (hi+.05)/(lo+.05)

def _verbatim(text,p):
    want=[s.strip() for s in text.splitlines()]
    have=[s.strip() for stanza in p['stanzas'] for s in stanza.splitlines()]
    return bool(want) and any(have[i:i+len(want)]==want for i in range(len(have)-len(want)+1))

def download_file(spec):
    path=(ROOT/spec['file']).resolve()
    if not path.is_relative_to(ROOT/'assets') or path.suffix.lower() not in ('.pdf','.ppt','.pptx'):
        raise ValueError('Invalid download path')
    payload=path.read_bytes()
    ext=path.suffix.lower()
    if ext=='.pdf' and not payload.startswith(b'%PDF-'): raise ValueError('Invalid PDF')
    if ext=='.ppt' and not payload.startswith(bytes.fromhex('D0CF11E0A1B11AE1')): raise ValueError('Invalid PPT')
    if ext=='.pptx':
        with zipfile.ZipFile(path) as deck:
            if not any(re.fullmatch(r'ppt/slides/slide\d+\.xml',s) for s in deck.namelist()): raise ValueError('No slides')
    size=f'{len(payload)/1048576:.1f} MB' if len(payload)>=1048576 else f'{max(1,round(len(payload)/1024))} KB'
    return dict(spec,format=ext[1:].upper(),size=size)

@lru_cache(maxsize=1)
def data():
    raw=json.loads(CONTENT_PATH.read_text(encoding='utf-8'))
    eids,pids,paths=set(),set(),set()
    for order,e in enumerate(raw['editions']):
        eid=e['id']
        if not re.fullmatch(r'[a-z0-9-]+',eid) or eid in eids: raise ValueError('Invalid/duplicate edition')
        eids.add(eid)
        if e['status']!='published' or not e['poems']: raise ValueError('Published editions need poems')
        month,year=e.get('month'),e.get('year')
        if month is not None and (not isinstance(month,int) or not 1<=month<=12): raise ValueError('Invalid month')
        if year is not None and (not isinstance(year,int) or year<1900): raise ValueError('Invalid year')
        slug=e.get('slug') or (f'{MONTHS[month-1].lower()}-{year}' if month and year else eid)
        path=f'creative-writing/anthology/{slug}'
        if path in paths: raise ValueError('Duplicate route')
        paths.add(path)
        date=f'{MONTHS[month-1]} {year}' if month and year else (MONTHS[month-1] if month else (str(year) if year else None))
        label=date+' · year not recorded' if month and not year else (date or 'Date not recorded')
        e.update(order=order,path=path,href=path+'.html',date=date,date_label=label)
        e['downloads']=[download_file(s) for s in e.get('downloads',[])]
        for p in e['poems']:
            if not re.fullmatch(r'[a-z0-9-]+',p['id']) or p['id'] in pids: raise ValueError('Invalid/duplicate poem')
            pids.add(p['id'])
            if not p['stanzas'] or not all(isinstance(s,str) and s.strip() for s in p['stanzas']): raise ValueError('Empty poem')
            if p.get('school') not in (None,*SCHOOLS): raise ValueError('Invalid school')
            if p.get('school') and not p.get('grade'): raise ValueError('Classification needs verified grade')
            if bool(p.get('author')) != bool(p.get('authorId')): raise ValueError('Author identity mismatch')
            if hashlib.sha256('\n\n'.join(p['stanzas']).encode()).hexdigest()!=p['source']['sha256']: raise ValueError(f'Source text drift: {p["id"]}')
            for excerpt in p.get('lines',[]):
                if not _verbatim(excerpt,p): raise ValueError('Excerpt differs from poem')
        if e.get('epigraph'):
            ref=next((p for p in e['poems'] if p['id']==e['epigraph']['poem']),None)
            if not ref or not _verbatim(e['epigraph']['text'],ref): raise ValueError('Invalid epigraph')
    return raw

def editions(): return data()['editions']
def poems_for(e,c='all'): return [p for p in e['poems'] if c=='all' or p.get('school')==c]
def in_collection(c='all'):
    chosen=[e for e in editions() if poems_for(e,c)]
    # Only complete dates participate in chronological order.
    dated=sorted((e for e in chosen if e.get('month') and e.get('year')),key=lambda e:(e['year'],e['month']),reverse=True)
    return dated+[e for e in chosen if e not in dated]
def published_poems():
    for e in in_collection():
        for n,p in enumerate(e['poems'],1): yield e,n,p
def counts(c='all'):
    chosen=in_collection(c)
    poems=[p for e in chosen for p in poems_for(e,c)]
    return len(chosen),len(poems),len({p['authorId'] for p in poems if p.get('authorId')})
def count(): return counts()[1]
def writer_count(): return counts()[2]
def plural(n,s): return f'{n} {s}{"" if n==1 else "s"}'
def stats_line(c):
    e,p,a=counts(c)
    return f'{plural(e,"edition")} / {plural(p,"poem")} / {plural(a,"named author")}'
def byline(p): return p.get('author') or 'Author not recorded'
def opening(p): return p['stanzas'][0].splitlines()[0].strip()
def poem_href(e,p): return f'{e["href"]}#poem-{p["id"]}'

def filter_html(active):
    links=[]
    for key,label in (('all','All Writing'),('junior','Junior'),('senior','Senior')):
        dest='creative-writing.html#archive' if key=='all' else f'creative-writing/{key}.html#archive'
        current=' aria-current="page"' if key==active else ''
        links.append(f'<a href="{dest}"{current}>{label}</a>')
    return '<nav class="cw-filter" aria-label="Writing collections">'+''.join(links)+'</nav>'

def excerpt_pool():
    pool=[]
    for e,_,p in published_poems():
        for text in p.get('lines',[]):
            pool.append(dict(lines=text.splitlines(),author=byline(p),grade=p.get('grade'),edition=e['topic'],date=e['date_label'],href=poem_href(e,p)))
    pool.sort(key=lambda x:'turning-ananda-priyan' not in x['href'])
    return pool

def hero_html(c):
    if c!='all':
        school=data()['schools'][c]
        return f'''<header class="cw-index-head" id="top" data-header-theme="light"><div class="cw-wrap">
<a class="cw-back" href="creative-writing.html#archive">All Writing</a><p class="cw-meta">Creative Writing / {esc(school['grades'])}</p>
<h1>{esc(school['name'])}</h1><p>Browse poems by students with a recorded {c} school grade.</p></div></header>'''
    pool=excerpt_pool(); x=pool[0]
    lines=''.join(f'<span class="cw-excerpt-line">{esc(s)}</span>' for s in x['lines'])
    payload=json.dumps(pool,ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
    return f'''<section class="cw-hero" id="top" aria-labelledby="cw-title" data-header-theme="dark">
<div class="cw-wrap cw-hero-grid"><div class="cw-hero-lead">
<p class="cw-meta">The CIRS student collection</p>
<h1 id="cw-title"><span>Creative</span> <span>Writing</span></h1>
<p class="cw-hero-intro">Poems from CIRS students, gathered into a collection to read and return to.</p>
<a class="cw-explore" href="creative-writing.html#archive">Explore the collection <span aria-hidden="true">↓</span></a>
<span class="cw-hand" aria-hidden="true">between the lines</span></div>
<div class="cw-paper-stage"><div class="cw-paper-back" aria-hidden="true"></div><div class="cw-paper">
<p class="cw-paper-label">A line from the collection</p><figure class="cw-feature" data-cw-feature>
<blockquote><p data-cw-excerpt>{lines}</p></blockquote>
<figcaption><span class="cw-feature-author" data-cw-author>{esc(x['author'])}</span>
<span class="cw-feature-grade" data-cw-grade>{esc(x['grade'] or '')}</span>
<span class="cw-feature-edition" data-cw-edition>{esc(x['edition'])}</span>
<span class="cw-feature-date" data-cw-date>{esc(x['date'])}</span></figcaption></figure>
<div class="cw-paper-actions"><a class="cw-read" href="{esc(x['href'])}" data-cw-read>Read this poem <span aria-hidden="true">↗</span></a>
<button type="button" class="cw-another" data-cw-another hidden>Another line <span aria-hidden="true">↻</span></button></div>
<svg class="cw-ink" viewBox="0 0 250 45" aria-hidden="true"><path d="M5 31C60 16 173 40 228 17M43 34C92 22 168 35 219 23M238 10l-12 26" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
</div></div></div><p class="cw-sr" role="status" aria-live="polite" aria-atomic="true" data-cw-announcement></p>
<script type="application/json" id="cw-excerpts">{payload}</script></section>'''

def archive_html(c):
    chosen=in_collection(c)
    if not chosen:
        return '''<div class="cw-empty"><h3>No published Junior writing yet.</h3><p>There are currently no poems with a recorded Junior School grade in this collection.</p>
<a class="cw-read" href="creative-writing.html#archive">Browse All Writing <span aria-hidden="true">↗</span></a></div>'''
    rows=[]
    for e in chosen:
        poems=poems_for(e,c); first=poems[0]
        label=plural(len(poems),'poem')
        if c!='all': label+=f' by {c} students / {len(e["poems"])} in the full edition'
        ep=e.get('epigraph')
        selected=next((p for p in poems if ep and p['id']==ep['poem']),first)
        text=ep['text'] if ep and selected['id']==ep['poem'] else opening(selected)
        href=e['href'] if c=='all' else poem_href(e,first)
        matching=''
        if c!='all':
            matching='<ul class="cw-matching-poems">'+''.join(f'<li><a href="{esc(poem_href(e,p))}">{esc(byline(p))} <span>{esc(p.get("grade") or "")}</span></a></li>' for p in poems)+'</ul>'
        rows.append(f'''<li class="cw-archive-row"><div class="cw-row-date">{esc(e['date_label'])}</div>
<div class="cw-row-main"><h3><a href="{esc(href)}">{esc(e['topic'])}<span class="cw-row-arrow" aria-hidden="true">↗</span></a></h3>
<p class="cw-row-count">{esc(label)}</p><p class="cw-row-excerpt">“{esc(text.replace(chr(10),' '))}” <span>{esc(byline(selected))}</span></p>{matching}</div></li>''')
    return '<ol class="cw-archive-list">'+'\n'.join(rows)+'</ol>'

def main_html(c):
    intro=('Read an edition from beginning to end, or follow a line that catches your eye. Each poem stays with its author’s words and line breaks.' if c=='all' else 'These links select poems with verified grades. The full editions remain available through All Writing.')
    values=dict(CW_HERO=hero_html(c),CW_INTRO=intro,CW_STATS=stats_line(c),CW_FILTER=filter_html(c),CW_ARCHIVE=archive_html(c))
    out=TEMPLATE_PATH.read_text(encoding='utf-8')
    for key,value in values.items(): out=out.replace('{{'+key+'}}',value)
    return out

def contents_list(e,compact=False):
    rows=[]
    for i,p in enumerate(e['poems'],1):
        name=p.get('title') or byline(p)
        detail=byline(p) if p.get('title') else 'Opening: '+opening(p)
        grade=f'<span class="cw-contents-grade">{esc(p["grade"])}</span>' if p.get('grade') else ''
        rows.append(f'<li><a href="{esc(poem_href(e,p))}"><span class="cw-number" aria-hidden="true">{i:02}</span><span><span class="cw-contents-name">{esc(name)}</span><span class="cw-contents-preview">{esc(detail)}</span>{grade}</span></a></li>')
    return '<ol class="cw-contents-list'+(' cw-contents-list--compact' if compact else '')+'">'+''.join(rows)+'</ol>'

def downloads_html(e):
    return ''.join(f'<a class="cw-read" href="{esc(d["file"])}" download>Download edition ({d["format"]}, {d["size"]})</a>' for d in e['downloads'])

def edition_html(e):
    poems=e['poems']; authors=len({p['authorId'] for p in poems if p.get('authorId')})
    facts=f'{e["date_label"]} / {plural(len(poems),"poem")} / {plural(authors,"named author")}'
    schools={p.get('school') for p in poems}
    if len(schools)==1 and None not in schools: facts+=' / '+data()['schools'][next(iter(schools))]['name']
    articles=[]
    for i,p in enumerate(poems):
        pid='poem-'+p['id']; name=p.get('title') or byline(p)
        author=f'<p class="cw-poem-author">{esc(byline(p))}</p>' if p.get('title') else ''
        grade=f'<p class="cw-poem-grade">{esc(p["grade"])}</p>' if p.get('grade') else ''
        # Preserve every character and newline. Encode trailing spaces as
        # entities so generated HTML also passes Git's whitespace checks.
        stanzas=''.join('<p class="cw-stanza">'+re.sub(r' +(?=\n|$)',
            lambda m:'&#32;'*len(m[0]),esc(s))+'</p>' for s in p['stanzas'])
        prev=f'<a href="{esc(poem_href(e,poems[i-1]))}" rel="prev">Previous poem</a>' if i else '<span></span>'
        nxt=f'<a href="{esc(poem_href(e,poems[i+1]))}" rel="next">Next poem</a>' if i+1<len(poems) else '<span></span>'
        articles.append(f'''<article class="cw-poem" id="{pid}" tabindex="-1" aria-labelledby="{pid}-name" data-cw-poem>
<header class="cw-poem-head"><p class="cw-meta">{i+1:02} / {len(poems):02}{' / Untitled poem' if not p.get('title') else ''}</p>
<h2 id="{pid}-name">{esc(name)}</h2>{author}{grade}<a class="cw-permalink" href="{esc(poem_href(e,p))}">Link to this poem <span aria-hidden="true">↗</span></a></header>
<div class="cw-verse">{stanzas}</div><nav class="cw-poem-nav" aria-label="Navigation for poem {i+1}">{prev}<a href="{e['href']}#contents">Return to contents</a>{nxt}
<a class="cw-poem-collection" href="creative-writing.html#archive">Return to the collection</a></nav></article>''')
    more=[x for x in in_collection() if x['id']!=e['id']][:2]
    links=''.join(f'<a href="{esc(x["href"])}">{esc(x["topic"])} <span aria-hidden="true">↗</span></a>' for x in more)
    return f'''<div class="cw-edition" data-cw-edition="{e['id']}" data-header-theme="light">
<header class="cw-edition-head" id="top"><div class="cw-wrap"><nav class="cw-breadcrumb" aria-label="Breadcrumb"><ol><li><a href="creative-writing.html#archive">Creative Writing</a></li><li><span aria-current="page">{esc(e['topic'])}</span></li></ol></nav>
<h1>{esc(e['topic'])}</h1><p class="cw-edition-intro">{esc(e['intro'])}</p><p class="cw-edition-facts">{esc(facts)}</p>{downloads_html(e)}</div></header>
<section class="cw-contents-section cw-wrap" id="contents" aria-label="Edition contents"><details class="cw-mobile-contents" data-cw-contents open><summary>Contents <span>{plural(len(poems),'poem')}</span></summary>{contents_list(e)}</details></section>
<div class="cw-reader cw-wrap"><aside class="cw-rail"><nav aria-label="Poem contents"><a class="cw-back" href="creative-writing.html#archive">All Writing</a><p class="cw-rail-title">{esc(e['topic'])}</p>{contents_list(e,True)}</nav></aside><div class="cw-poems">{''.join(articles)}</div></div>
<nav class="cw-more cw-wrap" aria-label="More editions"><p class="cw-meta">Continue reading</p>{links}<a href="creative-writing.html#archive">Explore the collection <span aria-hidden="true">↗</span></a></nav></div>'''

def empty_route_html(route):
    school=data()['schools'][route['collection']]['name']
    return f'''<div class="cw-edition cw-empty-route" data-header-theme="light"><div class="cw-wrap"><nav class="cw-breadcrumb" aria-label="Breadcrumb"><ol><li><a href="creative-writing.html#archive">Creative Writing</a></li><li>{esc(school)}</li></ol></nav>
<h1>No published edition at this address.</h1><p>This monthly address has no published poems. Browse the available collection instead.</p>
<div class="cw-empty-actions"><a class="cw-read" href="creative-writing.html#archive">Browse All Writing <span aria-hidden="true">↗</span></a><a href="creative-writing/{route['collection']}.html#archive">Visit {esc(school)}</a></div></div></div>'''

def page_entries():
    base=dict(sheet='cwriting',banner=None,jump=False,uc=False,cache_suffix='-literary-2')
    out={}
    for key in SCHOOLS:
        name=data()['schools'][key]['name']
        out[f'creative-writing/{key}']=dict(base,nav=name+' Creative Writing',litehead=True,title=name+' Creative Writing | CIRS',description=f'Published poems by {name} students at CIRS.',cw=dict(kind='main',collection=key))
    for e in editions():
        out[e['path']]=dict(base,nav=e['topic'],litehead=True,title=esc(e['topic']+' | Creative Writing | CIRS'),description=esc(e['intro']),cw=dict(kind='edition',edition=e['id']))
    for route in data()['legacyRoutes']:
        out[route['path']]=dict(base,nav='Creative Writing archive',litehead=True,title='Creative Writing archive | CIRS',description='Find the published CIRS Creative Writing collection.',cw=dict(kind='empty',route=route))
    return out

def render(spec):
    if spec['kind']=='main': return main_html(spec['collection'])
    if spec['kind']=='empty': return empty_route_html(spec['route'])
    return edition_html(next(e for e in editions() if e['id']==spec['edition']))
def head_html(spec): return '<meta name="color-scheme" content="light">\n'
if __name__=='__main__':
    for e in editions(): print(f'{e["path"]}: {plural(len(e["poems"]),"poem")}')
    print(stats_line('all'))
