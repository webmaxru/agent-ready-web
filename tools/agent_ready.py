#!/usr/bin/env python3
"""The agent-ready layer of the web edition: everything an AI agent or crawler reads besides the HTML.

Called by tools/build_site.py; configured in one place, the "agent_ready" object in tools/book.json.
Everything here is generated from the manuscript, tools/book.json and CHANGELOG.md; nothing is
written by hand per chapter. AGENT-READY.md describes each file, the checks it serves and the
checks the site skips on purpose.

  <page>.md                 the chapter's Markdown (Markua attribute lines removed), one per HTML page,
                            linked from the page with <link rel="alternate" type="text/markdown"> and a
                            Link: header (staticwebapp.config.json, generated routes)
  index.md, releases.md     the contents and the release history as Markdown
  llms.txt, llms-full.txt   llmstxt.org format: the book's map, and the whole book in one file
  robots.txt                RFC 9309 groups for AI search, user-triggered and training crawlers, each
                            with a Content-Signal line (contentsignals.org) and the Sitemap
  sitemap.xml               every page with <lastmod> (the release date of this version)
  releases.xml              Atom feed of the release history (CHANGELOG.md)
  toc.json                  the table of contents as data (used by the WebMCP tools)
  .well-known/agent-skills/ an Agent Skills discovery index (v0.2.0) with one skill: how to read,
                            search and cite this book
  .well-known/ard.json      Agentic Resource Discovery manifest (also served as ai-catalog.json)
  JSON-LD                   schema.org Book (with its Chapter parts) on the contents page, and
                            Chapter + BreadcrumbList on every chapter page (head_tags())

The .well-known files are also written to well-known/ (no dot) and the generated SWA routes
rewrite /.well-known/<file> to them, so the files are served even if a deploy step skips
dot-folders.
"""
import datetime, hashlib, html, json, pathlib, re

DEFAULTS = {
    "content_signal": "search=yes, ai-input=yes, ai-train=no",
    "training_crawlers": "follow-content-signal",   # or "allow" / "disallow"
    "ai_crawlers": {"search": [], "user": [], "training": []},
    "llms_full_txt": True, "markdown_pages": True, "json_ld": True, "feed": True,
    "webmcp": {"imperative_tool": True, "declarative_form": True},
    "agent_skill": True, "ard_manifest": True, "publisher_domain": "", "origin_trial_token": "",
}
SKILL_NAME = "read-this-book"
WELL_KNOWN_FILES = ("ard.json", "ai-catalog.json", "agent-skills/index.json", f"agent-skills/{SKILL_NAME}/SKILL.md")

def ar(cfg):
    out = dict(DEFAULTS)
    out.update(cfg.get("agent_ready") or {})
    return out

def esc(s):
    return html.escape(str(s), quote=True)

def page_md_name(page_name):
    return re.sub(r"\.html$", ".md", page_name)

def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ------------------------------------------------------------------ Markdown
def section_markdown(cfg, s, site, html_name, version):
    """The manuscript Markdown of one file, with a one-line source note agents can cite."""
    body = s.md.rstrip() + "\n"
    note = (f'> From "{cfg["title"]}" by {cfg["author"]}, version {version}. '
            f'Web page: {site}{html_name}. Free to read; not licensed for republication.\n\n')
    m = re.match(r"(#\s+[^\n]+\n)", body)
    return (m.group(1) + "\n" + note + body[m.end():].lstrip("\n")) if m else note + body

def first_sentence(s, limit=200):
    text = re.sub(r"```.*?```", "", s.body_md(), flags=re.S)
    for para in re.split(r"\n\s*\n", text):
        p = para.strip()
        if not p or p.startswith(("#", ">", "!", "|", "-", "*", "**Listing", "[^")) or p.lower().startswith("this chapter covers"):
            continue
        p = re.sub(r"\[\^[^\]]+\]", "", p)
        p = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", p)
        p = re.sub(r"[*_`]", "", re.sub(r"\s+", " ", p))
        m = re.match(r"(.+?[.!?])(\s|$)", p)
        p = m.group(1) if m else p
        return p if len(p) <= limit else p[:limit].rsplit(" ", 1)[0] + "…"
    return ""

def write_markdown(out, cfg, secs, site, page_name, version):
    for s in secs:
        (out / page_md_name(page_name(s))).write_text(section_markdown(cfg, s, site, page_name(s), version), encoding="utf-8")

