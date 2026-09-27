#!/usr/bin/env python3
"""Extract the structured pages of the old site into content/data/pages.yaml and
long-form page bodies into content/pages/*.html. Text is copied verbatim."""
import json, re, os, yaml
from bs4 import BeautifulSoup, NavigableString
import normalise as N   # reuses cleaners, url + image mapping (re-runs normalise, which is idempotent)

d = N.d
P = {p['slug']: p for p in d['pages']}
T = N.clean_text
soup = lambda slug: BeautifulSoup(P[slug]['html'], 'lxml')
def img(el):
    i = el.find('img') if el and el.name != 'img' else el
    return N.local_img(i.get('src')) if i is not None else None
def bg(slug):
    for cls, u in re.findall(r'\.(vc_custom_\d+)\{[^}]*?background-image:\s*url\(([^)]+)\)', P[slug].get('css', '')):
        li = N.local_img(u)
        if li: return li
    s = soup(slug)
    for el in s.find_all(style=re.compile('background-image')):
        for u in re.findall(r'url\(([^)]+)\)', el['style']):
            li = N.local_img(u)
            if li: return li
    return None
def paras_after(h, stop=('h2', 'h3')):
    out = []
    for el in h.find_all_next():
        if el.name in stop: break
        if el.name == 'p' and T(el.get_text()): out.append(T(el.get_text(' ')))
    return out
def find_h(s, text, tags=('h2', 'h3', 'h4', 'h5')):
    return s.find(lambda t: t.name in tags and T(t.get_text()).lower().startswith(text.lower()))
def labelled(p):
    """'Label: rest' paragraphs where Label is bold -> dict."""
    t = T(p.get_text(' ')); b = p.find(['strong', 'b'])
    if b and T(b.get_text()) and t.startswith(T(b.get_text())):
        lab = T(b.get_text()).rstrip(':'); return {'label': lab, 'text': t[len(T(b.get_text())):].lstrip(': ').strip()}
    if ':' in t[:40]:
        lab, rest = t.split(':', 1); return {'label': lab.strip(), 'text': rest.strip()}
    return {'label': '', 'text': t}

pages = {}

# ---- HOME ----
s = soup('new-home')
h2 = s.find('h2')
helping = find_h(s, 'Governments helping each other')
members_h = find_h(s, 'Member Countries')
pages['home'] = {
  'hero_title': T(h2.get_text()),
  'hero_lead': T(h2.find_next('p').get_text(' ')),
  'helping': {'title': T(helping.get_text()), 'paragraphs': paras_after(helping),
              'image': N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2020/11/governments-helping-img.jpg'),
              'caption': 'Communications in Natural Resources Training, Lebanon, November 2018'},
  'members': {'title': T(members_h.get_text()), 'paragraphs': [x for x in paras_after(members_h, stop=('h4',)) if not x.startswith('♦') and not x.startswith('*')]},
  'highlights': list(dict.fromkeys(a['href'].rstrip('/').split('/')[-1] for a in s.select('.postSliderowl a[href]') if 'newproducersgroup.org/' in a['href']))[:5],
}

# ---- HOW WE WORK (what-we-do) ----
s = soup('what-we-do')
mis = find_h(s, 'Our mission')
ua = find_h(s, 'Our unique approach'); pld = find_h(s, 'The Producer-Led Difference')
def plist(h, stop):
    out = []
    for el in h.find_all_next():
        if el.name in stop or (el.name in ('h2', 'h3') and el is not h): break
        if el.name == 'p' and T(el.get_text()): out.append(el)
    return out
ua_ps = plist(ua, ('h3',)); pld_ps = plist(pld, ('h2',))
hw = find_h(s, 'How we work', ('h2',))
hw_items = []
h4s = hw.find_all_next('h4')
for i in range(0, 8, 2): hw_items.append({'title': T(h4s[i].get_text()), 'text': T(h4s[i + 1].get_text())})
vals = find_h(s, 'Our values', ('h2',))
values = []
for h4 in vals.find_all_next('h4')[:6]:
    values.append({'title': T(h4.get_text()), 'text': T(h4.find_next('p').get_text(' '))})
