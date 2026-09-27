#!/usr/bin/env python3
"""Turn the raw WordPress export into clean, editable content files.

Inputs (migration/source/): wp_export.json, listing_meta.json, singles.json, image_keys.json, image_dims.json
Outputs (content/): publications/*.md, events/*.md, countries/*.md, data/*.yaml
Run once during migration; afterwards the content/ folder is the source of truth.
"""
import sys as _sys
if '--force' not in _sys.argv:
    raise SystemExit('This one-off script rebuilt content/ from the WordPress export on 27 September 2026.\n'
                     'Re-running it overwrites every hand edit in content/. Add --force only if that is what you want.')
import json, re, html, os, datetime, collections, unicodedata
import yaml
from bs4 import BeautifulSoup, Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
S = lambda *p: os.path.join(ROOT, *p)
d  = json.load(open(S('migration/source/wp_export.json')))
lm = json.load(open(S('migration/source/listing_meta.json')))
sg = json.load(open(S('migration/source/singles.json')))
IK = json.load(open(S('migration/source/image_keys.json')))
DIMS = json.load(open(S('migration/source/image_dims.json')))
REFMAP = IK['refmap']                      # original url -> webp key
SRC2KEY = {it['u']: it['k'] for it in IK['items']}
OLD = 'https://www.newproducersgroup.org'
UP = OLD + '/wp-content/uploads/'

def clean_text(s):
    s = html.unescape(s or '')
    s = s.replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'\s+([,.;:!?)](?:\s|$))', r'\1', s)

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def local_img(url):
    """Map an uploads URL (any size variant) to our local webp path, or None."""
    if not url: return None
    u = url.strip().strip('\'"').split('?')[0]
    if u.startswith('/wp-content'): u = OLD + u
    k = REFMAP.get(u) or SRC2KEY.get(u)
    if not k:
        base = re.sub(r'-\d+x\d+(?=\.\w+$)', '', u)
        k = REFMAP.get(base) or SRC2KEY.get(base)
        if not k:
            for ref, key in REFMAP.items():
                if re.sub(r'-\d+x\d+(?=\.\w+$)', '', ref) == base: k = key; break
    return ('/assets/img/wp/' + k) if k else None

# ---------- URL mapping old -> new ----------
page_links = {p['link'].rstrip('/').lower(): p['slug'] for p in d['pagesIdx']}
GET_INVOLVED_ANCHORS = {'1605957303133-0c960d0d-9285': 'member', '1605957303149-4de76300-64c9': 'sponsor', '1606130266293-4a2d8ce4-fe8b': 'partner'}
SPECIAL = {
    '/map-4': '/members/', '/sa%cc%83o-tome-e-principe': '/sao-tome-e-principe/', '/namibia': '/namibia/',
    '/new-home': '/', '/event': '/activities-and-events/', '/npg/get-involved': '/get-involved/',
}
def map_url(href):
    """Return new root-relative URL for internal links; keep external and uploads (PDFs) absolute."""
    if not href: return href
    h = html.unescape(href.strip())
    if h.startswith(('mailto:', 'tel:', '#')): return h
    if h.startswith('/') and not h.startswith('//'): h = OLD + h
    if not re.match(r'https?://(www\.)?newproducersgroup\.org', h, re.I): return h
    if '/wp-content/uploads/' in h:
        li = local_img(h)
        if li and re.search(r'\.(jpe?g|png|gif|webp)$', h.split('?')[0], re.I): return li
        return re.sub(r'^http://', 'https://', h)            # PDFs etc. stay on the current site
    path, _, frag = re.sub(r'^https?://(www\.)?newproducersgroup\.org', '', h, flags=re.I).partition('#')
    path = path.split('?')[0].rstrip('/').lower() or '/'
    if frag in GET_INVOLVED_ANCHORS: frag = GET_INVOLVED_ANCHORS[frag]
    if path in SPECIAL: new = SPECIAL[path]
    elif path == '/': new = '/'
    elif path.startswith('/event-tag/'): new = '/tag/' + path.split('/')[2] + '/'
    elif path.startswith('/events/'): new = '/category/' + path.split('/')[2] + '/'
    else: new = path + '/'
    new = re.sub(r'/page/\d+/$', '/', new)
    return new + ('#' + frag if frag else '')

