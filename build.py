#!/usr/bin/env python3
"""Build the NP4SE website from content/ + templates/ + assets/.

    python3 build.py              production build into dist/  (root-relative links, deploy anywhere)
    python3 build.py --preview    self-contained preview into preview/ (relative links, no form posts)

Requires Python 3.9+ with PyYAML, Jinja2, BeautifulSoup4 and Pillow:
    pip install pyyaml jinja2 beautifulsoup4 pillow
"""
import argparse, datetime, html, json, math, re, shutil, sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString
from jinja2 import ChainableUndefined, Environment, FileSystemLoader
from markupsafe import Markup
from PIL import Image

ROOT = Path(__file__).resolve().parent
CONTENT, TEMPLATES, ASSETS = ROOT / 'content', ROOT / 'templates', ROOT / 'assets'

ap = argparse.ArgumentParser()
ap.add_argument('--preview', action='store_true', help='relative links for a file:// or artifact preview')
ap.add_argument('--out', default=None)
ARGS = ap.parse_args()
PREVIEW = ARGS.preview
OUT = Path(ARGS.out) if ARGS.out else ROOT / ('preview' if PREVIEW else 'dist')
TODAY = datetime.date.today()
BUILD_WARNINGS = []

def warn(msg):
    BUILD_WARNINGS.append(msg)

# --------------------------------------------------------------------------- load
def read_yaml(p):
    with open(p, encoding='utf-8') as f:
        return yaml.safe_load(f)

FRONT = re.compile(r'^---\n(.*?)\n---\n?(.*)$', re.S)
def read_md(p):
    m = FRONT.match(p.read_text(encoding='utf-8'))
    meta = yaml.safe_load(m.group(1)) or {}
    meta['body'] = m.group(2).strip()
    return meta

SITE = read_yaml(CONTENT / 'data/site.yaml')
MEMB = read_yaml(CONTENT / 'data/members.yaml')
THEMES = read_yaml(CONTENT / 'data/themes.yaml')
TOPICS = read_yaml(CONTENT / 'data/topics.yaml')
PAGES = read_yaml(CONTENT / 'data/pages.yaml')
LONG = read_yaml(CONTENT / 'data/longform.yaml')
PHOTOS = read_yaml(CONTENT / 'data/photos.yaml')
COUNTRY_OPTIONS = read_yaml(CONTENT / 'data/countries_list.yaml')

# Documents (PDFs) still live on the WordPress server. Change documents_host in site.yaml
# to wherever the uploads end up once the new site replaces the old one (see README).
LEGACY_UPLOADS = 'https://www.newproducersgroup.org/wp-content/uploads/'
DOC_HOST = (SITE.get('documents_host') or LEGACY_UPLOADS)
def doc_url(u):
    if u and u.startswith(LEGACY_UPLOADS) and DOC_HOST != LEGACY_UPLOADS:
        return DOC_HOST.rstrip('/') + '/' + u[len(LEGACY_UPLOADS):]
    return u

# --------------------------------------------------------------------------- images
IMG_DIMS = {}
for p in (ASSETS / 'img').rglob('*'):
    if p.suffix.lower() in ('.webp', '.jpg', '.jpeg', '.png'):
        try:
            with Image.open(p) as im:
                IMG_DIMS['/' + p.relative_to(ROOT).as_posix()] = im.size
        except Exception:
            pass

def dims(src):
    return IMG_DIMS.get(src, (None, None))

def photo(key):
    """Stock photo record by key -> dict(src, alt, place, by)."""
    ph = PHOTOS[key]
    return {'key': key, 'src': f'/assets/img/photos/{key}.webp', 'alt': ph['alt'], 'place': ph.get('place') or '', 'by': ph['by']}

# --------------------------------------------------------------------------- regions, members
REGION_COLOURS = {'car': 'lagoon', 'wa': 'savanna', 'ces': 'laterite', 'mea': 'atlantic', 'peer': 'peer'}
HEX = {'lagoon': '#008C82', 'savanna': '#DDA12E', 'laterite': '#D0603E', 'atlantic': '#3C7BC4', 'peer': '#A3AFBA', 'ink': '#0F2B3D'}
INK = {'lagoon': '#00665F', 'savanna': '#80560A', 'laterite': '#A2421F', 'atlantic': '#2A5E9C', 'peer': '#5F7182', 'ink': '#0F2B3D'}
STAGE_COLOURS = {'Frontier': '#9CC3E6', 'Development of significant discoveries': '#3C7BC4', 'Production': '#1E4E8C'}
STAGE_SHORT = {'Frontier': 'Frontier', 'Development of significant discoveries': 'Development', 'Production': 'Production'}
ROLE_LABEL = {'member': 'Member', 'observer': 'Observer', 'peer': 'Established producer peer', 'former': 'Former member'}

# Equal Earth projection fitted to the 1000-px world map in assets/js/world.js
def project(lon, lat):
    A1, A2, A3, A4, M = 1.340264, -0.081106, 0.000893, 0.003796, math.sqrt(3) / 2
    l, p = math.radians(lon), math.radians(lat)
    th = math.asin(M * math.sin(p)); t2 = th * th; t6 = t2 ** 3
    x = l * math.cos(th) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return round(500.0 + 184.7347 * x, 1), round(243.358 - 184.7347 * y, 1)

