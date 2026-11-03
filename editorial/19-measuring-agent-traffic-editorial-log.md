# Editorial log: Chapter 19, Measuring agent traffic and outcomes

Writer W7, 2 November 2026.

## Pass 1: voice draft
- Planned around three questions (who visits, what they get, what comes of it) and the evidence ladder, so non-coders get the argument before any code.
- Built the demos first (standalone classifier, layer 19), then wrote listings straight from the files.
- Voice: first person for judgments ("in my experience", "I recommend a JSON log"), tutorial "let's", "Please note", "In simple words", parentheses for asides, no semicolons.

## Pass 2: substantive edit (professional-writing-editor)
- Structure: added "What they get: checking the policy against the log" and "Counting tool calls, not only pages" so the chapter covers all three questions, not only traffic counts.
- Role readability: Hands-on callouts open both code sections and name where to pick up again. Added "Reading the dashboard as a team" (one paragraph per role) and a KPI table by role.
- Fidelity fixes: the spoofed-GPTBot share was misstated ("one in fifteen") and corrected to 76 requests (almost 4%). Vercel categories now quote the real identifiers (`chatgpt-user`, `chatgpt-operator`, `ai_assistant`). The booking-event sentence no longer claims MCP tools emit it. The browser-agent sentence is hedged and cited. Footnote titles corrected against the pages (two Cloudflare blog titles were swapped, Google page titles updated).
- Slop check: no banned words, no "not X, but Y", 7 em dashes in 7.9k words.

## Pass 3: voice and fidelity recheck
- Every number checked against the validation table (Radar values with the 2 November 2026 date, the 2025 ratios with their month, range-file dates and prefix counts from the files).
- Every listing compared byte for byte with the demo file. Listing 19.3 and the jq output are real output from the synthetic log, and labelled synthetic.
- utm_source=chatgpt.com kept as an observed convention, explicitly not documented by OpenAI.
