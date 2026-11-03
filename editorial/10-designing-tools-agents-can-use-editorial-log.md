# Editorial log: Chapter 10, Designing tools agents can actually use

Writer: W4. Date: 2 November 2026.

## Pass 1: voice draft
- Built the layer (find_booking, lint audit) and the eval harness first, ran a smoke test with two real models, then a full run (440 episodes), and drafted against the results. Every number in the chapter comes from a results file.
- Voice: the opening is a real failure from the smoke run ("there's no cabin called Fjellro"). First person for the things I got wrong (two too-strict checks, the hint that made results worse). Signature phrases: "Let's start", "Let's have a look", "In simple words", "Please note", "Bottomline", "Personally for me".

## Pass 2: professional-writing-editor
- Fidelity: removed "the models mostly concluded the cabin doesn't exist" after counting (5 of 40); replaced with the full breakdown. Rewrote the date-format paragraph after the data showed the format did not change the December mistake (4/5 with both sets). Rewrote the OpenAI name-limit sentence after testing both APIs directly (128, no dots), and updated lint.js to match.
- Removed a claim about MCP list-change notifications (unclear after the stateless revision), kept ttlMs/cacheScope from the changelog.
- Honesty on iteration: the description-only fix looked like 4/5 and then 1/5. The chapter reports both and says why (sample size). Final table uses one consistent version of the "after" set (results/2026-11-02-after-final) against the main-run "before" set, documented in results/README.md.
- Kept the remaining failures in the text (acceptTerms set without asking once, 12/03 read as December twice), because they carry the argument for server-side and human commit.
- Slop check: no banned words, no semicolons in prose, 10 em dashes in ~9,100 words, no ":)".
- Role-readability: Hands-on callout before lint and harness, pointing non-coders to "What the eval showed". Roles section added.

## Pass 3: voice + fidelity
- Every number checked against the results JSON with a script (table 10.1, per-task totals, counts quoted in text). Listings byte-checked against the demo files (8 listings).
- Footnote titles checked against the live pages (MCP blog post title, Copilot Studio and AgentCore titles corrected).