REGIONS = {}
for k, r in MEMB['regions'].items():
    col = REGION_COLOURS[k]
    ph = r['photo'].rsplit('/', 1)[-1].rsplit('.', 1)[0]
    REGIONS[k] = {'key': k, 'name': r['name'], 'colour': col, 'hex': HEX[col], 'ink': INK[col],
                  'photo': photo(ph) if ph in PHOTOS else None, 'caption': r.get('photo_caption') or ''}
REGIONS['peer'] = {'key': 'peer', 'name': 'Established producer peers', 'colour': 'peer', 'hex': HEX['peer'], 'ink': INK['peer'], 'photo': photo('rig-blue'), 'caption': ''}

COUNTRY_FILES = {p.stem: read_md(p) for p in sorted((CONTENT / 'countries').glob('*.md'))}
MEMBERS, PEERS = [], []
for m in MEMB['members']:
    m = dict({'legacy_production': False, 'banner': None, 'photo': None, 'photo_caption': None, 'stage': ''}, **m)
    m['colour'] = REGION_COLOURS[m['region']]
    m['url'] = f"/{m['slug']}/"
    m['pt'] = project(m['lon'], m['lat'])
    m['role_label'] = ROLE_LABEL[m['role']]
    m['stage_short'] = STAGE_SHORT.get(m.get('stage') or '', '')
    cf = COUNTRY_FILES.get(m['slug'], {})
    m['resources'] = cf.get('resources') or []
    m['legacy_url'] = cf.get('legacy_url')
    MEMBERS.append(m)
for m in MEMB['peers']:
    m = dict(m)
    m['colour'] = 'peer'; m['url'] = None; m['pt'] = project(m['lon'], m['lat']); m['role_label'] = ROLE_LABEL['peer']
    PEERS.append(m)
ACTIVE = [m for m in MEMBERS if m['role'] in ('member', 'observer')]
BY_NAME = {m['name']: m for m in MEMBERS + PEERS}
BY_SLUG = {m['slug']: m for m in MEMBERS}
N_COUNTRIES = len(ACTIVE)
N_MEMBERS = sum(m['role'] == 'member' for m in ACTIVE)
N_OBSERVERS = sum(m['role'] == 'observer' for m in ACTIVE)

# --------------------------------------------------------------------------- themes & topics
THEME = {}
for t in THEMES:
    t = dict(t); t['url'] = f"/category/{t['slug']}/"; t['hex'] = HEX[t['colour']]; t['ink'] = INK[t['colour']]
    THEME[t['slug']] = t
TOPIC = {}
for t in TOPICS:
    t = dict(t); t['url'] = f"/tag/{t['slug']}/"
    if '-' in t['name'] and t['name'] == t['slug']:
        t['name'] = t['name'].replace('-', ' ')
    TOPIC[t['slug']] = t

def label_case(s):
    s = (s or '').strip()
    return s[:1].upper() + s[1:] if s and s[:1].islower() else s

# --------------------------------------------------------------------------- publications & events
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
STOP = set('a an and the of in on for to with from by at as is are be new oil gas emerging producers producer petroleum sector'.split())
def tokens(s):
    return {w for w in re.findall(r'[a-z0-9]+', (s or '').lower()) if w not in STOP and len(w) > 2}

def plain(html_str):
    t = re.sub(r'\s+', ' ', BeautifulSoup(html_str or '', 'html.parser').get_text(' ')).strip()
    return re.sub(r'\s+([,.;:!?)])', r'\1', t)

def excerpt(text, n=200):
    t = re.sub(r'\s+', ' ', text or '').strip()
    if len(t) <= n:
        return t
    cut = t[:n]; dot = cut.rfind('. ')
    return cut[:dot + 1] if dot > n * 0.55 else cut.rsplit(' ', 1)[0].rstrip(',;:') + '…'

def dedupe_sentence(s):
    """'X. X.' duplicated blurbs from the old site collapse to one."""
    if not s:
        return s
    half = len(s) // 2
    for cut in range(half - 2, half + 3):
        a, b = s[:cut].strip(), s[cut:].strip()
        if a and a == b:
            return a
    return s

def auto_summary(body_html, n=230):
    """First sentences of a body, with headings and list items punctuated so they read as prose."""
    s = BeautifulSoup(body_html or '', 'html.parser')
    for v in s.find_all(['video', 'figure', 'audio', 'script', 'style', 'table']):
        v.decompose()
    parts = []
    for el in s.find_all(['p', 'li', 'h2', 'h3', 'h4', 'h5', 'h6']):
        if el.name != 'li' and el.find_parent('li'):
            continue
        t = re.sub(r'https?://\S+', '', re.sub(r'\s+', ' ', el.get_text(' '))).strip()
        t = re.sub(r'\s+([,.;:!?)])', r'\1', t)
        if not t:
            continue
        if t[-1] not in '.!?:;…"”)':
            t += '.'
        parts.append(t)
        if sum(len(x) for x in parts) > n * 1.5:
            break
    return excerpt(' '.join(parts), n)

def pick_summary(summary, body):
    s = (summary or '').strip()
    flat = re.sub(r'\s+', ' ', plain(body))
    stem = re.sub(r'\s*(\[…\]|\[\.\.\.\]|…|\.\.\.)\s*$', '', s)
    if not s or 'http' in s or (len(stem) > 40 and flat.startswith(stem[:60])):
        return auto_summary(body) or s
    return dedupe_sentence(s)