hist = find_h(s, 'Our history', ('h2',))
history = []
for p in hist.find_all_next('p')[:4]:
    t = T(p.get_text(' ')); yr, _, rest = t.partition(':'); history.append({'year': yr.strip(), 'text': rest.strip()})
pages['how'] = {
  'banner': bg('what-we-do'),
  'mission_title': T(mis.get_text()), 'mission': T(mis.find_next('h4').get_text()), 'mission_text': T(mis.find_next('h4').find_next('p').get_text(' ')),
  'mission_images': [N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2023/12/GHANAA.jpg'), N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2021/01/IMG_1076.jpg')],
  'approach_title': T(ua.get_text()), 'approach_intro': T(ua_ps[0].get_text(' ')), 'approach': [labelled(p) for p in ua_ps[1:]],
  'difference_title': T(pld.get_text()), 'difference_intro': T(pld_ps[0].get_text(' ')), 'difference': [labelled(p) for p in pld_ps[1:4]],
  'workstreams': hw_items, 'values': values, 'history': history,
  'history_image': N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2020/11/Our-History-img.jpg'),
}

# ---- GOVERNANCE (about-us) ----
s = soup('about-us')
team_h = find_h(s, 'Our team', ('h3',))
team = []
for h4 in team_h.find_all_next('h4'):
    if h4.find_previous('h3') is not team_h: break
    wrap = h4.find_parent('div', class_='wpb_column') or h4.parent
    lines = [T(p.get_text(' ')) for p in h4.find_all_next('p', limit=3) if (p.find_parent('div', class_='wpb_column') is wrap)]
    team.append({'name': T(h4.get_text()), 'roles': lines, 'photo': img(wrap)})
def board(title):
    h = find_h(s, title, ('h3',)); intro = T(h.find_next('p').get_text(' '))
    ppl = []
    for h4 in h.find_all_next('h4'):
        if h4.find_previous('h3') is not h: break
        wrap = h4.find_parent('div', class_='wpb_column') or h4.parent
        lines = []
        for p in h4.find_all_next('p', limit=3):
            if p.find_parent('div', class_='wpb_column') is not wrap: break
            lines.extend(T(x) for x in p.get_text('\n').split('\n') if T(x))
        ppl.append({'name': T(h4.get_text()), 'roles': lines})
    return {'title': T(h.get_text()), 'intro': intro, 'people': ppl}
fin_h = find_h(s, 'Funders and financials', ('h3',))
fin_ps = []
for el in fin_h.find_all_next(['p', 'h3']):
    if el.name == 'h3': break
    t = T(el.get_text(' '))
    if t:
        a = el.find('a'); fin_ps.append({'text': t, 'link': N.map_url(a['href']) if a and a.get('href') else None})
part_h = find_h(s, 'Partner organisations', ('h3',))
partners = []
for a in part_h.find_all_next('a'):
    if a.find_parent('div', class_='threeboxSection'): break
    i = a.find('img')
    if i is not None: partners.append({'url': a['href'], 'logo': N.local_img(i['src'])})
pages['governance'] = {
  'banner': bg('about-us'), 'team_title': T(team_h.get_text()), 'team_intro': T(team_h.find_next('p').get_text(' ')), 'team': team,
  'advisory': board('Advisory Board'), 'trustees': board('Board of Trustees'),
  'financials_title': T(fin_h.get_text()), 'financials': fin_ps,
  'partners_title': T(part_h.get_text()), 'partners_intro': T(part_h.find_next('p').get_text(' ')), 'partners': partners,
}

# ---- IMPACT ----
s = soup('impact')
stats = [T(h.get_text(' ')).lstrip('⇒ ').strip() for h in s.find_all('h4')]
pages['impact'] = {'banner': bg('impact'), 'title': 'Impact', 'stats': stats}

