#!/usr/bin/env python3
"""Build the web edition (a static site) from the manuscript.

    python3 tools/build_site.py [--manuscript manuscript] [--out dist/site]

Reads manuscript/ (Book.txt order), tools/book.json, CHANGELOG.md (the release history page)
and theme/site/ (CSS, JS, templates, fonts, icons). Writes one page per part, chapter and
appendix, an about page, the release history, index.html, 404.html and search-index.json, plus
the agent-ready layer from tools/agent_ready.py (a Markdown twin of every page, llms.txt,
llms-full.txt, robots.txt with Content Signals, sitemap.xml, releases.xml, toc.json, JSON-LD,
.well-known/ files). Pages are flat <slug>.html files with relative links, so the same output
works on Azure Static Web Apps, on any static host and opened from a zip.
If book/staticwebapp.config.json exists it is copied into the output with the generated routes
(per-page Link headers, .well-known rewrites) added in front of its own.
"""
import argparse, datetime, html, json, pathlib, re, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bookmd
import agent_ready
from bookmd import esc, ROOT, THEME

SITE_THEME = THEME / "site"

def tpl(name):
    return (SITE_THEME / "templates" / name).read_text(encoding="utf-8")

def fill(template, **kw):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(kw.get(m.group(1), "")), template)

def page_name(s):
    return "about.html" if s.kind == "about" else f"{s.slug}.html"

def strip_tags(h):
    return html.unescape(re.sub(r"<[^>]+>", " ", h))

def short_label(s):
    if s.kind == "chapter":
        return f"Ch {s.number}"
    if s.kind == "appendix":
        return f"App {s.number}"
    return ""

# ------------------------------------------------------------------ navigation
def nav_html(secs, current, root=""):
    out, cur_idx = [], (secs.index(current) if current in secs else -1)
    open_list = False
    def close():
        nonlocal open_list
        if open_list:
            out.append("</ol>")
            open_list = False
    group = None
    for i, s in enumerate(secs):
        if s.kind == "part":
            close()
            out.append(f'<p class="nav-part"><a href="{root}{page_name(s)}">{esc(s.label)} · {esc(s.title)}</a></p>')
            group = "part"
            continue
        g = "appendix" if s.kind == "appendix" else ("front" if agent_ready._before_main(secs, s) else "back") if s.kind in ("about", "other") else "chapter"
        if g != "chapter" and group != g:
            close()
            out.append(f'<p class="nav-part">{ {"appendix": "Appendices", "front": "Front matter"}.get(g, "Back matter") }</p>')
            group = g
        if not open_list:
            out.append('<ol class="spine">')
            open_list = True
        state = "current" if s is current else "resolved" if (cur_idx >= 0 and i < cur_idx) else "pending"
        pin = f'<span class="pin-tag">{esc(short_label(s))}</span>' if short_label(s) else ""
        cls = ' class="is-current" aria-current="page"' if s is current else ""
        li = f'<li data-state="{state}"><a href="{root}{page_name(s)}"{cls}>{pin}<span class="chapter-name">{esc(s.title)}</span></a>'
        if s is current:
            h2 = [h for h in bookmd.headings(s) if h[0] == 2]
            if h2:
                li += '<ol class="sections">' + "".join(f'<li><a href="#{slug}">{esc(t)}</a></li>' for _, t, slug in h2) + "</ol>"
        out.append(li + "</li>")
    close()
    return "\n".join(out)

def search_form(cfg, root="", extra_class=""):
    """The book search: a real form (so it works as a WebMCP declarative tool) that app.js enhances.
    Agents can call it as the tool "search_book"; webmcp.js answers with the results instead of navigating."""
    tool = ""
    if agent_ready.ar(cfg).get("webmcp", {}).get("declarative_form"):
        tool = (' toolname="search_book" toolautosubmit tooldescription="Search the full text of the book '
                + esc(cfg["title"]) + '. Returns up to 10 matching sections with the chapter, the section title, '
                'the page URL with its anchor and a short text snippet."')
        pd = ' toolparamdescription="Words to look for in the book, for example: content signals robots.txt"'
    else:
        pd = ""
    return (f'<form class="search{extra_class}" role="search" action="{root}search.html" method="get"{tool}>'
            f'<input id="q" name="q" type="search" placeholder="Search the book  ( / )" aria-label="Search the book" '
            f'autocomplete="off" required minlength="2" data-base="{root}"{pd}>'
            f'<div id="results" class="results" aria-live="polite"></div></form>')

