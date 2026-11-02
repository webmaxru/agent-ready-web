# Changelog

All notable changes to *The Agent-Ready Web: How to make your website work for AI agents, layer by layer* are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/) as read for a book (see [RELEASING.md](RELEASING.md)).

Each version is a Git tag `vX.Y.Z`. Its GitHub Release carries the PDF, the print PDF, the EPUB and the HTML edition built from that tag. The web edition shows this file as its release history and as the Atom feed `releases.xml`.

## [1.0.0] - 2026-11-02

The first edition.

### Added

- The manuscript, as listed in `manuscript/Book.txt`: a preface, About this book, 20 chapters in five parts (foundations, content, capabilities, trust, operations), appendices A–D (a checklist by role, a reference, a glossary and resources) and About the author. About 189,000 words, 54 figures and 99 code listings, 626 pages in the PDF.
- A validation table for every chapter, appendix and the front matter (`validation/`, summarised in VALIDATION.md): 1,029 checked rows, each with its source and retrieval date. The status of every standard is as of 2 November 2026.
- The demos for every chapter in [webmaxru/agent-ready-web-demos](https://github.com/webmaxru/agent-ready-web-demos/releases/tag/v1.0.0) v1.0.0: Nordlys Cabins, made agent-ready one layer per chapter, with its tests.
- The web edition at https://agent-ready-web.salnikov.no, agent-ready by the book's own checklist: a Markdown version of every page, `llms.txt` and `llms-full.txt`, `robots.txt` with Content Signals, `sitemap.xml`, JSON-LD, an agent skill and an ARD manifest under `/.well-known/`, and WebMCP tools for searching and reading the book (see AGENT-READY.md).
- The PDF (7 × 9.25 in), the paperback interior for KDP (7.5 × 9.25 in), the EPUB and the HTML edition.