# ---- GET INVOLVED ----
s = soup('get-involved')
intro = T(find_h(s, 'GET INVOLVED', ('h2',)).find_next('p').get_text(' '))
mem = s.select_one('.bMember') or s
wel = find_h(s, 'New member countries', ('h4',)); ind = find_h(s, 'New individual members', ('h4',)); cost = find_h(s, 'Cost', ('h2',))
spon = find_h(s, 'Sponsor us', ('h4',)); part = find_h(s, 'Become a partner', ('h4',))
sp_ps = []
for el in spon.find_all_next(['p', 'h3']):
    if el.name == 'h3': break
    t = T(el.get_text(' '))
    if t:
        a = el.find('a'); sp_ps.append({'text': t, 'link': N.map_url(a['href']) if a and a.get('href') else None, 'link_text': T(a.get_text()) if a else None})
sponsors_h = find_h(s, 'Who are our sponsors', ('h3',))
sponsors = []
for el in sponsors_h.find_all_next(['a', 'img', 'h3']):
    if el.name == 'h3': break
    if el.name == 'a' and el.find('img') is not None: sponsors.append({'url': el['href'], 'logo': N.local_img(el.find('img')['src'])})
    elif el.name == 'img' and not el.find_parent('a'): sponsors.append({'url': None, 'logo': N.local_img(el['src'])})
partners_h = find_h(s, 'Who are our partners', ('h3',))
gpartners = []
for el in partners_h.find_all_next(['a', 'img', 'h3']):
    if el.name == 'h3': break
    if el.name == 'a' and el.find('img') is not None: gpartners.append({'url': el['href'], 'logo': N.local_img(el.find('img')['src'])})
    elif el.name == 'img' and not el.find_parent('a'): gpartners.append({'url': None, 'logo': N.local_img(el['src'])})
pages['get_involved'] = {
  'banner': bg('get-involved'), 'intro': intro,
  'member': {'image': N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2021/01/af835a9d-a733-4654-b543-ef30d5e73245-1-concentrate.jpeg'),
             'countries_title': T(wel.get_text()), 'countries': T(wel.find_next('p').get_text(' ')),
             'individuals_title': T(ind.get_text()), 'individuals': [T(p.get_text(' ')) for p in ind.find_all_next('p', limit=2)],
             'cost_title': T(cost.get_text()), 'cost': T(cost.find_next('p').get_text(' '))},
  'sponsor': {'paragraphs': sp_ps, 'sponsors': sponsors, 'image': N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2024/08/Staatsolie.jpg')},
  'partner': {'intro': T(part.find_next('p').get_text(' ')), 'partners': gpartners},
}

# ---- MEMBERS AREA ----
s = soup('members-area')
def section(title):
    h = find_h(s, title, ('h4', 'h3'))
    items = []
    for el in h.find_all_next(['p', 'li', 'h3', 'h4', 'h5']):
        if el.name in ('h3', 'h4') and el is not h: break
        if el.name == 'h5': break
        if el.name == 'p' and el.find_parent('li'): continue
        if el.name == 'li' and el.find_parent('li'): continue
        sub = None
        if el.name == 'li' and el.find('ul'):
            sub = [T(x.get_text(' ')) for x in el.find('ul').find_all('li')]
            nested = el.find('ul').extract()
        t = T(el.get_text(' '))
        if not t: continue
        a = el.find('a')
        items.append({'kind': el.name, 'text': t, 'link': N.map_url(a['href']) if a and a.get('href') else None, 'link_text': T(a.get_text()) if a else None, 'sub': sub})
    subs = {x for it in items for x in (it.get('sub') or [])}
    items = [it for it in items if it['text'] not in subs]
    return {'title': T(h.get_text()), 'items': items}
exch = []
for box in s.select('.exchangeBox'):
    dates = [T(p.get_text()) for p in box.find_all('p') if T(p.get_text())]
    exch.append({'title': T(box.find('h5').get_text()), 'date': dates[0] if dates else '', 'image': img(box)})
labs_h = find_h(s, 'Policy labs', ('h3',))
labs_intro = [T(p.get_text(' ')) for p in labs_h.find_all_next('p', limit=2)]
labs_list = [T(li.get_text(' ')) for li in labs_h.find_next('ul').find_all('li')]
labs = []
for name in ['Emissions Lab', 'Methane MMRV Programme', 'Future Economy Lab']:
    h = find_h(s, name, ('h4',))
    col = h.find_parent('div', class_='wpb_column')
    row = h.find_parent('div', class_='vc_row')
    ps = []
    for el in h.find_all_next(['p', 'h4', 'a', 'div']):
        if el.name == 'h4': break
        if el.name == 'p':
            t = T(el.get_text(' '))
            if t and t != 'Find out more': ps.append(t)
        if el.name == 'div' and 'wpb_wrapper' in (el.get('class') or []) and not el.find(['p', 'h4']) and T(el.get_text()) and el.find_previous('h4') is h:
            t = T(el.get_text(' '))
            if t not in ps and 'Read more' not in t and len(t) > 40: ps.append(t)
    link = None
    for a in h.find_all_next('a', limit=6):
        if T(a.get_text()) in ('Find out more', 'Read more'): link = N.map_url(a['href']); break
    im = None
    prev = h.find_previous('img')
    if prev is not None: im = N.local_img(prev.get('src'))
    labs.append({'title': name, 'paragraphs': ps, 'link': link, 'image': im})
pages['members_area'] = {
  'slides': [N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2020/12/tq566yPo-e1610386524420.jpeg'), N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2021/01/IMG_9679-scaled-e1609954139435.jpg')],
  'membership': section('Membership'), 'helpdesk': section('Help desk'), 'exchange': section('Exchange with your peers'),
  'exchanges': exch, 'labs_title': T(labs_h.get_text()), 'labs_intro': labs_intro, 'labs_list': labs_list, 'labs': labs,
  'labs_image': N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2020/11/Working-Groups-img.jpg'),
}