def common(cfg, root, title, desc, canonical, kind="chapter", og_type="article", md_name=None, ld=None):
    return dict(lang=cfg.get("language", "en"), page_title=esc(title), description=esc(desc), author=esc(cfg["author"]),
                canonical=esc(canonical), og_type=og_type, book_title=esc(cfg["title"]), book_subtitle=esc(cfg["subtitle"]),
                root=root, version=esc(bookmd.book_version(cfg)), newsletter_url=esc(cfg["newsletter_url"]),
                contact_url=esc(cfg["contact_url"]), kind=kind, cta_label=esc(cfg.get("cta_label", "Get updates")),
                sidebar_links=sidebar_links(cfg, root), search=search_form(cfg, root), head_extra=agent_ready.head_tags(cfg, root, md_name, ld))

def sidebar_links(cfg, root=""):
    links = [f'<a href="{root}releases.html">Release history</a>',
             f'<a href="{esc(cfg["newsletter_url"])}" rel="noopener">{esc(cfg.get("cta_label", "Get updates"))}</a>']
    if cfg.get("demo_url"):
        links.append(f'<a href="{esc(cfg["demo_url"])}" rel="noopener">Demo code</a>')
    if cfg.get("publisher_cta"):
        links.append(f'<a href="{esc(cfg["contact_url"])}" rel="noopener">For publishers: contact {esc(cfg["author"])}</a>')
    return "\n        ".join(links)

def footer_html(cfg, root=""):
    lines = bookmd.copyright_lines(cfg)
    first = esc(lines[0]) if lines else ""
    meta = [esc(bookmd.edition_line(cfg))]
    tw = bookmd.tested_with(cfg)
    if tw:
        meta.append(esc(tw))
    links = [f'<a href="{esc(cfg["newsletter_url"])}" rel="noopener">{esc(cfg.get("cta_label", "Get updates"))}</a>']
    if cfg.get("publisher_cta"):
        links.append(f'<a href="{esc(cfg["contact_url"])}" rel="noopener">For publishers: contact {esc(cfg["author"])}</a>')
    links.append(f'<a href="{esc(cfg["demo_url"])}" rel="noopener">Demo code (MIT)</a>')
    links.append(f'<a href="{root}llms.txt">llms.txt</a>')
    return (f'<p>{first} Free to read online; the text may not be republished without permission.</p>'
            f'<p class="meta">{" · ".join(meta)} · <a href="{root}releases.html">Release history</a></p>'
            f'<p>{" · ".join(links)}</p>')

def reading_cta(cfg, md_name=None):
    alt = f'<span>·</span><a href="{md_name}" type="text/markdown">This page as Markdown</a>' if md_name else ""
    return (f'<aside class="reading-cta" aria-label="Updates and other formats"><strong>Following the book?</strong> '
            f'<a href="{esc(cfg["newsletter_url"])}" rel="noopener">{esc(cfg.get("cta_label", "Get updates"))}</a>{alt}</aside>')

def pager(secs, s):
    reading = [x for x in secs]
    i = reading.index(s)
    prev_ = reading[i - 1] if i > 0 else None
    next_ = reading[i + 1] if i + 1 < len(reading) else None
    def a(x, cls, d):
        lab = f"{x.label}: " if x.label and x.kind != "part" else (f"{x.label} · " if x.kind == "part" else "")
        return f'<a class="{cls}" href="{page_name(x)}" rel="{ "prev" if cls == "prev" else "next"}"><span class="dir">{d}</span><span class="ttl">{esc(lab + x.title)}</span></a>'
    inner = (a(prev_, "prev", "Previous") if prev_ else "") + (a(next_, "next", "Next") if next_ else "")
    return f'<nav class="pager" aria-label="Previous and next">{inner}</nav>'

