# Editorial log: Chapter 8, Server-side tools with the Model Context Protocol

Writer W3. 2026-11-02.

## Pass 1: voice draft
- Plan: MCP for the whole team (roles, primitives, cost), who connects, what changed in 2026-07-28 with raw curl exchanges, choosing the tools, building (SDK, factory, mounting, Origin check), tools (schemas, structured output, errors, safe booking), annotations and confirmations, MCP Apps, resources and prompt, the registry, testing (SDK client, Inspector), trying it in a host, hosting, notes for 2025 tutorials, graders, summary.
- All JSON in the chapter is real output from the demo (curl against `npm start -- --upto=8`, Inspector CLI 2.13.0, SDK client).

## Pass 2: substantive edit
- Fidelity: the draft said Chapter 12 adds commerce tools through the registry. Checked the other layers: Chapter 12 does not, Chapters 14, 16 and 17 do. Text, figure 8.2, registry.js comment and the layer README corrected.
- Fidelity: removed an invented "90% of HTML" figure. Corrected the instructions length (309 characters, measured). Fixed a guide URI to a real article slug.
- Verified by experiment that the SDK validates structuredContent against outputSchema before claiming it.
- Role readability: added "Choosing the tools" (a product decision) and "Trying it in a real host"; Hands-on callouts on all code sections with pickup points.
- Hedging: maintainer-reported download numbers marked as such; host table framed as a November 2026 snapshot; VS Code config format called out as moving.

## Pass 3: voice recheck and fidelity
- No semicolons in prose, no banned phrases, absolute dates. Every version and quote checked against shared/validation/08-server-side-tools-with-mcp.md. Listings 8.1-8.6 byte-identical to demo files.