PUBS, EVENTS = [], []
for p in sorted((CONTENT / 'publications').glob('*.md')):
    m = read_md(p)
    m['kind'] = 'publication'
    m['url'] = f"/{m['slug']}/"
    m['date'] = str(m.get('date') or '')
    m['year'] = int(m['date'][:4]) if m['date'][:4].isdigit() else None
    m['sort'] = m['date']
    m['themes'] = [t for t in (m.get('themes') or []) if t in THEME]
    m['topics'] = [t for t in (m.get('topics') or []) if t in TOPIC]
    m['countries'] = m.get('countries') or []
    m['documents'] = [dict(d, url=doc_url(d['url'])) for d in (m.get('documents') or [])]
    m['type'] = m.get('type') or 'Publication'
    m['label'] = m['type']
    m['summary'] = pick_summary(m.get('summary'), m['body'])
    for k, v in (('image', None), ('authors', ''), ('formats', []), ('date_display', '')):
        m.setdefault(k, v)
    PUBS.append(m)
for p in sorted((CONTENT / 'events').glob('*.md')):
    m = read_md(p)
    m['kind'] = 'event'
    m['url'] = f"/event/{m['slug']}/"
    m['date_start'] = str(m['date_start']); m['date_end'] = str(m.get('date_end') or m['date_start'])
    m['year'] = int(m['date_start'][:4])
    m['sort'] = m['date_start']
    m['types'] = m.get('types') or []
    m['type'] = m['types'][0] if m['types'] else 'Event'
    m['label'] = m['type']
    m['themes'] = [t for t in (m.get('themes') or []) if t in THEME]
    m['topics'] = [t for t in (m.get('topics') or []) if t in TOPIC]
    m['countries'] = m.get('countries') or []
    m['documents'] = [dict(d, url=doc_url(d['url'])) for d in (m.get('documents') or [])]
    m['summary'] = pick_summary(m.get('summary'), m['body'])
    d0 = datetime.date.fromisoformat(m['date_start'])
    m['day'], m['mon'] = d0.day, MONTHS[d0.month - 1][:3]
    m['past'] = datetime.date.fromisoformat(m['date_end']) < TODAY
    for k, v in (('image', None), ('image_caption', ''), ('time', ''), ('authors', ''), ('formats', [])):
        m.setdefault(k, v)
        if m[k] is None and v != None: m[k] = v
    EVENTS.append(m)
PUBS.sort(key=lambda x: x['sort'], reverse=True)
EVENTS.sort(key=lambda x: x['sort'], reverse=True)
PUB = {p['slug']: p for p in PUBS}
EVT = {e['slug']: e for e in EVENTS}
ITEMS = PUBS + EVENTS

def item_by_ref(ref):
    if ref.startswith('event/'):
        return EVT.get(ref[6:])
    return PUB.get(ref)

# event -> its published summary (annual meetings, national seminars ...)
for e in EVENTS:
    e['summary_pub'] = None
    best, score = None, 0.0
    te = tokens(e['title'])
    for p in PUBS:
        if p['type'] not in ('Event summary', 'Video', 'Report') or not p['year']:
            continue
        pd = p['date'] + '-15' if len(p['date']) == 7 else p['date']
        try:
            gap = (datetime.date.fromisoformat(pd) - datetime.date.fromisoformat(e['date_start'])).days
        except ValueError:
            continue
        if gap < -45 or gap > 400:
            continue
        tp = tokens(p['title'])
        if not te or not tp:
            continue
        j = len(te & tp) / len(te | tp)
        if j > score:
            best, score = p, j
    if best and score >= 0.34:
        e['summary_pub'] = best
        best.setdefault('events', []).append(e)
for p in PUBS:
    p.setdefault('events', [])

def related(item, n=3, kinds=('publication', 'event')):
    scored = []
    for o in ITEMS:
        if o is item or o['kind'] not in kinds:
            continue
        s = 3 * len(set(o['countries']) & set(item['countries'])) + 2 * len(set(o['topics']) & set(item['topics'])) + 1.2 * len(set(o['themes']) & set(item['themes']))
        if o['kind'] == item['kind']:
            s += 0.3
        if s > 0:
            scored.append((s, o['sort'], o))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [o for _, _, o in scored[:n]]

# country -> items
for m in MEMBERS + PEERS:
    m['pubs'] = [p for p in PUBS if m['name'] in p['countries']]
    m['events'] = [e for e in EVENTS if m['name'] in e['countries']]
SPOTLIGHTS = PAGES['impact']['spotlights']
VOICES = PAGES['impact']['voices']
for m in MEMBERS:
    m['spotlights'] = [s for s in SPOTLIGHTS if m['name'] in (s.get('countries') or [])]
    m['voices'] = [v for v in VOICES if m['name'] in v['source'] or (m['name'] == 'Kenya' and 'Turkana' in v['source'])]
    # header photo: the licensed landscape where we have one, otherwise the old site's country photo
    if m.get('photo'):
        m['hero'] = photo(m['photo'].rsplit('/', 1)[-1].rsplit('.', 1)[0])
    elif m.get('banner'):
        m['hero'] = {'src': m['banner'], 'alt': f"{m['name']}", 'place': m['name'], 'by': None}
    else:
        m['hero'] = None
    reg = REGIONS[m['region']]
    m['card_photo'] = photo(m['photo'].rsplit('/', 1)[-1].rsplit('.', 1)[0]) if m.get('photo') else reg['photo']

# --------------------------------------------------------------------------- body HTML clean-up
KNOWN_URLS = set()   # filled once routes are known

