# About this book

*Agent-Ready Websites in Action* answers one question: how do I make my site work for AI agents? It does so layer by layer, on one running example, with every claim dated and sourced. This section explains how the book is organised, how to read it depending on your role, the conventions it uses, the code that comes with it and the versions it was tested with.

## Who should read this book

This book is for the whole web team: front-end, full-stack and back-end developers, designers, content and SEO people, product managers, architects, QA and test engineers, security engineers and the people who run analytics. The core reader is a developer who knows JavaScript or TypeScript, but every chapter starts in plain language and explains what each layer is for, what it costs and who owns it. You do not need any background in AI or machine learning. You need a working knowledge of the web: URLs, HTTP requests and responses, HTML pages and forms.

## How this book is organised: a roadmap

The book has 12 chapters in three parts, plus four appendices.

**Part 1, Seen and read**, is about the layers every site needs. Chapter 1 looks at who visits a website today, what "agent-ready" means as six layers, how to decide which layers you need, and introduces Nordlys Cabins and the two graders. Chapter 2 makes one page agent-ready end to end, with a first look at your own logs. Chapter 3 shows how agents see a page: the HTML, the accessibility tree and the screenshot, and what client-side rendering does to them. Chapter 4 decides who gets in, with robots.txt, Content Signals and AI Preferences, and checks the claims with IP ranges, reverse DNS and Web Bot Auth. Chapter 5 makes content readable: structured data that stays true to the page, Markdown by content negotiation, llms.txt and sitemaps.

**Part 2, Letting agents act**, is about capabilities for reading and for guests. Chapter 6 chooses the right agent interface for a site. Chapter 7 designs tools that agents can actually use, with a first threat model. Chapter 8 builds server-side tools, a plain API and an MCP server, and announces them through Link headers, the API catalog, MCP server cards, OAuth metadata, Agent Skills and the ARD manifest. Chapter 9 puts tools into the page with WebMCP.

**Part 3, Trust and production**, is about running it safely. Chapter 10 covers security for agent-facing sites. Chapter 11 handles agents acting for users: OAuth and delegated access, consent, the human in the loop, the agent-safe checkout and the two ways a shop can let an agent buy. Chapter 12 tests and measures agent-readiness in production and ends with a roadmap for your team.

The appendices are for reference: Appendix A is a checklist per role, Appendix B lists every file, header and standard with its status and date (including the commerce protocols), Appendix C covers pay per crawl and content licensing, and Appendix D is a glossary with resources.

## Reading paths

You can read the book from cover to cover, and the chapters build on each other in that order. But most readers have a job to do, so here are a few other ways in. Chapter 1 has a table with a suggested path for each role on a web team (Table 1.4). Look up your row there. The paths below are organised by goal instead.

| Your goal | Read |
| --- | --- |
| Understand the topic in one afternoon | Chapters 1 and 2, then the summaries at the end of each chapter |
| Make a content site readable by agents | Chapters 2 to 5, then 12 |
| Let agents book, buy or do things on your site | Chapters 2, 3, 6 to 9, then 10 and 11 |
| Decide what to build (product and architecture) | Chapters 1 and 6, then the chapters 6 points you to |
| Secure and govern agent access | Chapters 4, 10 and 11 |
| Put agent-readiness into CI and dashboards | Chapters 2 and 12 |
| Already read *Tools, Not Clicks* | Skim Chapter 9, read everything else |

Two chapters are worth everyone's time. Chapter 2 shows the whole loop (measure, change one layer, measure again) on a single page, and Chapter 6 is where a team decides what to build.

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

Layers live in folders under `nordlys-cabins/layers/`, with tests in `tests/`. A layer is enabled for every `--upto` value at or above its number, so you can run the site at any stage. The folder numbers come from the first edition of this book, which had 20 chapters, and the demos keep them so that every command in the repository still works. Table 0.1 maps the chapters of this edition to the layers and standalone demos they use.

Table 0.1 The chapters of this edition and their demos

| Chapter | Layer folders (`nordlys-cabins/layers/`) | Standalone demos (`chapters/`) |
| --- | --- | --- |
| 1 | none | none |
| 2 | `02-first-steps` | `02-your-first-agent-ready-page`, `19-measuring-agent-traffic` (a first log run) |
| 3 | `03-perception` | `03-how-agents-see-a-page` |
| 4 | `04-crawler-controls`, `15-bot-identity` | `15-signing-agent` |
| 5 | `05-structured-data`, `06-agent-content` | none |
| 6 | none | `13-choosing-the-right-agent-interface` |
| 7 | `10-tool-design` | `10-designing-tools-agents-can-use` |
| 8 | `07-public-api`, `08-mcp-server`, `11-discovery` | none |
| 9 | `09-webmcp` | none |
| 10 | `16-security` | `16-security-for-agent-facing-sites` |
| 11 | `14-oauth`, `17-consent`, `12-commerce` | `14-connect-an-agent` |
| 12 | `19-agent-analytics`, `20-versioning` | `18-testing-agent-readiness`, `19-measuring-agent-traffic`, `20-evolving-with-the-standards` |
| Appendix B | none | `appendix-b-reference` |

Because `--upto=N` turns on every layer up to N, a high number also turns on layers that this edition introduces later, for example `--upto=15` for the bot identity layer of Chapter 4.

**Standalone demos** (`chapters/<chapter>/`) are small, separate projects for chapters that need a tool of their own, such as the log classifier in Chapter 12 or the decision helper in Chapter 6. Most of them have no dependencies.

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

Chapters that use other packages name their versions where they use them. Chapter 12 and Appendix B explain how to keep track of what changes.

## Errata and feedback

Agent-readiness moves fast, and some details in this book will be out of date by the time you read them. If you find an error or something that changed, I would love to hear about it. The best places to reach me are the book's web edition and LinkedIn.[^atb-2]

[^atb-1]: Agent-ready web demos, https://github.com/webmaxru/agent-ready-web-demos (state of 2 November 2026).
[^atb-2]: The web edition of this book, https://agent-ready-web.salnikov.no, and Maxim Salnikov on LinkedIn, https://www.linkedin.com/in/webmax/.