def toc_entries(secs, page_name):
    rows = []
    for s in secs:
        rows.append({"kind": s.kind, "label": s.label, "number": s.number, "title": s.title,
                     "url": page_name(s), "markdown": page_md_name(page_name(s)), "words": s.words,
                     "sections": [{"title": t, "anchor": slug} for lvl, t, slug in _headings(s) if lvl == 2]})
    return rows

def _headings(s):
    import bookmd
    return bookmd.headings(s)

def index_markdown(cfg, secs, site, page_name, version):
    lines = [f"# {cfg['title']}", "", f"> {cfg['subtitle']}. By {cfg['author']}. Version {version}.", "",
             cfg.get("description", ""), "", "## Contents", ""]
    for s in secs:
        lab = f"{s.label}: " if s.label else ""
        indent = "" if s.kind in ("part", "other", "about") or s.part is None else "  "
        lines.append(f"{indent}- [{lab}{s.title}]({page_md_name(page_name(s))})")
    lines += ["", f"Release history: [releases.md](releases.md). Demo code (MIT): {cfg.get('demo_url', '')}", ""]
    return "\n".join(lines)

# ------------------------------------------------------------------ llms.txt
def llms_txt(cfg, secs, site, page_name, version):
    a = ar(cfg)
    out = [f"# {cfg['title']}", "", f"> {cfg['subtitle']}. {cfg.get('description', '')}", "",
           f"By {cfg['author']}. Version {version}, {cfg.get('edition', '')}. Free to read online at {site}. "
           f"Every page has a Markdown version: replace .html with .md. Content signals for this site: {a['content_signal']} "
           f"(see robots.txt). Code examples are MIT-licensed in {cfg.get('demo_url', '')}.", ""]
    groups = [("Front matter", [s for s in secs if s.kind in ("other", "about") and _before_main(secs, s)]),
              ("Chapters", [s for s in secs if s.kind == "chapter"]),
              ("Appendices", [s for s in secs if s.kind == "appendix"]),
              ("Back matter", [s for s in secs if s.kind in ("other", "about") and not _before_main(secs, s)])]
    for title, items in groups:
        if not items:
            continue
        out += [f"## {title}", ""]
        for s in items:
            lab = f"{s.label}: " if s.label else ""
            part = f" ({s.part.label}: {s.part.title})" if getattr(s, "part", None) is not None else ""
            desc = first_sentence(s)
            out.append(f"- [{lab}{s.title}]({site}{page_md_name(page_name(s))}){part}" + (f": {desc}" if desc else ""))
        out.append("")
    out += ["## Optional", ""]
    if a.get("llms_full_txt"):
        out.append(f"- [The whole book in one file]({site}llms-full.txt): every chapter's Markdown, in reading order")
    out.append(f"- [Release history]({site}releases.md): every version of the book and what changed")
    if cfg.get("demo_url"):
        out.append(f"- [Demo code]({cfg['demo_url']}): the running example and every chapter's demos (MIT)")
    comp = cfg.get("companion_book") or {}
    if comp.get("url"):
        out.append(f"- [{comp.get('title', 'Companion book')}]({comp['url']}): the author's earlier book, the deep dive on WebMCP")
    out.append("")
    return "\n".join(out)

def _before_main(secs, s):
    first_main = next((i for i, x in enumerate(secs) if x.kind in ("part", "chapter")), len(secs))
    return secs.index(s) < first_main

def llms_full_txt(cfg, secs, site, page_name, version):
    head = (f"# {cfg['title']}\n\n> {cfg['subtitle']}. By {cfg['author']}. Version {version}. "
            f"The complete text of the web edition ({site}), one file per section below, in reading order.\n\n")
    parts = [section_markdown(cfg, s, site, page_name(s), version) for s in secs]
    return head + "\n\n---\n\n".join(parts)