def fix_internal(href):
    """Map a root-relative link to a page that exists (old slugs, '-2' duplicates, dated suffixes)."""
    if not href or not href.startswith('/') or href.startswith('//'):
        return href
    path, frag = (href.split('#', 1) + [''])[:2]
    path, q = (path.split('?', 1) + [''])[:2]
    if path.startswith('/assets/') or path in KNOWN_URLS:
        return href
    if not path.endswith('/') and '.' not in path.rsplit('/', 1)[-1]:
        path += '/'
    cands = [path, re.sub(r'-\d/$', '/', path)]
    for c in cands:
        if c in KNOWN_URLS:
            return c + ('#' + frag if frag else '')
    pre = [u for u in KNOWN_URLS if len(u) > 12 and (path.startswith(u[:-1]) or u.startswith(path[:-1]))]
    if len(pre) == 1:
        return pre[0] + ('#' + frag if frag else '')
    warn(f'unresolved internal link {href}')
    return href

def process_body(raw):
    s = BeautifulSoup(raw or '', 'html.parser')
    # empty headings / paragraphs
    for el in s.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        if not el.get_text(strip=True) and not el.find(['img', 'figure', 'iframe', 'audio']):
            el.decompose()
    # heading hierarchy: pages carry the h1, bodies start at h2
    for el in s.find_all('h1'):
        el.name = 'h2'
    hs = s.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
    if hs:
        top = min(int(h.name[1]) for h in hs)
        for h in hs:
            h.name = 'h' + str(max(2, int(h.name[1]) - (top - 2)))
            last = h.contents[-1] if h.contents else None
            if isinstance(last, NavigableString) and last.rstrip().endswith(':'):
                last.replace_with(last.rstrip()[:-1])
    # figures wrapped in <p>
    for fig in s.find_all('figure'):
        par = fig.parent
        if par is not None and par.name == 'p':
            par.insert_before(fig.extract())
            if not par.get_text(strip=True) and not par.find(['img', 'figure']):
                par.decompose()
    # ul > li > ul (no text) -> flatten
    changed = True
    while changed:
        changed = False
        for li in s.find_all('li'):
            kids = [c for c in li.contents if not (isinstance(c, NavigableString) and not c.strip())]
            if len(kids) == 1 and getattr(kids[0], 'name', None) in ('ul', 'ol'):
                inner = kids[0]
                for sub in list(inner.find_all('li', recursive=False)):
                    li.insert_before(sub.extract())
                li.decompose(); changed = True
                break
    # lone images -> figure
    for img in s.find_all('img'):
        img['loading'] = 'lazy'; img['decoding'] = 'async'
        w, h = dims(img.get('src'))
        if w and not img.get('width'):
            img['width'], img['height'] = str(w), str(h)
        par = img.parent
        if par is not None and par.name == 'p' and len([c for c in par.contents if not (isinstance(c, NavigableString) and not c.strip())]) == 1:
            par.name = 'figure'; par['class'] = 'body-img'
    # tables scroll on their own
    for t in s.find_all('table'):
        wrap = s.new_tag('div', attrs={'class': 'table-wrap'})
        t.wrap(wrap)
    # video embeds -> link card (JS upgrades to an iframe on click on the live site)
    for fig in s.select('figure.embed'):
        prov = fig.get('data-provider') or 'video'
        watch = fig.get('data-watch') or fig.get('data-embed')
        fig.clear()
        a = s.new_tag('a', attrs={'class': 'embed-link', 'href': watch, 'target': '_blank', 'rel': 'noopener'})
        a.append(BeautifulSoup('<span class="play" aria-hidden="true"></span>'
                               f'<span class="tx"><b>Watch the recording</b><small>Video on {html.escape(prov)}</small></span>', 'html.parser'))
        fig.append(a)
    # self-hosted video files
    for v in s.find_all('video'):
        src = ''
        so = v.find('source')
        if so and so.get('src'):
            src = so['src'].split('?')[0]
        elif v.get('src'):
            src = v['src'].split('?')[0]
        src = doc_url(src)
        fig = s.new_tag('figure', attrs={'class': 'video'})
        if not PREVIEW:
            fig.append(BeautifulSoup(f'<video controls preload="metadata" src="{html.escape(src)}"></video>', 'html.parser'))
        fig.append(BeautifulSoup(f'<a class="doc" href="{html.escape(src)}" target="_blank" rel="noopener"><span>Watch the video</span><small>MP4 file</small></a>', 'html.parser'))
        par = v.parent
        v.replace_with(fig)
        if par is not None and par.name == 'div' and len([c for c in par.contents if not (isinstance(c, NavigableString) and not c.strip())]) == 1:
            par.unwrap()
    # audio
    for fig in s.select('figure.audio'):
        src = doc_url(fig.get('data-src') or '')
        fig.clear()
        name = src.rsplit('/', 1)[-1]
        if not PREVIEW:
            fig.append(BeautifulSoup(f'<audio controls preload="none" src="{html.escape(src)}"></audio>', 'html.parser'))
        fig.append(BeautifulSoup(f'<a class="doc" href="{html.escape(src)}" target="_blank" rel="noopener"><span>Listen to the audio overview</span><small>{html.escape(name.rsplit(".", 1)[-1].upper())} file</small></a>', 'html.parser'))
    # links
    for a in s.find_all('a'):
        href = (a.get('href') or '').strip()
        if re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', href):
            a['href'] = href = 'mailto:' + href
        if href.startswith('/') and not href.startswith('//'):
            a['href'] = fix_internal(href)
        elif href.startswith('http'):
            a['href'] = doc_url(href)
            a['rel'] = 'noopener'
            if '/wp-content/uploads/' in href or href.lower().endswith('.pdf'):
                a['target'] = '_blank'
    out = str(s)
    out = re.sub(r'\n{2,}', '\n', out).strip()
    return Markup(out)

