# Editorial log: Chapter 7, APIs agents can use

Writer W3. 2026-11-02.

## Pass 1: voice draft
- Drafted from the plan: decision first (when a plain API is enough, what it costs), then the Nordlys API, description, errors, retries, cancellation, pagination and limits, Arazzo, catalog, versions and access, graders, tests, checklist, summary.
- Every exchange in the text is real output from the demo (in-process `app.request` and one `curl` session against `npm start -- --upto=7`).

## Pass 2: substantive edit (professional-writing-editor)
- Fidelity: removed a sentence that claimed results from "my tests with tool descriptions" (no such test exists); replaced with a reasoned argument and a pointer to Chapter 10.
- Fidelity: the text said the tests validate the OpenAPI file with @scalar/openapi-parser, but no test did. Added the test (skips when the dev dependency is missing) and described it exactly. Corrected "the Chapter 7 tests check that earlier Link values survive" to the Chapter 11 test that really does it.
- Demo fix found while writing: the Arazzo workflow hard-coded `acceptTerms: true`. Changed to a required workflow input with const true, and the chapter now uses the mistake as an example.
- Role readability: added "What an API costs you" for PMs, Hands-on callouts on every section with listings (each names where non-coders pick up again), a checklist table at the end.
- Hedging: OpenAI retirement date marked as read from a search result; drafts (Idempotency-Key, RateLimit) carry Still in flux callouts; 3.1-vs-3.2 stated as judgment.

## Pass 3: voice recheck and fidelity
- No semicolons in prose, no banned phrases, absolute dates only. Few "not X, but Y" contrasts.
- Every number and name checked against shared/validation/07-apis-agents-can-use.md. Listings 7.1-7.6 diffed against the demo files (byte-identical).
