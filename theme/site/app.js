/* Web edition behaviour: mobile menu, copy buttons, current-section highlight, search.
   Search reads search-index.json (written by tools/build_site.py) on first use. Pressing Enter
   without picking a result submits the form to search.html?q=..., which lists every match.
   window.BookSearch is the same engine for webmcp.js (the WebMCP tools). */
(function () {
  var menu = document.querySelector('.menu');
  if (menu) menu.addEventListener('click', function () {
    var open = document.body.classList.toggle('nav-open');
    menu.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') document.body.classList.remove('nav-open'); });
  document.addEventListener('click', function (e) {
    if (document.body.classList.contains('nav-open') && !e.target.closest('.sidebar') && !e.target.closest('.menu')) document.body.classList.remove('nav-open');
  });
  document.querySelectorAll('.sidebar a').forEach(function (a) { a.addEventListener('click', function () { document.body.classList.remove('nav-open'); }); });

  // copy buttons
  document.querySelectorAll('pre.code').forEach(function (pre) {
    var b = document.createElement('button');
    b.className = 'copy'; b.type = 'button'; b.textContent = 'Copy'; b.setAttribute('aria-label', 'Copy code');
    b.addEventListener('click', function () {
      var lines = Array.prototype.map.call(pre.querySelectorAll('.ln'), function (l) { return l.textContent; });
      var text = lines.length ? lines.join('\n') : pre.innerText;
      var done = function (t) { b.textContent = t; setTimeout(function () { b.textContent = 'Copy'; }, 1500); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(function () { done('Copied'); }, function () { done('Press Ctrl+C'); });
      else done('Press Ctrl+C');
    });
    pre.appendChild(b);
  });

  // highlight the current section in the sidebar
  var links = Array.prototype.slice.call(document.querySelectorAll('.chapter-nav ol.sections a'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {}; links.forEach(function (a) { map[decodeURIComponent(a.hash.slice(1))] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && map[e.target.id]) { links.forEach(function (l) { l.classList.remove('active'); }); map[e.target.id].classList.add('active'); }
      });
    }, { rootMargin: '-10% 0px -80% 0px' });
    document.querySelectorAll('.prose h2[id]').forEach(function (h) { io.observe(h); });
  }

  // search: one engine (window.BookSearch) for the dropdown, the search page and the WebMCP tools
  var q = document.getElementById('q'), box = document.getElementById('results');
  var base = (q && q.getAttribute('data-base')) || '';
  var index = null;
  function load() {
    return index ? Promise.resolve(index) : fetch(base + 'search-index.json').then(function (r) { return r.json(); }).then(function (j) {
      index = j.map(function (e) { e.lx = e.x.toLowerCase(); e.lt = e.t.toLowerCase(); return e; }); return index;
    });
  }
  function find(text, limit) {
    var v = String(text || '').trim().toLowerCase();
    if (v.length < 2) return Promise.resolve([]);
    return load().then(function (ix) {
      var terms = v.split(/\s+/).filter(Boolean), hits = [];
      ix.forEach(function (e) {
        var score = 0, ok = true;
        for (var i = 0; i < terms.length; i++) { var t = terms[i], inT = e.lt.indexOf(t) >= 0, inX = e.lx.indexOf(t) >= 0; if (!inT && !inX) { ok = false; break; } score += (inT ? 10 : 0) + (inX ? 1 : 0); }
        if (ok) hits.push([score, e]);
      });
      hits.sort(function (a, b) { return b[0] - a[0]; });
      return hits.slice(0, limit || 12).map(function (h) {
        var e = h[1], i = e.lx.indexOf(terms[0]);
        var snip = i < 0 ? e.x.slice(0, 160) : (i > 60 ? '…' : '') + e.x.slice(Math.max(0, i - 60), i + 120) + '…';
        return { chapter: e.c, section: e.t, url: e.u, snippet: snip, terms: terms };
      });
    });
  }
  window.BookSearch = { load: load, find: find, base: base };
  function escH(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(s, terms) { var h = escH(s); terms.forEach(function (t) { h = h.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); }); return h; }
  function item(r) { return '<a href="' + base + r.url + '"><div class="r-c">' + escH(r.chapter) + '</div><div class="r-t">' + mark(r.section, r.terms) + '</div><div class="r-x">' + mark(r.snippet, r.terms) + '</div></a>'; }

  // search.html?q=...: the full result list
  var pageBox = document.getElementById('search-page');
  var qs = new URLSearchParams(location.search).get('q');
  if (pageBox && qs) {
    if (q) q.value = qs;
    find(qs, 50).then(function (rs) {
      pageBox.innerHTML = '<p>' + rs.length + (rs.length === 1 ? ' section matches' : ' sections match') + ' <strong>' + escH(qs) + '</strong>.</p>' +
        (rs.length ? '<div class="results results-page">' + rs.map(item).join('') + '</div>' : '');
    });
  }

  if (!q || !box) return;
  var sel = -1;
  function run() {
    var v = q.value.trim();
    if (v.length < 2) { box.classList.remove('open'); box.innerHTML = ''; return; }
    find(v, 12).then(function (rs) {
      sel = -1;
      box.innerHTML = rs.map(item).join('') || '<div class="none">No matches</div>';
      box.classList.add('open');
    });
  }
  q.addEventListener('input', run);
  q.addEventListener('focus', function () { load(); if (q.value.trim().length > 1) run(); });
  q.addEventListener('keydown', function (e) {
    var items = Array.prototype.slice.call(box.querySelectorAll('a'));
    if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && items.length) {
      e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      items.forEach(function (a, i) { a.classList.toggle('sel', i === sel); });
    } else if (e.key === 'Enter' && items.length && sel >= 0) { e.preventDefault(); location.href = items[sel].href; }
    else if (e.key === 'Escape') { box.classList.remove('open'); q.blur(); }
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.search')) box.classList.remove('open'); });
  document.addEventListener('keydown', function (e) { if (e.key === '/' && document.activeElement !== q && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); q.focus(); } });
})();
