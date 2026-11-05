## Chapter 10: Security for agent-facing sites

v2.0.0 draft, lead task 257dd4d0, 2026-11-04. Rows carried unchanged from the v1 validation tables named in the last column (status, source and retrieval date as validated in v1). Rows for v1 passages cut from this chapter are kept for traceability. 

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note | v1 row |
|---|---|---|---|---|---|---|
| 1 | Chrome: 'The primary new threat facing all agentic browsers is indirect prompt injection'; sources incl. malicious sites, third-party iframes, UGC such as reviews | VERIFIED | https://blog.google/security/architecting-security-for-agentic/ | 2026-11-02 | R4 §1; post dated 8 Dec 2025 | v1 ch16 #1 |
| 2 | Chrome User Alignment Critic, Agent Origin Sets (read-only vs read-writable), deterministic confirmations (banking, medical, Password Manager sign-in) | VERIFIED | https://blog.google/security/architecting-security-for-agentic/ | 2026-11-02 | R4 §1 | v1 ch16 #2 |
| 3 | Chrome VRP pays up to $20,000 for breaches of those boundaries | VERIFIED | https://blog.google/security/architecting-security-for-agentic/ | 2026-11-02 | R4 §1 | v1 ch16 #3 |
| 4 | OpenAI (Dec 2025): prompt injection 'unlikely to ever be fully solved' (quoted via Fortune) | VERIFIED | https://fortune.com/2025/12/23/openai-ai-browser-prompt-injections-cybersecurity-hackers/ | 2026-11-02 | R4 §1; openai.com refused direct fetch, stated in text | v1 ch16 #4 |
| 5 | OpenAI CISO: 'a frontier, unsolved security problem' at Atlas launch; logged out mode; Watch Mode | VERIFIED | https://simonwillison.net/2025/Oct/22/openai-ciso-on-atlas/ | 2026-11-02 | R4 §1 | v1 ch16 #5 |
| 6 | Anthropic (24 Nov 2025): ~1% attack success vs adaptive attacker; '1% attack success rate—while a significant improvement—still represents meaningful risk'; classifiers scan all untrusted content | VERIFIED | https://www.anthropic.com/research/prompt-injection-defenses | 2026-11-02 | R4 §1 | v1 ch16 #6 |
| 7 | Claude in Chrome help centre: <0.08% attack success on internal testing; permissions, blocklists, confirmations, action classifier | VERIFIED | https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely | 2026-11-02 | R4 §1; vendor-internal numbers, text says so | v1 ch16 #7 |
| 8 | Brave (20 Aug 2025): Comet steered by instructions behind a Reddit spoiler tag, exfiltrated email + OTP; SOP/CORS 'effectively useless' | VERIFIED | https://brave.com/blog/comet-prompt-injection/ | 2026-11-02 | R4 §1 | v1 ch16 #8 |
| 9 | Brave (21 Oct 2025): 'unseeable' injections, faint light-blue text on yellow in an image | VERIFIED | https://brave.com/blog/unseeable-prompt-injections/ | 2026-11-02 | R4 §1 | v1 ch16 #9 |
| 10 | UW (Roesner, Kohlbrenner; updated 15 Apr 2026): agent used to circumvent same-origin policy, PoC on ChatGPT Atlas | VERIFIED | https://agent-security.cs.washington.edu/agentic_browsers_sop.html | 2026-11-02 | R4 §1 | v1 ch16 #10 |
| 11 | 'Agent CSRF' is the author's own label, not a standard term | OPINION | — | 2026-11-02 | Stated as such in text | v1 ch16 #11 |
| 12 | WebMCP spec security text (PR #334, Oct 2026): risks 'apply broadly to any agent ... regardless of whether a site exposes WebMCP tools'; 'a malicious site can omit or misrepresent those hints' | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/334 | 2026-11-02 | R4 §1, WebMCP FACTS | v1 ch16 #12 |
| 13 | OWASP Top 10 for LLM Applications 2025: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM05 Improper Output Handling, LLM06 Excessive Agency; LLM01 mitigations (least privilege, human approval, segregate external content, adversarial testing) | VERIFIED | https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | 2026-11-02 | R4 §2 | v1 ch16 #13 |
| 14 | OWASP Top 10 for Agentic Applications 2026, announced 9 Dec 2025, ASI01–ASI10 names exactly as listed | VERIFIED | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | 2026-11-02 | Rechecked ASI01, ASI04, ASI09, ASI10 wording on the page in pass 3 | v1 ch16 #14 |
| 15 | Willison 'lethal trifecta' (16 Jun 2025): private data + untrusted content + external communication; 'Guardrails won't protect you' | VERIFIED | https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ | 2026-11-02 | R4 §2 | v1 ch16 #15 |
| 16 | Meta 'Agents Rule of Two': no more than two of untrusted input / sensitive systems or data / change state or communicate externally (via Oso) | VERIFIED | https://www.osohq.com/learn/agents-rule-of-two-a-practical-approach-to-ai-agent-security | 2026-11-02 | Meta's own post refused fetch; secondary source named in text | v1 ch16 #16 |
| 17 | Applying Rule of Two per tool is the author's lens | OPINION | — | — | Text frames it as 'I use them as a lens' | v1 ch16 #17 |
| 18 | OWASP cheat sheet: indirect sources incl. user reviews, web pages, 'hidden text in web pages'; 'Enforce permissions and parameter validation at the tool boundary' | VERIFIED | https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html | 2026-11-02 | R4 §2 | v1 ch16 #18 |
| 19 | CaMeL (DeepMind/ETH): 77% of AgentDojo tasks with provable security vs 84% undefended | VERIFIED | https://arxiv.org/abs/2503.18813 | 2026-11-02 | R4 §2, FACTS | v1 ch16 #19 |
| 20 | Chrome WebMCP tool security: untrustedContentHint for UGC; consequentialHint for booking/money; readOnlyHint; budgets 500/150/30 chars and 1.5K output, may change | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/secure-tools | 2026-11-02 | R4 §1; page updated 1 Sep 2026 | v1 ch16 #20 |
| 21 | Chrome agent security page: 'malicious manifests' and 'contaminated outputs' | VERIFIED | https://developer.chrome.com/docs/agents/security | 2026-11-02 | R4 §1 | v1 ch16 #21 |
| 22 | MCP tool annotations readOnlyHint, destructiveHint, idempotentHint, openWorldHint, no untrusted-content flag | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | Pass 3 recheck | v1 ch16 #22 |
| 23 | MCP blog 'Tool Annotations as Risk Vocabulary: What Hints Can and Can't Do' (16 Mar 2026) | VERIFIED | https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ | 2026-11-02 | R3 | v1 ch16 #23 |
| 24 | WebMCP best practices co-authored by Klepper, Salnikov, Beaufort; 'Recompute on confirmation'; 'Confirmation must recompute the current state and reject stale work.' | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/best-practices | 2026-11-02 | AUTHOR-FACTS.md, WebMCP FACTS | v1 ch16 #24 |
| 25 | MCP security best practices: scope minimisation; 'Poor scope design increases token compromise impact...'; no token passthrough; 'MCP proxy servers MUST implement per-client consent' | VERIFIED | https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices | 2026-11-02 | R4 §3 | v1 ch16 #25 |
| 26 | MCP authorization: servers 'MUST validate that access tokens were issued specifically for them as the intended audience'; RFC 8707 resource indicators; 'MUST NOT accept any tokens that were not explicitly issued for the MCP server' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | R3 §2, R4 §3 | v1 ch16 #26 |
| 27 | MCP elicitation: servers 'MUST use URL mode for interactions involving such sensitive information' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation | 2026-11-02 | R4 §3 | v1 ch16 #27 |
| 28 | Invariant Labs: tool poisoning, rug pull ('a malicious server can change the tool description after the client has already approved it'), tool shadowing | VERIFIED | https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks | 2026-11-02 | R4 §3 | v1 ch16 #28 |
| 29 | Streamable HTTP 2026-07-28: Mcp-Name header on tools/call; mismatch → 400 and JSON-RPC -32020 (HeaderMismatch) | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http | 2026-11-02 | Pass 3: rechecked -32020 on the page | v1 ch16 #29 |
| 30 | Unknown tool → JSON-RPC -32602, message 'Unknown tool: ...' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | Pass 3 recheck (spec example) | v1 ch16 #30 |
| 31 | Clients 'MUST consider tool annotations to be untrusted unless they come from trusted servers' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | Pass 3 recheck | v1 ch16 #31 |
| 32 | TS SDK v2 HTTP handler 'validates no Host header, no Origin header, and no token' | VERIFIED | https://ts.sdk.modelcontextprotocol.io/v2/serving/http | 2026-11-02 | R3 (Chapter 8 source) | v1 ch16 #32 |
| 33 | promptfoo OWASP Agentic red-team preset, plugin ids from owasp:agentic:asi01 | VERIFIED | https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/ | 2026-11-02 | R4 §2 | v1 ch16 #33 |
| 34 | Neither isitagentready nor Lighthouse Agentic Browsing checks tool authorization, review cleaning or logging | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R1 check lists (both graders) | v1 ch16 #34 |
| 35 | Listing 16.1 policy.js identical to demo; 16.2, 16.4, 16.5, 16.7–16.11 contiguous excerpts; 16.3 identical to a fresh run of scan-page.mjs | VERIFIED | demos/ (local diff) | 2026-11-02 | Pass 3: 16.1 refreshed after policy.js gained the Chapter 14/12/17 tools | v1 ch16 #35 |
| 36 | Tests passed with Node 22.23 and 24.22, Playwright 1.64.1, Chromium 156.0.8078.4 | VERIFIED | local run | 2026-11-02 | W6b rerun | v1 ch16 #36 |

### Figures

- Figure 10.1 (v1 Figure 16.1)
- Figure 10.2 (v1 Figure 16.2)

### Listings

- Listing 10.1 (v1 Listing 16.1)
- Listing 10.2 (v1 Listing 16.2)
- Listing 10.3 (v1 Listing 16.3)
- Listing 10.4 (v1 Listing 16.4)
- Listing 10.5 (v1 Listing 16.5)
- Listing 10.6 (v1 Listing 16.6)
- Listing 10.7 (v1 Listing 16.7)
- Listing 10.8 (v1 Listing 16.9)
- Listing 10.9 (v1 Listing 16.11)
- Listing 10.10 (v1 Listing 16.12)
