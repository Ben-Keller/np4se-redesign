import json,re,os,collections
from bs4 import BeautifulSoup
d=json.load(open('migration/source/wp_export.json')); sg=json.load(open('migration/source/singles.json'))
UP='https://www.newproducersgroup.org/wp-content/uploads/'
refs=collections.OrderedDict()
def add(u,why):
    if not u: return
    u=u.strip().strip("'\"").split('?')[0]
    if u.startswith('/wp-content'): u='https://www.newproducersgroup.org'+u
    if not u.startswith(UP): return
    if not re.search(r'\.(jpe?g|png|gif|webp)$',u,re.I): return
    refs.setdefault(u,set()).add(why)
SKIP_ICONS=re.compile(r'/2020/11/(icon-\d|Members-area-icon|Learn-more|Support-what-we-do|Our-Values-icon\d?|Annual-Meeting-icon|calander-icon2|Training-Sessions-icon)\.png$')
for p in d['pages']:
    s=BeautifulSoup(p['html'],'lxml')
    for i in s.find_all('img'): add(i.get('src'),'page:'+p['slug'])
    for el in s.find_all(style=True):
        for u in re.findall(r'url\(([^)]+)\)',el['style']): add(u,'pagebg:'+p['slug'])
    for cls,u in re.findall(r'\.(vc_custom_\d+)\{[^}]*?background-image:\s*url\(([^)]+)\)',p.get('css','')): add(u,'vcbg:'+p['slug'])
for p in d['posts']:
    s=BeautifulSoup(p['content']['rendered'],'lxml')
    for i in s.find_all('img'): add(i.get('src'),'post:'+p['slug'])
for x in sg['posts']: add(x.get('feat'),'feat:'+x['slug'])
for x in sg['events']: add(x.get('feat'),'evfeat:'+x['slug'])
for e in d['events']:
    add(e.get('img'),'evimg:'+e['slug'])
    for u in re.findall(r'url\(([^)]+)\)',e.get('banner','')): add(u,'evbanner:'+e['slug'])
    s=BeautifulSoup(e['content'],'lxml')
    for i in s.find_all('img'): add(i.get('src'),'evbody:'+e['slug'])
impact=['2026/02/Screenshot-2026-02-03-at-12.37.34-PM-1024x916.png','2026/02/Screenshot-2026-02-03-at-12.43.26-PM-1024x895.png','2026/02/Screenshot-2026-02-03-at-11.32.22-AM-1024x906.png','2026/02/Screenshot-2026-02-03-at-12.05.28-PM-1024x896.png','2026/02/Screenshot-2026-02-03-at-11.30.48-AM-1024x888.png','2026/02/Screenshot-2026-02-03-at-11.28.53-AM-1024x889.png','2026/02/Screenshot-2026-02-03-at-12.58.02-PM.png','2026/02/Screenshot-2026-02-02-at-5.47.51-PM.png','2026/02/Screenshot-2026-02-02-at-5.48.04-PM.png','2026/02/Screenshot-2026-02-02-at-5.50.37-PM.png','2026/02/Screenshot-2026-02-02-at-5.51.03-PM.png','2026/02/Screenshot-2026-02-03-at-10.29.36-AM-1024x352.png']
for u in impact: add(UP+u,'impact')
med={m['id']:m for m in d['media']}
for sl in d['sliders']:
    if sl.get('featured_media') and sl['featured_media'] in med: add(med[sl['featured_media']]['url'],'slider')
# drop old decorative icons and old logo
refs={u:w for u,w in refs.items() if not SKIP_ICONS.search(u) and 'NP4SE_Logo' not in u}
# map to media records for size selection
byurl={}
for m in d['media']:
    byurl[m['url']]=(m,'full')
    for k,(su,w,h) in (m.get('sizes') or {}).items(): byurl[su]=(m,k)
def base_of(u):  # strip -WxH and -scaled / -eNNN variants to find parent
    return re.sub(r'-\d+x\d+(?=\.\w+$)','',u)
plan=[]
for u,why in refs.items():
    m,k = byurl.get(u,(None,None))
    if m is None:
        b=base_of(u); m,k=byurl.get(b,(None,None))
    choice=u; w=h=None
    if m:
        cands=[(m['url'],m.get('w'),m.get('h'))]+[tuple(v) for v in (m.get('sizes') or {}).values()]
        cands=[c for c in cands if c[1]]
        # pick smallest candidate with width>=1600 else largest; but never upscale beyond referenced
        want=1600 if any(x.startswith(('vcbg','pagebg','evbanner','slider','feat','evfeat','evimg')) for x in why) else 1200
        if any('page:about-us' in x for x in why) and ('150x' in u or '-150x150' in u): want=300
        good=sorted([c for c in cands if c[1]>=want], key=lambda c:c[1])
        pick = good[0] if good else max(cands,key=lambda c:c[1])
        choice,w,h=pick
    plan.append({'ref':u,'src':choice,'w':w,'h':h,'why':sorted(why)})
json.dump(plan,open('migration/source/image_plan.json','w'),indent=1)
print(len(plan),'images;', sum(1 for p in plan if p['w']), 'matched to media')
est=0
mm={m['url']:m for m in d['media']}
for p in plan[:8]: print(p['ref'][-60:],'->',p['src'][-50:],p['w'],p['why'][:2])