# ---------- HTML cleaner for post/event bodies ----------
DROP_TEXT = re.compile(r'\[DISPLAY_ULTIMATE_SOCIAL_ICONS\]|\[/?vc_[^\]]*\]')
def clean_body(raw, docs_out=None):
    s = BeautifulSoup(raw or '', 'lxml')
    body = s.body or s
    for c in body.find_all(string=lambda t: isinstance(t, Comment)): c.extract()
    for el in body.find_all(['script', 'style', 'noscript', 'form']): el.decompose()
    # wp-block-file: object embed + button -> single download link
    for fb in body.select('.wp-block-file'):
        a = fb.find('a', href=re.compile(r'\.pdf', re.I))
        if a and docs_out is not None:
            btn = fb.find('a', class_=re.compile('wp-block-file__button'))
            docs_out.append({'label': (clean_text(btn.get_text()) if btn else '') or 'Download', 'url': map_url(a['href'])})
        fb.decompose()
    for ob in body.find_all('object'): ob.decompose()
    # iframes -> figure.embed (template decides iframe vs link)
    for fr in body.find_all('iframe'):
        src = html.unescape(fr.get('src', ''))
        m = re.search(r'youtube\.com/embed/([\w-]+)', src); v = re.search(r'vimeo\.com/video/(\d+)', src)
        if m: url, prov = 'https://www.youtube.com/watch?v=' + m.group(1), 'YouTube'
        elif v: url, prov = 'https://vimeo.com/' + v.group(1), 'Vimeo'
        else: url, prov = src, 'video'
        fig = s.new_tag('figure', attrs={'class': 'embed', 'data-embed': src.split('?')[0] + ('?dnt=1' if v else ''), 'data-watch': url, 'data-provider': prov})
        fr.replace_with(fig)
    # images -> local
    for im in body.find_all('img'):
        li = local_img(im.get('src'))
        if li:
            k = li.split('/')[-1]; w, h = DIMS.get(k, [None, None])
            im.attrs = {'src': li, 'alt': clean_text(im.get('alt', '')), 'loading': 'lazy'}
            if w: im['width'], im['height'] = str(w), str(h)
        else: im.decompose()
    for a in body.find_all('a'):
        href = a.get('href')
        attrs = {'href': map_url(href)} if href else {}
        if href and re.match(r'https?://', attrs.get('href', '')) and 'newproducersgroup.org/wp-content' not in attrs['href']:
            attrs['rel'] = 'noopener'
        a.attrs = attrs
        if not a.get_text(strip=True) and not a.find('img'): a.unwrap()
    KEEP = {'href', 'src', 'alt', 'width', 'height', 'loading', 'colspan', 'rowspan', 'class', 'data-embed', 'data-watch', 'data-provider', 'rel'}
    for el in body.find_all(True):
        for k in list(el.attrs):
            if k not in KEEP: del el.attrs[k]
        if el.name not in ('figure',) and 'class' in el.attrs: del el.attrs['class']
    for sp in body.find_all(['span', 'font']): sp.unwrap()
    for h1 in body.find_all('h1'): h1.name = 'h2'
    out = body.decode_contents() if hasattr(body, 'decode_contents') else str(body)
    out = DROP_TEXT.sub('', out)
    out = re.sub(r'<p>(\s|&nbsp;|<br/?>)*</p>', '', out)
    out = re.sub(r'\n{2,}', '\n', out).replace('\xa0', ' ').strip()
    return out

def first_text(html_str, n=240):
    t = clean_text(BeautifulSoup(html_str or '', 'lxml').get_text(' '))
    t = re.sub(r'\s*\[(…|&hellip;|\.\.\.)\]\s*$', '', t)
    if len(t) <= n: return t
    cut = t[:n]; dot = cut.rfind('. ')
    return (cut[:dot + 1] if dot > n * 0.5 else cut.rsplit(' ', 1)[0] + '…')

