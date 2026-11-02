## Chapter 14: Agents acting for users: OAuth and delegated access

Retrieved dates are the day the source was read for this chapter.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | MCP server is an OAuth 2.1 resource server ('A protected MCP server acts as an OAuth 2.1 resource server') | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Roles |
| 2 | Authorization OPTIONAL; STDIO 'SHOULD NOT follow this specification' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Protocol Requirements |
| 3 | AS 'may be hosted with the resource server or a separate entity' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Roles |
| 4 | MCP cites OAuth 2.1 draft-13 and CIMD draft-00 | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Standards Compliance |
| 5 | OAuth 2.1 current draft-ietf-oauth-v2-1-17 (last updated 2026-10-30) | VERIFIED | https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/ | 2026-11-02 | datatracker; R3 says 31 Oct, text says 'October 2026' |
| 6 | 401 example with resource_metadata and scope; servers SHOULD include scope; clients MUST treat challenge scopes as authoritative | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Scope Selection Strategy |
| 7 | 'MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC9728)'; clients MUST use it | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Overview |
| 8 | RFC 9728 published April 2025; path insertion example /.well-known/oauth-protected-resource/resource1; §3.3 resource must match URL used for request | VERIFIED | https://www.rfc-editor.org/rfc/rfc9728 | 2026-11-02 | RFC text |
| 9 | MCP clients: resource_metadata from WWW-Authenticate first, then path-inserted, then root | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery | 2026-11-02 | Protected Resource Metadata Discovery Requirements |
| 10 | Clients MUST support RFC 8414 and OIDC Discovery; order for issuer without path; issuer must match | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery | 2026-11-02 | Authorization Server Metadata Discovery |
| 11 | If code_challenge_methods_supported absent clients MUST refuse; S256 MUST | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations | 2026-11-02 | Authorization Code Protection |
| 12 | OpenAI: servers unsupported without S256; hosts use CIMD, DCR, predefined clients, PKCE; RFC 9207 'authorization server mix-up attacks' | VERIFIED | https://developers.openai.com/plugins/build/auth.md | 2026-11-02 | read by W5 |
| 13 | Clients MUST include resource parameter in authorization and token requests | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations | 2026-11-02 | Token Audience Binding |
| 14 | AS SHOULD include iss; advertise authorization_response_iss_parameter_supported | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Authorization Response Validation |
| 15 | Three registration mechanisms with priority order; CIMD 'most common'; 'Dynamic Client Registration is deprecated' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration | 2026-11-02 | read by W5 |
| 16 | CIMD example metadata document; client_id_metadata_document_supported; CIMD client IDs portable | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration | 2026-11-02 | verbatim JSON |
| 17 | CIMD draft-ietf-oauth-client-id-metadata-document-02, 6 Jul 2026 | VERIFIED | https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/ | 2026-11-02 | datatracker |
| 18 | Claude: 'Use Claude's published identity (Recommended)', 'Register automatically', 'Use your own OAuth client'; 'Sign in now', 'Sign in when needed', 'No sign in' | VERIFIED | https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp | 2026-11-02 | read by W5 |
| 19 | CIMD security: SSRF; localhost impersonation; MUST display redirect hostname | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations | 2026-11-02 | verbatim |
| 20 | Audience validation MUST; invalid/expired → 401; MUST NOT pass through tokens | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization ; .../security-considerations | 2026-11-02 | verbatim |
| 21 | Least privilege; scopes_supported minimal; step-up; 403 insufficient_scope format; retry limits; scopes determined dynamically | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization | 2026-11-02 | Scope Challenge Handling, Step-Up |
| 22 | Mcp-Method/Mcp-Name headers REQUIRED; intermediaries route without parsing body; servers MUST reject mismatches (-32020 HeaderMismatch) | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http | 2026-11-02 | Standard Request Headers, Server Validation |
| 23 | AS MUST validate exact redirect URIs (open redirection) | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations | 2026-11-02 | Open Redirection |
| 24 | AS MUST rotate refresh tokens for public clients; SHOULD issue short-lived access tokens | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations | 2026-11-02 | Token Theft |
| 25 | RFC 8252 loopback redirect, port may vary (§7.3), Oct 2017 | VERIFIED | https://www.rfc-editor.org/rfc/rfc8252 | 2026-11-02 | RFC header |
| 26 | RFC 8414 Jun 2018; RFC 8707 Feb 2020; RFC 9207 Mar 2022; RFC 9068 Oct 2021; RFC 7009 Aug 2013; RFC 8693 Jan 2020; RFC 9449 Sep 2023 | VERIFIED | https://www.rfc-editor.org/rfc/ | 2026-11-02 | RFC headers fetched |
| 27 | @cloudflare/workers-oauth-provider 1.2.4 | VERIFIED | https://www.npmjs.com/package/@cloudflare/workers-oauth-provider | 2026-11-02 | npm view, modified 2026-10-22 |
| 28 | 'Cloudflare Access now fully supports this OAuth flow' | VERIFIED | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | R3 2.32 |
| 29 | EMA stable 18 Jun 2026; quotes on IdP as decision-maker and ID-JAG; adopters Okta (XAA), Claude/Claude Code/Cowork, VS Code; servers Asana, Atlassian, Canva, Figma, Granola, Linear, Supabase | VERIFIED | https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/ | 2026-11-02 | read by W5 |
| 30 | ID-JAG draft-ietf-oauth-identity-assertion-authz-grant-06 (Oct 2026) | VERIFIED | https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-assertion-authz-grant/ | 2026-11-02 | datatracker last updated 2026-10-30 |
| 31 | MCP roadmap: finalize DPoP; human-presence under discussion | VERIFIED (via R3) | https://modelcontextprotocol.io/development/roadmap | 2026-11-02 | R3 2.31 |
| 32 | Individual 'OAuth for AI agents' drafts not WG-adopted | VERIFIED (via R3) | https://datatracker.ietf.org/ | 2026-11-02 | R3 2.29, 2.30 |
| 33 | auth.md: 'tells agents how to register on behalf of a user'; open; 'isn't tied to WorkOS infrastructure'; composes PRM and ID-JAG | VERIFIED | https://workos.com/auth-md | 2026-11-02 | read by W5; text paraphrases 'not tied to' |
| 34 | Radar: OAuth discovery 9,323 (8.1%), PRM 4,775 (4.1%), Auth.md 116 (0.10%) of 115,468 | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | R1 §3 facts 7, 12 |
| 35 | isitagentready oauthDiscovery/oauthProtectedResource/authMd criteria; Level 5 '2 of 3 … auth metadata' | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | read by W5 |
| 36 | Lighthouse Agentic Browsing has no auth audits | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | FACTS R4 §3 audit list |
| 37 | Nordlys outputs (401 header, PRM, AS metadata, CLI run) are real runs | VERIFIED | demos run | 2026-11-02 | shared/research/w5/ch14-run-outputs.txt; CLI query string shortened in text (disclosed) |
| 38 | Recommendation to use existing IdP; consent page rules; 'Connected agents' as backlog item | OPINION |  | 2026-11-02 | author's judgment |
| 39 | Production AS should check resolved IP for CIMD SSRF | OPINION | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations | 2026-11-02 | based on CIMD §6 SSRF guidance |

