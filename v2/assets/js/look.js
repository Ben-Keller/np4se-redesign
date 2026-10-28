/* NP4SE design panel: a temporary tool for trying looks on the real pages.
   Colour comes from named sets or a palette builder (a base colour, a harmony, vividness, greys, the ground
   and the bold block), plus where colour goes (header, footer, section rules, thin lines, photos, text
   contrast). Type comes from named pairs or a typeface for each role across six kinds of type, plus scale,
   rhythm and details. The look is applied before the page is drawn, kept in this browser, and can be shared
   as a link (?look=...). To remove the panel, set design_panel: false in content/data/site.yaml (or delete
   this file, v2/assets/css/look.css and the two lines that load them in v2/templates/base.html). */
(function () {
  'use strict';
  var h = document.documentElement, KEY = 'np-look', TAB = 'np-look-tab';
  var SANS = 'ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif';
  var SERIF = 'Georgia,"Times New Roman",serif';
  var MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace';

  /* ---------- typefaces ---------- */
  var KINDS = [['grotesque', 'Grotesque sans'], ['humanist', 'Humanist sans'], ['geometric', 'Geometric sans'], ['serif', 'Serif'], ['slab', 'Slab serif'], ['mono', 'Monospaced']];
  /* w and tr: the heading weight and letter spacing that suit each typeface; wide: it comes in several widths */
  var FONTS = {
    hanken: { name: 'Hanken Grotesk', kind: 'grotesque', q: 'Hanken+Grotesk:ital,wght@0,100..900;1,100..900', base: true, w: 600, tr: -0.024 },
    instrument: { name: 'Instrument Sans', kind: 'grotesque', q: 'Instrument+Sans:ital,wdth,wght@0,75..100,400..700;1,75..100,400..700', w: 600, tr: -0.02, wide: true },
    archivo: { name: 'Archivo', kind: 'grotesque', q: 'Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900', w: 650, tr: -0.022, wide: true },
    schibsted: { name: 'Schibsted Grotesk', kind: 'grotesque', q: 'Schibsted+Grotesk:ital,wght@0,400..900;1,400..900', w: 650, tr: -0.022 },
    plex: { name: 'IBM Plex Sans', kind: 'grotesque', q: 'IBM+Plex+Sans:ital,wdth,wght@0,85..100,100..700;1,85..100,100..700', w: 600, tr: -0.018, wide: true },
    franklin: { name: 'Libre Franklin', kind: 'grotesque', q: 'Libre+Franklin:ital,wght@0,100..900;1,100..900', w: 600, tr: -0.02 },
    publicsans: { name: 'Public Sans', kind: 'grotesque', q: 'Public+Sans:ital,wght@0,100..900;1,100..900', w: 600, tr: -0.02 },
    sourcesans: { name: 'Source Sans 3', kind: 'humanist', q: 'Source+Sans+3:ital,wght@0,200..900;1,200..900', w: 600, tr: -0.012 },
    fira: { name: 'Fira Sans', kind: 'humanist', q: 'Fira+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,600', w: 600, tr: -0.012 },
    avenir: { name: 'Avenir Next', kind: 'geometric', stack: '"Avenir Next","Avenir Next LT Pro",Avenir,"Nunito Sans",' + SANS, q: 'Nunito+Sans:ital,opsz,wdth,wght@0,6..12,75..125,200..1000;1,6..12,75..125,200..1000', w: 600, tr: -0.012 },
    jost: { name: 'Jost', kind: 'geometric', q: 'Jost:ital,wght@0,100..900;1,100..900', w: 500, tr: -0.01 },
    sourceserif: { name: 'Source Serif 4', kind: 'serif', q: 'Source+Serif+4:ital,opsz,wght@0,8..60,200..900;1,8..60,200..900', w: 500, tr: -0.012 },
    newsreader: { name: 'Newsreader', kind: 'serif', q: 'Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800', w: 500, tr: -0.008 },
    literata: { name: 'Literata', kind: 'serif', q: 'Literata:ital,opsz,wght@0,7..72,200..900;1,7..72,200..900', w: 500, tr: -0.012 },
    spectral: { name: 'Spectral', kind: 'serif', q: 'Spectral:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', w: 500, tr: -0.01 },
    plexserif: { name: 'IBM Plex Serif', kind: 'serif', q: 'IBM+Plex+Serif:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', w: 500, tr: -0.012 },
    caslon: { name: 'Libre Caslon Text', kind: 'serif', q: 'Libre+Caslon+Text:ital,wght@0,400;0,700;1,400', w: 400, tr: -0.01 },
    bitter: { name: 'Bitter', kind: 'slab', q: 'Bitter:ital,wght@0,100..900;1,100..900', w: 600, tr: -0.015 },
    zilla: { name: 'Zilla Slab', kind: 'slab', q: 'Zilla+Slab:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400', w: 600, tr: -0.008 },
    plexmono: { name: 'IBM Plex Mono', kind: 'mono', q: 'IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400', w: 500, tr: -0.02 },
    jetbrains: { name: 'JetBrains Mono', kind: 'mono', q: 'JetBrains+Mono:ital,wght@0,100..800;1,100..800', w: 500, tr: -0.02 }
  };
  Object.keys(FONTS).forEach(function (id) {
    var f = FONTS[id];
    if (!f.stack) f.stack = '"' + f.name + '",' + (f.kind === 'mono' ? MONO : f.kind === 'serif' || f.kind === 'slab' ? SERIF : SANS);
  });
  /* pairs: headings and text, sometimes a third typeface for labels and figures */
  var TYPE = {
    hanken: { name: 'Hanken Grotesk', head: 'hanken', body: 'hanken' },
    serifplex: { name: 'Source Serif 4 and IBM Plex Sans', head: 'sourceserif', body: 'plex' },
    avenir: { name: 'Avenir Next', head: 'avenir', body: 'avenir' },
    plex: { name: 'IBM Plex Sans', head: 'plex', body: 'plex' },
    franklin: { name: 'Libre Franklin and Public Sans', head: 'franklin', body: 'publicsans' },
    newsreader: { name: 'Newsreader and Source Sans 3', head: 'newsreader', body: 'sourcesans' },
    literata: { name: 'Literata and Fira Sans', head: 'literata', body: 'fira' },
    bitter: { name: 'Bitter and Fira Sans', head: 'bitter', body: 'fira' },
    archivo: { name: 'Archivo, narrow headings', head: 'archivo', body: 'archivo', width: 85, w: 650, tr: -0.03 },
    jost: { name: 'Jost and Source Serif 4', head: 'jost', body: 'sourceserif', ui: 'jost' },
    caslon: { name: 'Libre Caslon and Libre Franklin', head: 'caslon', body: 'franklin' },
    schibsted: { name: 'Schibsted Grotesk and Newsreader', head: 'schibsted', body: 'newsreader', ui: 'schibsted' },
    instrument: { name: 'Instrument Sans', head: 'instrument', body: 'instrument' },
    plexmono: { name: 'IBM Plex Sans with Plex Mono', head: 'plex', body: 'plex', ui: 'plexmono', fig: 'plexmono' }
  };
  var TDEF = { tw: 400, size: 17, leading: 1.6, scale: 'standard', labels: 'caps' };   /* what a pair leaves as it is */
  var SCALES = { compact: [0.84, 0.88, 0.93, 0.96], standard: [1, 1, 1, 1], generous: [1.14, 1.1, 1.06, 1.03], dramatic: [1.32, 1.2, 1.1, 1.05] };
  var SCALE_OPTS = [['compact', 'Compact'], ['standard', 'Standard'], ['generous', 'Generous'], ['dramatic', 'Dramatic']];
  var LABELS = { caps: ['12px', 600, '.06em', 'uppercase', 'normal'], small: ['14px', 600, '.03em', 'none', 'all-small-caps'], plain: ['13.5px', 500, '0em', 'none', 'normal'] };
  var LABEL_OPTS = [['caps', 'Capitals'], ['small', 'Small capitals'], ['plain', 'Plain']];

  /* ---------- colours ---------- */
  var CKEYS = ['accent', 'block', 'ink', 'head', 'bg', 'surface', 'rule'];
  /* accent: links and buttons; block: the one bold block on each page; rule: the short line over its heading.
     Greys, tints and the colours used on the block are worked out from these. A set given as b comes from the
     palette builder. */
  var COLOURS = {
    blue: { name: 'NP4SE blue', accent: '#0C6AB5', block: '#0C6AB5', ink: '#0F2B3D', head: '#0F2B3D', bg: '#FFFFFF', surface: '#F4F6F8', rule: '#DDA12E' },
    navy: { name: 'Navy', accent: '#0C6AB5', block: '#0F2B3D', ink: '#0F2B3D', head: '#0F2B3D', bg: '#FFFFFF', surface: '#F3F5F7', rule: '#DDA12E' },
    teal: { name: 'Teal', accent: '#00665F', block: '#00665F', ink: '#0F2B3D', head: '#0F2B3D', bg: '#FFFFFF', surface: '#F1F6F5', rule: '#DDA12E' },
    logo: { name: 'Logo colours', accent: '#00766C', block: '#0F2B3D', ink: '#0F2B3D', head: '#0F2B3D', bg: '#FFFFFF', surface: '#F2F6F6', rule: '#DDA12E' },
    previous: { name: 'Previous site', accent: '#0C6AB5', block: '#0C6AB5', ink: '#1E1B33', ink2: '#59517D', head: '#0C6AB5', bg: '#FFFFFF', surface: '#F8F8F8', rule: '#00A8E8' },
    forest: { name: 'Forest', accent: '#1D6A50', block: '#143F33', ink: '#14261F', head: '#14261F', bg: '#FFFFFF', surface: '#F2F5F3', rule: '#D9A63A' },
    laterite: { name: 'Laterite', accent: '#A9452B', block: '#3B2A23', ink: '#2B211C', head: '#2B211C', bg: '#FBF8F2', surface: '#F1EBE1', rule: '#D9A63A' },
    graphite: { name: 'Graphite', accent: '#0C6AB5', block: '#22262B', ink: '#1F2328', head: '#1F2328', bg: '#FFFFFF', surface: '#F3F4F5', rule: '#4F9BD9' },
    night: { name: 'Night', b: { base: '#0C6AB5', harmony: 'opposite', turn: 180, vivid: 0.5, temp: 'cool', ground: 'dark', block: 'accent' } }
  };
  var HARMONY = [['mono', 'One hue'], ['neighbour', 'Neighbours'], ['opposite', 'Opposites'], ['split', 'Split'], ['triad', 'Triad']];
  var TEMPS = [['cool', 'Cool'], ['neutral', 'Neutral'], ['warm', 'Warm'], ['tinted', 'Tinted']];
  var GROUNDS = [['white', 'White'], ['paper', 'Paper'], ['mist', 'Mist'], ['dark', 'Dark']];
  var BLOCKS = [['accent', 'Accent'], ['deep', 'Deep'], ['second', 'Second'], ['tint', 'Tint'], ['ink', 'Ink']];
  var USAGE = {
    header: ['Header', [['plain', 'Page'], ['tint', 'Light'], ['accent', 'Accent'], ['block', 'Block'], ['ink', 'Dark']]],
    footer: ['Footer', [['light', 'Light'], ['plain', 'Page'], ['block', 'Block'], ['ink', 'Dark']]],
    rules: ['Section rules', [['head', 'Headings'], ['accent', 'Accent'], ['rule', 'Rule'], ['light', 'Faint']]],
    lines: ['Thin lines', [['four', 'Four colours'], ['accent', 'Accent'], ['rule', 'Rule']]],
    photo: ['Photos', [['natural', 'Natural'], ['muted', 'Muted'], ['mono', 'Black and white'], ['duo', 'Duotone']]],
    contrast: ['Text contrast', [['soft', 'Softer'], ['standard', 'Standard'], ['strong', 'Stronger']]]
  };
  var UDEF = { header: 'plain', footer: 'light', rules: 'head', lines: 'four', photo: 'natural', contrast: 'standard' };
  var LINES4 = 'linear-gradient(90deg,var(--lagoon) 0 25%,var(--savanna) 0 50%,var(--laterite) 0 75%,var(--atlantic) 0)';
  var PHOTO = { natural: 'none', muted: 'saturate(.55) contrast(.96)', mono: 'grayscale(1) contrast(1.04)', duo: 'url(#lk-duo)' };
  var CONTRAST = { soft: [0.26, 0.42], standard: [0.17, 0.32], strong: [0.08, 0.2] };   /* how far secondary text moves towards the ground */

  /* ---------- presets: whole looks ---------- */
  var PRESETS = [
    { id: 'np4se', name: 'NP4SE blue', colours: 'blue', type: 'hanken', note: 'Hanken Grotesk throughout, with NP4SE blue for links and the bold block.' },
    { id: 'serif-plex', name: 'Serif and Plex', colours: 'blue', type: 'serifplex', note: 'Source Serif 4 headings and IBM Plex Sans text in NP4SE blue, as Valerie suggested.' },
    { id: 'previous', name: 'Previous site', colours: 'previous', type: 'avenir', note: 'Avenir Next with blue headings and the previous site’s text colours.' },
    { id: 'navy-plex', name: 'Navy and Plex', colours: 'navy', type: 'plex', u: { footer: 'block' }, note: 'IBM Plex Sans throughout, with a navy bold block and footer and blue links.' },
    { id: 'logo', name: 'Logo colours', colours: 'logo', type: 'franklin', note: 'Libre Franklin headings and Public Sans text in the logo’s navy, teal and gold.' },
    { id: 'teal', name: 'Teal and Newsreader', colours: 'teal', type: 'newsreader', t: { size: 18, leading: 1.65, labels: 'plain' }, u: { photo: 'muted' }, note: 'Newsreader headings and Source Sans 3 text with a teal bold block, plain labels and quieter photos.' },
    { id: 'paper', name: 'Paper and Literata', b: { base: '#0C6AB5', harmony: 'opposite', turn: 180, vivid: 0.5, temp: 'warm', ground: 'paper', block: 'deep' }, type: 'literata', t: { size: 18, leading: 1.7, scale: 'generous', labels: 'small' }, note: 'A warm paper ground and a deep blue block, Literata headings over Fira Sans, larger sizes and small-capital labels.' },
    { id: 'report', name: 'Forest report', colours: 'forest', type: 'bitter', u: { footer: 'ink', rules: 'accent' }, note: 'Bitter slab headings and Fira Sans text in forest green and gold, with a dark footer, like a printed report.' },
    { id: 'swiss', name: 'Swiss graphite', colours: 'graphite', type: 'archivo', t: { scale: 'dramatic', labels: 'plain' }, u: { lines: 'accent', photo: 'mono' }, note: 'Narrow Archivo headings at large sizes on graphite and white, black-and-white photos and one blue.' },
    { id: 'data', name: 'Data and mono', colours: 'navy', type: 'plexmono', t: { size: 16, leading: 1.55, scale: 'compact' }, u: { header: 'ink', photo: 'duo' }, note: 'IBM Plex Sans with Plex Mono for labels and figures, compact sizes, a dark header and duotone photos.' },
    { id: 'night', name: 'Night', colours: 'night', type: 'hanken', u: { photo: 'muted' }, note: 'A dark ground with light text, NP4SE blue and gold, made with the palette builder.' },
    { id: 'laterite', name: 'Laterite and Jost', colours: 'laterite', type: 'jost', t: { labels: 'small' }, u: { footer: 'block' }, note: 'Terracotta and dark brown on warm paper, with Jost headings and Source Serif 4 text.' },
    { id: 'blue-bar', name: 'Blue bar', b: { base: '#0C6AB5', harmony: 'opposite', turn: 180, vivid: 0.5, temp: 'cool', ground: 'white', block: 'tint' }, type: 'instrument', u: { header: 'accent', footer: 'ink' }, note: 'A blue header with the reversed logo, a light blue bold block and Instrument Sans throughout.' }
  ];

  /* ---------- colour arithmetic ---------- */
  function rgb(c) { c = String(c).replace('#', ''); return [parseInt(c.substr(0, 2), 16), parseInt(c.substr(2, 2), 16), parseInt(c.substr(4, 2), 16)]; }
  function hex(a) { return '#' + a.map(function (v) { v = Math.round(Math.max(0, Math.min(255, v))); return (v < 16 ? '0' : '') + v.toString(16); }).join('').toUpperCase(); }
  function mix(a, b, t) { var A = rgb(a), B = rgb(b); return hex(A.map(function (v, i) { return v + (B[i] - v) * t; })); }   /* t = share of b */
  function lum(c) { var w = [0.2126, 0.7152, 0.0722]; return rgb(c).reduce(function (s, v, i) { v /= 255; return s + w[i] * (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)); }, 0); }
  function contrast(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function isDark(c) { return contrast(c, '#000000') < contrast(c, '#FFFFFF'); }
  function toward(fg, bg, t) { while (t > 0 && contrast(mix(fg, bg, t), bg) < 4.5) t -= 0.01; return mix(fg, bg, Math.max(0, t)); }   /* fg moved towards bg, but still readable on it */
  /* OKLCH (lightness 0–1, chroma, hue in degrees): the builder works here, where equal steps look equal */
  function lin(v) { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
  function gam(v) { return 255 * (v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055); }
  function toLch(c) {
    var a = rgb(c).map(lin);
    var l = Math.cbrt(0.4122214708 * a[0] + 0.5363325363 * a[1] + 0.0514459929 * a[2]);
    var m = Math.cbrt(0.2119034982 * a[0] + 0.6806995451 * a[1] + 0.1073969566 * a[2]);
    var s = Math.cbrt(0.0883024619 * a[0] + 0.2817188376 * a[1] + 0.6299787005 * a[2]);
    var L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s;
    var A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s;
    var B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s;
    var H = Math.atan2(B, A) * 180 / Math.PI;
    return [L, Math.sqrt(A * A + B * B), H < 0 ? H + 360 : H];
  }
  function lchLin(L, C, H) {
    var r = H * Math.PI / 180, A = C * Math.cos(r), B = C * Math.sin(r);
    var l = L + 0.3963377774 * A + 0.2158037573 * B, m = L - 0.1055613458 * A - 0.0638541728 * B, s = L - 0.0894841775 * A - 1.2914855480 * B;
    l = l * l * l; m = m * m * m; s = s * s * s;
    return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s];
  }
  function fits(x) { return x.every(function (v) { return v >= -0.0001 && v <= 1.0001; }); }
  function lch(L, C, H) {   /* to hex, giving up chroma (not lightness or hue) where the screen can't show it */
    L = Math.max(0, Math.min(1, L)); C = Math.max(0, C);
    var x = lchLin(L, C, H);
    if (!fits(x)) { var lo = 0, hi = C; for (var i = 0; i < 24; i++) { var mid = (lo + hi) / 2; if (fits(lchLin(L, mid, H))) lo = mid; else hi = mid; } x = lchLin(L, lo, H); }
    return hex(x.map(function (v) { return gam(Math.max(0, Math.min(1, v))); }));
  }
  function reach(H, C, against, min, L, dir) {   /* hue H at chroma C, from lightness L outwards until it has contrast min */
    for (var i = 0; i < 100; i++) { var c = lch(L, C, H); if (contrast(c, against) >= min) return c; L += dir * 0.01; if (L < 0 || L > 1) break; }
    return dir < 0 ? '#000000' : '#FFFFFF';
  }

  /* ---------- the palette builder ---------- */
  var SHIFT = { mono: 0, neighbour: 40, opposite: 180, split: 150, triad: 120 };   /* where the second colour sits on the colour wheel */
  var GREY = { cool: [245, 0.035], neutral: [0, 0], warm: [70, 0.02], tinted: [-1, 0.035] };   /* the hue and chroma of the greys */
  function build(b) {
    var o = toLch(b.base), L0 = o[0], H = o[1] < 0.02 ? 250 : o[2], dark = b.ground === 'dark';
    var m = b.vivid <= 0.5 ? 0.25 + 1.5 * b.vivid : 1 + (b.vivid - 0.5) * 1.2;   /* at 0.5 the base colour keeps its own strength */
    var g = GREY[b.temp], gh = g[0] < 0 ? H : g[0], gc = g[1];
    var bg, surface, ink, head;
    if (dark) {
      bg = lch(0.2, gc * 0.7, gh); surface = lch(0.245, gc * 0.8, gh); ink = lch(0.93, gc * 0.3, gh); head = lch(0.98, gc * 0.15, gh);
    } else {
      bg = b.ground === 'paper' ? lch(0.983, 0.011, 85) : b.ground === 'mist' ? lch(0.982, gc ? 0.007 : 0, gh) : '#FFFFFF';
      surface = b.ground === 'paper' ? lch(0.953, 0.017, 85) : lch(0.963, gc ? Math.max(0.005, gc * 0.2) : 0, gh);
      ink = lch(0.27, gc * 1.4, gh); head = ink;
    }
    var ca = o[1] * m;   /* the base colour as picked, at the lightness its ground needs */
    var accent = reach(H, ca, bg, 4.6, L0, dark ? 1 : -1);
    var H2 = (H + (b.turn != null ? b.turn : SHIFT[b.harmony]) + 360) % 360;
    var block = {
      accent: reach(H, ca, '#FFFFFF', 4.6, L0, -1),
      deep: lch(dark ? 0.33 : 0.3, Math.min(ca, 0.085), H),
      second: b.harmony === 'mono' ? lch(0.37, ca * 0.75, H) : reach(H2, Math.max(ca, 0.06), '#FFFFFF', 4.6, Math.min(L0, 0.6), -1),
      tint: dark ? lch(0.3, Math.min(0.06, 0.02 + ca * 0.25), H) : lch(0.95, Math.min(0.05, 0.012 + ca * 0.2), H),
      ink: dark ? lch(0.9, gc * 0.4, gh) : ink
    }[b.block];
    var rh = b.harmony === 'mono' ? H : H2, rc = Math.max(0.03, Math.min(0.2, 0.15 * m));
    var rule = isDark(block) ? reach(rh, rc, block, 2.6, 0.78, 1) : reach(rh, rc, block, 2.6, 0.62, -1);
    return { accent: accent, block: block, ink: ink, head: head, bg: bg, surface: surface, rule: rule };
  }
  function nearest(list, value) {
    var best = list[0][0], d = 1e9;
    list.forEach(function (o) { var x = Math.abs(o[1] - value); if (x < d) { d = x; best = o[0]; } });
    return best;
  }
  function guessBuilder(c) {   /* a starting point for the builder that keeps close to the palette in use */
    var a = toLch(c.accent), i = toLch(c.ink), bg = toLch(c.bg), bl = toLch(c.block);
    var temp = i[1] < 0.012 ? 'neutral' : i[2] > 195 && i[2] < 290 ? 'cool' : i[2] > 40 && i[2] < 110 ? 'warm' : 'tinted';
    var ground = isDark(c.bg) ? 'dark' : bg[1] < 0.004 ? 'white' : bg[2] > 50 && bg[2] < 110 ? 'paper' : 'mist';
    var block = c.block === c.accent ? 'accent' : !isDark(c.block) ? 'tint' : bl[0] < 0.4 ? (bl[1] < 0.03 ? 'ink' : 'deep') : 'accent';
    var turn = Math.round((toLch(c.rule)[2] - a[2] + 540) % 360 - 180);   /* keep the rule's own hue: -180 to 180 degrees from the accent */
    var harmony = nearest([['mono', 0], ['neighbour', 40], ['triad', 120], ['split', 150], ['opposite', 180]], Math.abs(turn));
    return { base: c.accent, harmony: harmony, turn: harmony === 'mono' ? 0 : turn, vivid: 0.5, temp: temp, ground: ground, block: block };
  }

  /* ---------- looks: build, check, compare ---------- */
  function copy(o) { return JSON.parse(JSON.stringify(o)); }
  function same(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
  function assign(a, b) { Object.keys(b || {}).forEach(function (k) { a[k] = b[k]; }); return a; }
  function colourSet(id) {
    var k = COLOURS[id];
    if (k.b) return { cid: id, b: copy(k.b), c: build(k.b) };
    var c = {};
    CKEYS.forEach(function (x) { c[x] = k[x]; });
    if (k.ink2) c.ink2 = k.ink2;
    return { cid: id, b: null, c: c };
  }
  function typeSet(id) {
    var p = TYPE[id], f = FONTS[p.head];
    return { head: p.head, body: p.body, ui: p.ui || p.body, fig: p.fig || p.head, weight: p.w || f.w, track: p.tr != null ? p.tr : f.tr, width: p.width || 100 };
  }
  function fromPreset(p) {
    var col = p.colours ? colourSet(p.colours) : { cid: null, b: copy(p.b), c: build(p.b) };
    return clean({ cid: col.cid, tid: p.type, b: col.b, c: col.c, u: assign(assign({}, UDEF), p.u), t: assign(assign(typeSet(p.type), TDEF), p.t) });
  }
  var HEX = /^#[0-9A-Fa-f]{6}$/;
  function inList(list, v, d) { for (var i = 0; i < list.length; i++) if (list[i][0] === v) return v; return d; }
  function num(v, lo, hi, step, d) { v = +v; if (!isFinite(v)) return d; return +Math.max(lo, Math.min(hi, Math.round(v / step) * step)).toFixed(4); }
  /* Only well-formed looks are applied (links and storage are outside our control). clean() also fills in what
     older looks lack and puts every look's keys in the same order, so two looks can be compared as text. */
  function clean(s) {
    if (!s || typeof s !== 'object' || !s.c || !s.t) return null;
    var out = { cid: COLOURS[s.cid] ? s.cid : null, tid: TYPE[s.tid] ? s.tid : null, b: null, c: {}, u: {}, t: {} };
    for (var i = 0; i < CKEYS.length; i++) { if (!HEX.test(s.c[CKEYS[i]] || '')) return null; out.c[CKEYS[i]] = s.c[CKEYS[i]].toUpperCase(); }
    if (s.c.ink2 && HEX.test(s.c.ink2)) out.c.ink2 = s.c.ink2.toUpperCase();
    var b = s.b;
    if (b && typeof b === 'object' && HEX.test(b.base || '')) {
      var hm = inList(HARMONY, b.harmony, 'opposite');
      out.b = { base: b.base.toUpperCase(), harmony: hm, turn: hm === 'mono' ? 0 : num(b.turn, -180, 180, 1, SHIFT[hm]), vivid: num(b.vivid, 0, 1, 0.05, 0.5),
        temp: inList(TEMPS, b.temp, 'cool'), ground: inList(GROUNDS, b.ground, 'white'), block: inList(BLOCKS, b.block, 'accent') };
    }
    var u = s.u || {};
    Object.keys(USAGE).forEach(function (k) { out.u[k] = inList(USAGE[k][1], u[k], UDEF[k]); });
    var t = s.t, head = FONTS[t.head] ? t.head : 'hanken', body = FONTS[t.body] ? t.body : 'hanken';
    out.t = { head: head, body: body, ui: FONTS[t.ui] ? t.ui : body, fig: FONTS[t.fig] ? t.fig : head,
      weight: num(t.weight, 300, 900, 50, 600), track: num(t.track, -0.06, 0.04, 0.001, 0), width: num(t.width, 62, 125, 1, 100),
      tw: num(t.tw, 300, 500, 50, 400), size: num(t.size, 15, 20, 0.5, 17), leading: num(t.leading, 1.35, 1.95, 0.05, 1.6),
      scale: SCALES[t.scale] ? t.scale : 'standard', labels: LABELS[t.labels] ? t.labels : 'caps' };
    return out;
  }
  var PSTATES = PRESETS.map(fromPreset);
  function presetOf(s) { for (var i = 0; i < PSTATES.length; i++) if (same(s, PSTATES[i])) return PRESETS[i]; return null; }
  function isDefault(s) { return !s || same(s, PSTATES[0]); }

  /* ---------- from a look to the stylesheet's variables ---------- */
  function vars(s) {
    var c = s.c, t = s.t, u = s.u, v = {};
    var darkGround = isDark(c.bg), deep = isDark(c.ink) ? c.ink : c.bg, lift = darkGround ? '#FFFFFF' : '#000000';
    var onAccent = contrast(c.accent, '#FFFFFF') >= 4.5 ? '#FFFFFF' : deep;
    var onBlock = contrast(c.block, '#FFFFFF') >= 4.5 ? '#FFFFFF' : deep;
    var k = CONTRAST[u.contrast];
    v['--bg'] = c.bg; v['--surface'] = c.surface; v['--mist'] = mix(c.surface, c.ink, 0.05);
    v['--ink'] = c.ink; v['--ink-2'] = c.ink2 && u.contrast === 'standard' ? c.ink2 : mix(c.ink, c.bg, k[0]); v['--ink-3'] = mix(c.ink, c.bg, k[1]);
    v['--line'] = mix(c.ink, c.bg, 0.85); v['--line-2'] = mix(c.ink, c.bg, 0.92); v['--line-strong'] = mix(c.ink, c.bg, 0.76);
    v['--heading'] = c.head; v['--sec-rule'] = { head: c.head, accent: c.accent, rule: c.rule, light: mix(c.ink, c.bg, 0.76) }[u.rules];
    v['--accent'] = c.accent; v['--accent-hover'] = mix(c.accent, lift, 0.16); v['--accent-press'] = mix(c.accent, lift, 0.3);
    v['--accent-tint'] = mix(c.accent, c.bg, 0.91); v['--accent-line'] = mix(c.accent, c.bg, 0.55); v['--on-accent'] = onAccent;
    v['--block'] = c.block; v['--on-block'] = onBlock; v['--on-block-2'] = toward(onBlock, c.block, 0.12); v['--on-block-3'] = toward(onBlock, c.block, 0.18);
    v['--on-block-rule'] = mix(onBlock, c.block, 0.4); v['--on-block-line'] = mix(onBlock, c.block, 0.72);
    v['--on-block-wash'] = mix(c.block, onBlock, 0.08); v['--on-block-hover'] = mix(onBlock, c.block, 0.08);
    v['--rule'] = c.rule;
    v['--lines'] = { four: LINES4, accent: c.accent, rule: c.rule }[u.lines];
    v['--photo-filter'] = PHOTO[u.photo];
    v['--logo-sun'] = darkGround ? '#E9B54A' : '#DDA12E'; v['--logo-line'] = darkGround ? '#FFFFFF' : '#00665F';
    v['--font-head'] = FONTS[t.head].stack; v['--font-body'] = FONTS[t.body].stack; v['--font-ui'] = FONTS[t.ui].stack; v['--font-fig'] = FONTS[t.fig].stack;
    v['--head-weight'] = String(t.weight); v['--track'] = t.track + 'em'; v['--head-width'] = t.width + '%';
    v['--text-f'] = String(+(t.size / 17).toFixed(4)); v['--leading'] = String(t.leading); v['--text-weight'] = String(t.tw);
    var sc = SCALES[t.scale];
    v['--h1-f'] = String(sc[0]); v['--h2-f'] = String(sc[1]); v['--h3-f'] = String(sc[2]); v['--h4-f'] = String(sc[3]);
    var lb = LABELS[t.labels];
    v['--label-size'] = lb[0]; v['--label-weight'] = String(lb[1]); v['--label-track'] = lb[2]; v['--label-case'] = lb[3]; v['--label-caps'] = lb[4];
    return v;
  }
  /* the header or footer drawn on a colour of its own: the same variables, worked out for that colour */
  function partColour(s, part) {
    var c = s.c, darkest = isDark(c.ink) ? c.ink : mix(c.bg, '#000000', 0.35);
    if (part === 'header') return { plain: null, tint: c.surface, accent: c.accent, block: c.block, ink: darkest }[s.u.header];
    return { light: null, plain: c.bg, block: c.block, ink: darkest }[s.u.footer];
  }
  function scheme(X, s, footer) {
    var c = s.c, dx = isDark(X), lightC = isDark(c.ink) ? c.bg : c.ink, darkC = isDark(c.ink) ? c.ink : c.bg;
    var fg = dx ? (contrast(lightC, X) >= 7 ? lightC : '#FFFFFF') : (contrast(darkC, X) >= 7 ? darkC : '#000000');
    var ac = contrast(c.accent, X) >= 4.5 ? c.accent : fg, lift = ac === fg ? X : dx ? '#FFFFFF' : '#000000';   /* links in the text colour dim a little on hover */
    return { '--bg': X, '--surface': footer ? X : mix(X, fg, 0.06), '--mist': mix(X, fg, 0.1),
      '--ink': fg, '--ink-2': mix(fg, X, 0.18), '--ink-3': mix(fg, X, 0.34),
      '--line': mix(fg, X, dx ? 0.78 : 0.85), '--line-2': mix(fg, X, 0.9), '--line-strong': mix(fg, X, 0.7), '--heading': fg, '--sec-rule': fg,
      '--accent': ac, '--accent-hover': mix(ac, lift, 0.16), '--accent-press': mix(ac, lift, 0.3), '--accent-tint': mix(ac, X, 0.85), '--accent-line': mix(ac, X, 0.5),
      '--on-accent': contrast(ac, '#FFFFFF') >= 4.5 ? '#FFFFFF' : (isDark(fg) ? fg : X),
      '--logo-sun': dx ? '#E9B54A' : '#DDA12E', '--logo-line': dx ? '#FFFFFF' : '#00665F' };
  }
  var PAPER = { '--bg': '#FFFFFF', '--surface': '#F4F6F8', '--mist': '#E9ECEF', '--ink': '#0F2B3D', '--ink-2': '#384F5E', '--ink-3': '#5C6F7B', '--line': '#DBDFE2', '--line-2': '#ECEEEF', '--line-strong': '#C5CCD0', '--heading': '#0F2B3D' };
  function decl(v) { return Object.keys(v).map(function (k) { return k + ':' + v[k]; }).join(';'); }
  function scopedCss(s) {
    var out = '', hx = partColour(s, 'header'), fx = partColour(s, 'footer');
    if (hx) out += '/* the header on a colour of its own */\nheader.top{' + decl(scheme(hx, s)) + '}\n';
    if (fx) out += '/* the footer on a colour of its own */\n.site-foot{' + decl(scheme(fx, s, true)) + '}\n';
    if (isDark(s.c.bg)) out += '/* on a dark ground, maps, title pages and partner logos stay on white */\n.mapwrap,.locator,.doc-ph,.logos li{' + decl(PAPER) + '}\n';
    return out;
  }
  function duoSvg(s) {   /* the duotone for photos: shadows in the darkest colour, highlights in a pale version of the rule */
    var a = rgb(isDark(s.c.ink) ? s.c.ink : s.c.bg), b = rgb(mix(s.c.rule, '#FFFFFF', 0.72));
    var t = function (i) { return (a[i] / 255).toFixed(3) + ' ' + (b[i] / 255).toFixed(3); };
    return '<svg id="lk-svg" width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><filter id="lk-duo" color-interpolation-filters="sRGB">' +
      '<feColorMatrix type="matrix" values=".2126 .7152 .0722 0 0 .2126 .7152 .0722 0 0 .2126 .7152 .0722 0 0 0 0 0 1 0"/>' +
      '<feComponentTransfer><feFuncR type="table" tableValues="' + t(0) + '"/><feFuncG type="table" tableValues="' + t(1) + '"/><feFuncB type="table" tableValues="' + t(2) + '"/></feComponentTransfer></filter></svg>';
  }

  /* ---------- keep, share and apply ---------- */
  function save(s) { try { if (s && !isDefault(s)) localStorage.setItem(KEY, JSON.stringify(s)); else localStorage.removeItem(KEY); } catch (e) { /* private mode: fine */ } }
  function stored() { try { return clean(JSON.parse(localStorage.getItem(KEY) || 'null')); } catch (e) { return null; } }
  function encode(s) {
    var p = presetOf(s);
    if (p) return p.id;
    return btoa(JSON.stringify(s)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
  function decode(q) {
    for (var i = 0; i < PRESETS.length; i++) if (PRESETS[i].id === q) return copy(PSTATES[i]);
    try { return clean(JSON.parse(atob(q.replace(/-/g, '+').replace(/_/g, '/')))); } catch (e) { return null; }
  }
  function loadFont(id) {
    var f = FONTS[id];
    if (!f || f.base || document.getElementById('np-font-' + id)) return;
    var l = document.createElement('link');
    l.id = 'np-font-' + id; l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=' + f.q + '&display=swap';
    (document.head || h).appendChild(l);
  }
  function scopedEl() {
    var el = document.getElementById('lk-scoped');
    if (!el) { el = document.createElement('style'); el.id = 'lk-scoped'; (document.head || h).appendChild(el); }
    return el;
  }
  function placeDuo(s) {
    var old = document.getElementById('lk-svg');
    if (old) old.parentNode.removeChild(old);
    if (!s || s.u.photo !== 'duo') return;
    var d = document.createElement('div');
    d.innerHTML = duoSvg(s);
    (document.body || h).appendChild(d.firstChild);
  }
  function themeColour(c) { var m = document.querySelector('meta[name="theme-color"]'); if (m) m.setAttribute('content', c); }
  var applied = [];
  function apply(s) {
    applied.forEach(function (k) { h.style.removeProperty(k); });
    applied = [];
    h.style.removeProperty('color-scheme');
    if (isDefault(s)) { h.removeAttribute('data-look'); scopedEl().textContent = ''; placeDuo(null); themeColour('#FFFFFF'); return; }   /* the stylesheet's own values */
    var v = vars(s);
    Object.keys(v).forEach(function (k) { h.style.setProperty(k, v[k]); applied.push(k); });
    if (isDark(s.c.bg)) h.style.setProperty('color-scheme', 'dark');
    scopedEl().textContent = scopedCss(s);
    placeDuo(s);
    [s.t.head, s.t.body, s.t.ui, s.t.fig].forEach(loadFont);
    var p = presetOf(s);
    h.setAttribute('data-look', p ? p.id : 'custom');
    themeColour(partColour(s, 'header') || s.c.bg);
  }

  /* before the page is drawn: a look from the address (?look=...) or the one chosen last time */
  var state = null;
  try {
    var q = new URLSearchParams(location.search).get('look');
    if (q) { state = decode(q); if (state) save(state); }
  } catch (e) { /* old browser: no shared looks */ }
  if (!state) state = stored();
  if (state) apply(state);
  window.NP_LOOK = { vars: vars, presets: PRESETS, fromPreset: fromPreset, build: build, clean: clean, scopedCss: scopedCss, guessBuilder: guessBuilder, contrast: contrast };   /* for checks and the console */

  /* ---------- random looks, from the same options ---------- */
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
  function shuffledBuilder() {
    var hm = pick(HARMONY)[0];
    return { base: lch(0.42 + Math.random() * 0.18, 0.06 + Math.random() * 0.12, Math.random() * 360), harmony: hm, turn: SHIFT[hm] * pick([1, -1]), vivid: pick([0.35, 0.5, 0.5, 0.65, 0.8]),
      temp: pick(TEMPS)[0], ground: pick(['white', 'white', 'white', 'paper', 'paper', 'mist', 'mist', 'dark']), block: pick(BLOCKS)[0] };
  }
  function shuffledUsage() {
    return { header: pick(['plain', 'plain', 'plain', 'tint', 'accent', 'block', 'ink']), footer: pick(['light', 'light', 'plain', 'block', 'ink']),
      rules: pick(['head', 'head', 'accent', 'rule', 'light']), lines: pick(['four', 'four', 'accent', 'rule']), photo: pick(['natural', 'natural', 'muted', 'mono', 'duo']), contrast: 'standard' };
  }
  function shuffledType() {
    var ids = Object.keys(FONTS), of = function (kinds) { return ids.filter(function (id) { return kinds.indexOf(FONTS[id].kind) >= 0; }); };
    var sans = of(['grotesque', 'humanist', 'geometric']), serifs = of(['serif', 'slab']), monos = of(['mono']);
    var head = pick(sans.concat(serifs)), serifHead = FONTS[head].kind === 'serif' || FONTS[head].kind === 'slab', body;
    if (serifHead) body = Math.random() < 0.25 ? head : pick(sans);
    else body = Math.random() < 0.55 ? head : pick(sans.concat(of(['serif'])).filter(function (x) { return x !== head; }));
    var isSans = function (id) { return sans.indexOf(id) >= 0; };
    var r = Math.random(), ui = r < 0.8 ? (isSans(body) ? body : isSans(head) ? head : pick(sans)) : pick(monos);   /* labels and navigation in a sans or a mono */
    r = Math.random();
    var fig = r < 0.6 ? head : r < 0.8 ? ui : pick(monos), f = FONTS[head];
    return { head: head, body: body, ui: ui, fig: fig, weight: f.w, track: f.tr, width: f.wide ? pick([85, 92, 100]) : 100,
      tw: 400, size: pick([16, 17, 17, 18]), leading: pick([1.5, 1.55, 1.6, 1.65, 1.7]), scale: pick(SCALE_OPTS)[0], labels: pick(LABEL_OPTS)[0] };
  }

  /* ---------- the panel ---------- */
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  function current() { return state || PSTATES[0]; }
  function set(s) { state = clean(s); apply(state); save(state); render(); }
  var ICON = {
    x: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>',
    prev: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3.5L5.5 8l4.5 4.5"/></svg>',
    next: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3.5L10.5 8 6 12.5"/></svg>',
    shuffle: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4.5h2.6c1.5 0 2.3.6 3.2 2l1.4 2.4c.8 1.3 1.6 2.1 3.1 2.1H14M2 11h2.6c1.3 0 2-.5 2.6-1.4M9.8 5.9c.6-.9 1.4-1.4 2.6-1.4H14M12 2.5l2 2-2 2M12 9l2 2-2 2"/></svg>'
  };
  function seg(attr, key, list, label) {
    return '<div class="lk-opt"><span class="lk-lab" id="lk-l-' + key + '">' + label + '</span><div class="lk-seg" role="group" aria-labelledby="lk-l-' + key + '">' +
      list.map(function (o) { return '<button type="button" ' + attr + '="' + key + '" data-v="' + o[0] + '">' + esc(o[1]) + '</button>'; }).join('') + '</div></div>';
  }
  function slider(attr, key, label, min, max, step) {
    return '<label class="lk-field"><span>' + label + '</span><span class="lk-pick"><input type="range" ' + attr + '="' + key + '" min="' + min + '" max="' + max + '" step="' + step + '"><output data-out="' + key + '"></output></span></label>';
  }
  function fontSelect(role, label) {
    var html = '<label class="lk-field"><span>' + label + '</span><select data-t="' + role + '">';
    KINDS.forEach(function (k) {
      html += '<optgroup label="' + k[1] + '">' + Object.keys(FONTS).filter(function (id) { return FONTS[id].kind === k[0]; })
        .map(function (id) { return '<option value="' + id + '">' + esc(FONTS[id].name) + '</option>'; }).join('') + '</optgroup>';
    });
    return html + '</select></label>';
  }
  function sw(colours) { return '<span class="lk-sw">' + colours.map(function (c) { return '<i style="background:' + c + '"></i>'; }).join('') + '</span>'; }

  function makePanel() {
    if (document.getElementById('lk-panel')) return;
    var preview = (document.querySelector('meta[name="np:mode"]') || {}).content === 'preview';   /* the preview copy can't pass ?look= on, so it has no "Copy link" */
    var toggle = document.createElement('button');
    toggle.className = 'lk-toggle'; toggle.type = 'button';
    toggle.setAttribute('aria-expanded', 'false'); toggle.setAttribute('aria-controls', 'lk-panel');
    toggle.innerHTML = '<span class="lk-dots" aria-hidden="true"><i></i><i></i><i></i></span>Design';
    var p = document.createElement('section');
    p.className = 'lk-panel'; p.id = 'lk-panel'; p.hidden = true;
    p.setAttribute('role', 'dialog'); p.setAttribute('aria-label', 'Design panel');

    var html = '<div class="lk-top"><div class="lk-head"><h2>Design</h2><button class="lk-x" type="button" data-act="close" aria-label="Close the design panel">' + ICON.x + '</button></div>' +
      '<div class="lk-cycle"><button type="button" data-step="-1" aria-label="Previous preset">' + ICON.prev + '</button>' +
      '<div class="lk-now" aria-live="polite"><b data-out="name"></b><span data-out="count"></span></div>' +
      '<button type="button" data-step="1" aria-label="Next preset">' + ICON.next + '</button></div>' +
      '<p class="lk-note" data-out="note"></p>' +
      '<div class="lk-tabs" role="tablist" aria-label="Parts of the design panel">' +
      [['presets', 'Presets'], ['colour', 'Colour'], ['type', 'Type']].map(function (t) {
        return '<button type="button" role="tab" id="lk-tab-' + t[0] + '" aria-controls="lk-pane-' + t[0] + '" data-tab="' + t[0] + '">' + t[1] + '</button>';
      }).join('') + '</div></div><div class="lk-body">';

    /* presets */
    html += '<div class="lk-pane" role="tabpanel" id="lk-pane-presets" aria-labelledby="lk-tab-presets" data-pane="presets">' +
      '<p class="lk-intro">A temporary panel for trying colours and typefaces on the real pages. Your choice stays on as you move between pages, in this browser only.<span class="lk-keys"> With the panel open, the arrow keys step through the presets.</span></p>' +
      '<div class="lk-sec"><div class="lk-grid">';
    PRESETS.forEach(function (pr, i) {
      var st = PSTATES[i];
      html += '<button type="button" class="lk-pre" data-preset="' + pr.id + '"><span class="lk-mini" style="background:' + st.c.bg + '">' +
        '<span class="lk-aa" data-font="' + st.t.head + '" style="color:' + st.c.head + ';font-weight:' + st.t.weight + ';font-stretch:' + st.t.width + '%">Aa</span>' +
        sw([st.c.block, st.c.accent, st.c.rule]) + '</span><span class="lk-pn">' + esc(pr.name) + '</span></button>';
    });
    html += '</div><div class="lk-row lk-gap"><button type="button" class="lk-btn" data-act="shuffle-all">' + ICON.shuffle + 'Surprise me</button>' +
      '<span class="lk-hint">A random look from the options under Colour and Type.</span></div></div></div>';

    /* colour */
    html += '<div class="lk-pane" role="tabpanel" id="lk-pane-colour" aria-labelledby="lk-tab-colour" data-pane="colour" hidden>' +
      '<div class="lk-sec"><h3>Colour sets</h3><div class="lk-row">';
    Object.keys(COLOURS).forEach(function (id) {
      var k = colourSet(id).c;
      html += '<button type="button" class="lk-chip" data-colours="' + id + '">' + sw([k.bg === '#FFFFFF' ? k.head : k.bg, k.accent, k.block, k.rule]) + esc(COLOURS[id].name) + '</button>';
    });
    html += '</div></div><div class="lk-sec"><h3>Build a palette</h3><p class="lk-sub">Start from one colour and the rest follows from it. Changing any of these rebuilds the palette.</p>' +
      '<label class="lk-field"><span>Base colour</span><span class="lk-pick"><input type="color" data-b="base"><code data-hex="base"></code></span></label>' +
      seg('data-b', 'harmony', HARMONY, 'Harmony') +
      slider('data-b', 'vivid', 'Vividness', 0, 1, 0.05) +
      seg('data-b', 'temp', TEMPS, 'Greys') +
      seg('data-b', 'ground', GROUNDS, 'Ground') +
      seg('data-b', 'block', BLOCKS, 'Bold block') +
      '<div class="lk-row lk-gap"><button type="button" class="lk-btn" data-act="shuffle-colour">' + ICON.shuffle + 'Shuffle colours</button></div></div>' +
      '<div class="lk-sec"><h3>Where colour goes</h3>';
    Object.keys(USAGE).forEach(function (k) { html += seg('data-u', k, USAGE[k][1], USAGE[k][0]); });
    html += '</div><div class="lk-sec"><details class="lk-more"><summary>Each colour by hand</summary><div class="lk-fields">';
    [['accent', 'Links and buttons'], ['block', 'Bold block'], ['ink', 'Text'], ['head', 'Headings'], ['bg', 'Background'], ['surface', 'Footer and panels'], ['rule', 'Short rule']].forEach(function (f) {
      html += '<label class="lk-field"><span>' + f[1] + '</span><span class="lk-pick"><input type="color" data-c="' + f[0] + '"><code data-hex="' + f[0] + '"></code></span></label>';
    });
    html += '</div></details></div></div>';

    /* type */
    html += '<div class="lk-pane" role="tabpanel" id="lk-pane-type" aria-labelledby="lk-tab-type" data-pane="type" hidden><div class="lk-sec"><h3>Pairs</h3><div class="lk-row">';
    Object.keys(TYPE).forEach(function (id) {
      var t = typeSet(id);
      html += '<button type="button" class="lk-chip lk-tp" data-type="' + id + '"><span class="lk-aa" data-font="' + t.head + '" style="font-weight:' + t.weight + ';font-stretch:' + t.width + '%">Aa</span><span class="lk-aa lk-b" data-font="' + t.body + '">Aa</span>' + esc(TYPE[id].name) + '</button>';
    });
    html += '</div></div><div class="lk-sec"><h3>A typeface for each role</h3>' +
      fontSelect('head', 'Headings') + fontSelect('body', 'Running text') + fontSelect('ui', 'Labels and navigation') + fontSelect('fig', 'Figures and dates') +
      '<p class="lk-hint">Avenir Next shows on Macs and iPhones; elsewhere Nunito Sans stands in for it.</p></div>' +
      '<div class="lk-sec"><h3>Scale and rhythm</h3>' + seg('data-t', 'scale', SCALE_OPTS, 'Headings') +
      slider('data-t', 'size', 'Text size', 15, 20, 0.5) + slider('data-t', 'leading', 'Line spacing', 1.35, 1.95, 0.05) + '</div>' +
      '<div class="lk-sec"><h3>Details</h3>' +
      slider('data-t', 'weight', 'Heading weight', 300, 900, 50) + slider('data-t', 'track', 'Heading spacing', -0.06, 0.04, 0.002) +
      slider('data-t', 'width', 'Heading width', 62, 125, 1) + slider('data-t', 'tw', 'Text weight', 300, 500, 50) +
      seg('data-t', 'labels', LABEL_OPTS, 'Labels') +
      '<p class="lk-hint">Width changes Archivo, Instrument Sans and IBM Plex Sans, which come in narrower cuts.</p>' +
      '<div class="lk-row lk-gap"><button type="button" class="lk-btn" data-act="shuffle-type">' + ICON.shuffle + 'Shuffle type</button></div></div></div>';

    html += '</div><div class="lk-foot"><div class="lk-actions">' + (preview ? '' : '<button type="button" data-act="link">Copy link</button>') +
      '<button type="button" data-act="css">Copy settings</button><button type="button" data-act="reset">Reset</button></div>' +
      '<p class="lk-status" role="status" aria-live="polite"></p></div>';
    p.innerHTML = html;
    document.body.appendChild(p);
    document.body.appendChild(toggle);
    /* the sample letters are drawn in their own typeface */
    Array.prototype.forEach.call(p.querySelectorAll('[data-font]'), function (el) { el.style.fontFamily = FONTS[el.getAttribute('data-font')].stack; });

    function fontsFor(name) {
      if (name === 'presets') PSTATES.forEach(function (st) { loadFont(st.t.head); });
      if (name === 'type') Object.keys(TYPE).forEach(function (id) { var t = typeSet(id); [t.head, t.body, t.ui, t.fig].forEach(loadFont); });
    }
    function tab(name) {
      Array.prototype.forEach.call(p.querySelectorAll('[data-tab]'), function (b) { b.setAttribute('aria-selected', String(b.getAttribute('data-tab') === name)); });
      Array.prototype.forEach.call(p.querySelectorAll('[data-pane]'), function (el) { el.hidden = el.getAttribute('data-pane') !== name; });
      p.querySelector('.lk-body').scrollTop = 0;
      try { localStorage.setItem(TAB, name); } catch (e) { /* fine */ }
      if (!p.hidden) fontsFor(name);
    }
    var first = 'presets';
    try { first = localStorage.getItem(TAB) || 'presets'; } catch (e) { /* fine */ }
    tab(/^(presets|colour|type)$/.test(first) ? first : 'presets');

    function open(v) {
      p.hidden = !v; toggle.setAttribute('aria-expanded', String(v)); toggle.classList.toggle('on', v);
      if (v) {
        var on = p.querySelector('[data-tab][aria-selected="true"]');
        fontsFor('presets');
        if (on) fontsFor(on.getAttribute('data-tab'));
        p.querySelector('.lk-x').focus();
      } else toggle.focus();
    }
    toggle.addEventListener('click', function () { open(p.hidden); });
    function step(d) {
      var at = PRESETS.indexOf(presetOf(current()));
      if (at < 0) at = d > 0 ? -1 : 0;   /* from a look of your own: forward to the first preset, back to the last */
      set(copy(PSTATES[(at + d + PRESETS.length) % PRESETS.length]));
    }
    function builder(key, val) {
      var s = copy(current()), b = s.b || guessBuilder(s.c);
      b[key] = val;
      if (key === 'harmony') b.turn = SHIFT[val] * (b.turn < 0 ? -1 : 1);   /* a harmony picked by hand: its own distance, on the same side of the wheel */
      s.b = clean({ c: s.c, t: s.t, b: b }).b; s.c = build(s.b); s.cid = null;
      set(s);
    }
    p.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b || !p.contains(b)) return;
      var v = b.getAttribute('data-v'), s = copy(current());
      if (b.hasAttribute('data-tab')) tab(b.getAttribute('data-tab'));
      else if (b.hasAttribute('data-step')) step(+b.getAttribute('data-step'));
      else if (b.hasAttribute('data-preset')) { for (var i = 0; i < PRESETS.length; i++) if (PRESETS[i].id === b.getAttribute('data-preset')) set(copy(PSTATES[i])); }
      else if (b.hasAttribute('data-colours')) { var k = colourSet(b.getAttribute('data-colours')); s.cid = k.cid; s.b = k.b; s.c = k.c; set(s); }
      else if (b.hasAttribute('data-type')) { assign(s.t, typeSet(b.getAttribute('data-type'))); s.tid = b.getAttribute('data-type'); set(s); }
      else if (b.hasAttribute('data-b')) builder(b.getAttribute('data-b'), v);
      else if (b.hasAttribute('data-u')) { s.u[b.getAttribute('data-u')] = v; set(s); }
      else if (b.hasAttribute('data-t')) { s.t[b.getAttribute('data-t')] = v; set(s); }
      else act(b.getAttribute('data-act'), s);
    });
    p.addEventListener('input', function (e) {
      var el = e.target, s = copy(current()), k;
      if (el.hasAttribute('data-c')) {
        k = el.getAttribute('data-c'); s.c[k] = el.value.toUpperCase(); s.cid = null; s.b = null;
        if (k === 'ink') delete s.c.ink2;
        set(s);
      } else if (el.hasAttribute('data-b')) builder(el.getAttribute('data-b'), el.type === 'range' ? +el.value : el.value.toUpperCase());
      else if (el.hasAttribute('data-t')) {
        k = el.getAttribute('data-t');
        s.t[k] = el.tagName === 'SELECT' ? el.value : +el.value;
        if (['head', 'body', 'ui', 'fig', 'weight', 'track', 'width'].indexOf(k) >= 0) s.tid = null;   /* no longer the pair as set */
        if (k === 'head' && el.tagName === 'SELECT') { s.t.weight = FONTS[el.value].w; s.t.track = FONTS[el.value].tr; }
        set(s);
      }
    });
    function act(name, s) {
      if (name === 'close') open(false);
      else if (name === 'reset') { set(null); say('Back to the v2 default.'); }
      else if (name === 'link') {
        var u = location.origin + location.pathname + (isDefault(state) ? '' : '?look=' + encode(state)) + location.hash;
        copyText(u, 'Link copied. It opens this page with this look.');
      } else if (name === 'css') copyText(cssText(), 'Settings copied. They replace the first block in v2/assets/css/v2.css.');
      else if (name === 'shuffle-colour') { s.b = shuffledBuilder(); s.c = build(s.b); s.cid = null; set(s); }
      else if (name === 'shuffle-type') { s.t = shuffledType(); s.tid = null; set(s); }
      else if (name === 'shuffle-all') { s.b = shuffledBuilder(); s.c = build(s.b); s.cid = null; s.u = shuffledUsage(); s.t = shuffledType(); s.tid = null; set(s); }
    }
    document.addEventListener('keydown', function (e) {
      if (p.hidden) return;
      if (e.key === 'Escape') { open(false); return; }
      if (/INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || '')) return;
      if (e.key === '[' || e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
      if (e.key === ']' || e.key === 'ArrowRight') { e.preventDefault(); step(1); }
    });
    render();
  }

  function say(msg) {
    var st = document.querySelector('.lk-status');
    if (!st) return;
    st.textContent = msg; clearTimeout(say.t); say.t = setTimeout(function () { st.textContent = ''; }, 4000);
  }
  function copyText(text, msg) {
    var done = function () { say(msg); };
    var fallback = function () {
      var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.className = 'lk-copy';
      document.querySelector('.lk-foot').appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { /* not allowed */ }
      if (ok) { ta.remove(); done(); } else say('Copy it from the box below.');
    };
    try { navigator.clipboard.writeText(text).then(done, fallback); } catch (e) { fallback(); }
  }
  function roles(t) {   /* "Source Serif 4 for headings and figures, IBM Plex Sans for running text and labels and navigation" */
    var by = {}, order = [];
    [['headings', t.head], ['running text', t.body], ['labels and navigation', t.ui], ['figures', t.fig]].forEach(function (r) {
      if (!by[r[1]]) { by[r[1]] = []; order.push(r[1]); }
      by[r[1]].push(r[0]);
    });
    if (order.length === 1) return FONTS[order[0]].name + ' throughout';
    return order.map(function (id) { var r = by[id]; return FONTS[id].name + ' for ' + (r.length > 1 ? r.slice(0, -1).join(', ') + ' and ' + r[r.length - 1] : r[0]); }).join('; ');
  }
  function cssText() {   /* what to paste over the first block of v2/assets/css/v2.css */
    var s = current(), v = vars(s), p = presetOf(s), t = s.t, dark = isDark(s.c.bg);
    var extra = [t.head, t.body, t.ui, t.fig].filter(function (id, i, a) { return !FONTS[id].base && a.indexOf(id) === i; });
    var out = '/* The look: ' + (p ? p.name : 'a look of your own') + ', from the design panel. ' + roles(t) + '.\n';
    out += extra.length ?
      '   To load the typefaces, add this line to v2/templates/base.html after the Hanken Grotesk one (the logo keeps that):\n' +
      '   <link rel="stylesheet" href="https://fonts.googleapis.com/css2?' + extra.map(function (id) { return 'family=' + FONTS[id].q; }).join('&amp;') + '&amp;display=swap">\n' :
      '   Hanken Grotesk already loads in v2/templates/base.html.\n';
    if (extra.indexOf('avenir') >= 0) out += '   Avenir Next itself needs a web licence from Monotype; the line above loads Nunito Sans to stand in for it.\n';
    if (s.u.photo === 'duo') out += '   Duotone photos also need this filter in v2/templates/base.html, just after <body>:\n   ' + duoSvg(s) + '\n';
    out = out.replace(/\n$/, '') + ' */\n:root{\n  color-scheme:' + (dark ? 'dark' : 'light') + ';\n';
    Object.keys(v).forEach(function (k) { out += '  ' + k + ':' + v[k] + ';\n'; });
    return out + '}\n' + scopedCss(s);
  }
  function render() {
    var p = document.getElementById('lk-panel');
    if (!p) return;
    var s = current(), pr = presetOf(s), g = s.b || guessBuilder(s.c), t = s.t;
    var out = function (n) { return p.querySelector('[data-out="' + n + '"]'); };
    var press = function (sel, on) { Array.prototype.forEach.call(p.querySelectorAll(sel), function (b) { b.setAttribute('aria-pressed', String(on(b))); }); };
    out('name').textContent = pr ? pr.name : 'Your own look';
    out('count').textContent = pr ? (PRESETS.indexOf(pr) + 1) + ' of ' + PRESETS.length : 'not a preset';
    out('note').textContent = pr ? pr.note : 'A combination of your own. Copy link shares it; a preset starts again from one of the set looks.';
    press('[data-preset]', function (b) { return !!pr && b.getAttribute('data-preset') === pr.id; });
    press('[data-colours]', function (b) { return b.getAttribute('data-colours') === s.cid; });
    press('[data-type]', function (b) { return b.getAttribute('data-type') === s.tid; });
    press('button[data-b]', function (b) { return !!s.b && s.b[b.getAttribute('data-b')] === b.getAttribute('data-v'); });
    /* with a named or hand-set palette, a dashed outline shows where the builder would start from */
    Array.prototype.forEach.call(p.querySelectorAll('button[data-b]'), function (b) {
      if (!s.b && g[b.getAttribute('data-b')] === b.getAttribute('data-v')) b.setAttribute('data-guess', ''); else b.removeAttribute('data-guess');
    });
    press('[data-u]', function (b) { return s.u[b.getAttribute('data-u')] === b.getAttribute('data-v'); });
    press('button[data-t]', function (b) { return t[b.getAttribute('data-t')] === b.getAttribute('data-v'); });
    p.querySelector('input[data-b="base"]').value = g.base.toLowerCase(); p.querySelector('[data-hex="base"]').textContent = g.base;
    p.querySelector('input[data-b="vivid"]').value = g.vivid; out('vivid').textContent = Math.round(g.vivid * 100) + '%';
    CKEYS.forEach(function (k) { p.querySelector('[data-c="' + k + '"]').value = s.c[k].toLowerCase(); p.querySelector('[data-hex="' + k + '"]').textContent = s.c[k]; });
    ['head', 'body', 'ui', 'fig'].forEach(function (k) { p.querySelector('select[data-t="' + k + '"]').value = t[k]; });
    ['weight', 'track', 'width', 'tw', 'size', 'leading'].forEach(function (k) { p.querySelector('input[data-t="' + k + '"]').value = t[k]; });
    out('weight').textContent = t.weight; out('tw').textContent = t.tw;
    out('track').textContent = (t.track > 0 ? '+' : '') + t.track.toFixed(3) + ' em';
    out('width').textContent = t.width + '%';
    out('size').textContent = t.size + ' px';
    out('leading').textContent = t.leading.toFixed(2);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', makePanel); else makePanel();
  /* back to a page the browser kept in memory: show the look chosen since, as every other page does */
  window.addEventListener('pageshow', function (e) {
    if (!e.persisted) return;
    var s = stored();
    if (!same(s, state)) { state = s; apply(state); render(); }
  });
})();
