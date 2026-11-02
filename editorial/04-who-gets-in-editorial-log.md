# Editorial log: Chapter 4, Who gets in: robots.txt, AI crawlers and content signals

Writer: W2. All passes on 2 November 2026. Sources and statuses: shared/validation/04-who-gets-in.md.

## Pass 1: voice draft
- Planned from OUTLINE.md (Ch4 scope), R2 §5, R1 §1–§3, R4 §4. Built and tested the demo layer first (layers/04-crawler-controls, 7 tests), then wrote the chapter around the real files and the real generated robots.txt.
- Voice: first person for judgment ("Honestly, I don't blame anyone", "I think it is fair to say that out loud"), tutorial "let's" in the measurement and code sections, "you" for the reader, rhetorical questions, parentheses for asides, signature phrases ("In simple words", "Let's have a look", "of course").
- Re-checked primary sources the research did not cover in full: aipref attach-05 and vocab-08 text, draft-romm (expired), draft-kelley title and author, Amazon, Mistral and Perplexity crawler pages, Lighthouse 13.6.0 robots-txt audit safelist, Google sitemap and robots pages, Vercel and Cloudflare AI Crawl Control docs, ai.robots.txt repo.

## Pass 2: professional-writing-editor (structure, fidelity, slop, role-readability)
- Structure: purpose-first framework (four decisions) moved before any file syntax, so PMs and legal can stop after "Four decisions before any file"; Hands-on callout tells non-coders where to pick up ("What the graders see").
- Removed unverifiable experiential claims ("I have seen both versions many times", "In my experience", "one of the most common findings") and replaced them with neutral statements or documented pass rules.
- Corrected vendor rows after re-reading pages: Mistral (MistralAI-User "governs which sites these user requests can be made to", so Anthropic is the clearest but not the only exception), Amazonbot purpose wording and its 30-day robots cache.
- Replaced a "not X, but Y" contrast in the Nordlys decision, fixed a misquote of Google's lastmod sentence, made the Node.js version in the test claim match what was run (22.23.2).
- Role check: Table 4.1 (who owns what), Table 4.4 (Google controls) and the per-role checklist give designers-free roles (PM, legal, SEO, security, analytics) a complete path without code.

## Pass 3: voice and fidelity recheck
- Every number, token, draft name and date checked against the validation table (53 rows). Listings 4.1, 4.2, 4.4, 4.5 and the 4.6 excerpt diffed byte-identical with the demo files. Listing 4.3 is the real output of the demo (buildApp with upto 4, PUBLIC_ORIGIN https://nordlys.example).
- Lint: 0 semicolons in prose, 0 placeholders, 0 raw HTML, footnotes ch04-1..37 all defined and used, 3 figures exist, one H1.
- Honesty notes kept in text: Content Signals is not a standard and compliance is unmeasured, aipref is in flux, Meta's page could not be read, the level jump comes from one vendor-defined line, the real scanner cannot reach localhost.