MONTHS = {m: i for i, m in enumerate(['january','february','march','april','may','june','july','august','september','october','november','december'], 1)}
MON3 = {k[:3]: v for k, v in MONTHS.items()}
def month_num(tok):
    t = tok.lower().strip('.,')
    return MONTHS.get(t) or MON3.get(t[:3])
MNAME = ['', 'January','February','March','April','May','June','July','August','September','October','November','December']

# ---------- taxonomies ----------
cats = {c['id']: c for c in d['categories']}
tags = {t['id']: t for t in d['tags']}
ecats = {c['id']: c for c in d['ecats']}
etags = {t['id']: t for t in d['etags']}
THEME_NAMES = {'capacity': 'Building capacity', 'energy-transition': 'Energy transition', 'fostering-resilience': 'Fostering resilience',
               'new-path': 'New Path', 'overarching-issues': 'Overarching issues', 'socio-economic-returns': 'Socio-economic returns',
               'strategic-vision': 'Strategic vision', 'trust-accountability': 'Trust and accountability', 'emissions': 'Emissions'}
topic_names = {}
for t in list(d['tags']) + list(d['etags']):
    nm = clean_text(t['name'])
    if t['slug'] not in topic_names or (nm[:1].isupper() and not topic_names[t['slug']][:1].isupper()): topic_names[t['slug']] = nm

# ---------- members (from the home page list, colours = sector stage) ----------
STAGE = {'#0cb567': 'Frontier', '#ff6e49': 'Development of significant discoveries', '#0c6ab5': 'Production'}
home = next(p for p in d['pages'] if p['slug'] == 'new-home')
hs = BeautifulSoup(home['html'], 'lxml')
h5s = hs.find_all('h5')
def spans_with_stage(h5):
    out = {}
    for sp in h5.find_all(['span', 'a']):
        t = clean_text(sp.get_text()).replace('(observer)', '').replace('*', '').strip()
        st = re.search(r'color:\s*(#[0-9a-f]{6})', sp.get('style', ''), re.I)
        if t and st and st.group(1).lower() in STAGE and len(t) < 30 and '\n' not in t:
            out[t] = STAGE[st.group(1).lower()]
    return out
stage_members = spans_with_stage(h5s[0]); stage_peers = spans_with_stage(h5s[1])

REGION = {
 'car': ('Caribbean & Latin America', ['Bahamas','Barbados','Belize','Guyana','Suriname','Uruguay']),
 'wa':  ('West Africa', ['Ghana','Guinea','Liberia','Mauritania','Senegal','Sierra Leone']),
 'ces': ('Central, East & Southern Africa', ['DR Congo','Mozambique','Namibia','São Tomé e Príncipe','Somalia','Tanzania','Uganda']),
 'mea': ('Middle East & Asia-Pacific', ['Lebanon','Papua New Guinea','Timor-Leste']),
}
ATLAS = {'Bahamas':'044','Barbados':'','Belize':'084','Guyana':'328','Suriname':'740','Uruguay':'858','Ghana':'288','Guinea':'324','Liberia':'430',
 'Mauritania':'478','Senegal':'686','Sierra Leone':'694','DR Congo':'180','Mozambique':'508','Namibia':'516','São Tomé e Príncipe':'','Somalia':'706',
 'Tanzania':'834','Uganda':'800','Lebanon':'422','Papua New Guinea':'598','Timor-Leste':'626','Angola':'024','Brazil':'076','Indonesia':'360','Norway':'578','Kenya':'404'}
