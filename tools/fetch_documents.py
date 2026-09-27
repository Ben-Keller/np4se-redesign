#!/usr/bin/env python3
"""Copy every document the site links to (PDFs, audio, video) from the WordPress uploads
folder into assets/docs/, so the site no longer depends on WordPress.

    python3 tools/fetch_documents.py            # list what would be downloaded
    python3 tools/fetch_documents.py --download # download into assets/docs/<year>/<month>/<file>

Then set `documents_host: /assets/docs/` in content/data/site.yaml and rebuild.
Run it while the old site is still online.
"""
import re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPLOADS = 'https://www.newproducersgroup.org/wp-content/uploads/'
DEST = ROOT / 'assets' / 'docs'

urls = set()
for p in list((ROOT / 'content').rglob('*.md')) + list((ROOT / 'content').rglob('*.html')) + list((ROOT / 'content').rglob('*.yaml')):
    for u in re.findall(r'https://www\.newproducersgroup\.org/wp-content/uploads/[^\s"\'<>)]+', p.read_text(encoding='utf-8')):
        u = u.split('?')[0].rstrip('.,')
        if not re.search(r'\.(jpe?g|png|gif|webp)$', u, re.I):
            urls.add(u)

print(f'{len(urls)} documents referenced')
if '--download' not in sys.argv:
    for u in sorted(urls):
        print(' ', u[len(UPLOADS):])
    sys.exit(0)

for u in sorted(urls):
    out = DEST / u[len(UPLOADS):]
    if out.exists():
        continue
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'np4se-site-migration'}), timeout=60) as r:
            out.write_bytes(r.read())
        print('saved', out.relative_to(ROOT))
    except Exception as e:  # keep going; report at the end
        print('FAILED', u, e)
    time.sleep(0.3)
