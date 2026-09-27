import json,sys,re
from bs4 import BeautifulSoup, NavigableString
d=json.load(open('migration/source/wp_export.json'))
def outline(html, maxlen=100000):
    s=BeautifulSoup(html,'lxml')
    out=[]
    def walk(el,depth=0):
        for c in el.children:
            if isinstance(c,NavigableString):
                t=str(c).strip()
                if t and el.name in ('div','section','td','span','body','html','li') and len(t)>1: out.append('  '*0+'TXT: '+re.sub(r'\s+',' ',t)[:600])
                continue
            n=c.name
            if n in ('h1','h2','h3','h4','h5','h6'): out.append(f'{n.upper()}: '+c.get_text(' ',strip=True)[:300]); continue
            if n=='p':
                t=c.get_text(' ',strip=True)
                imgs=c.find_all('img'); links=[(a.get_text(' ',strip=True)[:60],a.get('href')) for a in c.find_all('a')]
                if t: out.append('P: '+t[:1200])
                for i in imgs: out.append(f'IMG: {i.get("src","")} alt="{i.get("alt","")}"')
                for lt,h in links:
                    if h and ('pdf' in h.lower() or not t or len(links)<4): out.append(f'  LINK: [{lt}] {h}')
                continue
            if n in ('ul','ol'):
                for li in c.find_all('li',recursive=False): out.append('LI: '+li.get_text(' ',strip=True)[:400]+ (' -> '+li.a.get('href') if li.a and li.a.get('href') else ''))
                continue
            if n=='img': out.append(f'IMG: {c.get("src","")} alt="{c.get("alt","")}"'); continue
            if n=='a':
                t=c.get_text(' ',strip=True); out.append(f'A: [{t[:80]}] {c.get("href")}'); 
                for i in c.find_all('img'): out.append(f'  IMG: {i.get("src","")}')
                continue
            if n in ('iframe','object','video','form'): out.append(f'{n.upper()}: {c.get("src") or c.get("data") or c.get("action")}'); 
            if n=='table':
                for tr in c.find_all('tr'): out.append('TR: '+' | '.join(td.get_text(' ',strip=True)[:120] for td in tr.find_all(['td','th'])))
                continue
            cls=c.get('class') or []
            st=c.get('style','')
            if 'background' in st:
                urls=re.findall(r"url\(([^)]+)\)",st); out.append('BG: '+str(urls))
            if any(x for x in cls if not x.startswith(('vc_col','wpb_','vc_column','vc_row','vc_inner','vc_custom'))) and n in ('div','section') and len(out)<100000:
                interesting=[x for x in cls if x not in ('container','row','wpb_wrapper','vc_column-inner','clearfix')]
                if interesting and any(k in ' '.join(interesting) for k in ['Banner','Section','box','Box','team','Team','slider','Slider','card','Card','member','Member','tab','Tab','accordion','Accordion','map','Map','partner','Partner','logo','Logo','impact','Impact','count','Count','quote','Quote','btn','Btn']):
                    out.append(f'--DIV.{".".join(interesting[:4])}')
            walk(c,depth+1)
    walk(s)
    return '\n'.join(out)
which=sys.argv[1:]
for p in d['pages']:
    if which and p['slug'] not in which: continue
    print(f"\n######## PAGE {p['slug']} | {p['title']} | {p['link']} | tmpl={p['template']}")
    print('DESC:',p.get('desc','')[:300]); print('OG:',p.get('ogimg',''))
    bgs=re.findall(r'\.(vc_custom_\d+)\{[^}]*?background-image:\s*url\(([^)]+)\)',p.get('css',''))
    if bgs: print('VCBG:',bgs[:12])
    print(outline(p['html']))