# --------------------------------------------------------------------------- URLs (prod: root-relative; preview: relative + index.html)
URL_ATTRS = re.compile(r'(\s(?:href|src|action|data-src|poster|data-href)=")(/(?!/)[^"]*)"')
CSS_URLS = re.compile(r'url\((["\']?)(/(?!/)[^)"\']*)\1\)')

def rel_url(target, page_url):
    if not target.startswith('/') or target.startswith('//'):
        return target
    path, frag = (target.split('#', 1) + [''])[:2]
    path, q = (path.split('?', 1) + [''])[:2]
    depth = 0 if page_url == '/' else page_url.strip('/').count('/') + 1
    if path.endswith('/'):
        path += 'index.html'
    out = '../' * depth + path.lstrip('/')
    if q:
        out += '?' + q
    if frag:
        out += '#' + frag
    return out

def finalise(html_str, page_url):
    if not PREVIEW:
        return html_str
    def attr(m):
        # keep absolute canonical/og URLs alone (they are built with site.url)
        return f'{m.group(1)}{rel_url(m.group(2), page_url)}"'
    html_str = URL_ATTRS.sub(attr, html_str)
    html_str = CSS_URLS.sub(lambda m: f'url({m.group(1)}{rel_url(m.group(2), page_url)}{m.group(1)})', html_str)
    return html_str

# --------------------------------------------------------------------------- jinja
class WarnUndefined(ChainableUndefined):
    """Missing optional fields are falsy and empty; printing one is reported so typos surface."""
    def __str__(self):
        warn(f'template printed an undefined value: {self._undefined_name}')
        return ''

env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True, trim_blocks=True, lstrip_blocks=True,
                  undefined=WarnUndefined)
env.tests['contains'] = lambda seq, x: x in (seq or [])

def f_markup(s):
    return Markup(s or '')

def f_date_long(iso):
    d = datetime.date.fromisoformat(str(iso)[:10])
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'

def f_nbsp_last(s):
    """Avoid a lone last word in headings."""
    s = str(s or '')
    parts = s.rsplit(' ', 1)
    return Markup(html.escape(parts[0]) + '&nbsp;' + html.escape(parts[1])) if len(parts) == 2 and len(parts[1]) < 10 else s

def f_initials(name):
    words = [w for w in re.sub(r'^(Dr|Ms\.?|Mr\.?|Mrs\.?|Amb\.|Prof\.)\s+', '', name).split() if w[:1].isalpha()]
    return (words[0][0] + (words[-1][0] if len(words) > 1 else '')).upper() if words else '·'

def f_link_text(item):
    """Render a {'text','link','link_text'} item: the link text inside the sentence becomes the link."""
    text, link, lt = item.get('text') or '', item.get('link'), item.get('link_text')
    esc = html.escape(text)
    if link and lt and lt in text and lt != text:
        rel = ' rel="noopener"' if link.startswith('http') else ''
        a = f'<a href="{html.escape(link)}"{rel}>{html.escape(lt)}</a>'
        esc = esc.replace(html.escape(lt), a, 1)
    return Markup(esc)

def f_stat(s):
    """'73% of members say ...' -> (value, title, text)."""
    m = re.match(r'^([\d,.]+\+?%?)\s+(.*)$', s)
    if not m:
        return None
    val, rest = m.group(1), m.group(2)
    if ':' in rest[:60]:
        title, text = rest.split(':', 1)
        return {'v': val, 'title': title.strip(), 'text': text.strip()}
    return {'v': val, 'title': '', 'text': rest.strip()}

def f_quoted(s):
    s = (s or '').strip()
    return s if '“' in s else f'“{s}”'

def f_json(o):
    return Markup(json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))

def f_cls_colour(c):
    return {'lagoon': '', 'savanna': 'sav', 'laterite': 'lat', 'atlantic': 'atl'}.get(c, 'plain')

def f_theme(slug):
    return THEME.get(slug)

def f_topic(slug):
    return TOPIC.get(slug)

def f_country(name):
    return BY_NAME.get(name)

def f_cover_colour(item):
    th = item.get('themes') or []
    return THEME[th[0]]['colour'] if th else 'ink'

def f_short_title(t):
    t = re.sub(r'\s*\((?:[^)]*edition[^)]*)\)\s*$', '', t, flags=re.I)
    return t.split(' – ')[0].split(': ')[0] if len(t) > 70 else t

env.filters.update(quoted=f_quoted, markup=f_markup, date_long=f_date_long, nbsp_last=f_nbsp_last, initials=f_initials,
                   link_text=f_link_text, stat=f_stat, tojson_attr=f_json, pillcls=f_cls_colour, theme=f_theme,
                   topic=f_topic, country=f_country, cover_colour=f_cover_colour, short_title=f_short_title,
                   label_case=label_case, excerpt=excerpt, plain=plain)

def email_js(e):
    return e

RING = []
for i, col in enumerate(['#008C82'] * 6 + ['#DDA12E'] * 6 + ['#D0603E'] * 7 + ['#3C7BC4'] * 3):
    a = math.radians(-90 + i * 360 / 22)
    RING.append((round(20 + 16.2 * math.cos(a), 2), round(20 + 16.2 * math.sin(a), 2), col))

