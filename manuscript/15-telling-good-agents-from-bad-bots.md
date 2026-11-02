# Chapter 15: Telling good agents from bad bots

This chapter covers

- Three questions about every automated request: which software, which operator, which person
- Why a user agent string is a claim, and what published IP ranges and reverse DNS add
- Web Bot Auth: HTTP Message Signatures (RFC 9421), the `Signature-Agent` header and the key directory
- Who signs in November 2026, and why a small site should verify and not sign
- Building it for Nordlys Cabins: a verifier with no dependencies, labels per request, rate limits per class with `RateLimit` headers
- Pay per crawl, HTTP 402 and licensing as policy options, with their real status

In Chapter 14 an agent learned to act for one Nordlys member. Ingrid allowed it, the agent got a token, and from then on every call to `/mcp` carried proof of *her* permission. That solved the problem of the person. It left another one open, and it is the older problem of the two.

Most automated traffic that reaches Nordlys Cabins never logs in. Crawlers read the cabin pages for search engines and AI training. Assistants fetch a page because someone asked about a cabin. Agents call the booking-session API from Chapter 12 to get a price. Scrapers copy the guide articles. A few clients hammer `/mcp` a little harder than anyone needs. All of them arrive with a `User-Agent` header, and many of them say they are someone they are not.

Chapter 4 decided what each kind of visitor is *allowed* to do (`robots.txt`, Content Signals). Chapter 19 will count who came. This chapter sits between them: at the moment a request arrives, how do we know who sent it, and how sure can we be? The answer decides who gets the generous rate limit, whose requests we trust enough to log under an operator's name, and who gets a polite `429`.

I'll be honest from the start: in November 2026 we can be sure about only a small part of the traffic. But that part is growing, the tools to verify it are free, and the protocol behind it, Web Bot Auth, is short enough to implement in an afternoon. Let's have a look.

## Three questions about every automated request

When an automated request knocks on the door, there are three different things you might want to know (Figure 15.1).

**Which software is this?** The `User-Agent` header answers it, for example `ChatGPT-User` or `Googlebot`. The answer comes from the client and costs nothing to fake.

**Which operator runs it?** This is the company or person responsible for the software and for the network it runs on: OpenAI, Google, Anthropic, a price-comparison startup, a student with a script. Published IP ranges, reverse DNS and cryptographic signatures answer this question, with different strength.

**Which person is behind it?** If an agent acts for a human, which human? Chapter 14 answered this one with OAuth, and only for people who have an account with you and say yes.

![Figure 15.1 — Three questions about one automated request. The User-Agent header claims which software sent it. IP ranges, reverse DNS and Web Bot Auth signatures show which operator is responsible. OAuth, from Chapter 14, shows which of your users allowed it. Each answer comes from a different place and has a different strength.](images/figure-15-1.png)

The three questions are independent, and mixing them up causes most of the mistakes I see. A valid signature from OpenAI tells you that OpenAI's infrastructure sent the request. It tells you nothing about the person who typed the prompt. An OAuth token from Ingrid tells you she allowed *some* client to act for her, not which company built it. And a `User-Agent` string tells you only what the client wanted you to read.

Please note that the IETF working group behind Web Bot Auth wrote the same split into its charter. Authenticating "the end user of a participating client or agent" is explicitly out of its scope, together with HTTP APIs and agent-to-agent traffic.[^ch15-3] So this chapter is about the middle question, the operator. It is the one that decides most of your bot policy.

## The user agent is a claim

Every major AI company documents the user agent tokens of its crawlers and agents. Chapter 4 listed them with their purposes (training, search, user-triggered fetches), and Chapter 19 lists them again with the IP files we use for analytics, so I won't repeat the table here. What matters for this chapter is how little a token proves.

Anyone can send any user agent — really, anyone. A scraper that wants to look respectable writes `GPTBot` or `Googlebot` into its header with one line of code, and the operators know it. Common Crawl, for example, warns site owners that it is "aware of crawlers falsely identifying themselves as CCBot".[^ch15-5]

It works the other way too. Many agents that act for a person don't announce themselves at all. An agent built into a browser runs in the person's own browser, so its requests carry that person's user agent, cookies and address. A cloud browser that does not sign looks like any other Chrome. From the user agent alone you cannot tell those visits from people.

So the user agent is good for one thing: sorting the traffic that is honest. If a request says `Claude-User`, it is probably Anthropic's user-triggered fetcher, and we can label it as a *claimed* agent. We should never give a claim more than we would give an anonymous visitor. That rule is the core of the Nordlys policy later in this chapter.

## The network: IP ranges and reverse DNS

The next step up is the network the request came from. Two methods exist, and both are documented by the operators themselves.

### Published IP ranges

OpenAI, Anthropic, Perplexity and Google publish the address ranges their crawlers and fetchers use, as small JSON files. OpenAI has one file per agent (`gptbot.json`, `searchbot.json`, `chatgpt-user.json` and one for its ad checker), Anthropic publishes `https://claude.com/crawling/bots.json`, Perplexity has `perplexitybot.json`, and Google has five files, from `common-crawlers.json` to `user-triggered-agents.json`.[^ch15-6][^ch15-7][^ch15-8][^ch15-9] If a request says `GPTBot` and comes from an address inside `gptbot.json`, it is very likely GPTBot. If it says `GPTBot` and comes from anywhere else, it is very likely lying.

The ranges have two weaknesses. They change often, so you have to download them on a schedule and keep the date with each copy (Chapter 19 shows a classifier that does exactly that). And they are shared: an address in a cloud provider's range can be reused by someone else later, and a cloud browser service used by many people sends all of them from the same addresses. Anthropic even warns that blocking its IP addresses instead of using `robots.txt` "may not work correctly or persistently guarantee an opt-out".[^ch15-7]

There is an individual Internet-Draft that proposes one JSON format for all these files (`draft-illyes-webbotauth-jafar-01`).[^ch15-4] Until something like it is adopted, every operator's file has its own shape, and your code needs one small parser per operator.

### Reverse DNS, then forward DNS

Google documents an older method that needs no file at all. You look up the host name of the requesting address (reverse DNS), check that the name ends in one of Google's domains, then look up that name and check that it resolves back to the same address (forward DNS). In Google's words: "Verify that the domain name is either googlebot.com, google.com, or googleusercontent.com."[^ch15-9]

The second lookup is the important one. Whoever controls an IP address controls its reverse DNS record, so a scraper on its own server can make its address resolve to `crawl-1-2-3-4.googlebot.com`. It cannot make Google's DNS servers resolve that name back to its address. Only the round trip proves anything.

Reverse DNS is reliable, but it costs two DNS lookups for every new address, and it adds latency to the first request from that address. So you do it at the edge, or in middleware with a cache, and only for requests that claim to be Google. The Nordlys layer below does exactly that.

