# Changelog

All notable changes to *Agent-Ready Websites in Action* (first edition: *The Agent-Ready Web*) are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/) as read for a book (see [RELEASING.md](RELEASING.md)).

Each version is a Git tag `vX.Y.Z`. Its GitHub Release carries the PDF, the print PDF, the EPUB and the HTML edition built from that tag. The web edition shows this file as its release history and as the Atom feed `releases.xml`.

## [2.0.0] - 2026-11-04

The second edition, *Agent-Ready Websites in Action*: a draft on the `v2` branch, not released.

### Changed

- The book follows a shorter outline: 12 chapters in three parts (Seen and read, Letting agents act, Trust and production) and appendices A–D, condensed from the 20 chapters of v1.0.0. About 106,800 words, 37 figures, 362 pages in the PDF (v1.0.0: about 189,000 words, 54 figures, 628 pages).
- Agent Skills and the ARD manifest are part of Chapter 8, next to MCP server cards and the API catalog. Pay per crawl, x402, MPP, RSL and TDMRep moved to the new Appendix C.
- Chapter and figure numbers changed throughout. The demos repository is unchanged: About this book maps its layer folders (numbered after the first edition's chapters) to the chapters of this edition.

### Added

- Chapter 3: a section on rendering for client-rendered apps (server-side rendering, hydration, no-JavaScript fallbacks), built on the measurements of the first edition.
- Chapter 11: "Two ways to buy: in-page tools or a protocol checkout", on WebMCP tools and a UCP checkout side by side, which channel an agent should use, whether the human-in-the-loop guarantees carry over, and which record a dispute relies on. Thanks to Francesco Marinoni Moretto for the question.

## [1.0.0] - 2026-11-02

The first edition.

### Added

- The manuscript, as listed in `manuscript/Book.txt`: a preface, About this book, 20 chapters in five parts (foundations, content, capabilities, trust, operations), appendices A–D (a checklist by role, a reference, a glossary and resources) and About the author. About 189,000 words, 54 figures and 99 code listings, 626 pages in the PDF.
- A validation table for every chapter, appendix and the front matter (`validation/`, summarised in VALIDATION.md): 1,029 checked rows, each with its source and retrieval date. The status of every standard is as of 2 November 2026.
- The demos for every chapter in [webmaxru/agent-ready-web-demos](https://github.com/webmaxru/agent-ready-web-demos/releases/tag/v1.0.0) v1.0.0: Nordlys Cabins, made agent-ready one layer per chapter, with its tests.
- The web edition at https://agent-ready-web.salnikov.no, agent-ready by the book's own checklist: a Markdown version of every page, `llms.txt` and `llms-full.txt`, `robots.txt` with Content Signals, `sitemap.xml`, JSON-LD, an agent skill and an ARD manifest under `/.well-known/`, and WebMCP tools for searching and reading the book (see AGENT-READY.md).
- The PDF (7 × 9.25 in), the paperback interior for KDP (7.5 × 9.25 in), the EPUB and the HTML edition.