# ------------------------------------------------------------------ robots.txt
def robots_txt(cfg, site):
    a = ar(cfg)
    sig = a["content_signal"].strip()
    crawlers = a.get("ai_crawlers") or {}
    train_policy = a.get("training_crawlers", "follow-content-signal")
    if train_policy == "follow-content-signal":
        train_allow = not re.search(r"ai-train\s*=\s*no", sig)
    else:
        train_allow = train_policy == "allow"
    lines = ["# robots.txt for the web edition of " + cfg["title"] + " (generated by tools/agent_ready.py).",
             "# Content-Signal states how the text may be used once fetched (https://contentsignals.org/):",
             "#   search   = building a search index and showing links and short excerpts",
             "#   ai-input = feeding the text into an AI model to answer a question (grounding, RAG)",
             "#   ai-train = training or fine-tuning AI models",
             "# Change it in one place: \"content_signal\" under \"agent_ready\" in tools/book.json.", "",
             "User-agent: *", f"Content-Signal: {sig}", "Allow: /", ""]
    def group(comment, names, allow):
        if not names:
            return []
        g = [comment] + [f"User-agent: {n}" for n in names] + [f"Content-Signal: {sig}", "Allow: /" if allow else "Disallow: /", ""]
        return g
    lines += group("# AI search crawlers: they index pages that AI assistants cite and link to.", crawlers.get("search", []), True)
    lines += group("# User-triggered fetchers: they read a page because a person asked an assistant to.", crawlers.get("user", []), True)
    lines += group("# AI training crawlers: " + ("allowed." if train_allow else "the book is not offered for model training (ai-train=no). Blocking them does not affect search or AI answers."),
                   crawlers.get("training", []), train_allow)
    lines += [f"Sitemap: {site}sitemap.xml", ""]
    return "\n".join(lines)

# ------------------------------------------------------------------ sitemap and feed
def sitemap_xml(site, urls, lastmod):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{esc(site + u)}</loc><lastmod>{lastmod}</lastmod></url>\n" for u in urls) + "</urlset>\n")

def release_date(releases, version):
    for v, date, _ in releases:
        if v == version and re.match(r"\d{4}-\d{2}-\d{2}$", date or ""):
            return date
    dated = [d for _, d, _ in releases if re.match(r"\d{4}-\d{2}-\d{2}$", d or "")]
    return max(dated) if dated else datetime.date.today().isoformat()

def atom_feed(cfg, site, releases, render_markdown):
    dated = [(v, d, b) for v, d, b in releases if re.match(r"\d{4}-\d{2}-\d{2}$", d or "")]
    updated = (max(d for _, d, _ in dated) if dated else datetime.date.today().isoformat()) + "T00:00:00Z"
    out = ['<?xml version="1.0" encoding="utf-8"?>', '<feed xmlns="http://www.w3.org/2005/Atom">',
           f"  <title>{esc(cfg['title'])}: releases</title>", f'  <link href="{esc(site)}releases.xml" rel="self"/>',
           f'  <link href="{esc(site)}releases.html"/>', f"  <id>{esc(site)}releases.xml</id>", f"  <updated>{updated}</updated>",
           f"  <author><name>{esc(cfg['author'])}</name></author>"]
    for v, d, body in dated:
        vid = "v" + v.replace(".", "-")
        out += ["  <entry>", f"    <title>Version {esc(v)}</title>", f'    <link href="{esc(site)}releases.html#{vid}"/>',
                f"    <id>{esc(site)}releases.html#{vid}</id>", f"    <updated>{d}T00:00:00Z</updated>",
                f'    <content type="html">{esc(render_markdown(body))}</content>', "  </entry>"]
    out.append("</feed>\n")
    return "\n".join(out)

# ------------------------------------------------------------------ JSON-LD
def _person(cfg):
    p = {"@type": "Person", "name": cfg["author"]}
    if cfg.get("author_url"):
        p["url"] = cfg["author_url"]
    if cfg.get("author_same_as"):
        p["sameAs"] = cfg["author_same_as"]
    return p

def book_ld(cfg, secs, site, page_name, version, date):
    parts = [s for s in secs if s.kind in ("chapter", "appendix")]
    d = {"@context": "https://schema.org", "@type": "Book", "@id": site + "#book", "name": cfg["title"],
         "alternativeHeadline": cfg.get("subtitle", ""), "description": cfg.get("description", ""), "url": site,
         "author": _person(cfg), "inLanguage": cfg.get("language", "en"), "bookEdition": cfg.get("edition", ""),
         "version": version, "dateModified": date, "isAccessibleForFree": True, "bookFormat": "https://schema.org/EBook",
         "copyrightHolder": _person(cfg), "copyrightYear": cfg.get("year", ""),
         "hasPart": [{"@type": "Chapter", "name": (f"{s.label}: {s.title}" if s.label else s.title), "position": i + 1,
                      "url": site + page_name(s)} for i, s in enumerate(parts)]}
    if cfg.get("demo_url"):
        d["isBasedOn"] = {"@type": "SoftwareSourceCode", "name": "Demo code", "codeRepository": cfg["demo_url"], "license": "https://opensource.org/license/mit"}
    return d

