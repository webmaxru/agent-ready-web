# About this book

*The Agent-Ready Web* answers one question: how do I make my site work for AI agents? It does so layer by layer, on one running example, with every claim dated and sourced. This section explains how the book is organised, how to read it depending on your role, the conventions it uses, the code that comes with it and the versions it was tested with.

## Who should read this book

This book is for the whole web team: front-end, full-stack and back-end developers, designers, content and SEO people, product managers, architects, QA and test engineers, security engineers and the people who run analytics. The core reader is a developer who knows JavaScript or TypeScript, but every chapter starts in plain language and explains what each layer is for, what it costs and who owns it. You do not need any background in AI or machine learning. You need a working knowledge of the web: URLs, HTTP requests and responses, HTML pages and forms.

## How this book is organised: a roadmap

The book has 20 chapters in five parts, plus four appendices.

**Part 1, How agents use the web**, sets the scene. Chapter 1 looks at who visits a website today (training crawlers, search and answer engines, fetchers acting for one person, browsing agents and agents that call tools), takes "agent-ready" apart into layers, introduces the two graders the book uses and meets Nordlys Cabins, the running example. Chapter 2 makes one page agent-ready from start to finish, measuring before and after. Chapter 3 shows how agents see a page (DOM, accessibility tree, screenshots) and why semantic HTML is the cheapest agent-readiness work you will ever do.

**Part 2, Being found and read**, is about content. Chapter 4 covers who gets in: robots.txt, the AI crawlers and what each vendor documents, Content Signals and the IETF's AI preferences work. Chapter 5 describes your content with schema.org structured data. Chapter 6 makes content easy for agents to read: Markdown versions, content negotiation, llms.txt, sitemaps and Link headers.

**Part 3, Letting agents act**, is about capabilities. Chapter 7 designs an HTTP API that agents call correctly. Chapter 8 builds a server-side tool layer with the Model Context Protocol. Chapter 9 adds in-page tools with WebMCP. Chapter 10 is about designing tools that agents actually use well, tested against real models. Chapter 11 makes capabilities discoverable through well-known files and catalogs. Chapter 12 covers agents that buy: commerce and payment protocols. Chapter 13 brings it together in a decision framework for choosing the right agent interface.

**Part 4, Trust**, is about safety. Chapter 14 handles agents acting for users with OAuth and delegated access. Chapter 15 tells good agents from bad bots with Web Bot Auth, verified bots and rate limits. Chapter 16 covers security for agent-facing sites, including prompt injection. Chapter 17 covers privacy, consent and keeping a human in the loop.

**Part 5, Production**, is about running it. Chapter 18 tests agent-readiness, both with deterministic checks in CI and with evals against real models. Chapter 19 measures agent traffic and outcomes. Chapter 20 is about evolving with the standards: versioning your interfaces, watching the specifications you depend on and planning a year of work.

The appendices are for reference: Appendix A is a checklist per role, Appendix B lists every file, header and standard at a glance with its status and date, Appendix C is a glossary, and Appendix D collects resources and tools.

## Reading paths

You can read the book from cover to cover, and the chapters build on each other in that order. But most readers have a job to do, so here are a few other ways in. Chapter 1 has a table with a suggested path for each role on a web team (Table 1.4). Look up your row there. The paths below are organised by goal instead.

| Your goal | Read |
| --- | --- |
| Understand the topic in one afternoon | Chapters 1 and 2, then the summaries at the end of each chapter |
| Make a content site readable by agents | Chapters 2 to 6, then 19 |
| Let agents book, buy or do things on your site | Chapters 2, 3, 7 to 13, then 14 to 16 |
| Decide what to build (product and architecture) | Chapters 1, 13 and 20, then the chapters 13 points you to |
| Secure and govern agent access | Chapters 4, 14 to 17 |
| Put agent-readiness into CI and dashboards | Chapters 2, 18 and 19 |
| Already read *Tools, Not Clicks* | Skim Chapter 9, read everything else |

Two chapters are worth everyone's time. Chapter 2 shows the whole loop (measure, change one layer, measure again) on a single page, and Chapter 13 is where a team decides what to build.

## The scorecard

From Chapter 2 on, every layer chapter re-runs two graders against Nordlys Cabins and reports what moved. The first is isitagentready.com from Cloudflare, which checks the discovery files and headers a site publishes and sums them up as a level from 0 to 5. The second is the Agentic Browsing category of Lighthouse, which audits a page as a browsing agent experiences it (the accessibility tree, layout stability, WebMCP tools, llms.txt). The two measure different things, so they sometimes disagree, and the book explains why each time. Treat the scores as a progress bar, not as the goal.

## Conventions

**Hands-on sections.** Sections with substantial code start with a callout like this:

> **Hands-on:** This section builds a log classifier. If you do not write code, skip to the report it prints, then continue with "Referrals: what comes back".

The callout tells you what the code achieves and where to pick up again if you skip it. The text around the code always explains the result in plain words, so you can follow the argument without reading a line of JavaScript.

**Other callouts.** Notes, Tips and Warnings work as in any technical book. A **Still in flux** callout marks something built on a draft standard or an experimental feature that is likely to change after November 2026.