def header_html(s, cfg):
    crumbs = ['<a href="index.html">Contents</a>']
    if s.part is not None:
        crumbs.append(f'<span>/</span><a href="{page_name(s.part)}">{esc(s.part.label)}</a>')
    elif s.kind == "appendix":
        crumbs.append('<span>/</span><span>Appendices</span>')
    label = f'<span class="label eyebrow">{esc(s.label)}</span>' if s.label else ""
    return (f'<header class="chapter-header"><div class="chapter-header-inner"><nav class="breadcrumb" aria-label="Breadcrumb">{"".join(crumbs)}</nav>'
            f'{label}<h1>{esc(s.title)}</h1></div></header>')


def _unlink(html):
    """Drop links inside a heading (linkify turns a domain name in a heading into one), so the
    heading anchor never nests a link: nested links leave the anchor with no accessible name."""
    return re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', html, flags=re.S)

def add_heading_anchors(body):
    return re.sub(r'<h([234]) id="([^"]+)">(.*?)</h\1>', lambda m: f'<h{m.group(1)} id="{m.group(2)}"><a class="heading-anchor" href="#{m.group(2)}">{_unlink(m.group(3))}</a></h{m.group(1)}>', body, flags=re.S)

# ------------------------------------------------------------------ pages
def link_mapper(secs):
    names = {s.slug: page_name(s) for s in secs}
    def lm(href):
        sp = bookmd.split_internal_link(href)
        if sp is None:
            return None
        path, frag = sp
        if not path:
            return None
        target = names.get(path)
        if not target:
            return None
        return target + (f"#{frag}" if frag else "")
    return lm

def chapter_desc(s, body):
    text = strip_tags(re.sub(r'<blockquote class="epigraph">.*?</blockquote>', "", body, flags=re.S))
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:180].rsplit(" ", 1)[0] + "…") if len(text) > 180 else text