def page_ld(cfg, s, site, page_name, secs):
    crumbs = [{"@type": "ListItem", "position": 1, "name": cfg["title"], "item": site}]
    if getattr(s, "part", None) is not None:
        crumbs.append({"@type": "ListItem", "position": 2, "name": f"{s.part.label}: {s.part.title}", "item": site + page_name(s.part)})
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": (f"{s.label}: {s.title}" if s.label else s.title), "item": site + page_name(s)})
    graph = [{"@type": "BreadcrumbList", "itemListElement": crumbs}]
    if s.kind in ("chapter", "appendix"):
        parts = [x for x in secs if x.kind in ("chapter", "appendix")]
        graph.append({"@type": "Chapter", "name": f"{s.label}: {s.title}", "url": site + page_name(s), "position": parts.index(s) + 1,
                      "author": _person(cfg), "inLanguage": cfg.get("language", "en"),
                      "isPartOf": {"@type": "Book", "@id": site + "#book", "name": cfg["title"], "url": site},
                      "encoding": {"@type": "MediaObject", "encodingFormat": "text/markdown", "contentUrl": site + page_md_name(page_name(s))}})
    return {"@context": "https://schema.org", "@graph": graph}

def ld_script(data):
    j = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{j}</script>'

def head_tags(cfg, root, md_name=None, ld=None):
    """Extra <head> tags for a page: Markdown alternate, feed, llms.txt, ARD, origin trial, JSON-LD."""
    a = ar(cfg)
    t = []
    if md_name and a.get("markdown_pages"):
        t.append(f'<link rel="alternate" type="text/markdown" href="{root}{md_name}">')
    if a.get("feed"):
        t.append(f'<link rel="alternate" type="application/atom+xml" title="{esc(cfg["title"])}: releases" href="{root}releases.xml">')
    t.append(f'<link rel="describedby" type="text/plain" href="{root}llms.txt">')
    if a.get("ard_manifest"):
        t.append(f'<link rel="ard" type="application/json" href="{root}.well-known/ard.json">')
    tok = (a.get("origin_trial_token") or "").strip()
    if tok:
        t.append(f'<meta http-equiv="origin-trial" content="{esc(tok)}">')
    if ld is not None and a.get("json_ld"):
        t.append(ld_script(ld))
    return "\n  ".join(t)

# ------------------------------------------------------------------ .well-known
def skill_md(cfg, site):
    return f"""---
name: {SKILL_NAME}
description: Read, search and cite "{cfg['title']}" by {cfg['author']}, a book on making websites work for AI agents. Use when a question is about agent-readiness of websites (llms.txt, structured data, robots.txt and content signals, MCP, WebMCP, agent identity, security, measuring agent traffic) and you want the book's answer with a link.
---

# Read "{cfg['title']}"

The web edition at {site} is free to read. Every page has a Markdown twin.

## Find the right part

1. Fetch {site}llms.txt. It lists every chapter with a one-line summary and a link to its Markdown.
2. Or fetch {site}toc.json for the same contents as data (kind, number, title, url, markdown, section anchors).
3. To search the full text, fetch {site}search-index.json: one entry per section with `u` (URL with anchor), `c` (chapter), `t` (section title) and `x` (plain text). In a browser that supports WebMCP, the pages also offer the tools `search_book`, `list_chapters` and `get_chapter`.

## Read

- Replace `.html` with `.md` in any page URL to get its Markdown, or follow the page's `<link rel="alternate" type="text/markdown">`.
- {site}llms-full.txt is the whole book in one file. Prefer single chapters when you can.

## Cite and use

- Cite the HTML page URL with its section anchor, the book title, the author ({cfg['author']}) and the version (in llms.txt and on every page).
- Content signals for this site are `{ar(cfg)['content_signal']}` (robots.txt). The text is free to read and quote briefly with a link; it is not licensed for republication or model training.
- Code examples are MIT-licensed in {cfg.get('demo_url', '')}.
"""