# ---- EVENTS HUB ----
s = soup('activities-and-events')
types = []
for name in ['Annual Meeting', 'Workshops', 'Training sessions', 'Virtual meetings']:
    h = find_h(s, name, ('h4',)); types.append({'title': T(h.get_text()), 'text': T(h.find_next('p').get_text(' '))})
pages['events'] = {'banner': bg('activities-and-events'), 'intro': T(find_h(s, 'Highlights', ('h2',)).find_next('p', string=None).get_text(' ')) if False else
                   T(s.find(string=re.compile('We offer several different types of events')).parent.get_text(' ')),
                   'types': types, 'highlights': list(dict.fromkeys(a['href'].rstrip('/').split('/')[-1] for a in s.select('.postSliderowl a[href]')))[:6],
                   'linkedin': 'https://www.linkedin.com/groups/7448187/'}
for slug, key in [('annual-meeting', 'annual_meeting'), ('training', 'training')]:
    s = soup(slug); h = find_h(s, 'Annual meeting' if key == 'annual_meeting' else 'Training', ('h2',))
    pages[key] = {'title': T(h.get_text()), 'intro': T(h.find_next('p').get_text(' '))}

# ---- RESOURCES ----
s = soup('resources-and-publications')
pages['resources'] = {'banner': bg('resources-and-publications'), 'highlights': list(dict.fromkeys(a['href'].rstrip('/').split('/')[-1] for a in s.select('.postSliderowl a[href]')))[:5]}

# ---- CONTACT / SUBSCRIPTION ----
s = soup('contact-us'); pages['contact'] = {'banner': bg('contact-us'), 'emails': ['contact@newproducersgroup.org', 'members@newproducersgroup.org']}
s = soup('subscription'); h = find_h(s, 'New Producers for Sustainable Energy', ('h2',))
ps = [T(p.get_text(' ')) for p in s.find_all('p') if T(p.get_text()) and not T(p.get_text()).startswith('Email Address')]
pages['subscription'] = {'intro': ps[0], 'consent': ps[-1]}
s = soup('unsubscribe'); pages['unsubscribe'] = {'intro': T(s.find(string=re.compile("sorry to see you go")).parent.get_text(' '))}

# ---- IMPACT: spotlights + voices (transcribed from the images on the live page) ----
pages['impact']['spotlights'] = yaml.safe_load(open(N.S('migration/source/impact_transcribed.yaml')))['spotlights']
pages['impact']['voices'] = yaml.safe_load(open(N.S('migration/source/impact_transcribed.yaml')))['voices']