**Listings.** Every listing has a number, the path of the file it comes from in the demos repository, and a short description. Code in listings is copied from files that were run and tested. When a listing shows only part of a file, it says "excerpt" and shows a continuous range of lines, so you can find it in the file. HTTP exchanges, command output and reports that are not files are real output, produced while writing the book.

**Code in text.** File names, header fields, URLs, user-agent tokens and code elements appear in `monospace`.

**Footnotes and dates.** Every fact from the outside world has a footnote with the title, the site, the URL and when it was retrieved. Numbers that describe the state of the web (traffic shares, adoption, versions) always carry their date, and most of them are from 2 November 2026. When I could not verify something, the text says so. When something is my opinion, the text says that too.

**Figures.** Diagrams were made for this book. Charts with data name their source and date in the caption.

## The demos repository

All the code in this book lives in one repository, `webmaxru/agent-ready-web-demos` on GitHub.[^atb-1] It contains two kinds of code.

**Nordlys Cabins** (`nordlys-cabins/`) is the running example: a fictional company that rents six cabins in Norway, with `nordlys.example` as its domain in the book. It has what a real booking site has: a cabin list with filters, cabin pages, an availability check, a booking form with server-side validation, cancellation, member sign-in with "My bookings", a guide with articles, an FAQ and a contact form. Data lives in JSON files and in memory, so there is no database to set up. The booking flow comes in two front ends that share the same business logic: `clean`, with semantic HTML and native controls, and `legacy`, which is what many real booking sites ship (clickable `<div>` elements, a custom date picker, content loaded late from undocumented endpoints). Chapter 2 uses both to show the difference.

Each chapter adds one folder under `nordlys-cabins/layers/`, named after its chapter number, with tests named after the chapter (`tests/ch19-*.test.js`, for example). A layer is enabled for every `--upto` value at or above its number, so you can run the site as it stands after any chapter.

**Standalone demos** (`chapters/<chapter>/`) are small, separate projects for chapters that need a tool of their own, such as the log classifier in Chapter 19 or the standards watcher in Chapter 20. Most of them have no dependencies.

To run Nordlys Cabins, you need Node.js 24 or later (Node.js 26, the current LTS line, is what the demos' continuous integration uses for browser tests):

```sh
npm install
npm start                      # http://127.0.0.1:3000, clean front end, every layer
npm test                       # node:test, then Playwright
```

These are the variations you will use most:

| What you want | Command |
| --- | --- |
| The agent-hostile baseline from Chapter 2 | `npm start -- --variant=legacy --upto=0` |
| The site as it stands after chapter N | `npm start -- --upto=N` |
| Another port | `npm start -- --port=8080` |
| A frozen date, for repeatable output | `npm start -- --now=2026-11-10` |
| Only the server tests | `npm run test:unit` |
| Only the browser tests | `npm run test:e2e` |

Browser tests use Playwright's Chromium. Install it once with `npx playwright install chromium` if you have not used Playwright on your machine. The demo accounts for sign-in are `ingrid@nordlys.example` and `ola@nordlys.example`, both with the password `nordlys-demo`.

## Versions used

The book was written and tested in November 2026. These are the main versions:

| Software or standard | Version |
| --- | --- |
| Node.js | 24 or later (26 for browser tests in CI) |
| Hono and its Node.js server | 4.13.16 and 2.1.6 |
| Playwright | 1.64.1 |
| Chrome for Testing (Lighthouse and browser probes) | 156 |
| Lighthouse (Agentic Browsing category) | 13.6.0 |
| Model Context Protocol | revision 2026-07-28 |
| WebMCP | Draft Community Group Report of 2 November 2026, Chrome origin trial 149 to 162 |
| schema.org | 30.1 |
| Web Bot Auth | `draft-ietf-webbotauth-httpsig-protocol-01` |

Chapters that use other packages name their versions where they use them. Chapter 20 explains how to find out what changed since.

## How the book measures its own web edition

A book about agent-ready websites should have one, so the web edition of this book follows its own advice. It publishes semantic HTML, a Markdown version of every page, an llms.txt, a robots.txt with Content Signals, structured data, an Agent Skill for reading and citing the book, and three WebMCP tools for searching and reading it. All of it is generated from the same manuscript as the printed book.

The web edition is measured with the same two graders as Nordlys Cabins. On 2 November 2026, before its first public deployment, six page types scored 1.00 in Lighthouse's Agentic Browsing category in a local test run, and the isitagentready.com checks it passes, skips and does not need are explained in Chapter 20, together with why it skips one of them. The live scores will be on the book's site once it is deployed.

## Errata and feedback

Agent-readiness moves fast, and some details in this book will be out of date by the time you read them. If you find an error or something that changed, I would love to hear about it. The best places to reach me are the book's web edition and LinkedIn.[^atb-2]

[^atb-1]: Agent-ready web demos, https://github.com/webmaxru/agent-ready-web-demos (state of 2 November 2026).
[^atb-2]: The web edition of this book, https://agent-ready-web.salnikov.no, and Maxim Salnikov on LinkedIn, https://www.linkedin.com/in/webmax/.