def build(manuscript, out):
    t0 = datetime.datetime.now()
    cfg = bookmd.load_config()
    version = bookmd.book_version(cfg)
    secs = bookmd.load_book(manuscript)
    warnings = bookmd.check_refs(secs, manuscript) + bookmd.config_warnings(cfg)
    for w in warnings:
        print("warning:", w, flush=True)
    out = pathlib.Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "assets" / "fonts").mkdir(parents=True)
    (out / "images").mkdir()
    for f in ("style.css", "app.js", "theme-toggle.js", "webmcp.js"):
        shutil.copy(SITE_THEME / f, out / "assets" / f)
    for f in (SITE_THEME / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "assets" / "fonts" / f.name)
    for f in (THEME / "fonts").glob("OFL-*.txt"):
        shutil.copy(f, out / "assets" / "fonts" / f.name)
    for f in ("favicon.svg", "apple-touch-icon.png"):
        if (SITE_THEME / f).exists():
            shutil.copy(SITE_THEME / f, out / f)
    site = cfg["site_url"].rstrip("/") + "/"
    arc = agent_ready.ar(cfg)
    rels = changelog_sections((ROOT / "CHANGELOG.md").read_text(encoding="utf-8") if (ROOT / "CHANGELOG.md").exists() else "")
    lastmod = agent_ready.release_date(rels, version)
    lm = link_mapper(secs)
    used_images = set()
    def image_url(src):
        p = bookmd.resolve_image(manuscript, src)
        if p:
            used_images.add(p)
            return "images/" + p.name
        return src
    search = []
    page_t = tpl("page.html")
    pages_written = []
    for s in secs:
        name = page_name(s)
        md_name = agent_ready.page_md_name(name) if arc.get("markdown_pages") else None
        ld = agent_ready.page_ld(cfg, s, site, page_name, secs)
        if s.kind == "part":
            items = "".join(f'<li><span class="pin-tag">{esc(c.label)}</span><a href="{page_name(c)}">{esc(c.title)}</a></li>' for c in s.children)
            intro = bookmd.render(s, link_map=lm, image_url=image_url)
            body = (f'<p class="spine-part">{esc(s.label)}</p><h1>{esc(s.title)}</h1>{intro}'
                    f'<ol class="part-chapters">{items}</ol>')
            html_ = fill(page_t, **common(cfg, "", f"{s.label}: {s.title} | {cfg['title']}", f"{s.label} of {cfg['title']}: {s.title}.", site + name, "part", md_name=md_name, ld=ld),
                         nav=nav_html(secs, s), header="", body=f'<div class="part-hero">{body}</div>', after=pager(secs, s), footer=footer_html(cfg))
            html_ = html_.replace('<main id="content" class="chapter-main">', '<main id="content">').replace('<article class="prose">', '<article>')
        else:
            body = bookmd.render(s, link_map=lm, image_url=image_url)
            body = add_heading_anchors(body)
            title = f"{s.label}: {s.title}" if s.label else s.title
            html_ = fill(page_t, **common(cfg, "", f"{title} | {cfg['title']}", chapter_desc(s, body), site + name, s.kind, md_name=md_name, ld=ld),
                         nav=nav_html(secs, s), header=header_html(s, cfg), body=body,
                         after=reading_cta(cfg, md_name) + pager(secs, s), footer=footer_html(cfg))
            # search entries: one per H2 section (plus the opening text)
            chunks = re.split(r'(?=<h2 id=")', body)
            for ch in chunks:
                m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>', ch, re.S)
                text = re.sub(r"\s+", " ", strip_tags(re.sub(r'<section class="footnotes".*', "", ch, flags=re.S))).strip()
                if not text:
                    continue
                search.append({"u": name + (f"#{m.group(1)}" if m else ""), "c": s.label or s.title,
                               "t": strip_tags(m.group(2)).strip() if m else s.title, "x": text[:4000]})
        (out / name).write_text(html_, encoding="utf-8")
        pages_written.append(name)
    for p in used_images:
        shutil.copy(p, out / "images" / p.name)

    write_index(cfg, secs, out, site)
    write_releases(cfg, secs, out, site, rels)
    write_404(cfg, out, site)
    write_search_page(cfg, secs, out, site)
    (out / "search-index.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # ---- the agent-ready layer (tools/agent_ready.py; AGENT-READY.md)
    (out / "toc.json").write_text(json.dumps({"title": cfg["title"], "version": version, "site": site,
                                              "entries": agent_ready.toc_entries(secs, page_name)}, ensure_ascii=False, indent=1), encoding="utf-8")
    if arc.get("markdown_pages"):
        agent_ready.write_markdown(out, cfg, secs, site, page_name, version)
        (out / "index.md").write_text(agent_ready.index_markdown(cfg, secs, site, page_name, version), encoding="utf-8")
        (out / "releases.md").write_text(f"# {cfg['title']}: release history\n\n" + "\n\n".join(
            f"## Version {v}" + (f" ({d})" if d else "") + f"\n\n{b}" for v, d, b in rels) + "\n", encoding="utf-8")
    (out / "llms.txt").write_text(agent_ready.llms_txt(cfg, secs, site, page_name, version), encoding="utf-8")
    if arc.get("llms_full_txt"):
        (out / "llms-full.txt").write_text(agent_ready.llms_full_txt(cfg, secs, site, page_name, version), encoding="utf-8")
    if arc.get("feed"):
        (out / "releases.xml").write_text(agent_ready.atom_feed(cfg, site, rels, bookmd.render_markdown), encoding="utf-8")
    urls = ["", "releases.html"] + [p for p in pages_written]
    (out / "sitemap.xml").write_text(agent_ready.sitemap_xml(site, urls, lastmod), encoding="utf-8")
    (out / "robots.txt").write_text(agent_ready.robots_txt(cfg, site), encoding="utf-8")
    well_known = agent_ready.write_well_known(out, cfg, site)
    swa = ROOT / "staticwebapp.config.json"
    if swa.exists():
        routes = agent_ready.swa_routes(cfg, ["index.html", "releases.html"] + pages_written, well_known)
        (out / "staticwebapp.config.json").write_text(agent_ready.merge_swa_config(swa.read_text(encoding="utf-8"), routes), encoding="utf-8")
    n = sum(1 for _ in out.rglob("*") if _.is_file())
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"site: {out} ({len(pages_written) + 3} pages, {len(used_images)} images, {n} files, {size / 1048576:.1f} MB) "
          f"in {(datetime.datetime.now() - t0).total_seconds():.1f} s", flush=True)
    return out

