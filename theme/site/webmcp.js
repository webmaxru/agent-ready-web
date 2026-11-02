/* WebMCP tools for the web edition (https://webmachinelearning.github.io/webmcp/).
   The page offers AI agents in the browser three tools:
     search_book    the search form in the sidebar (and on the contents page), declared with the
                    toolname/tooldescription attributes. When an agent submits it, this script answers
                    with the results (SubmitEvent.respondWith) instead of navigating to search.html.
     list_chapters  the table of contents as data (registered with document.modelContext.registerTool)
     get_chapter    one chapter's Markdown, by number, label or slug (registerTool)
   All three are read-only. Everything is feature-detected: in a browser without WebMCP this file
   does nothing. In Chrome, WebMCP needs the origin trial token (tools/book.json, agent_ready.
   origin_trial_token) or chrome://flags/#enable-webmcp-testing. Generated data: toc.json and
   search-index.json (tools/build_site.py). */
(function () {
  'use strict';
  var mc = document.modelContext;
  if (!mc || typeof mc.registerTool !== 'function') return;

  var base = '';
  var q = document.getElementById('q');
  if (q) base = q.getAttribute('data-base') || '';
  var tocP = null;
  function toc() {
    if (!tocP) tocP = fetch(base + 'toc.json').then(function (r) { if (!r.ok) throw new Error('toc.json: HTTP ' + r.status); return r.json(); });
    return tocP;
  }
  function abs(u) { return new URL(base + u, location.href).href; }

  // ---- search_book: the declarative form tool
  function search(text, limit) {
    if (window.BookSearch) return window.BookSearch.find(text, limit);
    return Promise.resolve([]);
  }
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || form.getAttribute('toolname') !== 'search_book' || !e.agentInvoked) return;
    e.preventDefault();
    var text = (new FormData(form).get('q') || '').toString();
    e.respondWith(search(text, 10).then(function (rs) {
      return { query: text, count: rs.length, results: rs.map(function (r) { return { chapter: r.chapter, section: r.section, url: abs(r.url), snippet: r.snippet }; }) };
    }));
  });

  // ---- list_chapters and get_chapter: imperative tools, registered once, all at once
  var controller = new AbortController();
  var tools = [
    {
      name: 'list_chapters',
      title: 'List the chapters',
      description: 'List every part, chapter and appendix of the book with its number, title, page URL, ' +
        'Markdown URL, word count and section headings. Use it to find where a topic is covered.',
      inputSchema: { type: 'object', properties: {} },
      annotations: { readOnlyHint: true },
      execute: function () {
        return toc().then(function (t) {
          return { title: t.title, version: t.version, entries: t.entries.map(function (e) {
            return { kind: e.kind, label: e.label, title: e.title, url: abs(e.url), markdown: abs(e.markdown), words: e.words,
                     sections: e.sections.map(function (s) { return s.title; }) };
          }) };
        });
      }
    },
    {
      name: 'get_chapter',
      title: 'Read a chapter',
      description: 'Return the Markdown text of one chapter or appendix of the book. Pass the chapter number ' +
        '(for example "5"), the appendix letter (for example "B") or the page slug from list_chapters. ' +
        'Long chapters are cut at max_chars; the result says so and gives the full Markdown URL.',
      inputSchema: {
        type: 'object',
        properties: {
          chapter: { type: 'string', description: 'Chapter number, appendix letter, or page slug' },
          max_chars: { type: 'integer', minimum: 1000, maximum: 200000, description: 'Longest text to return (default 60000)' }
        },
        required: ['chapter']
      },
      annotations: { readOnlyHint: true },
      execute: function (input, opts) {
        var want = String((input && input.chapter) || '').trim().toLowerCase().replace(/^(chapter|appendix)\s+/, '');
        var max = (input && input.max_chars) || 60000;
        return toc().then(function (t) {
          var e = t.entries.filter(function (x) {
            return x.kind !== 'part' && (String(x.number || '').toLowerCase() === want || x.url.replace(/\.html$/, '') === want ||
              (x.label || '').toLowerCase() === want);
          })[0];
          // a wrong argument is an answer the agent can act on, not an exception it never sees
          if (!e) return { error: 'No chapter "' + want + '" in this book.', hint: 'Call list_chapters for the valid numbers, appendix letters and slugs.' };
          return fetch(base + e.markdown, { signal: opts && opts.signal }).then(function (r) {
            if (!r.ok) throw new Error(e.markdown + ': HTTP ' + r.status);
            return r.text();
          }).then(function (md) {
            return { label: e.label, title: e.title, url: abs(e.url), markdown_url: abs(e.markdown), truncated: md.length > max, text: md.slice(0, max) };
          });
        });
      }
    }
  ];
  tools.forEach(function (tool) {
    mc.registerTool(tool, { signal: controller.signal }).catch(function (err) {
      if (window.console) console.warn('WebMCP: could not register ' + tool.name + ': ' + err);
    });
  });
})();
