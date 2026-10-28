#!/usr/bin/env python3
"""Make publication covers from the first page of each publication's PDF.

    python3 tools/make_covers.py            # download the PDFs that are missing, then make the covers
    python3 tools/make_covers.py --render   # make covers from PDFs already downloaded (no network)
    python3 tools/make_covers.py --force    # make every cover again

The PDFs are kept in tools/.pdf-cache/ (not committed). Each cover is written to
assets/img/covers/<publication slug>.webp, 600 px wide, and the next build shows it in the publication
lists, on the publication's page and in the featured block. Publications without a PDF keep their photo
or a plain title page. Run it while the old site is still online.

Downloading needs nothing beyond Python. Drawing the pages needs Pillow (in requirements.txt) and one of
pdftoppm (poppler), PyMuPDF, or on a Mac the built-in qlmanage/sips; without them the PDFs are still
downloaded, and the covers can be drawn later with --render.
"""
import re, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / 'tools' / '.pdf-cache'
OUT = ROOT / 'assets' / 'img' / 'covers'
WIDTH = 600
FRONT = re.compile(r'^---\n(.*?)\n---', re.S)


class CannotDraw(Exception):
    pass


def publications():
    """(slug, url of its first PDF) for every publication that has one."""
    for p in sorted((ROOT / 'content' / 'publications').glob('*.md')):
        fm = FRONT.match(p.read_text(encoding='utf-8')).group(1)
        slug = re.search(r'^slug:\s*(\S+)', fm, re.M).group(1).strip('\'"')
        for u in re.findall(r'^\s*(?:-\s*)?url:\s*(\S+)', fm, re.M):
            u = u.strip('\'"')
            if u.split('?')[0].lower().endswith('.pdf'):
                yield slug, u
                break


def download(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'np4se-site-covers'})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    if not data.startswith(b'%PDF'):
        raise ValueError('not a PDF')
    dest.write_bytes(data)


def first_page_png(pdf, tmp):
    """Draw page 1 of the PDF as a PNG in tmp and return its path."""
    png = tmp / 'page.png'
    if shutil.which('pdftoppm'):
        subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-png', '-singlefile', '-scale-to', str(WIDTH * 2),
                        str(pdf), str(tmp / 'page')], check=True, capture_output=True)
        return png
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf))
        page = doc[0]
        zoom = WIDTH * 2 / max(page.rect.width, page.rect.height)
        page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(str(png))
        return png
    except ImportError:
        pass
    if shutil.which('qlmanage'):   # macOS Quick Look draws the first page at the size asked for
        subprocess.run(['qlmanage', '-t', '-s', str(WIDTH * 2), '-o', str(tmp), str(pdf)], check=True, capture_output=True)
        made = tmp / (pdf.name + '.png')
        if made.exists():
            return made
    if shutil.which('sips'):       # macOS: converts the first page
        subprocess.run(['sips', '-s', 'format', 'png', str(pdf), '--out', str(png)], check=True, capture_output=True)
        return png
    raise CannotDraw('install poppler (brew install poppler) or PyMuPDF (pip install pymupdf)')


def render(pdf, dest):
    try:
        from PIL import Image
    except ImportError:
        raise CannotDraw('install Pillow (pip install -r requirements.txt)')
    with tempfile.TemporaryDirectory() as t:
        png = first_page_png(pdf, Path(t))
        with Image.open(png) as im:
            im = im.convert('RGB')
            if im.width > WIDTH:
                im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
            im.save(dest, 'WEBP', quality=82, method=6)


def main():
    render_only, force = '--render' in sys.argv, '--force' in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    made, kept, waiting, failed = 0, 0, 0, []
    for slug, url in publications():
        pdf, cover = CACHE / f'{slug}.pdf', OUT / f'{slug}.webp'
        if cover.exists() and not force:
            kept += 1
            continue
        if not pdf.exists():
            if render_only:
                failed.append((slug, 'PDF not downloaded yet'))
                continue
            try:
                download(url, pdf)
                print('downloaded', pdf.relative_to(ROOT))
                time.sleep(0.3)
            except Exception as e:  # keep going; report at the end
                failed.append((slug, f'download failed ({e})'))
                continue
        try:
            render(pdf, cover)
            made += 1
            print('cover', cover.relative_to(ROOT))
        except CannotDraw as e:
            waiting += 1
            reason = str(e)
        except subprocess.CalledProcessError as e:
            failed.append((slug, f'could not draw the PDF ({e.stderr.decode(errors="ignore")[:120].strip()})'))
    print(f'{made} covers made, {kept} already there')
    if waiting:
        print(f'{waiting} PDFs downloaded but not drawn: {reason}. Then run: python3 tools/make_covers.py --render')
    for slug, why in failed:
        print(f'  {slug}: {why}')


if __name__ == '__main__':
    main()