def hero_listing(secs, cfg):
    """The first listing of the book's first API chapter, shown on the cover as an artifact (content-driven)."""
    want = cfg.get("hero_listing", "")
    if not want:
        return ""
    for s in secs:
        body = bookmd.render(s)
        m = re.search(rf'<figure class="listing" id="listing-{re.escape(want.replace(".", "-"))}">(.*?)</figure>', body, re.S)
        if m:
            cap = re.search(r"<figcaption>(.*?)</figcaption>", m.group(1), re.S)
            pre = re.search(r"(<pre.*?</pre>)", m.group(1), re.S).group(1)
            lines = re.findall(r'<span class="ln">.*?</span>(?=<span class="ln">|</code>)', pre, re.S)
            if len(lines) > 24:  # the cover shows the head of the listing, the chapter has all of it
                pre = re.sub(r'(<code[^>]*>).*?(</code>)', lambda mm: mm.group(1) + "".join(lines[:24]) + mm.group(2), pre, flags=re.S)
            label = strip_tags(cap.group(1)).strip() if cap else ""
            lab = re.match(r"(Listing\s+\S+)", label)
            label = lab.group(1) + " · from the book" if lab else label
            return (f'<figure class="tool-artifact" aria-label="{esc(label)}"><div class="ta-bar"><i></i><i></i><i></i>'
                    f'<span>{esc(label)}</span></div>{pre}</figure>')
    return ""

def llms_artifact(cfg, secs, site):
    """The cover artifact when no hero listing is configured: the head of the site's own llms.txt."""
    lines = agent_ready.llms_txt(cfg, secs, site, page_name, bookmd.book_version(cfg)).splitlines()
    lines = [l if len(l) <= 64 else l[:63] + "…" for l in lines if l.strip()][:14]
    body = "".join(f'<span class="ln">{esc(l)}</span>' for l in lines)
    return (f'<figure class="tool-artifact" aria-label="GET /llms.txt · what an agent reads first"><div class="ta-bar"><i></i><i></i><i></i>'
            f'<span>GET /llms.txt · what an agent reads first</span></div><pre class="code long" data-lang="markdown"><code class="language-markdown">{body}</code></pre></figure>')