env.globals.update(site=SITE, RING=RING, P=PAGES, LONG=LONG, PUB=PUB, EVT=EVT, PUBS=PUBS, EVENTS=EVENTS, THEME=THEME, VOICES=VOICES, SPOTLIGHTS=SPOTLIGHTS, regions=REGIONS, members=MEMBERS, active=ACTIVE, peers=PEERS, themes=THEME, topics=TOPIC,
                   photo=photo, dims=dims, preview=PREVIEW, year=TODAY.year, N_COUNTRIES=N_COUNTRIES,
                   N_MEMBERS=N_MEMBERS, N_OBSERVERS=N_OBSERVERS, STAGE_COLOURS=STAGE_COLOURS, HEX=HEX, INK=INK,
                   country_options=COUNTRY_OPTIONS, role_label=ROLE_LABEL, related=related, item_by_ref=item_by_ref,
                   stage_short=STAGE_SHORT, stage_note_text=(MEMB.get('stage_note') or '').replace(': ', ' has ') + '.')

# --------------------------------------------------------------------------- routes
ROUTES = []   # (url, template, context)
def route(url, template, **ctx):
    ROUTES.append((url, template, ctx))
    KNOWN_URLS.add(url)

P = PAGES
HIGHLIGHT_PUBS = [PUB[s] for s in P['home']['highlights'] if s in PUB]
FLAGSHIP = PUB.get('guidelines-for-good-governance-in-emerging-oil-and-gas-producers-2026-4th-edition')
EVENT_HIGHLIGHTS = [EVT[s] for s in P['events']['highlights'] if s in EVT]

route('/', 'home.html', title=None, description=SITE['description'], nav='home',
      highlights=HIGHLIGHT_PUBS, flagship=FLAGSHIP, latest_events=EVENTS[:3])
route('/about-us/', 'governance.html', title='Governance', nav='about', description=P['governance']['team_intro'])
route('/what-we-do/', 'how.html', title='How we work', nav='about', description=P['how']['mission'])
route('/impact/', 'impact.html', title='Impact', nav='about', description='Spotlights and evidence of what the New Producers Group network has achieved with its member governments.')
route('/annual-report-2024-25/', 'annual_report.html', title='Annual report 2024–25', nav='about',
      description='The annual report and financial statements of New Producers for Sustainable Energy for the year ending April 2025.')
route('/members/', 'members.html', title='Member countries', nav='members',
      description=f'{N_COUNTRIES} countries new to oil and gas: {N_MEMBERS} members and {N_OBSERVERS} observers, with established producers as peers.')
route('/get-involved/', 'get_involved.html', title='Get involved', nav='involved', description=P['get_involved']['intro'])
route('/members-area/', 'members_area.html', title='Members area', nav='area',
      description=P['members_area']['membership']['items'][0]['text'])
route('/activities-and-events/', 'events.html', title='Activities and events', nav='events', description=P['events']['intro'] + '.',
      highlights=EVENT_HIGHLIGHTS)
route('/annual-meeting/', 'event_type.html', title='Annual meeting', nav='events', description=P['annual_meeting']['intro'],
      etype='Annual meeting', intro=P['annual_meeting']['intro'], banner='/assets/img/wp/2020-12-group-shot-annual-meeting-1.webp',
      banner_caption='Annual Meeting 2018, Accra, Ghana')
route('/training/', 'event_type.html', title='Training', nav='events', description=P['training']['intro'],
      etype='Training', intro=P['training']['intro'], banner='/assets/img/wp/2026-04-curtis-training-2026-1.webp',
      banner_caption='Strategic Foundations for Upstream Success, 2026')
route('/resources-and-publications/', 'library.html', title='Resources and publications', nav='resources', pub_types=Counter(p['type'] for p in PUBS).most_common(),
      description='Reports, policy briefs, papers, articles, videos and meeting summaries for governments in emerging oil and gas producers.')
route('/resources-and-publications/sovereign-ai-initiative/', 'sovereign_ai.html', title='Sovereign AI Initiative', nav='resources',
      description=P['sovereign_ai']['description'])
for key, meta in LONG.items():
    route(meta['url'], 'longform.html', title=meta.get('nav_title') or meta['title'], nav='resources' if meta['label'] != 'Legal' else None,
          description=meta['description'], lf=meta, key=key)
route('/contact-us/', 'contact.html', title='Contact us', nav=None, description='Get in touch with the New Producers for Sustainable Energy Secretariat.')
route('/subscription/', 'subscribe.html', title='Subscribe to updates', nav=None, description=P['subscription']['intro'], mode='subscribe')
route('/unsubscribe/', 'subscribe.html', title='Unsubscribe', nav=None, description=P['unsubscribe']['intro'], mode='unsubscribe')
route('/photo-credits/', 'credits.html', title='Photo credits', nav=None, description='Credits for the photography used on this website.', site_photos=list(PHOTOS.items()))
route('/thank-you/', 'thanks.html', title='Thank you', nav=None, description='Your form has been sent.')
for p in PUBS:
    route(p['url'], 'publication.html', title=p['title'], nav='resources', description=p['summary'], item=p)
for e in EVENTS:
    route(e['url'], 'event.html', title=e['title'], nav='events', description=e['summary'], item=e)
for m in MEMBERS:
    route(m['url'], 'country.html', title=m['name'], nav='members',
          description=f"{m['name']} in the New Producers Group: {m['role_label'].lower()}" + (f", {m['stage'].lower()} stage" if m.get('stage') else '') + '. Publications, events and resources.', c=m)
