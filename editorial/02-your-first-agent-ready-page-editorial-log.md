# Chapter 2 editorial log: Your first agent-ready page

Writer W1, 2 November 2026. Method as Chapter 1 (Book 2 voice method, no detectors or humanizers).

## Pass 1: voice draft
- Built around the measured loop: baseline with three instruments, three fixes, re-measure. All outputs in the chapter are real runs from 2 November 2026 (port numbers changed to 3000 for the reader).
- "Hands-on" notes before every code-heavy section, with versions named once.

## Pass 2: substantive edit
- Corrected the legacy analysis after a check: the read-only date inputs do have a name in the tree (placeholder fallback), so the text now says why the walk still fails (getByLabel ignores placeholders, and fill fails with "element is not editable", verified).
- Corrected isitagentready response keys to the real camelCase (`levelName`, `nextLevel`) and replaced a description with a real excerpt of the stored scan.
- Added the declarative API status (moved to an explainer in October 2026, still in Chrome's trial) after reading the explainer and Chrome's doc today. Replaced an unverified chrome://flags anchor with the flag name from FACTS.md.
- Browser support sentence rewritten to what chromestatus states (no browser by default, origin trial to 162, flag).
- Removed an invented anecdote ("I have watched it happen").
- Added the legacy plus layer 02 measurement (Level 1, walk 0/13) as the argument for never using one grader alone.
- Added "Five fixes that look right and are not" and "A first pass on your own site" for role readability.

## Pass 3: voice recheck and fidelity
- Signature moves: "Let's have a look", "In simple words", "Please note:", "Of course", "Bottomline:", "I bet", one ":)", six spaced em dashes.
- Listings 2.1 to 2.5 checked byte-identical against the demo files. Every number compared with the validation file.