CAPITAL = {'Bahamas':('Nassau',-77.35,25.06),'Barbados':('Bridgetown',-59.62,13.10),'Belize':('Belmopan',-88.77,17.25),'Guyana':('Georgetown',-58.16,6.80),
 'Suriname':('Paramaribo',-55.17,5.85),'Uruguay':('Montevideo',-56.16,-34.90),'Ghana':('Accra',-0.19,5.60),'Guinea':('Conakry',-13.71,9.64),
 'Liberia':('Monrovia',-10.80,6.30),'Mauritania':('Nouakchott',-15.98,18.08),'Senegal':('Dakar',-17.44,14.69),'Sierra Leone':('Freetown',-13.23,8.48),
 'DR Congo':('Kinshasa',15.31,-4.32),'Mozambique':('Maputo',32.58,-25.97),'Namibia':('Windhoek',17.08,-22.56),'São Tomé e Príncipe':('São Tomé',6.73,0.34),
 'Somalia':('Mogadishu',45.34,2.05),'Tanzania':('Dodoma',35.74,-6.17),'Uganda':('Kampala',32.58,0.35),'Lebanon':('Beirut',35.50,33.89),
 'Papua New Guinea':('Port Moresby',147.18,-9.44),'Timor-Leste':('Dili',125.58,-8.56),'Angola':('Luanda',13.23,-8.84),'Brazil':('Brasília',-47.88,-15.79),
 'Indonesia':('Jakarta',106.85,-6.21),'Norway':('Oslo',10.75,59.91),'Kenya':('Nairobi',36.82,-1.29)}
OBSERVERS = {'Papua New Guinea', 'Senegal', 'Timor-Leste'}
COUNTRY_SLUG = {'DR Congo': 'democratic-republic-of-congo', 'São Tomé e Príncipe': 'sao-tome-e-principe'}
# names used by the old site's hidden country filter / tags
ALIASES = {'DR Congo': ['Democratic Republic of Congo', 'drc'], 'São Tomé e Príncipe': ['São Tomé and Príncipe', 'sao-tome-and-principe'], 'Timor-Leste': ['timor-leste']}
# Unsplash photos from the design round, used where the old site has no photo of the country
UNSPLASH = {'Ghana': ('fishers', 'Elmina, Ghana'), 'Suriname': ('river', 'Boven Suriname, Suriname'), 'Namibia': ('dunes', 'Namib coast, Namibia'),
 'Uganda': ('crater-lake', 'Uganda'), 'Mozambique': ('palm-beach', 'Mozambique'), 'Senegal': ('dakar-boats', 'Île de Gorée, Dakar'),
 'Tanzania': ('dar-skyline', 'Dar es Salaam, Tanzania'), 'Lebanon': ('beirut', 'Beirut, Lebanon'), 'Timor-Leste': ('timor-coast', 'Adara, Timor-Leste')}
REGION_PHOTO = {'car': ('river', 'Boven Suriname, Suriname'), 'wa': ('boats-color', 'Elmina, Ghana'), 'ces': ('dunes', 'Namib coast, Namibia'), 'mea': ('timor-coast', 'Adara, Timor-Leste')}

country_pages = {p['slug']: p for p in d['pages'] if p['template'] in ('', 'templates/template-full-width.php') and p['title'] in
                 [*CAPITAL.keys(), 'Democratic Republic of Congo', 'São Tomé e Príncipe', 'Kenya']}

members = []
for rk, (rname, names) in REGION.items():
    for n in names:
        slug = COUNTRY_SLUG.get(n, slugify(n))
        cap = CAPITAL[n]
        members.append({'name': n, 'slug': slug, 'region': rk, 'role': 'observer' if n in OBSERVERS else 'member',
                        'stage': stage_members.get(n, stage_members.get(n.replace(' e ', ' and '), '')), 'legacy_production': n == 'Suriname',
                        'atlas_id': ATLAS[n], 'capital': cap[0], 'lon': cap[1], 'lat': cap[2]})
peers = [{'name': n, 'slug': slugify(n), 'region': 'peer', 'role': 'peer', 'stage': stage_peers.get(n, 'Production'),
          'atlas_id': ATLAS[n], 'capital': CAPITAL[n][0], 'lon': CAPITAL[n][1], 'lat': CAPITAL[n][2]} for n in ['Brazil', 'Indonesia', 'Norway', 'Angola']]