def write_index(cfg, secs, out, site):
    parts = [s for s in secs if s.kind == "part"]
    first = next((s for s in secs if s.kind == "chapter"), secs[0])
    pins = [f'<span class="pin-tag">v{esc(bookmd.book_version(cfg))}</span>', f'<span class="pin-tag">{esc(cfg.get("edition", ""))}</span>']
    tw = bookmd.tested_with(cfg)
    if tw:
        pins.append(f'<span class="pin-tag">{esc(tw)}</span>')
    artifact = hero_listing(secs, cfg) or llms_artifact(cfg, secs, site)
    hero = (f'<section class="hero"><div class="container hero-grid"><div>'
            f'<p class="eyebrow">{esc(cfg.get("eyebrow", ""))}</p><h1>{esc(cfg["title"])}</h1>'
            f'<p class="subtitle">{esc(cfg["subtitle"])}</p><p class="byline">{esc(cfg["author"])}</p>'
            f'<div class="pins">{"".join(pins)}</div><p class="lead">{esc(cfg["tagline"])}</p>'
            f'<div class="actions"><a class="btn btn-primary" href="{page_name(first)}">Start reading</a>'
            f'<a class="btn btn-secondary" href="{esc(cfg["newsletter_url"])}" rel="noopener">{esc(cfg.get("cta_label", "Get updates"))}</a>'
            f'<a class="btn btn-quiet" href="#contents">Contents ↓</a></div></div>'
            f'<div>{artifact}</div></div></section>')
    spine = "".join(f'<li class="spine-node"><a class="spine-link" href="#{p.slug}"><span class="spine-dot" aria-hidden="true"></span>'
                    f'<span class="spine-part">{esc(p.label)}</span><span class="spine-title">{esc(p.title)}</span></a></li>' for p in parts)
    blocks = []
    def entry(s):
        h2 = [t for lvl, t, _ in bookmd.headings(s) if lvl == 2 and t.lower() not in ("notes",)]
        secs_txt = esc(" · ".join(h2[:6]) + (" · …" if len(h2) > 6 else "")) if h2 else ""
        num = esc(s.number) if s.number else ""
        return (f'<li><span class="num">{num}</span><div><a href="{page_name(s)}">{esc(s.title)}</a>'
                + (f'<span class="secs">{secs_txt}</span>' if secs_txt else "") + "</div></li>")
    for p in parts:
        blocks.append(f'<div class="contents-part" id="{p.slug}"><div class="contents-part-head"><span class="spine-part">{esc(p.label)}</span>'
                      f'<h3><a href="{page_name(p)}">{esc(p.title)}</a></h3></div><ol class="contents-list">'
                      + "".join(entry(c) for c in p.children) + "</ol></div>")
    apps = [s for s in secs if s.kind == "appendix"]
    if apps:
        blocks.append('<div class="contents-part" id="appendices"><div class="contents-part-head"><span class="spine-part">Appendices</span>'
                      '<h3>Reference</h3></div><ol class="contents-list">' + "".join(entry(a) for a in apps) + "</ol></div>")
    others = [s for s in secs if s.kind in ("about", "other")]
    loose = [s for s in secs if s.kind == "chapter" and s.part is None]
    if loose:
        blocks.insert(0, '<div class="contents-part"><ol class="contents-list">' + "".join(entry(c) for c in loose) + "</ol></div>")
    if others:
        blocks.append('<div class="contents-part" id="back-matter"><div class="contents-part-head"><span class="spine-part">Back matter</span></div><ol class="contents-list">'
                      + "".join(f'<li><span class="num"></span><div><a href="{page_name(s)}">{esc(s.title)}</a></div></li>' for s in others)
                      + f'<li><span class="num"></span><div><a href="releases.html">Release history</a><span class="secs">Every edition, what changed, and when</span></div></li></ol></div>')
    words = sum(s.words for s in secs)
    contents = (f'<section class="section-block" id="contents"><div class="container"><p class="eyebrow">Contents</p><h2>{len([s for s in secs if s.kind == "chapter"])} chapters in {len(parts)} parts</h2>'
                f'<p class="lead">Free to read online, from the first chapter to the appendices. About {round(words, -3):,} words.</p>'
                f'{search_form(cfg, "", " contents-search")}'
                f'<nav class="resolution-path" aria-label="Parts"><ol class="spine-track">{spine}</ol></nav>'
                f'<div class="contents">{"".join(blocks)}</div></div></section>')
    second = (f'<div><h3>For publishers</h3><p>Interested in publishing this book? Contact {esc(cfg["author"])} directly.</p>'
              f'<a class="btn btn-secondary" href="{esc(cfg["contact_url"])}" rel="noopener">Contact {esc(cfg["author"])}</a></div>') if cfg.get("publisher_cta") else (
              f'<div><h3>For agents</h3><p>This site is built to be read by AI agents too: llms.txt, a Markdown version of every page, '
              f'structured data and WebMCP tools. The book explains each of them.</p>'
              f'<a class="btn btn-secondary" href="llms.txt">Read llms.txt</a></div>')
    cta = (f'<section class="section-block"><div class="container"><div class="cta-band">'
           f'<div><h3>{esc(cfg.get("cta_label", "Get updates"))}</h3><p>{esc(cfg.get("cta_blurb", ""))}</p>'
           f'<a class="btn btn-primary" href="{esc(cfg["newsletter_url"])}" rel="noopener">{esc(cfg.get("cta_label", "Get updates"))}</a></div>'
           f'{second}</div></div></section>')
    copyright_ = "".join(f"<p>{esc(l)}</p>" for l in bookmd.copyright_lines(cfg))
    footer = (copyright_ + f'<p class="meta">{esc(bookmd.edition_line(cfg))} · <a href="releases.html">Release history</a> · '
              f'<a href="about.html">About the author</a></p>')
    ld = agent_ready.book_ld(cfg, secs, site, page_name, bookmd.book_version(cfg),
                             agent_ready.release_date(changelog_sections((ROOT / "CHANGELOG.md").read_text(encoding="utf-8")) if (ROOT / "CHANGELOG.md").exists() else [], bookmd.book_version(cfg)))
    page = fill(tpl("index.html"), **common(cfg, "", f'{cfg["title"]}: {cfg["subtitle"]}', cfg["description"], site, "index", "book",
                                            md_name="index.md" if agent_ready.ar(cfg).get("markdown_pages") else None, ld=ld),
                body=hero + contents + cta, footer=footer)
    (out / "index.html").write_text(page, encoding="utf-8")