> **Note:** Google's user-triggered fetchers and agents follow the same rules. Requests from `Google-Agent`, which Google describes as used by "agents hosted on Google infrastructure to navigate the web and perform actions upon user request", come from the ranges in `user-triggered-agents.json`, and Google says its user-triggered fetchers "generally ignore robots.txt rules" because a person asked for the fetch.[^ch15-10] Network checks tell you the request really came from Google. They don't tell you it will follow your `robots.txt`.

Network evidence answers the operator question for the big crawlers quite well. It stops working when the operator is small, when the traffic comes from shared infrastructure, or when one service sends requests for many different customers. That gap is what Web Bot Auth closes.

## Web Bot Auth: a signature on every request

In simple words, Web Bot Auth lets an automated client sign each HTTP request with a private key and tell the site where to find the matching public key. A site that checks the signature knows which operator sent the request, whatever the user agent says and whichever network the request came from. It is the first identity mechanism for bots that does not depend on the bot's address.

The idea is not new cryptography. It combines two existing standards: HTTP Message Signatures (RFC 9421, February 2024) for the signature itself, and JSON Web Keys for publishing the public keys.[^ch15-1] What Web Bot Auth adds is a profile: which parts of the request must be signed, which parameters are required, and where the keys live.

### HTTP Message Signatures in five minutes

RFC 9421 signs *parts* of an HTTP message — the parts you choose. The signer picks a list of components, for example the authority (host name), the method, the path and a few headers, and builds a short text called the *signature base*: one line per component with its value, plus a last line with the signature parameters. Then it signs that text and sends two headers:

- `Signature-Input` lists the components and the parameters (when the signature was created, when it expires, which key signed it)
- `Signature` carries the signature bytes, base64-encoded

The receiver rebuilds the same signature base from the request it received and checks the signature with the public key. If any covered component changed on the way (another path, another host), the check fails. Components that were not covered can change freely, which is why the choice of components matters.