for mm in members:
    if not mm['stage']: print('WARN no stage', mm['name'])

# ---------- publications ----------
pub_meta = {p['href'].rstrip('/').split('/')[-1]: p for p in lm['pubList']}
single_p = {x['slug']: x for x in sg['posts']}
pub_countries = collections.defaultdict(set)
for c, hrefs in lm['pubByCountry'].items():
    for h in hrefs: pub_countries[h.rstrip('/').split('/')[-1]].add(c)
pub_format = collections.defaultdict(list)
for t, hrefs in lm['pubByType'].items():
    for h in hrefs: pub_format[h.rstrip('/').split('/')[-1]].append(t.capitalize())
media_by_id = {mm['id']: mm for mm in d['media']}

def canon_country(name):
    for mm in members + peers:
        if name == mm['name'] or name in ALIASES.get(mm['name'], []): return mm['name']
    return {'Ivory Coast': "Côte d'Ivoire"}.get(name, name)

def countries_from_tags(slugs):
    out = set()
    for s in slugs:
        for mm in members + peers + [{'name': 'Kenya', 'slug': 'kenya'}]:
            if s == mm['slug'] or s in ALIASES.get(mm['name'], []) or s == slugify(mm['name']): out.add(mm['name'])
        if s == 'drc': out.add('DR Congo')
    return out

os.makedirs(S('content/publications'), exist_ok=True)
pubs = []
for p in d['posts']:
    slug = p['slug']; lmp = pub_meta.get(slug, {}); sx = single_p.get(slug, {})
    left = (lmp.get('left') or '').replace('\xa0', ' ')
    ptype = re.sub(r'\s*\d{4}\s*$', '', left).strip() or 'Article'
    hdr = sx.get('hdr') or []
    disp = hdr[0] if hdr and re.match(r'^[A-Z][a-z]{2} \d{4}$', hdr[0]) else ''
    if disp:
        mo, yr = disp.split(); date = f"{yr}-{MON3[mo.lower()]:02d}"
    else:
        date = p['date'][:7]; disp = datetime.date(int(date[:4]), int(date[5:]), 1).strftime('%b %Y')
    authors = clean_text(lmp.get('authors') or (hdr[1] if len(hdr) > 1 else ''))
    docs = []
    body = clean_body(p['content']['rendered'], docs)
    for lab, url in sx.get('docLinks', []):
        u = map_url(url)
        if u and all(u != x['url'] for x in docs): docs.append({'label': lab, 'url': u})
    img = local_img(sx.get('feat')) or (local_img(media_by_id[p['featured_media']]['url']) if p.get('featured_media') in media_by_id else None)
    themes = [cats[c]['slug'] for c in p['categories'] if c in cats and cats[c]['slug'] != 'uncategorized']
    topics = [tags[t]['slug'] for t in p['tags'] if t in tags]
    ctry = sorted({canon_country(c) for c in pub_countries.get(slug, set())} | countries_from_tags(topics))
    summary = first_text(p['excerpt']['rendered'] if p.get('excerpt') else body, 260)
    fm = {'title': clean_text(p['title']['rendered']), 'slug': slug, 'date': date, 'date_display': disp, 'type': ptype,
          'formats': sorted(pub_format.get(slug, [])), 'authors': authors or None, 'themes': themes, 'topics': topics, 'countries': ctry,
          'image': img, 'summary': summary, 'documents': docs, 'legacy_url': p['link']}
    pubs.append(fm)
    with open(S('content/publications', slug + '.md'), 'w') as f:
        f.write('---\n' + yaml.safe_dump({k: v for k, v in fm.items() if v not in (None, [], '')}, sort_keys=False, allow_unicode=True, width=1000) + '---\n' + body + '\n')

# ---------- events ----------
ev_list = {e['href'].rstrip('/').split('/')[-1]: e for e in lm['evList']}
single_e = {x['slug']: x for x in sg['events']}
ev_countries = collections.defaultdict(set)
for c, hrefs in lm['evByCountry'].items():
    for h in hrefs: ev_countries[h.rstrip('/').split('/')[-1]].add(c)