def changelog_sections(text):
    """[(version, date, markdown body)] from CHANGELOG.md (Keep a Changelog)."""
    out = []
    for m in re.finditer(r"^## \[([^\]]+)\]\s*[-–—]?\s*(.*?)\s*$\n(.*?)(?=^## \[|\Z)", text, re.M | re.S):
        body = re.sub(r"(?m)^\[[^\]]+\]: \S+\s*$", "", m.group(3)).strip()
        out.append((m.group(1), m.group(2), body))
    return out

def write_releases(cfg, secs, out, site, rels):
    current = bookmd.book_version(cfg)
    parts = ['<p class="lead">Every edition of the book is a numbered version. Each one is also published as a PDF and an EPUB '
             'built from exactly the same text. A major version is a new edition, a minor version adds or rewrites sections, '
             'and a patch version fixes mistakes.</p>']
    nav = []
    for ver, date, body in rels:
        vid = "v" + ver.replace(".", "-")
        nav.append((vid, ver))
        md_body = re.sub(r"\]\((?!https?:|#|mailto:)([^)]+)\)", "](#)", body)  # repo-relative links make no sense here
        md_body = re.sub(r"\[([^\]]+)\]\(#\)", r"\1", md_body)
        state = '<span class="pin-tag">current</span>' if ver == current else ""
        date_txt = esc(date) if date else ""
        parts.append(f'<h2 id="{vid}">Version {esc(ver)}</h2><p class="release-assets"><span class="pin-tag">{date_txt}</span>{state}</p>'
                     + bookmd.render_markdown(md_body))
    body = "\n".join(parts)
    fake = type("S", (), {})()
    nav_extra = '<ol class="spine">' + "".join(f'<li data-state="pending"><a href="#{v}"><span class="pin-tag">v{esc(x)}</span><span class="chapter-name">Version {esc(x)}</span></a></li>' for v, x in nav) + "</ol>"
    header = ('<header class="chapter-header"><div class="chapter-header-inner"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Contents</a></nav>'
              '<span class="label eyebrow">Release history</span><h1>Editions and changes</h1></div></header>')
    md = "releases.md" if agent_ready.ar(cfg).get("markdown_pages") else None
    page = fill(tpl("page.html"), **common(cfg, "", f"Release history | {cfg['title']}", f"Every edition of {cfg['title']} and what changed.", site + "releases.html", "releases", md_name=md),
                nav=nav_html(secs, None) + '<p class="nav-part">Release history</p>' + nav_extra, header=header,
                body=f'<div class="release-history">{body}</div>', after=reading_cta(cfg, md), footer=footer_html(cfg))
    (out / "releases.html").write_text(page, encoding="utf-8")

def write_search_page(cfg, secs, out, site):
    """search.html?q=...: where the search form lands without JavaScript's dropdown (app.js fills it)."""
    header = ('<header class="chapter-header"><div class="chapter-header-inner"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Contents</a></nav>'
              '<span class="label eyebrow">Search</span><h1>Search the book</h1></div></header>')
    body = ('<div id="search-page" class="search-page" aria-live="polite"><p>Type at least two letters in the search box. '
            'Results list every matching section with a link to it.</p></div>')
    page = fill(tpl("page.html"), **common(cfg, "", f"Search | {cfg['title']}", f"Search the full text of {cfg['title']}.", site + "search.html", "search"),
                nav=nav_html(secs, None), header=header, body=body, after="", footer=footer_html(cfg))
    page = page.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n  <link rel="canonical"')
    (out / "search.html").write_text(page, encoding="utf-8")

def write_404(cfg, out, site):
    body = ('<section class="notfound"><div><p class="code404">404</p><h1>This page is not in the book</h1>'
            '<p class="lead">The link may be from an older edition. The contents page has every chapter.</p>'
            '<p><a class="btn btn-primary" href="/index.html">Go to the contents</a></p></div></section>')
    page = fill(tpl("plain.html"), **common(cfg, "/", f"Page not found | {cfg['title']}", cfg["description"], site + "404.html", "plain", "website"), body=body)
    page = page.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n  <link rel="canonical"')
    (out / "404.html").write_text(page, encoding="utf-8")

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manuscript", default=str(bookmd.MANUSCRIPT))
    ap.add_argument("--out", default=str(ROOT / "dist" / "site"))
    a = ap.parse_args(argv)
    build(pathlib.Path(a.manuscript), pathlib.Path(a.out))

if __name__ == "__main__":
    main()
