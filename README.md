# NP4SE website

The new website for New Producers for Sustainable Energy (the New Producers Group), rebuilt from
everything on newproducersgroup.org as of 27 September 2026.

It is a static site: a small Python script turns the content files in `content/` into plain HTML pages
in `dist/`. There is no database, no WordPress and nothing to patch. Every page keeps the address it had
on the old site, so existing links, bookmarks and search results keep working.

| | |
|---|---|
| Pages | 260: 49 publications, 61 events, 23 country pages, 9 theme pages, 93 topic pages and the main pages |
| Images | 150 images from the old site (the organisation's photos, partner logos, event graphics), plus 26 licensed landscape and industry photos |
| Documents | 41 PDFs and media files, still served from the WordPress uploads folder (see *Before you switch the domain*) |

## Build it

You need Python 3.9 or newer.

```bash
pip install -r requirements.txt
python3 build.py                 # writes the site to dist/
python3 -m http.server -d dist   # then open http://localhost:8000
```

The build checks every internal link and stops with a list if any page links to a page that does not exist.

`python3 build.py --base-url https://ben-keller.github.io/np4se-redesign` builds for another address: every
internal link then starts with `/np4se-redesign/`, which is what a GitHub Pages project address needs. The
deploy workflow does this for you with whatever address GitHub Pages reports.

`python3 build.py --preview` writes a copy to `preview/` with relative links, forms switched off and no
external embeds. That is the version used for the shareable preview; don't deploy it.

## Deploy it (GitHub Pages)

`.github/workflows/deploy.yml` builds the site on GitHub and publishes it with GitHub Pages every time
something is pushed to `main`. `dist/` is not committed; GitHub builds it.

**One-time setup.** In the repository on GitHub, open *Settings → Pages* and under *Build and deployment*
set *Source* to **GitHub Actions**. Then push to `main`, or open *Actions → Deploy site to GitHub Pages →
Run workflow*. The first run takes a minute or two; the address appears on the run's summary page and in
*Settings → Pages*: https://ben-keller.github.io/np4se-redesign/.

While the site lives on that github.io address, search engines are asked not to index it, so it doesn't
compete with the live WordPress site (`index_on_github_io` in `content/data/site.yaml` turns this off).

**Custom domain.** When you are ready for the site to take over newproducersgroup.org (or a test subdomain
such as new.newproducersgroup.org first):

1. Optional but recommended: verify the domain for your account (GitHub profile *Settings → Pages → Add a
   domain*), which protects it from being claimed by another repository.
2. Enter the domain in the repository's *Settings → Pages → Custom domain*.
3. At the DNS provider, point `www` at `ben-keller.github.io` with a CNAME record. For the bare domain,
   add A records for 185.199.108.153, 185.199.109.153, 185.199.110.153 and 185.199.111.153 (and, if
   wanted, AAAA records for 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153 and
   2606:50c0:8003::153).
4. Tick *Enforce HTTPS* once GitHub has issued the certificate.
5. Run the workflow again (*Actions → Run workflow*). The build picks up the new address: links lose the
   `/np4se-redesign/` prefix, canonical links and the sitemap use the domain, and indexing is allowed.

No `CNAME` file is needed: with an Actions workflow GitHub keeps the domain in the repository settings.

**Forms.** GitHub Pages serves files only, so it cannot receive form posts. Until a form service is set up,
each form (contact, membership, sponsorship, partnership, subscribe, unsubscribe) opens the visitor's email
app with their message addressed to contact@newproducersgroup.org. To have submissions delivered straight
to an inbox, create an endpoint with a form service (Formspree, Basin, FormSubmit and similar), put its URL
in `form_action` in `content/data/site.yaml` and push; every form then posts there. The service will
handle visitors' names and email addresses, so check its terms and mention it in the privacy policy.

**Other hosts.** `dist/` is plain files and works on any static host (Netlify, Cloudflare Pages, an
ordinary web server). Old addresses redirect through small pages generated in `dist/`, so no server
rules are needed.

## Before you switch the domain

1. **Documents.** PDFs, the audio overview and one video are linked at
   `www.newproducersgroup.org/wp-content/uploads/…`. When this site replaces WordPress on the same
   domain, those files need a new home. Either:
   - run `python3 tools/fetch_documents.py --download` while the old site is still up, set
     `documents_host: /assets/docs/` in `content/data/site.yaml` and push, so the files ship with the
     site; or
   - keep WordPress running on a subdomain (for example archive.newproducersgroup.org) and set
     `documents_host` to its uploads folder.

   Either way, old links to `/wp-content/uploads/…` are forwarded to the new location by the 404 page.
2. **Forms.** Decide between the email fallback and a form service, then send a test message through
   each form and check it arrives.
3. **Redirects.** Old addresses that changed (`/map-4/`, `/event-tag/…`, `/events/…`, the encoded
   São Tomé address and a few old duplicates) get a small redirect page each; `/sliders/…` and old
   upload links are forwarded by the 404 page. `/members/` is new.
4. **Search engines.** Submit `https://www.newproducersgroup.org/sitemap.xml` in Google Search Console.

## Edit content

Everything editable is in `content/`. Change a file, run the build, and the change appears on every page
that uses it.

| To change | Edit |
|---|---|
| Menu, footer, emails, charity details, form settings | `content/data/site.yaml` |
| Text on the main pages (home, governance, how we work, impact, get involved, members area, events, Sovereign AI…) | `content/data/pages.yaml` |
| Member countries, regions, sector stages, observer status, map positions | `content/data/members.yaml` |
| Themes (name, colour, header photo) | `content/data/themes.yaml` |
| Field development plans, methane programme, working groups, privacy policy, terms | `content/pages/<name>.html` and `content/data/longform.yaml` |
| A publication | `content/publications/<slug>.md` |
| An event | `content/events/<slug>.md` |
| Curated resources on a country page | `content/countries/<slug>.md` |
| Licensed photos and their credits | `content/data/photos.yaml` and `assets/img/photos/` |

**Add a publication:** copy an existing file in `content/publications/`, rename it to the new address
(the file name becomes the URL), and edit the fields between the `---` lines:

```yaml
---
title: Title as it should appear
slug: file-name-without-md
date: 2026-10          # year-month, used for sorting
date_display: Oct 2026
type: Report           # Report, Policy brief, Paper, Article, Event summary or Video
authors: Name One, Name Two
themes: [energy-transition]          # slugs from themes.yaml
topics: [methane, licensing]         # slugs from topics.yaml
countries: [Ghana, Uganda]           # names as in members.yaml
image: /assets/img/wp/your-image.webp
summary: One or two sentences for cards and search.
documents:
- label: Download document
  url: https://…/your-file.pdf
---
<p>The body, in HTML.</p>
```

Events work the same way, with `date_start`, `date_end` (YYYY-MM-DD), `date_display`, an optional
`time` and `types` (Annual meeting, Training, Workshop or Virtual meeting). Country and theme pages,
the map panel, search, related items and the event summaries are all worked out from these fields, so
nothing else needs updating.

Images: save a WebP or JPEG under `assets/img/`, about 1400 px wide, and reference it by its path.

## How it fits together

- `build.py` loads `content/`, works out relationships (country ↔ publications and events, event ↔ its
  published summary, related items), renders `templates/*.html` with Jinja, copies `assets/`, and writes
  the map data (`np-data.js`), the search index (`search-index.js`), `sitemap.xml`, `robots.txt` and a
  redirect page for each old address that changed.
- `assets/css/site.css` holds the design: white ground, deep navy ink and one colour per region
  (lagoon for the Caribbean and Latin America, savanna for West Africa, laterite for Central, East and
  Southern Africa, Atlantic blue for the Middle East and Asia-Pacific), set in Source Serif 4 and
  Hanken Grotesk from Google Fonts.
- `assets/js/site.js` adds the menus, site search, list filters, form handling, video playback and the
  interactive maps. Every page still works without it.
- `assets/js/world.js` is the world map (Natural Earth outlines in the Equal Earth projection).
- `migration/` holds the scripts and raw export used once to move the content out of WordPress. They
  are kept for the record; re-running them overwrites hand edits, so they refuse to run without `--force`.

## Corrections made while moving the content

The content was copied as it was, with these fixes:

- **Partner logos (Get involved page):** the NRGI logo linked to Squire Patton Boggs and the OGCI logo to
  the Society of Petroleum Engineers; both now link to their own sites. The Squire Patton Boggs, IPIECA,
  Commonwealth Secretariat and Governance Action Hub logos had no link and now have one. The African
  Development Bank and Columbia Center logos appeared twice and now appear once.
- **AFREC logo** linked to cegce.org, an unrelated site; it now links to au-afrec.org.
- **Staatsolie sponsor logo** had no link; it now links to staatsolie.com.
- **Annual report 2024–25 page** embedded a story from stories.newproducersgroup.org that no longer
  exists (the page showed nothing). It now links to the report on Google Drive and the accounts at the
  Charity Commission.
- **Impact page:** the six spotlights and six quotes were images of text. They are now real text,
  readable by screen readers and search engines, each spotlight with a photo from the country.
- **One event date:** "National Oil Companies and Climate-Related Financial Risk" showed the date the
  site was copied (a WordPress default for events without a date). It is now 23 March 2021, from the
  events listing.
- Event start times of 12:00 am (meaning no time was set) are no longer shown.
- **Broken links fixed:** `/national-seminar-for-uganda-2019-2/`, `/event/government-review-of-field-development-plans-12-21-october-2020/`,
  an email address without `mailto:`, and the "Invite" link in the members area, which pointed at a
  page-builder anchor that no longer exists.
- A sentence repeated twice in a country resource blurb now appears once.
- The subscription page banner (a Getty Images photo) was not carried over.

**For the team to decide:** the old home page says the network has "over 1,000 government officials
from 22 countries" while the Impact page says "900+ members across 23 countries". Both are kept on
their pages; it would help to settle on one figure.

## Photography

Photos of meetings, trainings and exchanges are the organisation's own, taken from the old site. The
landscape and industry photographs are from Unsplash, used under the Unsplash License and credited on
`/photo-credits/`. Replacing them over time with photographs from member countries would make the site
more personal; `content/data/photos.yaml` lists them with their credits.
