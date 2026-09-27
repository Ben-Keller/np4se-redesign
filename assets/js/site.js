/* NP4SE website behaviour: navigation, search, filters, forms, embeds and maps.
   Every page works without this file; it adds interaction on top. */
(function () {
  'use strict';
  var $ = function (s, e) { return (e || document).querySelector(s); };
  var $$ = function (s, e) { return Array.prototype.slice.call((e || document).querySelectorAll(s)); };
  var metaC = function (n) { var m = document.querySelector('meta[name="' + n + '"]'); return m ? m.getAttribute('content') : null; };
  var BASE = metaC('np:base'); if (BASE === null) BASE = '/';
  var PREVIEW = metaC('np:mode') === 'preview';
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var NP = window.NP = window.NP || {};
  /* Root-relative site URL -> URL that works here: prefixed with the base path on the live site
     (e.g. /np4se-redesign on a GitHub Pages project address), relative in the preview build. */
  NP.url = function (u) {
    if (!u || u.charAt(0) !== '/' || u.charAt(1) === '/') return u;
    if (!PREVIEW) return BASE.replace(/\/$/, '') + u;
    var parts = u.split('#'), p = parts[0];
    if (p.slice(-1) === '/') p += 'index.html';
    return BASE + p.replace(/^\//, '') + (parts[1] ? '#' + parts[1] : '');
  };

  /* ---------------- navigation ---------------- */
  var menu = $('#menu'), burger = $('#burger');
  function closeSubs(except) { $$('.mi.open').forEach(function (li) { if (li !== except) { li.classList.remove('open'); $$('[aria-expanded]', li).forEach(function (b) { b.setAttribute('aria-expanded', 'false'); }); } }); }
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      document.body.classList.toggle('menu-open', open);
    });
  }
  $$('.mi button.mt, .mi .caret').forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var li = b.closest('.mi'), open = !li.classList.contains('open');
      closeSubs(li);
      li.classList.toggle('open', open);
      $$('[aria-expanded]', li).forEach(function (x) { x.setAttribute('aria-expanded', String(open)); });
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.mi')) closeSubs(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeSubs();
      if (menu && menu.classList.contains('open')) { burger.click(); burger.focus(); }
    }
  });

  /* ---------------- copy buttons ---------------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-copy]'); if (!b) return;
    var text = b.getAttribute('data-copy');
    var done = function () { var t = b.textContent; b.textContent = 'Copied'; setTimeout(function () { b.textContent = t; }, 1600); };
    var fallback = function () { var a = b.parentNode.querySelector('a'); if (a) { var r = document.createRange(); r.selectNodeContents(a); var s = getSelection(); s.removeAllRanges(); s.addRange(r); } };
    try { navigator.clipboard.writeText(text).then(done, fallback); } catch (err) { fallback(); }
  });

  /* ---------------- search ---------------- */
  var search = $('#search'), sq = $('#search-q'), sres = $('#search-res'), lastFocus = null, idxLoading = false;
  function loadIndex(cb) {
    if (window.NP_SEARCH) return cb();
    if (idxLoading) return;
    idxLoading = true;
    var s = document.createElement('script');
    s.src = NP.url('/assets/js/search-index.js');
    s.onload = function () { idxLoading = false; cb(); };
    s.onerror = function () { idxLoading = false; sres.innerHTML = '<p class="sr-empty">Search is unavailable right now.</p>'; };
    document.head.appendChild(s);
  }
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function runSearch() {
    var q = norm(sq.value).trim();
    if (!window.NP_SEARCH) { sres.innerHTML = '<p class="sr-hint">Loading\u2026</p>'; return; }
    if (!q) { sres.innerHTML = '<p class="sr-hint">Type to search ' + window.NP_SEARCH.length + ' pages: publications, events, member countries and more.</p>'; return; }
    var toks = q.split(/\s+/).filter(Boolean);
    var hits = [];
    window.NP_SEARCH.forEach(function (r) {
      var t = norm(r.t), all = t + ' ' + norm(r.s) + ' ' + norm(r.x) + ' ' + norm(r.k);
      var score = 0;
      for (var i = 0; i < toks.length; i++) {
        if (all.indexOf(toks[i]) < 0) return;
        score += t.indexOf(toks[i]) >= 0 ? 3 : 1;
      }
      if (t.indexOf(q) === 0) score += 4;
      if (r.k.indexOf('Country') === 0 && t.indexOf(q) >= 0) score += 3;
      hits.push([score, r.y || 0, r]);
    });
    hits.sort(function (a, b) { return b[0] - a[0] || b[1] - a[1]; });
    if (!hits.length) { sres.innerHTML = '<p class="sr-empty">No results for \u201c' + esc(sq.value) + '\u201d. Try a country, a year or a topic such as methane.</p>'; return; }
    sres.innerHTML = hits.slice(0, 40).map(function (h, i) {
      var r = h[2];
      return '<a class="sr-item' + (i === 0 ? ' on' : '') + '" href="' + esc(NP.url(r.u)) + '"><small>' + esc(r.k) + '</small><b>' + esc(r.t) + '</b>' + (r.s ? '<span>' + esc(r.s) + '</span>' : '') + '</a>';
    }).join('');
  }
  function openSearch() {
    if (!search) return;
    lastFocus = document.activeElement;
    search.hidden = false; document.body.classList.add('search-open');
    closeSubs();
    setTimeout(function () { sq.focus(); sq.select(); }, 10);
    loadIndex(runSearch); runSearch();
  }
  function closeSearch() {
    if (!search || search.hidden) return;
    search.hidden = true; document.body.classList.remove('search-open');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  $$('[data-search-open]').forEach(function (b) { b.addEventListener('click', openSearch); });
  $$('[data-search-close]').forEach(function (b) { b.addEventListener('click', closeSearch); });
  if (sq) {
    sq.addEventListener('input', runSearch);
    sq.addEventListener('keydown', function (e) {
      var items = $$('.sr-item', sres), cur = items.findIndex(function (a) { return a.classList.contains('on'); });
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); if (!items.length) return;
        var n = e.key === 'ArrowDown' ? Math.min(items.length - 1, cur + 1) : Math.max(0, cur - 1);
        items.forEach(function (a, i) { a.classList.toggle('on', i === n); });
        items[n].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' && cur >= 0) { e.preventDefault(); location.href = items[cur].href; }
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSearch();
    var typing = /INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || '');
    if (((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !typing)) { e.preventDefault(); openSearch(); }
  });

  /* ---------------- forms ---------------- */
  $$('form[data-form]').forEach(function (f) {
    var ok = $('[data-ok]', f);
    f.addEventListener('submit', function (e) {
      if (!f.checkValidity()) return;
      e.preventDefault();
      var btn = $('button[type="submit"]', f);
      if (PREVIEW) {
        ok.textContent = 'Preview only: on the live site this form is sent to the Secretariat.';
        ok.hidden = false; return;
      }
      var trap = $('[name="_gotcha"]', f);
      if (trap && trap.value) { f.reset(); ok.hidden = false; return; }
      /* No form service configured: open the visitor's email app with the message filled in. */
      var to = f.getAttribute('data-mailto');
      if (to) {
        var lines = [];
        $$('input, select, textarea', f).forEach(function (el) {
          if (!el.name || !el.value || el.type === 'hidden' || el.name.charAt(0) === '_' || el.name === 'form-name') return;
          var lab = el.id ? $('label[for="' + el.id + '"]', f) : null;
          lines.push((lab ? lab.textContent.replace(/\s*\*\s*$/, '').trim() : el.name) + ': ' + el.value);
        });
        location.href = 'mailto:' + to + '?subject=' + encodeURIComponent(f.getAttribute('data-subject') || '') +
          '&body=' + encodeURIComponent(lines.join('\r\n'));
        ok.textContent = 'Your email app should open with this message, ready to send to ' + to + '.';
        ok.classList.remove('err'); ok.hidden = false;
        return;
      }
      var data = new FormData(f);
      var req = fetch(f.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
      if (btn) { btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = 'Sending\u2026'; }
      req.then(function (r) {
        if (!r.ok) throw new Error(r.status);
        f.reset(); ok.classList.remove('err'); ok.hidden = false;
        if (btn) { btn.disabled = false; btn.textContent = btn.dataset.label; }
      }).catch(function () { f.submit(); });
    });
  });
  (function prefill() {
    var el = $('#sub-email'); if (!el) return;
    try { var v = new URLSearchParams(location.search).get('email'); if (v) el.value = v; } catch (err) { /* ignore */ }
  })();

  /* ---------------- video embeds (live site: play in place) ---------------- */
  $$('figure.embed').forEach(function (fig) {
    var a = $('.embed-link', fig), src = fig.getAttribute('data-embed');
    if (!a || !src || PREVIEW) return;
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var url = src.replace('www.youtube.com/embed/', 'www.youtube-nocookie.com/embed/');
      url += (url.indexOf('?') < 0 ? '?' : '&') + 'autoplay=1';
      var fr = document.createElement('iframe');
      fr.src = url; fr.title = 'Video'; fr.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen'; fr.allowFullscreen = true;
      fig.innerHTML = ''; fig.appendChild(fr);
    });
  });

  /* ---------------- list filters (library, events) ---------------- */
  $$('[data-filter]').forEach(function (bar) {
    var root = bar.parentElement, list = $('[data-list]', root);
    if (!list) return;
    var items = $$('[data-q]', list), total = items.length, noun = bar.getAttribute('data-filter') === 'events' ? 'events' : 'publications';
    var st = { q: '', type: '', theme: '', country: '', year: '' };
    var q = $('[data-q]', bar), tSel = $('[data-type-select]', bar), thSel = $('[data-theme-select]', bar), cSel = $('[data-country-select]', bar), ySel = $('[data-year-select]', bar);
    var chips = $$('.chip[data-type]', bar), count = $('[data-count]', bar), empty = $('[data-empty]', list);
    function apply(push) {
      var toks = norm(st.q).split(/\s+/).filter(Boolean), n = 0;
      items.forEach(function (it) {
        var d = it.dataset, hay = norm(d.q);
        var ok = (!st.type || d.type.split('|').indexOf(st.type) >= 0) &&
          (!st.theme || d.themes.split(' ').indexOf(st.theme) >= 0) &&
          (!st.country || d.countries.split('|').indexOf(st.country) >= 0) &&
          (!st.year || +d.year >= +st.year) &&
          toks.every(function (t) { return hay.indexOf(t) >= 0; });
        it.hidden = !ok; if (ok) n++;
      });
      $$('[data-ygroup]', list).forEach(function (g) { g.hidden = !$$('[data-q]', g).some(function (x) { return !x.hidden; }); });
      if (empty) empty.hidden = n > 0;
      if (count) count.textContent = n === total ? 'Showing all ' + total + ' ' + noun : 'Showing ' + n + ' of ' + total + ' ' + noun;
      if (push && !PREVIEW && history.replaceState) {
        var p = new URLSearchParams();
        Object.keys(st).forEach(function (k) { if (st[k]) p.set(k, st[k]); });
        var s = p.toString();
        history.replaceState(null, '', location.pathname + (s ? '?' + s : '') + location.hash);
      }
    }
    function sync() {
      if (q) q.value = st.q;
      if (tSel) tSel.value = st.type;
      if (thSel) thSel.value = st.theme;
      if (cSel) cSel.value = st.country;
      if (ySel) ySel.value = st.year;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c.getAttribute('data-type') === st.type)); });
    }
    if (q) q.addEventListener('input', function () { st.q = q.value.trim(); apply(true); });
    [[tSel, 'type'], [thSel, 'theme'], [cSel, 'country'], [ySel, 'year']].forEach(function (p) {
      if (p[0]) p[0].addEventListener('change', function () { st[p[1]] = p[0].value; apply(true); });
    });
    chips.forEach(function (c) { c.addEventListener('click', function () { st.type = c.getAttribute('data-type'); sync(); apply(true); }); });
    var reset = $('[data-reset]', bar);
    if (reset) reset.addEventListener('click', function () { st = { q: '', type: '', theme: '', country: '', year: '' }; sync(); apply(true); });
    $$('[data-set-type]').forEach(function (a) {
      a.addEventListener('click', function () { st.type = a.getAttribute('data-set-type'); sync(); apply(true); });
    });
    try {
      var P = new URLSearchParams(location.search);
      Object.keys(st).forEach(function (k) { if (P.get(k)) st[k] = P.get(k); });
    } catch (err) { /* ignore */ }
    sync(); apply(false);
  });

  /* ---------------- table of contents ---------------- */
  $$('[data-toc]').forEach(function (nav) {
    var src = $('[data-toc-source]'); if (!src) return;
    var hs = $$('h2', src); if (hs.length < 3) return;
    var ol = $('ol', nav);
    hs.forEach(function (h, i) {
      if (!h.id) h.id = 's-' + (h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || i);
      var li = document.createElement('li'); li.innerHTML = '<a href="#' + h.id + '">' + esc(h.textContent) + '</a>'; ol.appendChild(li);
    });
    nav.hidden = false;
    if ('IntersectionObserver' in window) {
      var links = $$('a', ol);
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (en) { if (en.isIntersecting) links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + en.target.id); }); });
      }, { rootMargin: '-15% 0px -70% 0px' });
      hs.forEach(function (h) { io.observe(h); });
    }
  });

  /* ---------------- maps ---------------- */
  var W = window.WORLD, D = window.NP_DATA;
  if (!W || !D) return;
  var NS = 'http://www.w3.org/2000/svg';
  var ROLE = { member: 'Member', observer: 'Observer', peer: 'Established producer peer', former: 'Former member' };
  var LBL = { 'Bahamas': [8, -3], 'Barbados': [8, 4], 'Belize': [-8, 4, 'end'], 'Guyana': [-8, -3, 'end'], 'Suriname': [8, 9], 'Uruguay': [8, 4], 'Ghana': [4, 14], 'Guinea': [-8, -4, 'end'], 'Liberia': [-8, 9, 'end'], 'Mauritania': [-8, -2, 'end'], 'Senegal': [-8, 3, 'end'], 'Sierra Leone': [-8, 4, 'end'], 'DR Congo': [7, 13], 'Mozambique': [8, 4], 'Namibia': [-8, 4, 'end'], 'S\u00e3o Tom\u00e9 e Pr\u00edncipe': [-8, 5, 'end'], 'Somalia': [8, 4], 'Tanzania': [8, 5], 'Uganda': [-7, -6, 'end'], 'Lebanon': [8, 4], 'Papua New Guinea': [8, 4], 'Timor-Leste': [-8, 12, 'end'], 'Angola': [-8, 10, 'end'], 'Brazil': [8, 4], 'Indonesia': [-8, -5, 'end'], 'Norway': [8, 4] };
  var M = D.members, R = D.regions, byName = {}, byAtlas = {}, bySlug = {};
  M.forEach(function (m) { byName[m.n] = m; if (m.id) byAtlas[m.id] = m; bySlug[m.s] = m; });
  var uid = 0;
  function colourOf(m, mode) {
    if (m.role === 'peer') return R.peer.hex;
    if (m.role === 'former') return '#FFFFFF';
    return mode === 'stage' ? (D.stageHex[m.stage] || R.peer.hex) : R[m.r].hex;
  }
  function el(tag, attrs) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); return e; }

  function buildMap(host, o) {
    var id = 'm' + (++uid), svg = el('svg', { viewBox: o.viewBox || '0 10 1000 430', preserveAspectRatio: 'xMidYMid meet' });
    if (o.decorative) svg.setAttribute('aria-hidden', 'true');
    var defs = '<defs>';
    var hatch = function (key, hex) { return '<pattern id="' + id + '-h-' + key + '" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff"/><rect width="2.4" height="5" fill="' + hex + '"/></pattern>'; };
    Object.keys(R).forEach(function (k) { defs += hatch(k, R[k].hex); });
    D.stages.forEach(function (s, i) { defs += hatch('s' + i, D.stageHex[s]); });
    svg.innerHTML = defs + '</defs>';
    var g = el('g', {});
    if (!o.noGrat) g.appendChild(el('path', { 'class': 'grat', d: W.grat }));
    var lands = [];
    W.c.forEach(function (c) {
      var p = el('path', { d: c.d, 'class': 'land' });
      var m = byAtlas[c.i];
      if (m && (m.role !== 'former' || o.former)) { p.dataset.name = m.n; lands.push([p, m]); if (o.interactive && m.role !== 'former') p.classList.add('hot'); }
      g.appendChild(p);
    });
    var dots = [], labels = [];
    M.forEach(function (m) {
      if (m.role === 'former' && !o.former) return;
      var x = m.pt[0], y = m.pt[1], d = el('g', { 'class': 'dot' + (m.role === 'former' ? ' former' : '') });
      d.dataset.name = m.n;
      if (o.interactive) {
        d.setAttribute('tabindex', '0'); d.setAttribute('role', 'button');
        d.setAttribute('aria-label', m.n + ', ' + ROLE[m.role] + (m.role === 'peer' ? '' : ', ' + R[m.r].n));
      }
      d.appendChild(el('circle', { 'class': 'halo', cx: x, cy: y, r: 11 }));
      d.appendChild(el('circle', { 'class': 'core', cx: x, cy: y, r: o.dotR || (o.labels ? 4 : 3.5) }));
      g.appendChild(d); dots.push([d, m]);
      if (o.labels && LBL[m.n]) {
        var off = LBL[m.n], t = el('text', { 'class': 'lbl' + (m.role === 'peer' ? ' peer' : ''), x: x + off[0], y: y + off[1] });
        if (off[2]) t.setAttribute('text-anchor', off[2]);
        t.textContent = m.n; t.dataset.name = m.n; g.appendChild(t); labels.push([t, m]);
      }
    });
    svg.appendChild(g);
    host.innerHTML = ''; host.appendChild(svg);
    if (!o.viewBox) {
      /* on phones, crop to the part of the world where the network is, so countries are big enough to tap */
      var fit = function () { svg.setAttribute('viewBox', host.clientWidth && host.clientWidth < 640 ? '232 28 712 356' : '0 10 1000 430'); };
      fit(); var tmo; window.addEventListener('resize', function () { clearTimeout(tmo); tmo = setTimeout(fit, 150); });
    }
    var tip = document.createElement('div'); tip.className = 'tip'; host.appendChild(tip);
    var api = {
      svg: svg, g: g,
      recolour: function (mode) {
        lands.forEach(function (x) {
          var p = x[0], m = x[1];
          if (m.role === 'former') { p.style.fill = ''; return; }
          var key = mode === 'stage' && m.role !== 'peer' ? 's' + D.stages.indexOf(m.stage) : m.r;
          p.style.fill = m.role === 'observer' ? 'url(#' + id + '-h-' + key + ')' : colourOf(m, mode);
        });
        dots.forEach(function (x) { var c = $$('circle', x[0]); c.forEach(function (ci) { ci.setAttribute('fill', colourOf(x[1], mode)); }); });
      },
      select: function (n) { $$('.dot, .land.hot', svg).forEach(function (e) { e.classList.toggle('sel', e.dataset.name === n); }); },
      filter: function (fn) {
        dots.concat(labels).concat(lands).forEach(function (x) { var on = fn(x[1]); x[0].style.opacity = on ? '' : '.14'; x[0].style.pointerEvents = on ? '' : 'none'; });
      }
    };
    if (o.interactive) {
      var show = function (e, m) {
        var r = host.getBoundingClientRect();
        tip.innerHTML = esc(m.n) + '<small>' + ROLE[m.role] + (m.role === 'peer' || m.role === 'former' ? '' : ' \u00b7 ' + esc(R[m.r].n)) + (o.stageTip && m.stage && m.role !== 'former' ? ' \u00b7 ' + esc(D.stageShort[m.stage] || m.stage) : '') + '</small>';
        tip.style.left = (e.clientX - r.left) + 'px'; tip.style.top = (e.clientY - r.top) + 'px'; tip.classList.add('show');
      };
      var hide = function () { tip.classList.remove('show'); };
      dots.concat(lands).forEach(function (x) {
        var node = x[0], m = x[1];
        if (m.role === 'former' && node.tagName === 'path') return;
        node.addEventListener('mousemove', function (e) { show(e, m); });
        node.addEventListener('mouseleave', hide);
        node.addEventListener('click', function () { hide(); o.onPick(m); });
        node.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); o.onPick(m); } });
      });
    }
    api.recolour(o.colour || 'region');
    return api;
  }

  function legend(host, mode) {
    if (!host) return;
    var h = '';
    if (mode === 'stage') {
      D.stages.forEach(function (s) { h += '<span><i style="background:' + D.stageHex[s] + '"></i><b>' + esc(s) + '</b> ' + M.filter(function (m) { return m.stage === s && (m.role === 'member' || m.role === 'observer'); }).length + '</span>'; });
    } else {
      ['car', 'wa', 'ces', 'mea'].forEach(function (k) { h += '<span><i style="background:' + R[k].hex + '"></i><b>' + esc(R[k].n) + '</b> ' + M.filter(function (m) { return m.r === k && (m.role === 'member' || m.role === 'observer'); }).length + '</span>'; });
    }
    h += '<span><i class="obs"></i>Observer (hatched)</span><span><i style="background:' + R.peer.hex + '"></i>Established producer peer</span>';
    if (host.hasAttribute('data-former')) h += '<span><i class="former"></i>Former member</span>';
    host.innerHTML = h;
  }

  /* home: click a country to open its page */
  $$('[data-map="home"]').forEach(function (host) {
    buildMap(host, { interactive: true, onPick: function (m) { if (m.u) location.href = NP.url(m.u); } });
    legend($('[data-legend]', host.parentNode), 'region');
  });

  /* members page: filters, colour modes, profile panel */
  $$('[data-map="full"]').forEach(function (host) {
    var page = host.closest('[data-members]'), panel = $('#panel'), leg = $('[data-legend]', host.parentNode);
    if (leg) leg.setAttribute('data-former', '');
    var mode = 'region', filt = 'all', selected = null;
    var map = buildMap(host, { interactive: true, labels: true, former: true, stageTip: true, onPick: function (m) { pick(m.n, true); } });
    legend(leg, mode);
    function matches(m) {
      if (filt === 'all') return true;
      if (filt === 'observer') return m.role === 'observer';
      if (filt === 'peer') return m.role === 'peer';
      return m.r === filt && m.role !== 'peer';
    }
    function applyFilter() {
      map.filter(matches);
      $$('.rg [data-name]', page).forEach(function (a) { a.classList.toggle('dim', !matches(byName[a.dataset.name] || {})); });
    }
    function pick(n, fromMap) {
      selected = n; map.select(n);
      $$('.rg [data-name]', page).forEach(function (a) { a.classList.toggle('sel', a.dataset.name === n); });
      renderPanel();
      if (!PREVIEW && history.replaceState && byName[n] && byName[n].s) history.replaceState(null, '', '#' + byName[n].s);
      if (fromMap && window.innerWidth < 1040) panel.scrollIntoView({ block: 'start', behavior: 'smooth' });
    }
    function renderPanel() {
      var m = byName[selected]; if (!m) return;
      var reg = R[m.r], img = m.img || reg.img, cap = m.img ? m.ic : reg.cap;
      var lat = Math.abs(m.ll[1]).toFixed(2) + '\u00b0' + (m.ll[1] >= 0 ? 'N' : 'S'), lon = Math.abs(m.ll[0]).toFixed(2) + '\u00b0' + (m.ll[0] >= 0 ? 'E' : 'W');
      var pillc = { car: '', wa: 'sav', ces: 'lat', mea: 'atl' }[m.r]; if (pillc === undefined) pillc = 'plain';
      var stage = m.stage ? esc(m.stage) + (m.legacy ? ', marginal legacy production' : '') : '';
      var h = (img ? '<figure class="ph">' + '<img src="' + esc(NP.url(img)) + '" alt="' + esc(cap) + '">' + (cap ? '<figcaption><i style="background:' + reg.hex + '"></i>' + esc(cap) + '</figcaption>' : '') + '</figure>' : '');
      h += '<div class="pb"><span class="pill ' + pillc + '">' + esc(m.role === 'peer' ? 'Established producer peer' : reg.n) + '</span><h2 class="pt">' + esc(m.n) + '</h2>';
      h += '<dl class="kv"><dt>Status</dt><dd>' + ROLE[m.role] + '</dd>' + (stage && m.role !== 'peer' ? '<dt>Stage</dt><dd>' + stage + '</dd>' : '') + '<dt>Capital</dt><dd>' + esc(m.cap) + ' <span class="small num" style="color:var(--ink-3)">' + lat + ' ' + lon + '</span></dd>';
      h += (m.np ? '<dt>Publications</dt><dd class="num">' + m.np + '</dd>' : '') + (m.ne ? '<dt>Events</dt><dd class="num">' + m.ne + '</dd>' : '') + '</dl>';
      if (m.rel && m.rel.length) h += '<div class="rel"><span class="label">Latest</span>' + m.rel.map(function (r) { return '<a href="' + esc(NP.url(r[1])) + '">' + esc(r[0]) + '<small>' + esc(r[2]) + ' \u00b7 ' + r[3] + '</small></a>'; }).join('') + '</div>';
      h += '<div class="btnrow">' + (m.u ? '<a class="btn sm" href="' + esc(NP.url(m.u)) + '">' + esc(m.n) + ' page</a>' : '') + '<button class="btn sm line" type="button" data-clear>Clear</button></div></div>';
      panel.innerHTML = h;
      $('[data-clear]', panel).addEventListener('click', function () { selected = null; map.select(null); $$('.rg .sel', page).forEach(function (a) { a.classList.remove('sel'); }); panel.innerHTML = panel0; });
    }
    var panel0 = panel.innerHTML;
    $$('[data-filter-chips] .chip', page).forEach(function (c) {
      c.addEventListener('click', function () {
        filt = c.getAttribute('data-f');
        $$('[data-filter-chips] .chip', page).forEach(function (x) { x.setAttribute('aria-pressed', String(x === c)); });
        applyFilter();
      });
    });
    $$('[data-colour]', page).forEach(function (b) {
      b.addEventListener('click', function () {
        mode = b.getAttribute('data-colour');
        $$('[data-colour]', page).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        map.recolour(mode); legend(leg, mode);
      });
    });
    $$('.rg [data-name]', page).forEach(function (a) {
      a.addEventListener('click', function (e) { if (e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); pick(a.dataset.name, false); panel.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); });
    });
    var fromHash = function () { var h0 = (location.hash || '').slice(1); if (h0 && bySlug[h0]) pick(bySlug[h0].n, false); };
    fromHash(); window.addEventListener('hashchange', fromHash);
  });

  /* country pages: zoomed locator */
  $$('[data-map="locator"]').forEach(function (host) {
    var m = byName[host.getAttribute('data-country')]; if (!m) return;
    var w = 240, h = 166, x = Math.max(0, Math.min(1000 - w, m.pt[0] - w / 2)), y = Math.max(10, Math.min(440 - h, m.pt[1] - h / 2));
    var map = buildMap(host, { viewBox: [x, y, w, h].join(' '), noGrat: true, decorative: true, former: true, dotR: 2.4 });
    var reg = R[m.r];
    $$('.land', map.svg).forEach(function (p) {
      var o = byName[p.dataset.name];
      if (!o) return;
      if (o.n === m.n) { p.style.fill = m.role === 'former' ? '#C9D3DB' : reg.hex; }
      else if (o.role === 'member' || o.role === 'observer') { p.style.fill = R[o.r].hex; p.style.opacity = '.28'; }
      else p.style.fill = '';
    });
    $$('.dot', map.svg).forEach(function (d) {
      var mine = d.dataset.name === m.n;
      d.style.display = mine ? '' : 'none';
      if (mine) { $('.halo', d).setAttribute('r', 7); $('.halo', d).style.opacity = '.25'; $$('circle', d).forEach(function (c) { c.setAttribute('fill', m.role === 'former' ? '#5F7182' : reg.hex); }); }
    });
    var lab = document.createElement('span'); lab.className = 'll'; lab.textContent = m.cap + ' \u00b7 ' + Math.abs(m.ll[1]).toFixed(1) + '\u00b0' + (m.ll[1] >= 0 ? 'N' : 'S') + ' ' + Math.abs(m.ll[0]).toFixed(1) + '\u00b0' + (m.ll[0] >= 0 ? 'E' : 'W');
    host.appendChild(lab);
  });
})();