for t in THEME.values():
    items = [x for x in ITEMS if t['slug'] in x['themes']]
    if items:
        route(t['url'], 'taxonomy.html', title=t['name'], nav='resources', description=f"Publications and events on {t['name'].lower()} from the New Producers Group.",
              tax=t, tax_kind='Theme', items=items)
for t in TOPIC.values():
    items = [x for x in ITEMS if t['slug'] in x['topics']]
    if items:
        route(t['url'], 'taxonomy.html', title=label_case(t['name']), nav='resources', description=f"Publications and events tagged {t['name']}.",
              tax=t, tax_kind='Topic', items=items)
route('/404.html', '404.html', title='Page not found', nav=None, description='')

# --------------------------------------------------------------------------- render
def out_path(url):
    if url.endswith('.html'):
        return OUT / url.lstrip('/')
    return OUT / url.lstrip('/') / 'index.html'

def render_all():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # bodies need KNOWN_URLS, so process them now
    for x in ITEMS:
        x['html'] = process_body(x['body'])
    for key in LONG:
        LONG[key]['html'] = process_body((CONTENT / 'pages' / f'{key}.html').read_text(encoding='utf-8'))
    for m in MEMBERS:
        for res in m['resources']:
            res['url'] = fix_internal(res['url']) if res['url'].startswith('/') else doc_url(res['url'])
            res['text'] = dedupe_sentence(res.get('text') or '')
    for url, tpl, ctx in ROUTES:
        base = '' if not PREVIEW else ('' if url == '/' else '../' * (url.strip('/').count('/') + 1))
        page = dict(ctx, url=url, base=base, fragment=(PREVIEW and url == '/'))
        html_out = env.get_template(tpl).render(page=page, **ctx)
        html_out = finalise(html_out, '/' if url == '/404.html' else url)
        p = out_path(url)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html_out, encoding='utf-8')

def copy_assets():
    """Copy assets; images are copied only if a page, script or stylesheet uses them."""
    used = set()
    for p in OUT.rglob('*.html'):
        used.update(re.findall(r'assets/img/[^"\'()\s,]+', p.read_text(encoding='utf-8')))
    shutil.copytree(ASSETS, OUT / 'assets', dirs_exist_ok=True,
                    ignore=lambda d, names: [n for n in names if Path(d, n).is_file() and '/assets/img/' in Path(d, n).as_posix() + '/'
                                             and Path(d, n).relative_to(ROOT).as_posix() not in used
                                             and Path(d, n).parent != ASSETS / 'img'])
    return used

def write_data_js():
    """Map + search data, shared by all pages that need them."""
    def mrec(m):
        rel = sorted(m['pubs'] + m['events'], key=lambda x: x['sort'], reverse=True)[:4]
        return {'n': m['name'], 's': m['slug'], 'r': m['region'], 'role': m['role'], 'stage': m.get('stage') or '',
                'legacy': bool(m.get('legacy_production')), 'id': m.get('atlas_id') or '', 'cap': m['capital'],
                'll': [m['lon'], m['lat']], 'pt': list(m['pt']), 'u': m.get('url'),
                'img': (m['card_photo'] or {}).get('src') if m.get('card_photo') else None,
                'ic': (m['card_photo'] or {}).get('place') if m.get('card_photo') else '',
                'np': len(m['pubs']), 'ne': len(m['events']),
                'rel': [[x['title'], x['url'], x['label'], x['year']] for x in rel]}
    data = {'regions': {k: {'n': r['name'], 'c': r['colour'], 'hex': r['hex'], 'ink': r['ink'],
                            'img': r['photo']['src'] if r['photo'] else None, 'cap': r['caption'] or (r['photo']['place'] if r['photo'] else '')}
                        for k, r in REGIONS.items()},
            'members': [mrec(m) for m in MEMBERS] + [mrec(dict(m, pubs=m['pubs'], events=m['events'], card_photo=None)) for m in PEERS],
            'stages': list(STAGE_COLOURS.keys()), 'stageHex': STAGE_COLOURS, 'stageShort': STAGE_SHORT,
            'stageNote': MEMB.get('stage_note', '')}
    (OUT / 'assets/js/np-data.js').write_text('window.NP_DATA=' + json.dumps(data, ensure_ascii=True, separators=(',', ':')) + ';\n', encoding='ascii')
    idx = []
    for url, tpl, ctx in ROUTES:
        if url == '/404.html' or tpl in ('taxonomy.html',):
            continue
        it = ctx.get('item'); c = ctx.get('c')
        if it:
            kind = ('Event · ' + it['date_display']) if it['kind'] == 'event' else f"{it['type']} · {it.get('date_display', '')}"
            extra = ' '.join([it.get('authors') or '', ' '.join(it['countries']), ' '.join(TOPIC[t]['name'] for t in it['topics'])])
            idx.append({'t': it['title'], 'u': url, 'k': kind, 's': excerpt(it['summary'], 150), 'x': extra, 'y': it['year'] or 0})
        elif c:
            idx.append({'t': c['name'], 'u': url, 'k': 'Country · ' + c['role_label'], 's': REGIONS[c['region']]['name'], 'x': c['capital'], 'y': 0})
        else:
            idx.append({'t': ctx.get('title') or SITE['name'], 'u': url, 'k': 'Page', 's': excerpt(ctx.get('description') or '', 150), 'x': '', 'y': 0})
    for t in THEME.values():
        if t['url'] in KNOWN_URLS:
            idx.append({'t': t['name'], 'u': t['url'], 'k': 'Theme', 's': '', 'x': '', 'y': 0})
    (OUT / 'assets/js/search-index.js').write_text('window.NP_SEARCH=' + json.dumps(idx, ensure_ascii=True, separators=(',', ':')) + ';\n', encoding='ascii')

