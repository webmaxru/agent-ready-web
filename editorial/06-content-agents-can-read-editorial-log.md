# Editorial log: Chapter 6, Content agents can read

Writer: W2. All passes on 2 November 2026. Sources and statuses: shared/validation/06-content-agents-can-read.md.

## Pass 1: voice draft
- Planned from OUTLINE.md (Ch6 scope), R2 §4, R1 §1 and §3 (Radar content types, adoption, isitagentready checks). Built the layer and tests first, measured tokens with gpt-tokenizer 4.1.0, ran real Lighthouse 13.6.0 (agentic category) before and after the layer.
- Re-checked: Lighthouse llms-txt source in the 13.6.0 package, isitagentready llms-full.txt pass criteria, status of the Google, OpenAI platform and OpenAI developers llms.txt URLs, Checkly and Feedfetcher pages.

## Pass 2: professional-writing-editor (structure, fidelity, slop, role-readability)
- Structure: evidence first (why HTML is expensive), then options (Table 6.1), then rules, then the hands-on build. Non-coders get "How agents find the Markdown" and the checklists without code.
- Fidelity: an unsupported "most Markdown-capable domains are on platforms" sentence rewritten as my reading; "agent frameworks cut pages off" softened; a Chapter 2 back-reference removed; real Lighthouse result reported as "category 100 both times" with the N/A explanation instead of implying a score jump; Listing 6.3 labelled with the PUBLIC_ORIGIN note.
- Code changes found while writing: home front matter title fallback; HEAD behaviour verified for .md and pages; legacy variant checked (Markdown works, the Chapter 5 price audit fails on legacy because legacy renders prices client-side, which is correct).
- Tables renumbered by order of appearance (6.1 approaches, 6.2 agents, 6.3 edge vs data, 6.4 tokens, 6.5 graders). Footnotes renumbered by first citation.

## Pass 3: voice and fidelity recheck
- Code listings 6.1, 6.2, 6.4, 6.6 are exact substrings of the demo files. Listings 6.3 and 6.5 are real output. The three Lighthouse lines are copied from the Lighthouse source.
- Lint: no semicolons in prose (the only ones are inside inline code such as `;q=0.9`), 0 placeholders, 0 em dashes, footnotes ch06-1..22 defined, used, in order, 3 figures exist, one H1.
- Honesty notes kept: Markdown is <0.1% of AI bot traffic, browsing agents gain nothing from it, llms.txt has little measured traffic and Google Search ignores it, the level jump comes from one header, Chapter 4 claim about Chapters 18/20 softened to "Chapter 18 shows how to run the real scanner from CI".