Both headers are Structured Fields dictionaries, so one request can carry several signatures with different labels (`sig1`, `sig2`, or Google's `g`). That detail matters later: a request that went through a cloud browser and a proxy might be signed by both.

### What Web Bot Auth adds

The Web Bot Auth profile lives in one IETF working group draft, `draft-ietf-webbotauth-httpsig-protocol-01`, published on 29 October 2026 by Thibault Meunier (Cloudflare) and Sandor Major (Google).[^ch15-2] It merged two earlier individual drafts, one for the architecture and one for the key directory.[^ch15-4] Its requirements for a signature are short enough to quote almost in full:

- The signature must cover `@authority` or `@target-uri`, so it is bound to your site.
- `created` and `expires` are required, and "it is RECOMMENDED that expires be no more than 24 hours after created".
- `keyid` must be the JWK SHA-256 thumbprint of the key (RFC 7638, and RFC 8037 for Ed25519 keys).
- `tag` must be `web-bot-auth`.

It also defines a new header, `Signature-Agent`. Its value is a dictionary whose members are HTTPS URLs, one per signature label, and the URL says who signed. The keys for that URL live in a key directory, a JSON Web Key Set served with the media type `application/http-message-signatures-directory+json`, usually at `/.well-known/http-message-signatures-directory` on the agent's own domain.[^ch15-2] The `Signature-Agent` header is itself covered by the signature, so nobody can swap the URL without breaking it.

Listing 15.1 shows a signed request from the test agent we build later in this chapter. It is real output from my run, with the agent's directory on a local port.

**Listing 15.1** A request signed with Web Bot Auth (output of `chapters/15-signing-agent/signer.mjs`)

```http
GET /cabins HTTP/1.1
Host: 127.0.0.1:3015
User-Agent: NordlysTestAgent/1.0
Signature-Agent: sig1="http://127.0.0.1:8977"
Signature-Input: sig1=("@authority" "@method" "@path" "signature-agent";key="sig1");created=1793659269;expires=1793659569;keyid="-LKDDMS1ZfRUbOdIYm8NJfZLEvt2pUgsY-kHzKDrIpw";alg="ed25519";nonce="2kyD1ao2/jRJ6dZyuMQZUEjxbvFdH1hsc3AAGpBaj0c=";tag="web-bot-auth"
Signature: sig1=:wDsjolQasBzTvl0nSqjAuNt+LTKWkSxHxJqSQTBZu3tmsNR1w5Q4kJ2EbXQHHpjiO2LGAedrenKsan8j5bDtDA==:
```

Let's read it line by line. `Signature-Agent` names the agent (`sig1="http://127.0.0.1:8977"`, a local test address, which is why it is not HTTPS). `Signature-Input` says that the signature labelled `sig1` covers the authority, the method, the path and the `sig1` member of `Signature-Agent`, was created at a Unix time and expires five minutes later, and was made with the key whose thumbprint is the `keyid`. The `nonce` is a random value the agent adds so that two signatures are never identical. And `Signature` carries the Ed25519 signature for label `sig1`.

Figure 15.2 shows how a verifier turns those three headers into an answer.

![Figure 15.2 — Anatomy of a Web Bot Auth check. The verifier rebuilds the signature base from the covered components of the request, finds the agent URL in Signature-Agent, fetches that agent's key directory (only for agents on its allowlist, and cached), picks the key whose thumbprint equals keyid, and verifies the Ed25519 signature. The result is a label for the request.](images/figure-15-2.png)

### What a signature proves, and what it does not

This is the part I'd ask every security person and product manager on the team to read, because a signature is easy to overestimate.

A valid signature proves that whoever controls the URL in `Signature-Agent` published the key that signed this request. The draft is careful about this: resolving the URL "establishes that the host named in the URL served this key set at fetch time", and that is "all it gives you". It "does not say that the operator of that URL is honest, or that it is the same party everyone knows about".[^ch15-2] So a valid signature from `https://chatgpt.com` is strong evidence, because you know who runs `chatgpt.com`. A valid signature from `https://totally-legit-agent.example` proves only that someone owns that domain.

Four more limits matter in practice.

**It names an operator, and only that.** A signed request from an agent service used by thousands of people tells you which service. Which of its users? No idea. Cloudflare's bot directory makes this explicit with two labels. A *Direct* bot is "operated by a single, narrow operator", while an *Intermediary* is "an agentic service that a wide range of end users can operate", which "introduces transitive trust: you may trust the intermediary operator, but not necessarily every end user driving it".[^ch15-14] Cloudflare says it is experimenting with forwarding information about the end user in the `Forwarded` header (RFC 7239), which is not standardised for this purpose yet.

**It binds the signature to your site, and only loosely to the request.** A signature that covers only `@authority` verifies "against any method, path, or body sent to that authority until it expires", so anyone who sees it can replay it within that time.[^ch15-2] Covering `@method` and `@path` (as our test agent does) narrows it. Short lifetimes narrow it further.

**It does not cover the body.** No component in the profile covers the request body. An agent that wants that has to send and sign a `Content-Digest` header, and the draft does not require it, because most automated traffic is `GET`.[^ch15-2]

**Replay protection is your policy.** The `nonce` parameter exists, but the draft "defines no additional nonce requirements", and rejecting duplicate nonces needs shared state across all your servers.[^ch15-2] For a rate-limiting decision you don't need it. For anything that changes data you have better tools anyway: the OAuth token from Chapter 14 and the confirmations from Chapter 16.

Bottomline: a verified signature is the best answer to "which operator sent this?" that the web has today. Whether to trust what the request *asks for* is a different question, and the Nordlys code below never confuses the two.

> **Still in flux:** Web Bot Auth is still a working group draft. The IETF `webbotauth` working group's charter milestones (an authentication technique to the IESG in April 2026 and a best-practice document in August 2026) have passed without a submission, and header details changed between earlier drafts. For example, `Signature-Agent` was a plain string before it became a dictionary, and deployments still send the old form.[^ch15-3][^ch15-2] Pin the draft number in your code comments, accept both forms, and keep all signature handling in one module.

## Who signs today

As of November 2026 the list of signers is short, but it includes the agents most likely to visit a booking site.

**OpenAI** signs requests from ChatGPT agent. Its key directory is live at `https://chatgpt.com/.well-known/http-message-signatures-directory`. When I fetched it on 2 November 2026 it held one Ed25519 key with `nbf` and `exp` dates, plus two extra fields, `"signature_agent": "https://chatgpt.com"` and `"purpose": "ai"`, and it was served with `Cache-Control: no-store, no-transform`.[^ch15-12]

**Google** calls its support experimental. Its guide says that "a subset of requests made by the Google-Agent are signed with Web Bot Auth", that those requests carry `Signature-Agent: g="https://agent.bot.goog"` (note the `g` label), and, very clearly: "We don't sign every request of a particular agent. Be sure that you fall back to the established methods of bot verification."[^ch15-11] Its directory at `https://agent.bot.goog` held five Ed25519 keys when I fetched it, with short `kid` values that are not thumbprints, and `Cache-Control: public, max-age=3600`.[^ch15-13] That is one more reason to compute the thumbprint yourself instead of trusting a directory's `kid`.

**The card networks** use it for agent commerce. Visa's Trusted Agent Protocol asks merchants to verify RFC 9421 signatures from "Visa-approved AI agents", and Cloudflare reported that both that protocol and Mastercard's Agent Pay "leverage Web Bot Auth as the agent authentication layer".[^ch15-18][^ch15-19] Chapter 12 covers what that means for checkout.

The verifying side is broader, because CDNs and firewalls did the work for their customers:

- Cloudflare folded signed agents into its *Verified bots* on 1 July 2026, with the Direct and Intermediary labels from the previous section. A bot becomes verified when it identifies itself honestly, by a Web Bot Auth signature, a published IP list with a stable user agent, or reverse DNS.[^ch15-14][^ch15-15]
- AWS WAF Bot Control added Web Bot Auth support on 21 November 2025, and verified signed bots are allowed by default there.[^ch15-16]
- Vercel's bot management verifies bots by reverse DNS and Web Bot Auth, and its verified bots directory classes ChatGPT's user and operator agents as `ai_assistant`.[^ch15-17]
- Akamai has said publicly that it supports the protocol. I could read this only in search results, not in Akamai's own documentation, so treat it as unverified.

How many sites take part? Cloudflare Radar counts how many of the 115,468 top domains it scanned publish a key directory. On 2 November 2026 that was 118 domains, or 0.10%.[^ch15-26] Please read that number correctly: a directory is something you publish when *you send* signed requests. It measures operators of bots and agents, not sites that verify them. Nobody publishes a count of verifying sites, and since most verification happens inside CDNs, you would not see it from outside anyway.

## Verify, don't sign

Now the decision for your own site. Web Bot Auth has two sides, and most websites only ever need one of them.

**Signing** is for whoever *sends* automated requests: an AI company's agent, a search crawler, a price-monitoring bot, a partner integration that polls your API. Signing means generating a key pair, publishing the public key in a directory on your domain, signing every request, and rotating keys from time to time. If Nordlys ran a bot that checked competitor prices, it would sign. It doesn't, so it won't. isitagentready.com agrees: its Web Bot Auth check looks for a key directory, but the check is informational, and "Failures are shown as neutral and do not affect the score".[^ch15-27]

**Verifying** is for whoever *receives* them, which is every website. And here you have three options, from least to most work:

1. **Let your edge do it.** If your site is behind Cloudflare, AWS WAF, Vercel or another provider that verifies signed agents, the work is done before the request reaches you. Your job is to write rules that use the result (allow verified agents on the booking flow, rate-limit everyone else) and to make sure your logs keep it.
2. **Use a library in your server.** Cloudflare publishes a reference implementation under the Apache 2.0 licence (`github.com/cloudflare/web-bot-auth`), with a browser-extension signer, Rust code, a Workers example and a Caddy verifier. Its npm package `web-bot-auth` was at version 0.2.0 (31 August 2026) when I checked, with `sign` and `verify` functions for Ed25519 and RSA-PSS keys. The generic package `http-message-signatures` (1.0.6) implements RFC 9421 without the Web Bot Auth profile.[^ch15-20][^ch15-21] Please note that the `web-bot-auth` README still cited the `-protocol-00` draft when I read it, so check which draft your library follows.
3. **Write a small verifier.** The profile is narrow enough that a careful implementation with your platform's crypto library is a few hundred lines. That is what we do for Nordlys, because it lets us see every step, and the demo has no dependencies to fall out of date.

Whichever you choose, the policy questions are the same, and they belong to the whole team. Which agents do we fetch keys for? What does a verified agent get that an anonymous client doesn't? What happens to an *invalid* signature? Let's answer them for Nordlys Cabins.

> **Tip:** If you do operate a bot, the operator checklist is short: an Ed25519 key, a directory served over HTTPS with the right media type, signatures that cover at least `@authority` and `Signature-Agent`, and short lifetimes. Then ask the big edge providers to list your bot (Cloudflare has a submission form for its bot directory).[^ch15-14] The test agent later in this chapter shows the signing side in about sixty lines.

## Hands-on: verifying signed agents in Nordlys Cabins

> **Hands-on:** This section builds layer `15-bot-identity` in the demo app: a Web Bot Auth verifier with no dependencies, an optional DNS check for Google's crawlers, a label for every request and rate limits per class. If you don't write code, read the next paragraph for the policy, look at Figure 15.3, and pick up again at "Rate limits that explain themselves".

The policy for Nordlys is simple, and I'd suggest something similar for most small sites. Every request gets exactly one label from the strongest evidence it carries. Nobody is blocked because of a label. The label only decides which rate-limit bucket a request counts against on the agent-facing endpoints (`/mcp` and the booking-session API under `/ucp/`), and what we write into the log for Chapter 19.

| Label | Evidence | Rate limit on agent endpoints |
| --- | --- | --- |
| `verified-agent` | a valid Web Bot Auth signature from an allowlisted agent | 300 requests per minute per agent |
| `verified-network` | an unsigned request whose Google claim passed reverse and forward DNS | 120 per minute per crawler |
| `invalid-signature` | a signature that is present but does not verify | 60 per minute per address |
| `claimed-agent` | a known user agent token, nothing more | 60 per minute per address |
| `unidentified` | nothing | 60 per minute per address |

Two decisions in this table deserve a comment. An invalid signature gets *no* penalty beyond the anonymous limit, because the draft says an unsigned request "does not establish whether the sender is human or automated", and a broken signature is more often a clock or a proxy problem than an attack.[^ch15-2] We log it, though, because a series of them from one address is worth a look. And the limits are per *bucket*: all requests from a verified agent share one bucket named after the agent, while anonymous requests get one bucket per address. That is the whole reward for signing: a verified agent is no longer mixed up with every other client on the same cloud address.

Figure 15.3 shows the layer as a flow.

![Figure 15.3 — The Nordlys bot identity layer. A signed request is verified against the agent's key directory. An unsigned request that claims to be Google can be confirmed by reverse and forward DNS. Every request gets one label, the label picks a rate-limit bucket on /mcp and /ucp/, and every response from those endpoints says where the client stands in RateLimit headers.](images/figure-15-3.png)

### One label per request

Listing 15.2 is the policy in code. It takes the result of the signature check, the user agent and the result of the DNS check, and returns one label. The order of the `if` statements *is* the evidence ladder: a signature beats a confirmed network, which beats a claim.

**Listing 15.2** `nordlys-cabins/layers/15-bot-identity/identity.js` — one label per request, and the rate-limit bucket for it

```js
// One label per request, from the strongest evidence available:
// a verified signature > a confirmed network > a User-Agent claim > nothing.
const KNOWN_AGENTS = [
  { token: 'ChatGPT-User', operator: 'https://chatgpt.com' },
  { token: 'ChatGPT Agent', operator: 'https://chatgpt.com' },
  { token: 'Google-Agent', operator: 'https://agent.bot.goog' },
  { token: 'Googlebot', operator: 'https://google.com' },
  { token: 'GPTBot', operator: 'https://openai.com' },
  { token: 'OAI-SearchBot', operator: 'https://openai.com' },
  { token: 'ClaudeBot', operator: 'https://anthropic.com' },
  { token: 'Claude-User', operator: 'https://anthropic.com' },
  { token: 'PerplexityBot', operator: 'https://perplexity.ai' },
];

export function identify(signature, userAgent = '', network = null) {
  const claimed = KNOWN_AGENTS.find((a) => userAgent.includes(a.token));
  const claim = claimed?.token ?? null;
  if (signature.status === 'verified') return { kind: 'verified-agent', agent: signature.agent, keyid: signature.keyid, userAgentClaim: claim };
  if (signature.status === 'invalid') return { kind: 'invalid-signature', reason: signature.reason, userAgentClaim: claim };
  if (network?.status === 'confirmed') return { kind: 'verified-network', userAgentClaim: network.token, host: network.host };
  if (claimed) return { kind: 'claimed-agent', userAgentClaim: claim, operator: claimed.operator, network: network?.status ?? 'unchecked' };
  return { kind: 'unidentified' };
}

/** The bucket a rate limiter counts against: a verified identity by name, everyone else by address. */
export function rateKey(identity, ip) {
  if (identity.kind === 'verified-agent') return `agent:${identity.agent}`;
  if (identity.kind === 'verified-network') return `crawler:${identity.userAgentClaim}`;
  return `ip:${ip}`;
}
```

The `rateKey` function at the end is where the reward happens. A verified agent is counted by its URL (`agent:https://chatgpt.com`), a confirmed crawler by its token, and everyone else by address. The list of known tokens is deliberately short. It is only used to say *who a request claims to be* in the log, never to grant anything.

### Checking the signature

Listing 15.3 verifies a request. It implements the validation rules of the draft and nothing more: find a signature with `tag="web-bot-auth"`, make sure it covers the authority and the `Signature-Agent` member, check the time window, find the key in that agent's directory by thumbprint, rebuild the signature base and verify.

**Listing 15.3** `nordlys-cabins/layers/15-bot-identity/verify.js` — verifying a Web Bot Auth signature

```js
// Verifying Web Bot Auth signatures (draft-ietf-webbotauth-httpsig-protocol-01).
// The result is a label for the request, never a reason to trust its content.
import { parseDictionary, parseSignatureInput, signatureBase, thumbprint, verifyBase } from './httpsig.js';

export function createVerifier({ directory, now = () => Math.floor(Date.now() / 1000), maxLifetime = 86400, skew = 60 }) {
  return async function verifyRequest(request) {
    const inputHeader = request.headers.get('signature-input');
    const sigHeader = request.headers.get('signature');
    if (!inputHeader || !sigHeader) return { status: 'unsigned' };

    const signatures = parseDictionary(sigHeader);
    const agentHeader = request.headers.get('signature-agent') ?? '';
    // Legacy form: a bare string. It belongs to whichever label covers it.
    const legacy = agentHeader.startsWith('"');
    const agents = legacy ? null : parseDictionary(agentHeader);

    let lastError = 'no web-bot-auth signature';
    for (const [lbl, raw] of parseDictionary(inputHeader)) {
      const input = parseSignatureInput(raw);
      if (input.params.tag !== 'web-bot-auth') continue;
      try {
        const names = input.items.map((i) => i.name);
        if (!names.includes('@authority') && !names.includes('@target-uri')) throw new Error('signature covers no authority');
        const agentItem = input.items.find((i) => i.name === 'signature-agent');
        if (!agentItem) throw new Error('Signature-Agent is not covered');
        const member = legacy ? agentHeader : agents.get(agentItem.params.key ?? lbl);
        // A member is a bare quoted URL. The draft says to ignore members that carry parameters.
        if (!member || !/^"[^"]+"$/.test(member)) throw new Error('no usable Signature-Agent member for this signature');
        const agent = member.slice(1, -1);

        const { created, expires, keyid } = input.params;
        const t = now();
        if (typeof created !== 'number' || typeof expires !== 'number') throw new Error('created and expires are required');
        if (created > t + skew) throw new Error('signature is from the future');
        if (expires < t - skew) throw new Error('signature has expired');
        if (expires - created > maxLifetime) throw new Error('signature lives too long');

        const keys = await directory.keys(agent);
        // Select by thumbprint, computed here: a directory's own kid is a label, not proof.
        const key = keys.find((k) => k.kty === 'OKP' && thumbprint(k) === keyid);
        if (key && ((key.nbf && t < key.nbf - skew) || (key.exp && t > key.exp + skew))) throw new Error('key is outside its validity period');
        if (!key) throw new Error('keyid is not in the agent\'s directory');
        const sig = signatures.get(lbl)?.match(/^:([A-Za-z0-9+/=]+):$/)?.[1];
        if (!sig) throw new Error('no signature value for this label');
        if (!verifyBase(signatureBase(request, input), sig, key)) throw new Error('signature does not verify');
        return { status: 'verified', agent, keyid, label: lbl };
      } catch (e) {
        lastError = e.message;
      }
    }
    return { status: 'invalid', reason: lastError };
  };
}
```

Some details are worth pointing out, because each of them is a mistake I could imagine making.

- The function never throws. It returns `unsigned`, `verified` or `invalid` with a reason, so a broken header cannot break a page.
- It accepts both forms of `Signature-Agent`: the current dictionary (`sig1="https://..."`) and the legacy bare string that some deployments still send. A member with parameters is ignored, as the draft requires.
- It looks the key up in *this agent's* directory, never in a global pool of keys. The draft insists on this: "Key lookup MUST be keyed on the (URL, key) pair, not on the key alone", because otherwise a request could be attributed to one agent with a key published by another.[^ch15-2]
- It computes the thumbprint itself (`thumbprint(k) === keyid`). A directory's own `kid` is just a label, and Google's directory, for one, uses short `kid` values that are not thumbprints.
- It respects the key's own `nbf` and `exp` dates when the directory gives them, as OpenAI's does.
- The time checks allow 60 seconds of clock skew, and refuse signatures that live longer than 24 hours, matching the draft's recommendation.

The signature base itself comes from `httpsig.js`, about a hundred lines that parse the Structured Fields headers, rebuild the base as RFC 9421 section 2.5 defines it, and call Ed25519 from `node:crypto`. I won't print it here (it is in the demos repository), but its tests are the most important ones in the layer: they check our signature base against the test vectors published in RFC 9421 appendix B.2.6 and in the draft's appendix E.2. If your own implementation reproduces those vectors byte for byte, it agrees with everyone else's.

### Fetching keys safely

To verify, we need the agent's public keys, and that means our server makes an HTTP request to a URL that a stranger put in a header. That is a textbook server-side request forgery (SSRF) risk, and the draft lists the precautions: a size limit, a key count limit, a timeout, a limit on redirects and no fetches to private addresses.[^ch15-2] Listing 15.4 shows how the Nordlys directory client applies them.

**Listing 15.4** `nordlys-cabins/layers/15-bot-identity/directory.js` (excerpt) — fetching and caching an agent’s key directory

```js
    async keys(agentUrl) {
      const id = new URL(agentUrl).href.replace(/\/$/, '');
      if (!trusted.has(id)) throw new Error('agent is not on the allowlist');
      if (new URL(id).protocol !== 'https:' && !allowHttp) throw new Error('directory must use https');
      const hit = cache.get(id);
      if (hit && hit.until > now()) {
        if (hit.error) throw new Error(hit.error); // a recent failure: don't hammer the operator
        return hit.keys;
      }
      try {
        const { keys, maxAge } = await fetchDirectory(directoryUrl(agentUrl));
        // At least 5 minutes, even for no-store: one fetch per request is what the draft warns against.
        cache.set(id, { keys, until: now() + Math.min(Math.max(maxAge, 300), 86400) * 1000 });
        return keys;
      } catch (e) {
        cache.set(id, { error: e.message, until: now() + 60_000 }); // negative cache, short on purpose
        throw e;
      }
    },
  };

  async function fetchDirectory(target) {
    const res = await fetchImpl(target, { redirect: 'manual', signal: AbortSignal.timeout(5000), headers: { accept: MEDIA_TYPE } });
    if (res.status !== 200) throw new Error(`directory answered ${res.status}`);
    if (target.endsWith(WELL_KNOWN) && !res.headers.get('content-type')?.startsWith(MEDIA_TYPE))
      throw new Error('directory has the wrong media type');
    const text = await res.text();
    if (text.length > 65536) throw new Error('directory is too large');
    const keys = JSON.parse(text).keys;
    if (!Array.isArray(keys)) throw new Error('directory has no keys array');
    if (keys.length > 16) throw new Error('directory has too many keys');
    const maxAge = Number(/max-age=(\d+)/.exec(res.headers.get('cache-control') ?? '')?.[1] ?? 3600);
    return { keys, maxAge };
  }
}
```

The first line of defence is the allowlist. We fetch keys only for agents we decided to trust (`https://chatgpt.com` and `https://agent.bot.goog` by default, plus anything in the `NORDLYS_WBA_TRUST` setting). A signature from any other agent comes back as `invalid` with the reason "agent is not on the allowlist", and the server never contacts that URL. Because the allowlist holds only public HTTPS origins, it also covers the "no private addresses" rule. If you ever replace the allowlist with "fetch any directory", add an address filter before you deploy.

The rest follows the draft: HTTPS only, no redirects (`redirect: 'manual'` turns a redirect into a non-200 answer), five seconds at most, 64 KB at most, 16 keys at most and the right media type at the well-known address.

Caching needs a decision. The draft asks verifiers to use normal HTTP caching and says a verifier "should not fetch the directory for every request".[^ch15-2] OpenAI's directory said `no-store` when I fetched it, which taken literally means a fetch per request. So the Nordlys client keeps a directory for at least five minutes and at most a day, following `max-age` in between. Failures are cached for one minute, so a directory that is down doesn't turn every signed request into an outgoing fetch. The draft suggests at most five minutes for that kind of negative cache.

### Confirming Google by DNS

For unsigned requests that claim to be `Googlebot` or `Google-Agent`, the layer can run the reverse-then-forward DNS check from earlier in the chapter (Listing 15.5). It is off by default in the demo, because it makes real DNS lookups, and you switch it on with `NORDLYS_RDNS=1`.

**Listing 15.5** `nordlys-cabins/layers/15-bot-identity/rdns.js` — reverse DNS, a domain check and forward DNS

```js
// Reverse-then-forward DNS, the check Google documents for its crawlers and fetchers.
// A name proves nothing on its own: the forward lookup must lead back to the same address.
import { promises as dns } from 'node:dns';

// Domains from https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests
export const DNS_RULES = [
  { token: 'Googlebot', domains: ['googlebot.com', 'google.com', 'googleusercontent.com'] },
  { token: 'Google-Agent', domains: ['googlebot.com', 'google.com', 'googleusercontent.com'] },
];

export function createDnsCheck({ resolver = dns, ttl = 3_600_000, now = () => Date.now() } = {}) {
  const cache = new Map(); // "token ip" -> { result, until }

  return async function checkDns(ip, userAgent = '') {
    const rule = DNS_RULES.find((r) => userAgent.includes(r.token));
    if (!rule || !ip) return null; // nothing to confirm
    const key = `${rule.token} ${ip}`;
    const hit = cache.get(key);
    if (hit && hit.until > now()) return hit.result;

    let result = { status: 'mismatch', token: rule.token };
    try {
      for (const raw of await resolver.reverse(ip)) {
        const host = raw.toLowerCase().replace(/\.$/, '');
        if (!rule.domains.some((d) => host === d || host.endsWith(`.${d}`))) continue;
        const addresses = ip.includes(':') ? await resolver.resolve6(host) : await resolver.resolve4(host);
        if (addresses.includes(ip)) { result = { status: 'confirmed', token: rule.token, host }; break; }
      }
    } catch {
      result = { status: 'unresolved', token: rule.token }; // DNS failed: no evidence either way
    }
    cache.set(key, { result, until: now() + ttl });
    return result;
  };
}
```

Notice the three outcomes. `confirmed` means both lookups agreed. `mismatch` means the address does not belong to Google, which for a request that *says* it is Googlebot is a strong hint that it is lying. `unresolved` means DNS failed, and we treat that as no evidence at all. The check matches whole domain labels, so `googlebot.com.evil.example` does not pass, and its results are cached for an hour per address.

### Rate limits that explain themselves

A `429 Too Many Requests` with no explanation is the most common way sites talk to bots, and the least useful one. An agent that hits it has to guess when to come back, and a polite agent backs off far more than it needs to. There is a better way, and it is close to standard.

The IETF HTTPAPI working group's draft `draft-ietf-httpapi-ratelimit-headers-11` (May 2026) defines two response headers.[^ch15-22] `RateLimit-Policy` describes a quota: `"anonymous";q=60;w=60` means a policy named `anonymous` with a quota of 60 requests in a 60-second window. `RateLimit` says where this client stands right now: `"anonymous";r=59;t=60` means 59 requests remain and the window resets in 60 seconds. Clients that understand the headers can pace themselves, and with `Retry-After` on the `429`, even clients that don't know the draft can do the right thing. Like Web Bot Auth, this is a draft, so the names could still change. Personally for me, it is worth sending anyway: the cost is two headers, and the benefit is agents that stop guessing.

Listing 15.6 is the limiter. It is a fixed window per bucket, the simplest algorithm that works, and it returns the headers with every decision.

**Listing 15.6** `nordlys-cabins/layers/15-bot-identity/ratelimit.js` — a fixed-window limiter that sends RateLimit headers

```js
// A fixed-window limiter per bucket that tells the client where it stands,
// using the RateLimit and RateLimit-Policy fields (draft-ietf-httpapi-ratelimit-headers-11).
export function createLimiter({ policies, window = 60, now = () => Date.now() }) {
  const windows = new Map(); // bucket -> { start, used }

  return function take(bucket, policy) {
    const quota = policies[policy];
    const t = now();
    let w = windows.get(bucket);
    if (!w || t - w.start >= window * 1000) windows.set(bucket, (w = { start: t, used: 0 }));
    w.used += 1;
    const reset = Math.max(1, Math.ceil((w.start + window * 1000 - t) / 1000));
    return {
      allowed: w.used <= quota,
      headers: {
        'ratelimit-policy': `"${policy}";q=${quota};w=${window}`,
        ratelimit: `"${policy}";r=${Math.max(0, quota - w.used)};t=${reset}`,
        ...(w.used > quota ? { 'retry-after': String(reset) } : {}),
      },
    };
  };
}
```

A fixed window in memory is fine for one server. With several servers behind a load balancer, keep the counters in a shared store (Redis or your CDN's rate limiting), or set each server's quota to its share of the total. The headers stay the same either way.

### Wiring it into the app

Listing 15.7 is the middleware that ties it together. It runs before authentication (`ctx.beforeAuth`, the hook the demo app's layer contract provides for exactly this), so that layer 14's OAuth check and every later layer can read the label from `c.get('botIdentity')`.

**Listing 15.7** `nordlys-cabins/layers/15-bot-identity/index.js` (excerpt) — the bot identity middleware

```js
    ctx.beforeAuth(async (c, next) => {
      const ip = c.req.header('x-forwarded-for')?.split(',')[0].trim() || c.env?.incoming?.socket?.remoteAddress || 'local';
      const ua = c.req.header('user-agent') ?? '';
      const signature = await verifyRequest(c.req.raw);
      const network = signature.status === 'unsigned' ? await checkDns(ip, ua) : null;
      const identity = identify(signature, ua, network);
      c.set('botIdentity', identity);
      if (identity.kind !== 'unidentified') ctx.events.emit('bot.identified', identity, { c });

      if (c.req.path === '/mcp' || c.req.path.startsWith('/ucp/')) {
        const bucket = rateKey(identity, ip);
        const policy = bucket.startsWith('agent:') ? 'verified-agent' : bucket.startsWith('crawler:') ? 'verified-crawler' : 'anonymous';
        const { allowed, headers } = take(bucket, policy);
        if (!allowed) return c.json({ error: 'rate_limited', detail: `Limit ${POLICIES[policy]} requests per minute for ${policy} clients.` }, 429, headers);
        await next();
        for (const [name, value] of Object.entries(headers)) c.res.headers.set(name, value);
      } else {
        await next();
      }
      if (env.NORDLYS_WBA_DEBUG === '1') c.res.headers.set('x-nordlys-bot-identity', identity.kind + (identity.agent ? ` ${identity.agent}` : ''));
    });
```

Three things happen in order: the label, the event, the limit. The DNS check runs only when there was no signature at all, because a signed request already has better evidence (and a bad signature should not be rescued by DNS). The `bot.identified` event is how Chapter 19's analytics layer learns about verified agents without importing anything from this layer. And the rate limit applies only on the two agent-facing endpoints. Pages stay unlimited at the application level, because a person browsing cabins should never meet a `429` from us (your CDN can still protect pages against floods).

The address comes from `X-Forwarded-For`, which is right only when the app runs behind a proxy you control that sets that header. Exposed directly to the internet, the app must use the socket address instead, or any client can pick its own bucket. This is the kind of deployment detail I'd put in the runbook.

### Testing with a signing agent

To test a verifier you need something that signs. The demos repository has a small test agent in `chapters/15-signing-agent/`. It generates a fresh Ed25519 key in memory, serves the public key as a directory on a local port, signs one request and prints the label Nordlys gave it. Listing 15.8 is its signing function.

**Listing 15.8** `chapters/15-signing-agent/signer.mjs` (excerpt) — signing a request the way an agent operator would

```js
/** Sign a Request: covers @authority, @method, @path and our Signature-Agent member. */
export function signRequest(request, { privateJwk, agentUrl, label = 'sig1', lifetime = 300, now = Math.floor(Date.now() / 1000) }) {
  const headers = new Headers(request.headers);
  headers.set('signature-agent', `${label}="${agentUrl}"`);
  const items = [
    { name: '@authority', params: {} }, { name: '@method', params: {} }, { name: '@path', params: {} },
    { name: 'signature-agent', params: { key: label } },
  ];
  const raw = serializeInput(items, {
    created: now, expires: now + lifetime, keyid: thumbprint(privateJwk), alg: 'ed25519',
    nonce: randomBytes(32).toString('base64'), tag: 'web-bot-auth',
  });
  const signed = new Request(request, { headers });
  const signature = signBase(signatureBase(signed, { items, raw }), privateJwk);
  headers.set('signature-input', `${label}=${raw}`);
  headers.set('signature', `${label}=:${signature}:`);
  return new Request(request, { headers });
}
```

Run Nordlys with the local agent on its allowlist, then run the agent against it:

```bash
NORDLYS_WBA_TRUST=http://127.0.0.1:8977 NORDLYS_WBA_ALLOW_HTTP=1 NORDLYS_WBA_DEBUG=1 \
  npm start -w nordlys-cabins -- --upto=15 --port=3000
node demos/chapters/15-signing-agent/signer.mjs http://127.0.0.1:3000/
```

`NORDLYS_WBA_ALLOW_HTTP=1` exists only for this local test, because real directories must use HTTPS, and `NORDLYS_WBA_DEBUG=1` adds an `x-nordlys-bot-identity` header to every response so you can see the label. The agent printed the headers from Listing 15.1, then `200 OK  x-nordlys-bot-identity: verified-agent http://127.0.0.1:8977`.

An unsigned request that only *claims* to be ChatGPT, sent with curl to the booking-session API, shows the other side: the label and the rate-limit headers (Listing 15.9, with the security headers from earlier chapters left out).

**Listing 15.9** An unsigned request to `/ucp/` that claims to be ChatGPT-User (response headers, shortened)

```http
HTTP/1.1 404 Not Found
content-type: application/json
ratelimit: "anonymous";r=59;t=60
ratelimit-policy: "anonymous";q=60;w=60
x-nordlys-bot-identity: claimed-agent
```

The automated tests in `nordlys-cabins/tests/ch15-bot-identity.test.js` go further. They check the signature base and signature against the RFC 9421 and draft test vectors, they tamper with requests (another path, an expired signature, an unknown key, an agent that is not on the allowlist, a `Signature-Agent` member with parameters) and expect `invalid` every time, never `verified`. They check that a failing directory is fetched only once a minute, that a key past its `exp` date does not verify, that the DNS check refuses look-alike names and names that don't resolve back, and that the 61st anonymous request in a minute gets a `429` with `Retry-After` while a verified agent still gets through. On Node.js 24.22.1 all 13 tests pass:

```bash
node --test nordlys-cabins/tests/ch15-bot-identity.test.js
```

## Pay per crawl, HTTP 402 and licensing

Once you can tell operators apart reliably, a new question appears: could some of them pay? This is where most of the hype in this area lives, so let's be precise about what exists in November 2026.

**Pay per crawl** is Cloudflare's product, announced on 1 July 2025. A site sets a price per request, and a crawler without an agreement gets `HTTP 402 Payment Required` with a `crawler-price` header. A crawler that wants to pay sends `crawler-exact-price` or `crawler-max-price` and gets the content with a `crawler-charged` header. Crawlers must authenticate with Web Bot Auth, which is exactly why the signature matters here: the site needs to know whom to charge.[^ch15-23] As of Cloudflare's documentation updated on 28 July 2026, pay per crawl was still in closed beta, with Cloudflare acting as merchant of record.[^ch15-24] Cloudflare publishes no adoption numbers for it.

**x402** and **MPP** are the open protocols that use the same status code for agents paying per API call. Chapter 12 explains both. Note that pay per crawl and x402 use different, incompatible headers, and that HTTP itself reserves 402 "for future use" without defining it in detail.

**RSL** (Really Simple Licensing) 1.0 is a specification published on 10 December 2025 by a group of publishers and platforms, with editors from the RSL Collective, Condé Nast, Ziff Davis, Schema.org, Yahoo, Automattic, O'Reilly and Fastly. It describes licensing terms for content in an XML file that `robots.txt` points to with a `License:` line.[^ch15-25] It is a way to *state* terms. Enforcing them still needs the identity and edge tools from this chapter.

**Commercial intermediaries** such as TollBit sell the same idea as a service, negotiating with AI companies on behalf of publishers. I haven't verified their terms, so I only name them as an option to research.

What does Nordlys do with all this? Nothing, and I think that is the right answer for most booking sites, shops and SaaS products. Nordlys earns money when an agent books a cabin. Charging the agent for reading the cabin page would only make it recommend someone else's cabin. Pay per crawl and RSL make sense when the content *is* the product: news, reference works, research, recipes, stock photos. If that is your business, the order of work is the same as here: verify identities first, measure who reads what (Chapter 19), and only then put a price on it.

## What the graders see

isitagentready.com has one check for this chapter, `webBotAuth`, in its Bot Access Control group: a key directory at `/.well-known/http-message-signatures-directory` with a valid JWK Set. As I said above, it is informational and does not affect the score.[^ch15-27] It does count for the top level, though. Level 5, "Agent-Native", needs Level 4 plus "2 of 3: Web Bot Auth, all four integration checks, auth metadata".[^ch15-27] A site that only verifies, like Nordlys, publishes no directory and so does not get this check. That is fine: Nordlys can reach Level 5 with the integration checks and the OAuth metadata from Chapter 14 (Chapter 11 has the ladder).

I'd add a caution here. Publishing a key directory only to pass a check, without ever signing a request, tells agents and graders something that isn't true. If you don't send automated traffic, leave the check neutral.

The Lighthouse Agentic Browsing category has no audit for bot identity. It looks at pages as an agent sees them, and nothing in this chapter changes a page.

And the adoption context from Radar, once more with its date: 118 of 115,468 scanned domains (0.10%) published a Web Bot Auth key directory on 2 November 2026.[^ch15-26] The same Radar page reported that 16% of responses to AI bots were `403` and 2.6% were `429` in the week to 2 November 2026, so plenty of sites already refuse AI bots. They mostly do it by user agent, which is exactly the evidence this chapter says not to trust on its own.

## A checklist per role

- **Security and platform:** decide whether your edge verifies signed agents, and if so, which labels reach the origin and the logs. Verify by signature first, network second, user agent never on its own. Treat key directory fetches as outgoing requests to untrusted URLs.
- **Developers:** keep all signature code in one module with the draft number in a comment. Test against the RFC 9421 and draft test vectors. Send `RateLimit-Policy`, `RateLimit` and `Retry-After` on agent endpoints.
- **Product managers:** decide what a verified agent gets (a bigger quota, access to booking sessions, nothing) and who maintains the allowlist. Treat an Intermediary as many unknown users behind one known operator.
- **Analytics:** log the label, the `Signature-Agent` and the `keyid` with every request (Chapter 19 shows a JSON log that keeps them).
- **Legal and commercial:** decide whether your content is the product. If it is, follow pay per crawl and RSL. If it isn't, don't put a price on reading.
- **QA:** include signed, unsigned, spoofed and expired requests in your test suite, and a client that exceeds the limit.

## What to watch

- New revisions of `draft-ietf-webbotauth-httpsig-protocol` and whether it reaches the IESG. The working group also has individual drafts in the queue, including a registry and "Signature Agent card" (`draft-meunier-webbotauth-registry-04`, 27 October 2026), crawler best practices, a JSON format for IP ranges and anonymous bot authentication.[^ch15-4]
- Google moving from "a subset of requests" to signing all Google-Agent traffic, and other AI companies publishing directories.
- How intermediaries pass information about the end user. Cloudflare's experiment with the `Forwarded` header is the one to follow.[^ch15-14]
- `draft-ietf-httpapi-ratelimit-headers` becoming an RFC, and clients that pace themselves by it.
- Pay per crawl leaving closed beta, and whether any adoption numbers appear for it or for RSL.

## Summary

- Every automated request raises three separate questions: which software, which operator, which person. The user agent claims the first, IP ranges, reverse DNS and signatures answer the second, and OAuth (Chapter 14) answers the third.
- A user agent string is a claim. Use it to sort honest traffic, never to grant anything.
- Published IP ranges and reverse-then-forward DNS identify the big crawlers well, but fail for shared infrastructure and small operators.
- Web Bot Auth (`draft-ietf-webbotauth-httpsig-protocol-01`, 29 October 2026) signs requests with RFC 9421 HTTP Message Signatures and names the signer in `Signature-Agent`, with keys in a JSON Web Key Set at `/.well-known/http-message-signatures-directory`.
- A valid signature proves which operator controls the key. It says nothing about the operator's honesty, the end user behind an intermediary or the request body.
- OpenAI signs ChatGPT agent traffic, Google signs some Google-Agent requests experimentally, and Cloudflare, AWS WAF and Vercel verify signed bots for their customers. Only 0.10% of the domains Radar scanned published a key directory on 2 November 2026.
- A typical website should verify and not sign. Nordlys Cabins verifies with an allowlist, a cached and size-limited directory client and thumbprint lookup per agent, labels every request, and gives verified agents their own rate-limit bucket.
- `RateLimit-Policy`, `RateLimit` and `Retry-After` turn a bare `429` into instructions an agent can follow.
- Pay per crawl, x402 and RSL are options for sites whose content is the product. Pay per crawl was still in closed beta in November 2026, and none of them fit a booking site.

[^ch15-1]: A. Backman, J. Richer, M. Sporny, "HTTP Message Signatures", RFC 9421, February 2024, https://www.rfc-editor.org/rfc/rfc9421 (retrieved November 2026).
[^ch15-2]: T. Meunier, S. Major, "HTTP Message Signatures for automated traffic", draft-ietf-webbotauth-httpsig-protocol-01, 29 October 2026, IETF, https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt, sections 4.4, 5.2, 5.2.1, 5.2.3, 5.4, 5.5.1, 6.7, 6.11 and appendix C (retrieved November 2026).
[^ch15-3]: "Web and Internet Transport Bot Authentication (webbotauth): About", IETF Datatracker, https://datatracker.ietf.org/wg/webbotauth/about/ (retrieved November 2026).
[^ch15-4]: "webbotauth: Documents", IETF Datatracker, https://datatracker.ietf.org/wg/webbotauth/documents/ (retrieved November 2026).
[^ch15-5]: "CCBot", Common Crawl, https://commoncrawl.org/ccbot (retrieved November 2026).
[^ch15-6]: "Overview of OpenAI Crawlers", OpenAI Platform documentation, https://platform.openai.com/docs/bots (retrieved November 2026).
[^ch15-7]: "Does Anthropic crawl data from the web, and how can site owners block the crawler?", Claude Help Center, https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler (retrieved November 2026).
[^ch15-8]: "Perplexity Crawlers", Perplexity documentation, https://docs.perplexity.ai/docs/resources/perplexity-crawlers (retrieved November 2026).
[^ch15-9]: "Verifying Google requests", Google Crawling Infrastructure, https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests (retrieved November 2026).
[^ch15-10]: "Google user-triggered fetchers", Google Crawling Infrastructure, https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers (retrieved November 2026).
[^ch15-11]: "Google's Guide to Authenticating Requests with Web Bot Auth (Experimental)", Google Crawling Infrastructure, https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth (retrieved November 2026).
[^ch15-12]: OpenAI key directory, https://chatgpt.com/.well-known/http-message-signatures-directory, fetched on 2 November 2026 (retrieved November 2026).
[^ch15-13]: Google agent key directory, https://agent.bot.goog/.well-known/http-message-signatures-directory, fetched on 2 November 2026 (retrieved November 2026).
[^ch15-14]: "Signed agents", Cloudflare Bots documentation, https://developers.cloudflare.com/bots/concepts/bot/signed-agents/ (retrieved November 2026).
[^ch15-15]: "Verified bots", Cloudflare Bots documentation, https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ (retrieved November 2026).
[^ch15-16]: "AWS WAF announces Web Bot Auth support", AWS What's New, 21 November 2025, https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/ (retrieved November 2026).
[^ch15-17]: "Bot Management", Vercel documentation, https://vercel.com/docs/bot-management (retrieved November 2026).
[^ch15-18]: "Getting Started - Trusted Agent Protocol", Visa Developer, https://developer.visa.com/docs/trusted-agent-protocol (retrieved November 2026).
[^ch15-19]: "Helping AI agents transact with Visa and Mastercard", The Cloudflare Blog, 24 October 2025, https://blog.cloudflare.com/secure-agentic-commerce (retrieved November 2026).
[^ch15-20]: "web-bot-auth", Cloudflare on GitHub, https://github.com/cloudflare/web-bot-auth (retrieved November 2026).
[^ch15-21]: npm registry entries for `web-bot-auth` (version 0.2.0, 31 August 2026) and `http-message-signatures` (version 1.0.6, 4 June 2026), https://registry.npmjs.org/web-bot-auth and https://registry.npmjs.org/http-message-signatures (retrieved November 2026).
[^ch15-22]: R. Polli et al., "RateLimit header fields for HTTP", draft-ietf-httpapi-ratelimit-headers-11, May 2026, https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ (retrieved November 2026).
[^ch15-23]: "Introducing pay per crawl", The Cloudflare Blog, 1 July 2025, https://blog.cloudflare.com/introducing-pay-per-crawl/ (retrieved November 2026).
[^ch15-24]: "What is Pay Per Crawl?", Cloudflare AI Crawl Control docs, updated 28 July 2026, https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/what-is-pay-per-crawl/ (retrieved November 2026).
[^ch15-25]: "RSL 1.0 Specification", RSL Standard, https://rslstandard.org/rsl, and the RSL guide at https://rslstandard.org/ (retrieved November 2026).
[^ch15-26]: "AI Insights: Adoption of AI agent standards" and "AI Insights", Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards, data dated 2 November 2026 (retrieved November 2026).
[^ch15-27]: "llms-full.txt", isitagentready.com, https://isitagentready.com/llms-full.txt, Bot Access Control checks and "Levels" (retrieved November 2026).