## Demos

- Layer `nordlys-cabins/layers/14-oauth/`: index.js, jwt.js, clients.js, grants.js, authorization-server.js, resource-server.js, tools.js, account.js, README.md (no new dependencies; needs layer 08)
- Standalone: `demos/chapters/14-connect-an-agent/` (agent.mjs, package.json, README.md), no dependencies
- Tests: `tests/ch14-oauth.test.js` (10 tests, in-process, MCP SDK client 2.4.0) and `tests/ch14-agent-cli.test.js` (1 test, real server on a free port). `node --test tests/ch14-*.test.js` → 11 pass, 0 fail (2 Nov 2026, Node 22.23.2).
- Interaction found: layer 16-security's tools.lock.json predates the two new tools, so ch16 'pinned tool definitions catch a silent change' fails when 14-oauth is present; it passes without it. Lock needs regenerating with all layers (reported to lead).
- Listings 14.1–14.6 are byte-identical excerpts generated from the files.
- Re-run by W5b on 2 Nov 2026 with Node 24.22.1 (the demos require Node >= 24): ch14-oauth 10/10 and ch14-agent-cli 1/1 pass. The ch16 interaction noted above did not reproduce in a full unit run (ch16 passed).

## Figures

- figure-14-1: the four OAuth roles on nordlys.example
- figure-14-2: discovery and authorization sequence (401 → PRM → AS metadata → authorize → token → call)
