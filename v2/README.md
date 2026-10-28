# Design v2

A second design for the NP4SE website, built from the same content as the main one. Every page, address,
map, filter and form is the same; what changes is how the site looks and reads. The two are built side
by side so they can be compared before deciding which goes live.

| | Main design | v2 |
|---|---|---|
| Type | Source Serif 4 headings with an italic accent, Hanken Grotesk text | Hanken Grotesk only, headings heavier and smaller, in sentence case. The design panel tries other typefaces on the same pages (see *Design panel*) |
| Colour | White and navy, four regional colours across the interface, tinted bands | White and navy with the NP4SE blue from the previous site (#0C6AB5) for links and buttons, and one bold blue block per page. Gold appears once, as a short rule over that block. The regional colours stay on the maps and in the thin four-colour lines |
| Labels | Uppercase labels over most headings | Type labels on publication and event listings only; elsewhere a plain way back to the section |
| Shapes | Rounded buttons, pills, chips, caption pills over photos, round buttons | Square buttons with small corners, tags and statuses as plain text, captions under photos, no floating buttons |
| Home | Text beside a collage of two photos | One full-width photograph with the ring badge on its edge |
| Sections | Statistics strip, four-card grids, split headings | Figures as a short list beside the introduction, two-column lists with rules, section titles over a thin navy rule |
| Publications | Coloured covers drawn in CSS | The first page of each PDF (see *Covers*), with a plain title page until it exists |
| Motion | Sunrise intro, logo hover, rising titles, scroll reveals, count-ups, map sweep, four-colour progress bars | The same, with the home photo rising from its horizon |

## Build and look at it

```bash
python3 build.py --design v2                  # writes dist-v2/
python3 -m http.server -d dist-v2             # then open http://localhost:8000
python3 build.py --design v2 --preview        # self-contained copy in preview-v2/
```

Every production build of the main design, including the one the deploy workflow runs on GitHub, also
builds v2 into `/v2/` next to it while `build_v2: true` is set in `content/data/site.yaml`. On GitHub
Pages that's https://ben-keller.github.io/np4se-redesign/v2/, and its pages ask search engines not to
index them. Set `build_v2` to false to stop publishing it.

## Design panel

Every v2 page has a *Design* button in its bottom-right corner. It opens a temporary panel for trying
colours and typefaces on the real pages, so the direction can be chosen by looking at the site itself.
The arrows at the top, or the arrow keys while the panel is open, step through thirteen presets; the
tabs below them open each part of the look.

| Preset | Typefaces | Colours and where they go |
|---|---|---|
| NP4SE blue (the default) | Hanken Grotesk | NP4SE blue links and bold block, a gold rule over it |
| Serif and Plex | Source Serif 4 headings, IBM Plex Sans text | NP4SE blue, as Valerie suggested |
| Previous site | Avenir Next | The previous site's blue headings and text colours |
| Navy and Plex | IBM Plex Sans | A navy bold block and footer, blue links |
| Logo colours | Libre Franklin headings, Public Sans text | The logo's navy, teal and gold |
| Teal and Newsreader | Newsreader headings, Source Sans 3 text | Teal, with plain labels and quieter photos |
| Paper and Literata | Literata headings, Fira Sans text, larger sizes | A warm paper ground and a deep blue block |
| Forest report | Bitter slab headings, Fira Sans text | Forest green and gold, a dark footer |
| Swiss graphite | Archivo with narrow headings, large sizes | Graphite and white, black-and-white photos, one blue |
| Data and mono | IBM Plex Sans, with Plex Mono for labels and figures | Navy, a dark header, duotone photos |
| Night | Hanken Grotesk | A dark ground with NP4SE blue and gold |
| Laterite and Jost | Jost headings, Source Serif 4 text | Terracotta and dark brown on warm paper |
| Blue bar | Instrument Sans | A blue header, a light blue bold block, a dark footer |

**Colour.** Nine colour sets, or a palette built from one base colour: its harmony (where the second
colour, used for the rule, sits on the colour wheel), vividness, the temperature of the greys, the ground
(white, paper, mist or dark) and the bold block (accent, deep, second colour, tint or ink). The builder
keeps every pair of text and background colours readable, at 4.5:1 or better.

*Where colour goes* is separate from the palette. It sets the header and footer colours (with the
reversed logo on dark ones), the section rules, the thin lines, how photos are treated (natural, muted,
black and white, duotone) and text contrast. Each colour can also be set by hand.

**Type.** Fourteen pairs, or a typeface for each role (headings, running text, labels and navigation,
figures and dates) from 21 typefaces in six kinds: grotesque, humanist and geometric sans, serif, slab
serif and monospaced. Heading sizes come in four scales, from compact to dramatic. Text size and line
spacing are set separately, as are the headings' weight, spacing and width and the labels' style
(capitals, small capitals or plain).

*Shuffle* buttons draw a random look from the same options, which is a quick way to see the range.
Whatever you choose stays on as you move between pages, in that browser only.

*Copy link* gives the page's address with the look in it (`?look=serif-plex`, or a longer code for a mix
of your own), so someone else sees the same thing. The self-contained preview copy built with `--preview`
leaves this button out, as it can't pass the look on through the address. *Copy settings* gives a block to
paste over the first one in `v2/assets/css/v2.css`, with the Google Fonts line its typefaces need and,
for coloured headers, footers or a dark ground, the few rules that go with it: that is how a chosen look
becomes the design. *Reset* goes back to the default.

Avenir Next is installed on Macs and iPhones only; elsewhere the panel shows Nunito Sans, a free typeface
close to it. Using Avenir Next for real would mean buying a web licence from Monotype, which is why the
previous site looked different on Windows. The panel itself is `v2/assets/js/look.js` and
`v2/assets/css/look.css`; setting `design_panel: false` in `content/data/site.yaml` takes it off the
pages, and the main design doesn't have it.

## Covers

`tools/make_covers.py` downloads each publication's PDF into `tools/.pdf-cache/` (not committed), draws
its first page and saves it as `assets/img/covers/<slug>.webp`. Run it once while the old site is still
up, from the project folder:

```bash
python3 tools/make_covers.py
```

It needs the internet and something that can draw a PDF page: on a Mac that's built in; elsewhere
install poppler or PyMuPDF. Then build as usual and commit `assets/img/covers/`. Publications whose PDF
is missing keep a plain title page; run the script again later to fill them in, or with `--force` to
redraw them all.

## How it is put together

- `v2/templates/` holds the templates that differ from `templates/`; the build looks there first and
  falls back to `templates/` for the rest, so content and page structure stay shared.
- `v2/assets/css/v2.css` is the whole stylesheet for this design. Its first block holds the look: colours,
  typefaces, sizes and the other variables the design panel changes. The second holds what stays the same
  in every look: the brand and map colours, layout sizes and easing.
- `assets/js/site.js` is shared. The v2 base template sets `window.NP_CFG` to point the count-ups at its
  own figures and add its blocks to the scroll animations.
- Headings that come from the content in title case (the workstreams, the spotlight titles) are shown in
  sentence case by the `sentence` filter in `build.py`. Country names, acronyms and the word after a
  dash or colon keep their capitals.

To make v2 the main design, copy `v2/templates/*` over `templates/` and `v2/assets/css/v2.css` into
`assets/css/`, set `build_v2: false` and build without `--design`. To drop it, set `build_v2: false` and
delete `v2/`.
