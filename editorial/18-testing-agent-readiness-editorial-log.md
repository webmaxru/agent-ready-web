# Editorial log: Chapter 18, Testing agent-readiness

Writer: W6b (W6 built most of the demo before its process ended). All passes on 2 November 2026. Sources and statuses: shared/validation/18-testing-agent-readiness.md.

## Pass 1: voice draft
- Planned from OUTLINE.md (Chapter 18 scope), R4 §3, R1 §1, §4 and §5, and the demo W6 left in `chapters/18-testing-agent-readiness/`. Ran every step of the pipeline locally before writing (unit tests, readiness, structured data, robots/llms, Lighthouse median of 3 on four pages, Playwright agent paths), then wrote around the real output.
- Added to the demo: `evals/injection-eval.mjs` (Chapter 16's promised injection eval, reusing Chapter 10's harness and Chapter 16's `untrusted.js`), its unit tests, an `eval:injection` script, README rows and the results of a 120-episode run with four real models.
- Extra real outputs captured for the text: a regression run against `--upto=6`, the Lighthouse details behind the `/cabins` 0.5 warning, and MCP Inspector 2.13.0 `--cli` calls (npx cache removed afterwards).
- Voice: first-person practice and opinions ("The practical rule I follow", "my favourite thing in this chapter"), "Let's have a look", "Please note", "In simple words", "I bet", "to be precise", "of course". No semicolons, no em dashes in prose.

## Pass 2: professional-writing-editor
- Structure: why tests (decay), two kinds with a table, what breaks and who breaks it, deterministic checks, agent paths, exploration tools, evals, flakiness and budgets, the pipeline, ownership, graders, summary. Each code-heavy section opens with a Hands-on callout naming where non-coders pick up.
- Fidelity fixes during the pass: the llms.txt paragraph now says what Lighthouse's audit actually checks (read in the 13.6.0 source) instead of folding the proposal's summary into it. The DevTools-panel claim is attributed to Chrome's documentation, because only the CLI was run. The chrome-devtools-mcp description was cut back to what the toolkit post says. "Every chapter since" became "the layer chapters since". The eval paragraph no longer claims that the live Nordlys enforces confirmation on cancellations, it points to Chapters 16 and 17 instead. Cost wording replaced with measured tokens and seconds.
- Split one over-long sentence, removed an invented detail ("winter high season") and an unsupported aside about cron timing.
- Role-readability: a table of what breaks and who breaks it, a role ownership table, the product-manager framing of the eval numbers.

## Pass 3: voice recheck and fidelity check
- Every number checked against the runs: level 4 and the failing checks, 11/11 robots/llms rows, 18 llms.txt links, Lighthouse 1 / 0.92 / 1 / 1, 136 s for twelve Lighthouse runs, 4/4 Playwright in 1.6 s, the eval table, 7 of 10 lookups before cancelling, the two quoted model answers (string-matched in the results file), the token and time medians.
- Listings: 18.1, 18.3, 18.4, 18.6, 18.7, 18.9, 18.11, 18.12 and 18.13 are contiguous excerpts of the demo files (checked by script). 18.2, 18.5, 18.8 and 18.10 are real output from 2 November 2026.
- Figures 18.1 to 18.3 rendered and inspected as PNG. Figure 18.3 uses the real eval numbers.
- Words: about 8,500 (code and output about 12%).