def well_known_files(cfg, site):
    a = ar(cfg)
    files = {}
    if a.get("agent_skill"):
        sm = skill_md(cfg, site)
        files[f"agent-skills/{SKILL_NAME}/SKILL.md"] = sm
        files["agent-skills/index.json"] = json.dumps({
            "$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
            "skills": [{"name": SKILL_NAME, "type": "skill-md",
                        "description": f'Read, search and cite "{cfg["title"]}" (llms.txt, Markdown pages, search index, WebMCP tools).',
                        "url": f"/.well-known/agent-skills/{SKILL_NAME}/SKILL.md", "digest": "sha256:" + sha256(sm)}]}, indent=2) + "\n"
    if a.get("ard_manifest") and a.get("agent_skill"):
        host = re.sub(r"^https?://", "", site).strip("/")
        pub = (a.get("publisher_domain") or host).strip()
        slug = re.sub(r"[^a-z0-9.-]", "-", cfg.get("file_stem", "book").lower()).strip("-")
        manifest = {"specVersion": "1.0",
                    "host": {"displayName": f"{cfg['title']} (web edition)", "identifier": site.rstrip("/")},
                    "entries": [{"identifier": f"urn:air:{pub}:books:{slug}-reader",
                                 "displayName": f"Read \"{cfg['title']}\"",
                                 "type": 'text/markdown; profile="urn:air:agent-skills"',
                                 "url": f"{site}.well-known/agent-skills/{SKILL_NAME}/SKILL.md",
                                 "description": f"An agent skill for reading, searching and citing the book {cfg['title']} by {cfg['author']}.",
                                 "representativeQueries": ["how do I make my website work for AI agents",
                                                           "what should llms.txt contain for a website",
                                                           "how do content signals in robots.txt work",
                                                           "when should a site use MCP or WebMCP"],
                                 "tags": ["book", "agent-readiness", "web"]}]}
        txt = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        files["ard.json"] = txt
        files["ai-catalog.json"] = txt
    return files

def write_well_known(out, cfg, site):
    files = well_known_files(cfg, site)
    for rel, text in files.items():
        for base in (".well-known", "well-known"):
            p = out / base / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
    return sorted(files)

# ------------------------------------------------------------------ Azure Static Web Apps routes
CT = {".json": "application/json", ".md": "text/markdown; charset=utf-8"}

def swa_routes(cfg, html_pages, well_known):
    """Routes merged into dist/site/staticwebapp.config.json: Link headers and .well-known rewrites."""
    a = ar(cfg)
    routes = []
    for rel in well_known:
        ext = pathlib.PurePosixPath(rel).suffix
        h = {"Access-Control-Allow-Origin": "*"}
        if ext in CT:
            h["Content-Type"] = CT[ext]
        routes.append({"route": f"/.well-known/{rel}", "rewrite": f"/well-known/{rel}", "headers": h})
    common = ['</llms.txt>; rel="describedby"; type="text/plain"']
    if a.get("feed"):
        common.append('</releases.xml>; rel="alternate"; type="application/atom+xml"')
    home = ['</index.md>; rel="alternate"; type="text/markdown"'] + common + ['</sitemap.xml>; rel="sitemap"; type="application/xml"']
    if a.get("ard_manifest") and "ard.json" in well_known:
        home.append('</.well-known/ard.json>; rel="ard"; type="application/json"')
    if a.get("agent_skill"):
        home.append('</.well-known/agent-skills/index.json>; rel="describedby"; type="application/json"')
    for r in ("/", "/index.html"):
        routes.append({"route": r, "headers": {"Link": ", ".join(home)}})
    if a.get("markdown_pages"):
        for name in html_pages:
            if name == "index.html":
                continue
            routes.append({"route": "/" + name, "headers": {"Link": ", ".join([f'</{page_md_name(name)}>; rel="alternate"; type="text/markdown"'] + common)}})
    return routes

def merge_swa_config(root_config_text, routes):
    cfg = json.loads(root_config_text)
    cfg["routes"] = routes + list(cfg.get("routes", []))   # generated exact routes first; first match wins
    mt = cfg.setdefault("mimeTypes", {})
    mt.setdefault(".md", "text/markdown; charset=utf-8")
    mt.setdefault(".txt", "text/plain; charset=utf-8")
    # compact: Static Web Apps rejects a config file over 20 KB (infra/check_site.py checks it)
    return json.dumps(cfg, ensure_ascii=False, separators=(",", ":")) + "\n"
