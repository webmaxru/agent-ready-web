# Agent-Ready Websites in Action

This repository holds the manuscript of *Agent-Ready Websites in Action: How to make your website work for AI agents, layer by layer* by Maxim Salnikov (version 2.0.0, 12 chapters in three parts), together with its figure sources, editorial records, theme, build tools and hosting setup. The runnable demos, including the running example Nordlys Cabins, live in the companion repository [webmaxru/agent-ready-web-demos](https://github.com/webmaxru/agent-ready-web-demos). The web edition is hosted on Azure Static Web Apps at https://agent-ready-web.salnikov.no once deployed (see [`DEPLOY.md`](DEPLOY.md)).

The book develops the ideas of the author's earlier book, *Tools, Not Clicks: Building Agent-Ready Websites with WebMCP* ([webmcp.salnikov.no](https://webmcp.salnikov.no)), into the whole field of agent-readiness, and this repository uses the same layout and build.

## What lives where

| Path | What it is |
| --- | --- |
| [`manuscript/`](manuscript/) | The book: one Markdown file per part, chapter and appendix, in the order of `Book.txt`. Plain Markdown, no styling. Images go in `manuscript/resources/images/` and are referenced as `images/<file>.png` (Leanpub's layout). |
| [`figures/`](figures/) | Sources of the figures (`figures/src/*.svg`) and the script that renders them into `manuscript/resources/images/`. Read [`figures/PALETTE.md`](figures/PALETTE.md) first. |
| [`theme/`](theme/) | Everything about how the book looks: the web edition (`site/`), the PDF (`print/`), the EPUB (`epub/`) and the fonts. Swapping the theme never touches the manuscript. See [`theme/README.md`](theme/README.md). |
| [`tools/`](tools/) | The build: [`build.py`](tools/build.py) is the one entry point; [`book.json`](tools/book.json) holds the title, version, copyright lines, links and the agent-ready settings; [`agent_ready.py`](tools/agent_ready.py) writes the files agents read; [`lint_manuscript.py`](tools/lint_manuscript.py) checks the manuscript; [`serve.py`](tools/serve.py) previews the site with its hosting headers; [`wordcount.py`](tools/wordcount.py) writes the table below. |
| [`tools/fixtures/manuscript/`](tools/fixtures/manuscript/) | A two-page build fixture that uses every manuscript convention. CI builds it while `manuscript/` is still empty. It is never published. |
| `editorial/` | Editorial logs, one per chapter: the passes each chapter went through and what was checked. |
| [`infra/`](infra/) | Azure Static Web Apps infrastructure for the web edition, with a one-command deploy. See [`DEPLOY.md`](DEPLOY.md) and [`CUSTOM-DOMAIN.md`](CUSTOM-DOMAIN.md). |
| [`staticwebapp.config.json`](staticwebapp.config.json) | The web edition's hosting rules and security headers; the site build copies it into `dist/site/` and adds the generated routes (Link headers, `.well-known` rewrites). |
| [`.github/workflows/`](.github/workflows/) | Book CI (lint, all builds, EPUBCheck and the agent-readiness audit on every pull request), Release (from a merged release pull request or a `v*` tag) and the web deploy. |
| [`AGENT-READY.md`](AGENT-READY.md) | How the web edition makes itself agent-ready, which checks it passes and which it skips on purpose. |
| [`CHANGELOG.md`](CHANGELOG.md), [`RELEASING.md`](RELEASING.md) | What changed in each version, and how to cut a release. |
| [`VALIDATION.md`](VALIDATION.md) | How the book was checked against the specifications, documentation and tools it describes, with every finding and its source. |
| `dist/` | Build output (not committed). |

## Manuscript

Read in this order. Word counts are `wc -w` on the Markdown source (code included); the last column is the share of words inside code blocks. The table is generated: `python3 tools/wordcount.py --update`.

<!-- wordcount:start -->
The manuscript is being written. The table fills in with `python3 tools/wordcount.py --update` once `manuscript/Book.txt` lists the chapters.
<!-- wordcount:end -->

## Manuscript conventions

The manuscript stays clean Markdown, so the same files work on Leanpub (or at a publisher) and in this repo's build. `python3 tools/lint_manuscript.py` checks most of these rules.

1. CommonMark with pipe tables, fenced code with a language tag and footnotes. No raw HTML, CSS classes, inline styles, front matter or Leanpub-only asides. The only Markua attribute lines are `{class: part}` in the part files and `{sample: true}` / `{sample: false}`, which mark the Leanpub sample.
2. One `#` heading per file: `# Chapter N: Title`, `# Appendix X: Title`, `# Preface`, `# About the Author`, and `# Part 1: Title` in the part files. Sections use `##` to `####`.
3. Figures are one line, `![Figure N.M — Caption.](images/figure-N-M.png)`. The alt text is the caption. The SVG source lives in `figures/src/`, and `python3 figures/render.py figure-N-M` renders it to `manuscript/resources/images/`.
4. Listings have a bold label line above the fence: `**Listing 8.3** `nordlys-cabins/layers/08-mcp-server/server.js` — title`. Every listing is byte-identical to a file in the demos repository, or marked as an excerpt.
5. Callouts are blockquotes that start with a bold word: `> **Note:**`, `> **Warning:**`, `> **Tip:**`, `> **Still in flux:**` (for drafts), and `> **Hands-on:**`, which opens every code-heavy section and tells readers who don't write code what the section achieves and where to pick up again.
6. Footnote ids are unique across the book: `[^ch08-3]`, `[^appA-2]`, `[^pre-1]`.
7. Cross-references use chapter numbers in words ("Chapter 6"), not file links.
8. No placeholders of any kind. If something is unknown, the text says so in plain words.

## Build

Python 3.11 or later.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r tools/requirements.txt
python -m playwright install chromium      # only for the PDFs

python3 tools/lint_manuscript.py            # placeholders, raw HTML, images, footnotes, numbering, Book.txt, anchors
python3 tools/build.py                      # everything; or: build.py site | zip | epub | pdf | print
python3 tools/serve.py                      # preview dist/site on http://localhost:8080 with the hosting headers
```

| Command | Output |
| --- | --- |
| `python3 tools/build.py site` | `dist/site/`: the web edition (home page, one page per part, chapter and appendix, About, Release history, search, 404) and its agent-ready layer (a Markdown twin of every page, `llms.txt`, `llms-full.txt`, `robots.txt` with Content Signals, `sitemap.xml`, `releases.xml`, JSON-LD, `.well-known/` files, WebMCP tools; see [`AGENT-READY.md`](AGENT-READY.md)) |
| `python3 tools/build.py zip` | `dist/Agent-Ready-Websites-in-Action-HTML-v<version>.zip`: the web edition for offline reading |
| `python3 tools/build.py epub` | `dist/Agent-Ready-Websites-in-Action-Maxim-Salnikov-v<version>.epub` |
| `python3 tools/build.py pdf` | `dist/Agent-Ready-Websites-in-Action-Maxim-Salnikov-v<version>.pdf`: 7 × 9.25 in, for reading and Leanpub |
| `python3 tools/build.py print` | `dist/Agent-Ready-Websites-in-Action-Maxim-Salnikov-v<version>-print-7.5x9.25.pdf`: the KDP paperback interior, 7.5 × 9.25 in, same text block |

Any command takes `--manuscript DIR` to build another manuscript folder, for example the fixture: `python3 tools/build.py --manuscript tools/fixtures/manuscript`. The PDF builds use Playwright's Chromium, or the browser in `CHROME_PATH`.

## Editions and releases

Every release is a Git tag `vX.Y.Z` with a GitHub Release carrying the PDF, the print PDF, the EPUB and the HTML edition (zip), all built from that tag, with the version's [`CHANGELOG.md`](CHANGELOG.md) section as its notes. Releases come only from merged code: merging a release pull request cuts the release (see [`RELEASING.md`](RELEASING.md)). The current version is in [`tools/book.json`](tools/book.json) and on the book's copyright page. The web edition shows the release history at https://agent-ready-web.salnikov.no/releases.html and as an Atom feed at `/releases.xml`.

- **PDF**, 7 × 9.25 in, for reading and Leanpub.
- **Print PDF**, 7.5 × 9.25 in, the paperback interior for KDP (7 × 9.25 is not a KDP trim size; the print variant keeps the text block, so the pagination stays the same).
- **EPUB 3**, checked with EPUBCheck, for e-book stores.
- **Web edition**, deployed to Azure Static Web Apps on every change to `main` and on every release.
- [Book CI](.github/workflows/ci.yml) lints the manuscript, builds every edition, runs EPUBCheck and the Lighthouse agentic-browsing audit on every pull request; the built files are attached to the run.

## Publishing

The target publisher is Manning. If a publisher takes the book, its production process and contract decide which of the self-publishing channels below stay open, so treat them as the fallback.

**Leanpub.** Either upload the release's PDF and EPUB (readers get this theme), or let Leanpub build from this repository: its GitHub writing mode reads `manuscript/Book.txt` and the files it lists, with images from `manuscript/resources/images/`. In that mode, turn off Leanpub's chapter numbering (the headings carry their numbers), and mark the sample with `{sample: true}` / `{sample: false}` lines.

**KDP paperback.** Trim size **7.5 × 9.25 in**, no bleed, black ink on white paper. Upload the release's `-print-7.5x9.25.pdf`. Its inside margin is 1.125 in, above KDP's minimum for a book of 501 to 700 pages (0.75 in). Use KDP's cover calculator with the final page count for the spine.

**Kindle e-book.** Upload the release's EPUB and check it in Kindle Previewer.

## Licence

The text is © 2026 Maxim Salnikov, all rights reserved; it is free to read online and not licensed for republication. The demo code in [webmaxru/agent-ready-web-demos](https://github.com/webmaxru/agent-ready-web-demos) is MIT-licensed. The fonts in `theme/fonts/` are under the SIL Open Font License (the licence files are next to them).
