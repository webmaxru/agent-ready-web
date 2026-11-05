## Chapter 3: How agents see a page

v2 writer (Part 1), 2026-11-04. Rows carried from the first edition with status, source and retrieval date unchanged. The last column names the v1 row.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note | v1 row |
|---|---|---|---|---|---|---|
| 1 | web.dev: three views (screenshots, raw HTML, a11y tree), combined; screenshot quote 'slow and expensive' | VERIFIED | https://web.dev/articles/ai-agent-site-ux | 2026-11-02 | R2 §1 rows 18-19, §1 summary | v1 ch3 #1 |
| 2 | Anthropic browser tool: a11y tree with [ref_2] refs + screenshots; filter interactive; reference quote; hidden-text quote | VERIFIED | https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool | 2026-11-02 | R2 §1 rows 7-10, verbatim | v1 ch3 #2 |
| 3 | Comet: Accessibility.getFullAXTree YAML + Markdown (third-party) | VERIFIED | https://labs.zenity.io/post/perplexity-comet-a-reversing-story | 2026-11-02 | labelled as third-party in text | v1 ch3 #3 |
| 4 | Playwright MCP: accessibility snapshots, vision opt-in | VERIFIED | https://github.com/microsoft/playwright-mcp | 2026-11-02 | README read today: 'not pixel-based input', --caps=vision | v1 ch3 #4 |
| 5 | ChatGPT Atlas 'uses ARIA tags' quote | VERIFIED | https://simonwillison.net/2025/Oct/21/introducing-chatgpt-atlas/ | 2026-11-02 | secondary quote of OpenAI help page, flagged in footnote | v1 ch3 #5 |
| 6 | Roselli post title | VERIFIED | https://adrianroselli.com/2025/10/openai-aria-and-seo-making-the-web-worse.html | 2026-11-02 | R2 §1 row 14 | v1 ch3 #6 |
| 7 | Edge Browse with Copilot captures screenshots | VERIFIED | https://support.microsoft.com/en-us/edge/copilot/browse-with-copilot | 2026-11-02 | R2 §1 row 17 | v1 ch3 #7 |
| 8 | Computer-use models: screenshot then action loop | VERIFIED | https://platform.openai.com/docs/guides/tools-computer-use ; https://blog.google/technology/google-deepmind/gemini-computer-use-model/ | 2026-11-02 | R2 §1 row 15 and summary | v1 ch3 #8 |
| 9 | Chrome: a11y tree 'primary data model' | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 |  | v1 ch3 #9 |
| 10 | Three-views numbers (Table 3.2) | VERIFIED | three-views.mjs local runs, legacy and clean upto 2 | 2026-11-02 | Chromium 156.0.8078.4, Playwright 1.64.1 | v1 ch3 #10 |
| 11 | Clean tree 23 vs snapshot 15: date input parts (Show date picker, Month/Day/Year spinbuttons) | VERIFIED | private/analytics/w1-measurements-2026-11-02/three-views-clean/2-ax-tree.json | 2026-11-02 |  | v1 ch3 #11 |
| 12 | Chrome DevTools full accessibility tree toggle quote | VERIFIED | https://developer.chrome.com/blog/full-accessibility-tree | 2026-11-02 | read today | v1 ch3 #12 |
| 13 | Playwright ariaSnapshot / toMatchAriaSnapshot, partial matching | VERIFIED | https://playwright.dev/docs/aria-snapshots | 2026-11-02 | read today | v1 ch3 #13 |
| 14 | toMatchAriaSnapshot example for availability region | OPINION | illustrative snippet, matches the real snapshot captured locally | 2026-11-02 | not a demo file, labelled as example | v1 ch3 #14 |
| 15 | MDN: name, description, role, state | VERIFIED | https://developer.mozilla.org/en-US/docs/Glossary/Accessibility_tree | 2026-11-02 | R2 §2 row 10 | v1 ch3 #15 |
| 16 | Blink derives tree, layout wrappers ignored | VERIFIED | https://developer.chrome.com/blog/full-accessibility-tree | 2026-11-02 | R2 §2 row 9 | v1 ch3 #16 |
| 17 | HTML-AAM WD 26 Oct 2026, accname 1.2 WD 21 Oct 2026 | VERIFIED | https://www.w3.org/TR/html-aam-1.0/ ; https://www.w3.org/TR/accname-1.2/ | 2026-11-02 | R2 §2 rows 6-7 (W3C API) | v1 ch3 #17 |
| 18 | Rendered booking error HTML and CDP node for email field | VERIFIED | local run, POST /book/fjellro and Accessibility.getPartialAXTree | 2026-11-02 | output shortened, stated in text | v1 ch3 #18 |
| 19 | Legacy snapshot: textboxes named from placeholder, '− 2 + Check' text | VERIFIED | local Playwright ariaSnapshot | 2026-11-02 |  | v1 ch3 #19 |
| 20 | WAI-ARIA 1.2 Rec 6 Jun 2023, 1.3 WD 4 Jun 2026 | VERIFIED | https://www.w3.org/TR/wai-aria-1.2/ ; https://www.w3.org/TR/wai-aria-1.3/ | 2026-11-02 | R2 §2 rows 4-5 | v1 ch3 #20 |
| 21 | Nordlys uses aria-label Footer nav, aria-current breadcrumb, role=status availability result | VERIFIED | nordlys-cabins/src/views/layout.js, pages.js | 2026-11-02 |  | v1 ch3 #21 |
| 22 | No vendor doc says agents watch live regions | OPINION | R2 §2 summary (UNVERIFIED either way) | 2026-11-02 | phrased as 'I could not find' | v1 ch3 #22 |
| 23 | First rule of ARIA quote | VERIFIED | https://www.w3.org/TR/using-aria/ | 2026-11-02 | read today | v1 ch3 #23 |
| 24 | ARIA in HTML: avoid redundant roles | VERIFIED | https://w3c.github.io/html-aria/ | 2026-11-02 | R2 §2 row 12 | v1 ch3 #24 |
| 25 | autocomplete tokens in WHATWG HTML | VERIFIED | https://html.spec.whatwg.org/multipage/form-control-infrastructure.html | 2026-11-02 | R2 §2 row 13 | v1 ch3 #25 |
| 26 | button command/commandfor, dialog closedby | VERIFIED | MDN button and dialog pages | 2026-11-02 | R2 §2 rows 14-15 | v1 ch3 #26 |
| 27 | 33 rules list (Listing 3.2) from Lighthouse 13.6.0 | VERIFIED | lighthouse@13.6.0 npm package, core/audits/agentic/agent-accessibility-tree.js (13.6.0) | 2026-11-02 | copied by script, 33 entries | v1 ch3 #27 |
| 28 | Lighthouse docs group checks: names and labels, tree integrity, visibility | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R2 §2 row 3 | v1 ch3 #28 |
| 29 | Not in subset: color-contrast, heading-order, landmarks, image-alt, html-has-lang | VERIFIED | Lighthouse TARGET_RULES | 2026-11-02 | R2 §2 row 2 | v1 ch3 #29 |
| 30 | Fixture results: 10 agent-rule violations; aria-hidden-focus needs review; --all adds color-contrast, html-has-lang, image-alt, region | VERIFIED | agent-axe.mjs local runs, axe-core 4.14.0 | 2026-11-02 | tests/ch03-perception.spec.js | v1 ch3 #30 |
| 31 | axe 'incomplete' quote | VERIFIED | https://github.com/dequelabs/axe-core/blob/develop/doc/API.md | 2026-11-02 | read today | v1 ch3 #31 |
| 32 | Lighthouse counts only violations | VERIFIED | agent-accessibility-tree.js: filters artifacts.Accessibility.violations | 2026-11-02 | source read | v1 ch3 #32 |
| 33 | Both front ends: 0 violations of 33 rules on six pages; full rules: clean 0, legacy landmark-one-main, page-has-heading-one, region | VERIFIED | agent-axe.mjs local runs | 2026-11-02 |  | v1 ch3 #33 |
| 34 | Site CSP requires bypassCSP for axe injection | VERIFIED | local run error 'violates the following Content Security Policy directive' | 2026-11-02 |  | v1 ch3 #34 |
| 35 | Perception contract results: clean all pass 13 pages; legacy 12 pages, one-main 12/12, one-h1 8/12, no-click-divs 12/12 | VERIFIED | GET /__audit on local servers upto=3 | 2026-11-02 |  | v1 ch3 #35 |
| 36 | Legacy has no booking page (redirect), only overlay | VERIFIED | local run: /book returns non-200 in-app on legacy | 2026-11-02 |  | v1 ch3 #36 |
| 37 | CLS 0.116 on legacy (Chapter 2) | VERIFIED | private/analytics/w1-measurements-2026-11-02/lighthouse/legacy0-fjellro.json | 2026-11-02 |  | v1 ch3 #37 |
| 38 | web.dev ghost elements, overlays, target size | VERIFIED | https://web.dev/articles/ai-agent-site-ux | 2026-11-02 | R2 §2 row 18 | v1 ch3 #38 |
| 39 | DevTools command menu 'Disable JavaScript' | VERIFIED | https://developer.chrome.com/docs/devtools/javascript/disable | 2026-11-02 | long-standing DevTools feature | v1 ch3 #39 |
| 40 | Legacy widget markup (div controls, read-only inputs with placeholders, no form) | VERIFIED | DOM captured with Playwright from nordlys-cabins legacy variant | 2026-11-02 | public/js/legacy.js, src/views/layout.js | v1 ch2 #1 |
| 41 | Legacy content injected after 400 ms | VERIFIED | nordlys-cabins/src/config.js legacyDelayMs default 400 | 2026-11-02 |  | v1 ch2 #2 |
| 42 | Clean availability form is a GET form with action on /cabins/fjellro, sent complete in the server HTML (used in "Rendering for client-rendered apps") | VERIFIED | v1 ch2 "The fix, part 1: semantic HTML" markup block, captured from nordlys-cabins clean front end | 2026-11-02 | server output reformatted for print in v1 | v1 ch2 (markup block, no own row) |
| 43 | SSR, hydration and progressive-enhancement guidance in "Rendering for client-rendered apps" | EDITORIAL | none (general engineering explanation, no numbers or vendor claims) | 2026-11-04 | numbers in the section reuse v1 ch3 #10, v1 ch2 #2, v1 ch3 #37 | none |
