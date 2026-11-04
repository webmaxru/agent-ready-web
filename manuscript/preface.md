{sample: true}

# Preface

In the autumn of 2026 I finished a book about one browser API. *Tools, Not Clicks* is about WebMCP, the proposal that lets a web page hand an AI agent a set of tools instead of making it click through the interface. Its first edition was tagged on 15 October 2026, and its second major version was released on 2 November 2026, because the specification had moved that much in between.[^pre-1]

While I was writing it, the same question kept coming back from people who had nothing to do with WebMCP. A content lead at a publisher. A product manager at a travel company. A front-end developer whose manager had read an article about "AI traffic". A designer who wanted to know whether agents can use her date picker. They all asked some version of what my editor at Manning put in one sentence: "How do I make my site work for AI agents?"

WebMCP is one answer to that question, and not the first one most sites need. Before an agent can call a tool on your page, it has to be allowed in, find your content, read it without guessing, understand what your business offers, and act in a way you can trust and measure. Each of those steps has its own standards, its own tools and its own owners on a web team. This book covers all of them, one layer at a time, and tells you when each layer is worth the effort.

## How this book relates to *Tools, Not Clicks*

The two books are companions, and they do not compete. *Tools, Not Clicks* goes deep on one layer: the WebMCP API, its design, its security model and how to build with it in real applications. This book goes wide. It covers access control for crawlers, structured data, content formats for agents, APIs, MCP servers, WebMCP, tool design, discovery, commerce, delegated access, bot identity, security, privacy, testing, measurement and the standards process, and it helps you choose between them.

So WebMCP gets one chapter here (Chapter 9), written for readers who meet it for the first time. If you have read *Tools, Not Clicks*, skim that chapter for the November 2026 changes and spend your time elsewhere. If you finish this book and want to go deeper on in-page tools, the other book is waiting for you, and its web edition is free to read.[^pre-2]

## Why now

You could ask whether it is too early for a book like this. Most of the standards it covers are drafts. Some of them will change before you read this. I thought about that a lot, and I decided that 2026 is exactly the right time, for three reasons.

The first reason is that agents became regular visitors. Cloudflare Radar, which sees a large share of the web's traffic, shows AI bots and crawlers as a steady part of it, and the big AI companies now document separate crawlers for training, for search and for fetching a page because a person asked a question about it.[^pre-3] Chapter 1 has the numbers. In simple words: if you run a public website, agents already visit it, whether or not you did anything for them.

The second reason is that "agent-ready" became measurable. In April 2026 Cloudflare launched isitagentready.com, which scans a site for the files and headers agents look for. In May 2026 Lighthouse, the auditing tool built into Chrome, added an Agentic Browsing category that checks a page the way a browsing agent experiences it.[^pre-4] The two graders measure different things and sometimes disagree, but together they turned a vague idea into scores a team can track. This book uses both of them from Chapter 2 to Chapter 12.

The third reason is that the platforms started moving for you. In 2026 a large e-commerce platform began shipping WebMCP tools and commerce protocol files on its stores by default, and CDNs and hosting providers added switches for agent verification, Markdown versions of pages and crawler controls.[^pre-5] When your platform can turn something on for you, the important skill is knowing what it does, whether you want it and how to check that it works. That is what this book is for.

And yes, things will change. Appendix B lists every standard in this book with its status and date and explains how to read where it stands, and Chapter 12 turns that into a habit for your team. Every claim in this book carries the date it was true and the source it came from, so you can check it again.

## Who this book is for

When I planned the book, the first answer was "front-end and full-stack developers who know JavaScript", and they remain the core readers. If that is you, every chapter has hands-on sections, and the demos repository has code you can run.

But agent-readiness is not a job one developer does on a Friday afternoon. Deciding which crawlers may read your content is a business decision. Structured data and content formats belong to the people who own the content. Whether to expose a booking tool to agents is a product decision, and how it looks when an agent fills in a form on someone's behalf is a design decision. Security, privacy, testing and analytics each have their own owners. So I wrote the book for the whole web team. Every chapter starts with plain language, code-heavy sections are clearly marked, and Chapter 1 has a reading path for each role.

You do not need to know anything about AI to read this book. You need to know how the web works, roughly: what a URL, an HTTP request and an HTML page are. When the book needs something from the world of language models, it explains it where it comes up.

## How I wrote it

Everything in this book was tested in November 2026. The running example, Nordlys Cabins, is a small booking site that you can run on your own machine, and every chapter adds one layer to it with tests that pass. Every number has a source and a date. When the evidence is thin, I say so. When a vendor says a technique does nothing for its product, I say that too, even if the technique still helps elsewhere. And when I give an opinion, I tell you it is one.

I also used the methods this book teaches on the book itself. Its web edition publishes Markdown versions of every page, an llms.txt, structured data and WebMCP tools, and Chapter 12 reports how it scores in both graders.

## About this edition

This is the second edition of the book. The first edition (version 1.0.0, November 2026) had 20 chapters in five parts and 628 pages. This one follows a shorter, simpler outline: 12 chapters in three parts, with the same six layers, the same running example and the same validation table behind every claim. Most of the work was cutting, not writing. The new parts are a section on rendering for client-rendered apps in Chapter 3, a section on the two ways a shop can let an agent buy in Chapter 11, and Appendix C, which collects pay per crawl and content licensing in one place. The demos repository did not change, and About this book maps its folders to the chapters of this edition.

## Thanks

This book stands on the work of many people I have never met: the members of the W3C and IETF groups and the Model Context Protocol community who write these specifications in the open, the browser and platform teams who ship them early enough for the rest of us to try, and the developers who publish their measurements instead of keeping them to themselves. Thank you to the web developer communities in Oslo and beyond, whose questions shaped this book long before it had a title. And thank you, reader, for caring about how the web works for everyone who uses it, people and agents alike.

Maxim Salnikov
Oslo, November 2026

[^pre-1]: Release history of *Tools, Not Clicks*, https://github.com/webmaxru/webmcp-book (tag v1.0.0 on 15 October 2026, release v2.0.0 on 2 November 2026).
[^pre-2]: *Tools, Not Clicks: Building Agent-Ready Websites with WebMCP*, web edition, https://webmcp.salnikov.no (retrieved 2 November 2026).
[^pre-3]: Cloudflare Radar, "AI Insights", https://radar.cloudflare.com/ai-insights, and OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots (both retrieved November 2026).
[^pre-4]: Cloudflare blog, "Introducing the Agent Readiness score. Check to see if your site is agent-ready", 17 April 2026, https://blog.cloudflare.com/agent-readiness/, and Lighthouse release notes for v13.2.0 (1 May 2026), https://github.com/GoogleChrome/lighthouse/releases (both retrieved November 2026).
[^pre-5]: Scans made for this book on 2 November 2026 (see Chapter 1), and Cloudflare blog, "Introducing Markdown for Agents", 12 February 2026, https://blog.cloudflare.com/markdown-for-agents/ (retrieved November 2026).