ev_type = collections.defaultdict(list)
for t, hrefs in lm['evByType'].items():
    for h in hrefs: ev_type[h.rstrip('/').split('/')[-1]].append(t.capitalize())

def parse_event_dates(li_date, left, fallback):
    """li_date like '15 May, 2026' is the true start; left like '27-8 July 2022' carries the end."""
    start = None
    if li_date:
        mt = re.match(r'(\d{1,2}) ([A-Za-z]{3,})\.?,? (\d{4})', li_date.strip())
        if mt: start = datetime.date(int(mt.group(3)), month_num(mt.group(2)), int(mt.group(1)))
    end = None
    if left:
        mt = re.match(r'(\d{1,2})(?:-(\d{1,2}))? ([A-Za-z]+) (\d{4})', left.strip())
        if mt:
            yr, mo = int(mt.group(4)), month_num(mt.group(3))
            d1, d2 = int(mt.group(1)), int(mt.group(2) or mt.group(1))
            end = datetime.date(yr, mo, d2)
            if not start:
                start = datetime.date(yr, mo, d1) if d1 <= d2 else (datetime.date(yr, mo, 1) - datetime.timedelta(days=1)).replace(day=d1)
    if not start: start = datetime.date.fromisoformat(fallback[:10])
    if not end or end < start: end = start
    if (end - start).days > 60: end = start          # guard against malformed ranges
    if start == end: disp = f"{start.day} {MNAME[start.month]} {start.year}"
    elif start.month == end.month and start.year == end.year: disp = f"{start.day}–{end.day} {MNAME[start.month]} {start.year}"
    elif start.year == end.year: disp = f"{start.day} {MNAME[start.month]} – {end.day} {MNAME[end.month]} {start.year}"
    else: disp = f"{start.day} {MNAME[start.month]} {start.year} – {end.day} {MNAME[end.month]} {end.year}"
    return start, end, disp

os.makedirs(S('content/events'), exist_ok=True)
events = []
for e in d['events']:
    slug = e['slug']; li = dict((k, v) for k, v in (e.get('li') or []))
    start, end, disp = parse_event_dates(li.get('date'), (ev_list.get(slug) or {}).get('left'), e['date'])
    docs = []
    body = clean_body(e['content'], docs)
    sx = single_e.get(slug, {})
    for u in sx.get('allDocs', []):
        u2 = map_url(u)
        if all(u2 != x['url'] for x in docs):
            lab = 'Download document' if u2.lower().endswith('.pdf') else 'Read more'
            docs.append({'label': lab, 'url': u2})
    img = local_img(e.get('img')) or local_img(sx.get('feat'))
    themes = [ecats[c]['slug'] for c in e.get('tribe_events_cat', []) if c in ecats]
    topics = [etags[t]['slug'] for t in e.get('event_tag', []) if t in etags]
    ctry = sorted({canon_country(c) for c in ev_countries.get(slug, set())} | countries_from_tags(topics))
    time = li.get('tim', '').strip() or None
    fm = {'title': clean_text(e['title']), 'slug': slug, 'date_start': start.isoformat(), 'date_end': end.isoformat(), 'date_display': disp,
          'time': time, 'types': sorted(ev_type.get(slug, [])), 'themes': themes, 'topics': topics, 'countries': ctry, 'image': img,
          'image_caption': clean_text(e.get('cap')) or None, 'summary': first_text(body, 260), 'documents': docs, 'legacy_url': e['link']}
    events.append(fm)
    with open(S('content/events', slug + '.md'), 'w') as f:
        f.write('---\n' + yaml.safe_dump({k: v for k, v in fm.items() if v not in (None, [], '')}, sort_keys=False, allow_unicode=True, width=1000) + '---\n' + body + '\n')