with open(N.S('content/data/pages.yaml'), 'w') as f:
    yaml.safe_dump(pages, f, sort_keys=False, allow_unicode=True, width=1000)

# ---- long-form bodies ----
os.makedirs(N.S('content/pages'), exist_ok=True)
def longform(slug, start_text=None, drop_first_heading=True):
    s = soup(slug)
    for sel in ['.threeboxSection', '.BenBanner', '.aboutBanner', '.eventBanner', '.contactBanner', 'form', '.to-the-content', '.entry-header', 'header']:
        for el in s.select(sel): el.decompose()
    body = N.clean_body(str(s))
    b = BeautifulSoup(body, 'lxml')
    for el in b.find_all(['div', 'article', 'section', 'u']): el.unwrap()
    for el in b.find_all(['h2', 'h3', 'h4', 'h5', 'p']):
        if not el.get_text(strip=True) and not el.find(['img', 'audio']): el.decompose()
    for el in b.find_all(['table', 'td', 'th', 'tr']):
        for k in ('width', 'height'): el.attrs.pop(k, None)
    for h in b.find_all(['h3', 'h4', 'h5']):
        st = h.find('strong')
        if st and st.get_text(strip=True) == h.get_text(strip=True): st.unwrap()
    for au in b.find_all('audio'):
        src = au.find('source')['src'].split('?')[0] if au.find('source') else ''
        fig = b.new_tag('figure', attrs={'class': 'audio', 'data-src': src}); au.replace_with(fig)
    body = (b.body.decode_contents() if b.body else str(b)).strip()
    body = re.sub(r'\n{2,}', '\n', body)
    if drop_first_heading: body = re.sub(r'^\s*<h[23]>.*?</h[23]>', '', body, count=1, flags=re.S)
    return body
for slug in ['field-development-plans', 'methane-programme', 'working-group-information-governments-can-expect-from-operators',
             'unsticking-the-sticky-clauses-working-group', 'privacy-policy', 'terms-of-use']:
    body = longform(slug)
    open(N.S('content/pages', slug + '.html'), 'w').write(body + '\n')
# Sovereign AI: structured
sb = BeautifulSoup(longform('sovereign-ai-initiative', drop_first_heading=False), 'lxml')
q = sb.find('h3'); ps = [p for p in sb.find_all('p')]
def phtml(p): return p.decode_contents().strip()
blocks = []; cur = {'title': None, 'paras': []}
for p in ps:
    t = T(p.get_text(' '))
    if p.find('strong') and T(p.find('strong').get_text()) == t and len(t) < 60:
        blocks.append(cur); cur = {'title': t, 'paras': []}
    else: cur['paras'].append(phtml(p))
blocks.append(cur)
pages['sovereign_ai'] = {'banner': N.local_img('https://www.newproducersgroup.org/wp-content/uploads/2023/11/Naadira-Team-1980x1320.jpg'),
  'question': T(q.get_text()), 'intro': blocks[0]['paras'], 'components': [b for b in blocks[1:] if b['title'] in ('AI Advisory Desk', 'Upstream National Emissions Dashboard')],
  'principle': next((b['paras'][-1] for b in blocks if b['title'] == 'Upstream National Emissions Dashboard'), ''),
  'support': next((b for b in blocks if b['title'] == 'Support this work'), None),
  'description': P['sovereign-ai-initiative']['desc']}
comp = pages['sovereign_ai']['components']
for c in comp:
    if c['title'] == 'Upstream National Emissions Dashboard' and len(c['paras']) > 1: c['paras'] = c['paras'][:-1]
with open(N.S('content/data/pages.yaml'), 'w') as f:
    yaml.safe_dump(pages, f, sort_keys=False, allow_unicode=True, width=1000)
print(yaml.safe_dump(pages['sovereign_ai'], allow_unicode=True, width=200))
print(yaml.safe_dump({k: (list(v.keys()) if isinstance(v, dict) else v) for k, v in pages.items()}, width=200)[:3000])
