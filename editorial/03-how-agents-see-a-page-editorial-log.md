# Chapter 3 editorial log: How agents see a page

Writer W1, 2 November 2026. Method as Chapter 1.

## Pass 1: voice draft
- Structure: three views (with Table 3.1 of what vendors document), how the tree is built (real CDP node), semantic HTML first and ARIA second, forms, the 33 rules, the perception contract, stable layout, team checklist.
- All measurements produced by the new chapter scripts (three-views.mjs, agent-axe.mjs) and the new layer's audit.

## Pass 2: substantive edit
- Comet row labelled as third-party analysis. Atlas quote labelled as a secondary quote of the OpenAI help page.
- Live regions: no claim that agents use them (no source), stated as such.
- Discovered and documented that axe reports aria-hidden-focus as "needs review", which Lighthouse ignores. Added it to the fixture test.
- Discovered that the site CSP blocks axe injection, documented bypassCSP.
- The perception contract passes labelled-controls on the legacy front end only because it has no controls in its HTML. Said so in the text instead of hiding it.
- Removed an invented "80 pixels" example.
- Added "Reading the tree like an agent", "Seeing your own pages" and "Patterns that break perception" for practitioners.

## Pass 3: voice recheck and fidelity
- Signature moves: "In simple words", "Please note:", "Bottomline:", "I bet", one ":)", six spaced em dashes, "Let's look".
- Listings 3.1 to 3.3 byte-identical. Numbers compared with the validation file.
