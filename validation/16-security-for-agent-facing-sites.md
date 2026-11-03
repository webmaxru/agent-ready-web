## Chapter 16: Security for agent-facing sites

Retrieved dates are the day the source was read for this chapter (research files R1–R4 and the W6/W6b checks).

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | Chrome: 'The primary new threat facing all agentic browsers is indirect prompt injection'; sources incl. malicious sites, third-party iframes, UGC such as reviews | VERIFIED | https://blog.google/security/architecting-security-for-agentic/ | 2026-11-02 | R4 §1; post dated 8 Dec 2025 |
| 2 | Chrome User Alignment Critic, Agent Origin Sets (read-only vs read-writable), deterministic confirmations (banking, medical, Password Manager sign-in) | VERIFIED | https://blog.google/security/architecting-security-for-agentic/ | 2026-11-02 | R4 §1 |
| 3 | Chrome VRP pays up to $20,000 for breaches of those boundaries | VERIFIED | https://blog.google/security/architecting-security-for-agentic/ | 2026-11-02 | R4 §1 |
| 4 | OpenAI (Dec 2025): prompt injection 'unlikely to ever be fully solved' (quoted via Fortune) | VERIFIED | https://fortune.com/2025/12/23/openai-ai-browser-prompt-injections-cybersecurity-hackers/ | 2026-11-02 | R4 §1; openai.com refused direct fetch, stated in text |
| 5 | OpenAI CISO: 'a frontier, unsolved security problem' at Atlas launch; logged out mode; Watch Mode | VERIFIED | https://simonwillison.net/2025/Oct/22/openai-ciso-on-atlas/ | 2026-11-02 | R4 §1 |
| 6 | Anthropic (24 Nov 2025): ~1% attack success vs adaptive attacker; '1% attack success rate—while a significant improvement—still represents meaningful risk'; classifiers scan all untrusted content | VERIFIED | https://www.anthropic.com/research/prompt-injection-defenses | 2026-11-02 | R4 §1 |
| 7 | Claude in Chrome help centre: <0.08% attack success on internal testing; permissions, blocklists, confirmations, action classifier | VERIFIED | https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely | 2026-11-02 | R4 §1; vendor-internal numbers, text says so |
| 8 | Brave (20 Aug 2025): Comet steered by instructions behind a Reddit spoiler tag, exfiltrated email + OTP; SOP/CORS 'effectively useless' | VERIFIED | https://brave.com/blog/comet-prompt-injection/ | 2026-11-02 | R4 §1 |
| 9 | Brave (21 Oct 2025): 'unseeable' injections, faint light-blue text on yellow in an image | VERIFIED | https://brave.com/blog/unseeable-prompt-injections/ | 2026-11-02 | R4 §1 |
| 10 | UW (Roesner, Kohlbrenner; updated 15 Apr 2026): agent used to circumvent same-origin policy, PoC on ChatGPT Atlas | VERIFIED | https://agent-security.cs.washington.edu/agentic_browsers_sop.html | 2026-11-02 | R4 §1 |
| 11 | 'Agent CSRF' is the author's own label, not a standard term | OPINION | — | 2026-11-02 | Stated as such in text |
| 12 | WebMCP spec security text (PR #334, Oct 2026): risks 'apply broadly to any agent ... regardless of whether a site exposes WebMCP tools'; 'a malicious site can omit or misrepresent those hints' | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/334 | 2026-11-02 | R4 §1, WebMCP FACTS |
| 13 | OWASP Top 10 for LLM Applications 2025: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM05 Improper Output Handling, LLM06 Excessive Agency; LLM01 mitigations (least privilege, human approval, segregate external content, adversarial testing) | VERIFIED | https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | 2026-11-02 | R4 §2 |
| 14 | OWASP Top 10 for Agentic Applications 2026, announced 9 Dec 2025, ASI01–ASI10 names exactly as listed | VERIFIED | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | 2026-11-02 | Rechecked ASI01, ASI04, ASI09, ASI10 wording on the page in pass 3 |
| 15 | Willison 'lethal trifecta' (16 Jun 2025): private data + untrusted content + external communication; 'Guardrails won't protect you' | VERIFIED | https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ | 2026-11-02 | R4 §2 |
| 16 | Meta 'Agents Rule of Two': no more than two of untrusted input / sensitive systems or data / change state or communicate externally (via Oso) | VERIFIED | https://www.osohq.com/learn/agents-rule-of-two-a-practical-approach-to-ai-agent-security | 2026-11-02 | Meta's own post refused fetch; secondary source named in text |
| 17 | Applying Rule of Two per tool is the author's lens | OPINION | — | — | Text frames it as 'I use them as a lens' |
| 18 | OWASP cheat sheet: indirect sources incl. user reviews, web pages, 'hidden text in web pages'; 'Enforce permissions and parameter validation at the tool boundary' | VERIFIED | https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html | 2026-11-02 | R4 §2 |
| 19 | CaMeL (DeepMind/ETH): 77% of AgentDojo tasks with provable security vs 84% undefended | VERIFIED | https://arxiv.org/abs/2503.18813 | 2026-11-02 | R4 §2, FACTS |
| 20 | Chrome WebMCP tool security: untrustedContentHint for UGC; consequentialHint for booking/money; readOnlyHint; budgets 500/150/30 chars and 1.5K output, may change | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/secure-tools | 2026-11-02 | R4 §1; page updated 1 Sep 2026 |
| 21 | Chrome agent security page: 'malicious manifests' and 'contaminated outputs' | VERIFIED | https://developer.chrome.com/docs/agents/security | 2026-11-02 | R4 §1 |
| 22 | MCP tool annotations readOnlyHint, destructiveHint, idempotentHint, openWorldHint, no untrusted-content flag | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | Pass 3 recheck |
| 23 | MCP blog 'Tool Annotations as Risk Vocabulary: What Hints Can and Can't Do' (16 Mar 2026) | VERIFIED | https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ | 2026-11-02 | R3 |
| 24 | WebMCP best practices co-authored by Klepper, Salnikov, Beaufort; 'Recompute on confirmation'; 'Confirmation must recompute the current state and reject stale work.' | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/best-practices | 2026-11-02 | AUTHOR-FACTS.md, WebMCP FACTS |
| 25 | MCP security best practices: scope minimisation; 'Poor scope design increases token compromise impact...'; no token passthrough; 'MCP proxy servers MUST implement per-client consent' | VERIFIED | https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices | 2026-11-02 | R4 §3 |
| 26 | MCP authorization: servers 'MUST validate that access tokens were issued specifically for them as the intended audience'; RFC 8707 resource indicators; 'MUST NOT accept any tokens that were not explicitly issued for the MCP server' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | R3 §2, R4 §3 |
| 27 | MCP elicitation: servers 'MUST use URL mode for interactions involving such sensitive information' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation | 2026-11-02 | R4 §3 |
| 28 | Invariant Labs: tool poisoning, rug pull ('a malicious server can change the tool description after the client has already approved it'), tool shadowing | VERIFIED | https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks | 2026-11-02 | R4 §3 |
| 29 | Streamable HTTP 2026-07-28: Mcp-Name header on tools/call; mismatch → 400 and JSON-RPC -32020 (HeaderMismatch) | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http | 2026-11-02 | Pass 3: rechecked -32020 on the page |
| 30 | Unknown tool → JSON-RPC -32602, message 'Unknown tool: ...' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | Pass 3 recheck (spec example) |
| 31 | Clients 'MUST consider tool annotations to be untrusted unless they come from trusted servers' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | Pass 3 recheck |
| 32 | TS SDK v2 HTTP handler 'validates no Host header, no Origin header, and no token' | VERIFIED | https://ts.sdk.modelcontextprotocol.io/v2/serving/http | 2026-11-02 | R3 (Chapter 8 source) |
| 33 | promptfoo OWASP Agentic red-team preset, plugin ids from owasp:agentic:asi01 | VERIFIED | https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/ | 2026-11-02 | R4 §2 |
| 34 | Neither isitagentready nor Lighthouse Agentic Browsing checks tool authorization, review cleaning or logging | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R1 check lists (both graders) |
| 35 | Listing 16.1 policy.js identical to demo; 16.2, 16.4, 16.5, 16.7–16.11 contiguous excerpts; 16.3 identical to a fresh run of scan-page.mjs | VERIFIED | demos/ (local diff) | 2026-11-02 | Pass 3: 16.1 refreshed after policy.js gained the Chapter 14/12/17 tools |
| 36 | Tests passed with Node 22.23 and 24.22, Playwright 1.64.1, Chromium 156.0.8078.4 | VERIFIED | local run | 2026-11-02 | W6b rerun |

## Demos

- `nordlys-cabins/layers/16-security/` (policy.js, untrusted.js, reviews.js, access.js, gateway.js, audit-log.js, pins.js, pin-tools.mjs, tools.lock.json, index.js)
- `nordlys-cabins/tests/ch16-security.test.js`: `node --test tests/ch16-security.test.js` in `nordlys-cabins/` → 6/6 pass (Node 22.23.2 and 24.22.1, 2 Nov 2026)
- `chapters/16-security-for-agent-facing-sites/` (scan-page.mjs, fixtures/, scan-page.test.js): `node --test scan-page.test.js` → 3/3 pass (Playwright 1.64.1, Chromium 156.0.8078.4)
- Note for the lead: the tests import `@modelcontextprotocol/server` and `@modelcontextprotocol/client` (2.4.0), which are not declared in any package.json of the demos tree; the reruns installed them with `--no-save` in a scratch copy.

## Figures

- figure-16-1 (site as carrier and as victim)
- figure-16-2 (Rule of Two applied to the Nordlys MCP tools)