# ---------- countries: curated resources from the old country pages ----------
os.makedirs(S('content/countries'), exist_ok=True)
def country_page_for(name):
    for p in d['pages']:
        t = clean_text(p['title'])
        if t == name or (name == 'DR Congo' and t == 'Democratic Republic of Congo') or (name == 'São Tomé e Príncipe' and 'Tom' in t): return p
    return None
def banner_from_css(p):
    m = re.findall(r'\.(vc_custom_\d+)\{[^}]*?background-image:\s*url\(([^)]+)\)', p.get('css', ''))
    for cls, u in m:
        if 'banner-img-1' in u: continue
        li = local_img(u)
        if li: return li
    return None
all_countries = members + [{'name': 'Kenya', 'slug': 'kenya', 'region': 'ces', 'role': 'former', 'stage': '', 'atlas_id': '404',
                            'capital': 'Nairobi', 'lon': 36.82, 'lat': -1.29}]
for c in all_countries:
    p = country_page_for(c['name'])
    items = []
    banner = None
    if p:
        banner = banner_from_css(p)
        sp = BeautifulSoup(p['html'], 'lxml')
        for para in sp.find_all('p'):
            a = para.find('a')
            txt = clean_text(para.get_text(' '))
            if not txt: continue
            if a and a.get('href'):
                title = clean_text(a.get_text(' '))
                blurb = clean_text(txt.replace(title, '', 1))
                items.append({'title': title.rstrip(':'), 'url': map_url(a['href']), 'text': blurb})
            elif items:
                items[-1]['text'] = (items[-1]['text'] + ' ' + txt).strip()
    c['banner'] = banner
    c['has_legacy_page'] = bool(p)
    photo = UNSPLASH.get(c['name'])
    c['photo'] = ('/assets/img/photos/' + photo[0] + '.jpg') if photo else None
    c['photo_caption'] = photo[1] if photo else None
    with open(S('content/countries', c['slug'] + '.md'), 'w') as f:
        fm = {'name': c['name'], 'slug': c['slug'], 'resources': items}
        if p: fm['legacy_url'] = p['link']
        f.write('---\n' + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000) + '---\n')

# ---------- data files ----------
os.makedirs(S('content/data'), exist_ok=True)
def dump(name, obj):
    with open(S('content/data', name), 'w') as f: yaml.safe_dump(obj, f, sort_keys=False, allow_unicode=True, width=1000)

dump('members.yaml', {'regions': {k: {'name': v[0], 'photo': '/assets/img/photos/' + REGION_PHOTO[k][0] + '.jpg', 'photo_caption': REGION_PHOTO[k][1]} for k, v in REGION.items()},
                      'members': [{k: v for k, v in c.items()} for c in all_countries], 'peers': peers,
                      'stages': ['Frontier', 'Development of significant discoveries', 'Production'],
                      'stage_note': 'Suriname: marginal legacy production'})
dump('themes.yaml', [{'slug': k, 'name': v} for k, v in THEME_NAMES.items()])
dump('topics.yaml', [{'slug': k, 'name': v} for k, v in sorted(topic_names.items())])

# country list for form selects (from the old contact form)
cp = next(p for p in d['pages'] if p['slug'] == 'contact-us')
sel = BeautifulSoup(cp['html'], 'lxml').find('select', attrs={'name': 'Country'})
dump('countries_list.yaml', [clean_text(o.get_text()) for o in sel.find_all('option')][1:])

print('publications', len(pubs), 'events', len(events), 'countries', len(all_countries))
print('types', collections.Counter(p['type'] for p in pubs))
print('pubs without image', [p['slug'] for p in pubs if not p['image']])
print('events without image', [e['slug'] for e in events if not e['image']])
print('events types', collections.Counter(t for e in events for t in e['types']), 'untyped', sum(1 for e in events if not e['types']))
print('sample event dates', [(e['slug'][:30], e['date_display']) for e in events[:6]])
print('country resources', {c['slug']: len(yaml.safe_load(open(S('content/countries', c['slug'] + '.md')).read().split('---')[1])['resources']) for c in all_countries})