def write_meta_files():
    if PREVIEW:
        return
    base = SITE['url'].rstrip('/')
    urls = [u for u, t, c in ROUTES if u != '/404.html']
    lastmod = {}
    for x in ITEMS:
        lastmod[x['url']] = x['sort'][:10] if len(x['sort']) >= 10 else x['sort'] + '-01'
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f'  <url><loc>{base}{html.escape(u)}</loc>' + (f'<lastmod>{lastmod[u]}</lastmod>' if u in lastmod else '') + '</url>')
    sm.append('</urlset>')
    (OUT / 'sitemap.xml').write_text('\n'.join(sm) + '\n', encoding='utf-8')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n', encoding='utf-8')
    red = ['# Old WordPress addresses -> new pages (Netlify format; see README for other hosts)',
           '/map-4/                         /members/                  301',
           '/sa%cc%83o-tome-e-principe/     /sao-tome-e-principe/      301',
           '/sa%CC%83o-tome-e-principe/     /sao-tome-e-principe/      301',
           '/slide-anything-popup-preview/  /                          301',
           '/sliders/*                      /                          301',
           '/event/                         /activities-and-events/    301',
           '/events/                        /activities-and-events/    301',
           '/events/list/                   /activities-and-events/    301',
           '/category/uncategorized/        /resources-and-publications/ 301',
           '/events/:slug/                  /category/:slug/           301',
           '/event-tag/:slug/               /tag/:slug/                301',
           '/national-seminar-for-uganda-2019-2/  /national-seminar-for-uganda-2019/  301',
           '/event/government-review-of-field-development-plans-12-21-october-2020/  /event/government-review-of-field-development-plans/  301',
           '/feed/                          /                          301',
           '/s\u00e3o-tome-e-principe/       /sao-tome-e-principe/      301',
           '/sa\u0303o-tome-e-principe/      /sao-tome-e-principe/      301',
           ''] + [f"/tag/{t['slug']}/  {THEME[t['slug']]['url'] if t['slug'] in THEME else '/resources-and-publications/'}  301"
                  for t in TOPIC.values() if t['url'] not in KNOWN_URLS] + [
           '',
           '# Documents: while WordPress still serves /wp-content/uploads/, nothing is needed here.',
           '# When this site replaces WordPress on the same domain, point the uploads at their new home, e.g.:',
           '# /wp-content/uploads/*  https://archive.newproducersgroup.org/wp-content/uploads/:splat  301']
    (OUT / '_redirects').write_text('\n'.join(red) + '\n', encoding='utf-8')
    (OUT / '_headers').write_text('/assets/*\n  Cache-Control: public, max-age=604800\n', encoding='utf-8')

# --------------------------------------------------------------------------- link check
HREF = re.compile(r'\s(?:href|src|action)="([^"]+)"')
def link_check():
    problems = []
    files = {p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()}
    for p in OUT.rglob('*.html'):
        page_dir = p.parent
        for u in HREF.findall(p.read_text(encoding='utf-8')):
            u = html.unescape(u)
            if re.match(r'^(https?:|mailto:|tel:|#|data:|javascript:)', u) or u.startswith('//'):
                continue
            path = u.split('#', 1)[0].split('?', 1)[0]
            if not path:
                continue
            if PREVIEW:
                target = (page_dir / path).resolve()
                try:
                    rel = target.relative_to(OUT.resolve()).as_posix()
                except ValueError:
                    problems.append((p.relative_to(OUT).as_posix(), u)); continue
            else:
                rel = path.lstrip('/')
                if rel == '' or rel.endswith('/'):
                    rel += 'index.html'
            if rel not in files:
                problems.append((p.relative_to(OUT).as_posix(), u))
    return problems

def copy_data_images():
    """Images referenced only from the map data (country cards) or CSS."""
    for p in list((OUT / 'assets/js').glob('*.js')) + list((OUT / 'assets/css').glob('*.css')):
        for ref in re.findall(r'assets/img/[^"\'()\s,]+', p.read_text(encoding='utf-8')):
            src, dst = ROOT / ref, OUT / ref
            if src.exists() and not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

if __name__ == '__main__':
    render_all()
    copy_assets()
    write_data_js()
    copy_data_images()
    write_meta_files()
    probs = link_check()
    n_html = sum(1 for _ in OUT.rglob('*.html'))
    print(f'Built {n_html} pages into {OUT.relative_to(ROOT)}/ ({"preview" if PREVIEW else "production"})')
    print(f'  {len(PUBS)} publications, {len(EVENTS)} events, {len(MEMBERS)} country pages, '
          f'{sum(1 for u in KNOWN_URLS if u.startswith("/category/"))} themes, {sum(1 for u in KNOWN_URLS if u.startswith("/tag/"))} topics')
    for w in sorted(set(BUILD_WARNINGS)):
        print('  warning:', w)
    if probs:
        print(f'  {len(probs)} broken links:')
        for pg, u in probs[:40]:
            print('   ', pg, '->', u)
        sys.exit(1)
    print('  link check: all internal links resolve')
