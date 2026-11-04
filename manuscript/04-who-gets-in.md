# Chapter 4: Who gets in: policy and proof

This chapter covers

- The kinds of automated visitors that arrive from AI companies, and four decisions about them, made from your own logs
- Writing that policy into `robots.txt` with groups per purpose, Content Signals and a sitemap
- The IETF AI Preferences drafts and Google's own controls for AI features, with their status as of November 2026
- Why a user agent is only a claim, and what IP ranges, reverse DNS and Web Bot Auth signatures add
- Verifying signed agents in Nordlys Cabins, with rate limits per class that explain themselves

Chapters 2 and 3 were about the page itself. This chapter steps back to the front door. Before an agent can read your cabin descriptions or book anything, it has to arrive, and before it arrives someone at your company has (or hasn't) decided whether it is welcome.

Most teams never made that decision on purpose. The `robots.txt` file was written years ago by whoever set up the site, it says `Allow: /` to everyone, and it has not been touched since. Then, sometime in 2024 or 2025, a headline about AI training made someone nervous, and a block of `Disallow: /` lines for "the AI bots" appeared at the bottom. Sometimes that block also locks out the very assistants that send customers. Honestly, I don't blame anyone: the vocabulary for talking about this became clear only quite recently, when the vendors started to document their crawlers per purpose.

This chapter gives you that vocabulary in two halves. The first half is policy: who visits, four decisions a team can make in one meeting, and the files that carry them. The second half is proof: when a request arrives, how do we know who sent it, and how sure can we be? Product managers, legal, content and SEO people decide here, and developers implement. The code sections are marked, and you can skip them without losing the thread.

## Who knocks on the door

Let's start with data rather than opinions. Cloudflare Radar publishes AI crawler traffic for its network, and the "crawl purpose" chart is the most useful single picture I know of what arrives at a website from AI companies. For the seven days ending 2 November 2026, Radar classified AI crawler traffic like this: 41.4% for training, 41.3% for mixed training and search, 12.3% for search, 3.7% for user actions and 1.3% undeclared.[^ch04-1]

And sites are reacting. Sixteen percent of all responses that Radar saw going to AI bots in that week were `403 Forbidden`, and among the top 10,000 domains, 708 of the 4,387 `robots.txt` files disallow GPTBot at least partly.[^ch04-1] A lot of websites are already making some decision. The question is whether it is the decision they meant.

The vendors' own documentation now splits their automated traffic by purpose, and that split is the key to this chapter. *Training crawlers* (GPTBot, ClaudeBot, CCBot) collect content to train models. *Search crawlers* (OAI-SearchBot, Claude-SearchBot, PerplexityBot and Googlebot, because Google's AI Overviews and AI Mode are built on normal Search crawling) build an index that links back to sources. *User-triggered fetchers and agents* (ChatGPT-User, Claude-User, Perplexity-User, Google-Agent) fetch a page because one person asked an assistant to, right now.

Each kind costs you something different and gives back something different. Training gives back little that you can measure. Search can send visitors and citations. User-triggered fetches are, quite literally, customers using a different interface. That is why "block AI" or "allow AI" is the wrong unit of decision. The right unit is the purpose.

## Four decisions, made from your own logs

Here is the framework I suggest. Before anybody edits a file, the people who own the business answer four questions, one per purpose (Figure 4.1):

1. **Search.** Do we want to appear in classic search results and in AI search indexes that link back to us?
2. **AI answers.** May our content be used as input for AI-generated answers (grounding, retrieval-augmented generation, summaries in an assistant), assuming the answer cites us?
3. **Agents acting for a person.** May an assistant fetch and use our pages, including transactional ones, when a user asks it to?
4. **Training.** May our content be used to train or fine-tune generative AI models?

![Figure 4.1 — Four purposes, four decisions. Each kind of automated visitor maps to one business question, and each answer maps to a different control: robots.txt groups for crawlers, Content Signals for usage, Google's own settings for its AI features, and authentication for anything private.](images/figure-4-1.png)

For most commercial sites, the first three answers are "yes": a booking site, a shop or a SaaS product wants to be found, quoted and used. The fourth answer is where companies genuinely differ. A news publisher may say no to training, while a developer tool's documentation may say yes to everything.

Make the decisions with your own logs open, not with opinions. The first look in Chapter 2 already tells you which kinds of visitor come today, how many of your responses to them are `403` or `429`, and how much traffic nobody can name. Write those numbers into the meeting notes. Chapter 12 turns them into a regular report, so the answers can be revisited when the numbers change.

Almost none of these questions are technical, even though the developer who owns the server usually ends up editing `robots.txt`. The product manager owns the four answers, legal owns whether a training "no" needs a formal reservation of rights, content and SEO own Google's settings in Search Console, developers own the files, headers, CDN rules and tests, and security makes sure nothing private relies on `robots.txt`.

### The Nordlys Cabins decision

For our running example, the (fictional) Nordlys team answers like this:

- Search: yes. Guests find cabins through search, classic and AI.
- AI answers: yes. An assistant that recommends Fjellro for a February ski week and links to the booking page is doing marketing for free.
- Agents acting for a person: yes, including the booking pages. A guest who asks an assistant to "book Fjellro from 12 to 14 February" should succeed. Private pages (accounts, existing bookings) stay behind sign-in, as they already are.
- Training: no. The team sees no benefit in it, and the cabin descriptions and guides are its own work.

Write the answers down somewhere everyone can read them. We put them in code in a moment, but the code is the implementation, not the decision.

## robots.txt, the 2026 refresher

The Robots Exclusion Protocol is older than most people who edit it, and since September 2022 it is an IETF standard, RFC 9309.[^ch04-2] It is worth re-reading the essentials, because AI crawlers rely on exactly these rules.

A `robots.txt` file lives at the root of an origin (`https://nordlys.example/robots.txt`) and consists of *groups*. Each group starts with one or more `User-agent` lines naming product tokens, followed by `Allow` and `Disallow` rules with path prefixes. A crawler finds the group that matches its own token and obeys that group only. If no group names it, it uses the `*` group. Within a group, the most specific (longest) matching rule wins, so `Allow: /` together with `Disallow: /account/` means "everything except the account area".

- **One group per crawler.** A crawler that has its own group ignores the `*` group completely, so every group has to be complete on its own.
- **Errors mean something.** Google treats a `4xx` response for `robots.txt` (except `429`) as "no restrictions" and a `5xx` as a reason to stop crawling the site for 12 hours.[^ch04-3] A broken deploy can quietly change your policy for a day.
- **Disallow is not noindex.** A crawler that may not fetch a page cannot see a `noindex` instruction on it.

And the most important sentence in the whole RFC, quoted exactly: "These rules are not a form of access authorization."[^ch04-2] `robots.txt` is a request. Well-behaved crawlers honour it. Anything else is free to ignore it, and some kinds of agents ignore it on purpose.

## Who is who: the AI user agents

Now the part that changes fastest. Each major AI vendor publishes a page listing its crawlers and fetchers, what each one is for and how it treats `robots.txt`. Table 4.1 summarises those pages as I read them on 2 November 2026. Please read it as a dated snapshot: tokens are added, renamed and retired, and the vendor pages are the source of truth.

**Table 4.1** AI user agents and control tokens by purpose, as documented by their vendors (checked 2 November 2026)

| Token | Vendor | Purpose | What the vendor says about robots.txt |
| --- | --- | --- | --- |
| GPTBot | OpenAI | Training | Honours it[^ch04-4] |
| ClaudeBot | Anthropic | Training | Honours it[^ch04-5] |
| Google-Extended | Google | Training and grounding for Gemini (not Search) | A control token with no crawler of its own[^ch04-6] |
| Applebot-Extended | Apple | Training Apple's models | A control token, "does not crawl webpages"[^ch04-7] |
| CCBot | Common Crawl | Public dataset, widely used for training | Honours it, and warns about spoofed CCBot user agents[^ch04-8] |
| Meta-ExternalAgent | Meta | Training and indexing | Documented on a page we could not load (unverified)[^ch04-9] |
| Amazonbot | Amazon | Mixed: may train Amazon models and improve Amazon products | Honours it, using a cached copy up to 30 days old[^ch04-10] |
| OAI-SearchBot | OpenAI | Search in ChatGPT | Honours it[^ch04-4] |
| Claude-SearchBot | Anthropic | Search quality | Honours it[^ch04-5] |
| PerplexityBot | Perplexity | Search index, "not used to crawl content for AI foundation models" | Honours it[^ch04-11] |
| Amzn-SearchBot | Amazon | Search (for example Alexa), not training | Honours it[^ch04-10] |
| Googlebot | Google | Search, including AI Overviews and AI Mode | Honours it[^ch04-6] |
| ChatGPT-User | OpenAI | Fetches for a user's request | "robots.txt rules may not apply"[^ch04-4] |
| Claude-User | Anthropic | Fetches for a user's request | Honours it[^ch04-5] |
| Perplexity-User | Perplexity | Fetches for a user's request | "generally ignores robots.txt rules"[^ch04-11] |
| Google-Agent and other user-triggered fetchers | Google | Fetches and actions for a user's request | "generally ignore robots.txt rules"[^ch04-12] |
| Amzn-User | Amazon | Fetches for a user's request | "may not follow all robots.txt directives"[^ch04-10] |

Some rows deserve a comment.

**Control tokens are not crawlers.** Google-Extended and Applebot-Extended never appear in your access logs. They exist only as names in `robots.txt`, and the vendor checks whether you disallowed them before using the content for model training (and, for Google, for grounding answers in Gemini apps). Google says Google-Extended "does not impact a site's inclusion in Google Search nor is it used as a ranking signal in Google Search."[^ch04-6] So blocking it does *not* take you out of AI Overviews.

**User-triggered fetchers mostly don't ask.** OpenAI, Perplexity, Google and Amazon all document that their user-triggered fetchers may ignore `robots.txt`: a person asked for this page, so the fetcher acts like that person's browser. Anthropic is the clearest exception. It says all three of its bots, including Claude-User, honour `robots.txt`, and that disabling Claude-User "prevents our system from retrieving your content in response to a user query."[^ch04-5] Read this the other way round: if your `robots.txt` blocks everything that looks like AI, the one assistant that actually listens to you is the one you have locked out of your booking pages.

## Content Signals: saying what your content may be used for

`robots.txt` answers one question: may this crawler fetch this path? It says nothing about what happens to the content afterwards. A search crawler that fetched your page could, in principle, feed it to a model. For years the only way to say "index me, but don't train on me" was to know which token each vendor uses for which purpose, as in Table 4.1.

In September 2025 Cloudflare proposed a more direct way, the Content Signals Policy.[^ch04-13] It adds one line to `robots.txt` that states your preference for three uses:

- `search`: building a search index and providing search results, meaning hyperlinks and short excerpts. Search, in this definition, "does not include providing AI-generated search summaries."
- `ai-input`: "inputting content into one or more AI models (e.g., retrieval augmented generation, grounding, or other real-time taking of content for generative AI search answers)."
- `ai-train`: training or fine-tuning AI models.

Each signal is `yes` or `no`, and a missing signal means you neither grant nor restrict anything. For Nordlys the line reads:

```text
Content-Signal: search=yes, ai-input=yes, ai-train=no
```

Three facts help you judge how much weight to put on this line. It is widely deployed, by one company: Cloudflare turned on managed `robots.txt` for over 3.8 million domains by September 2025, and Radar's November 2026 snapshot found Content Signals on 8.9% of the top domains it scanned, up from about 4% in April 2026.[^ch04-13][^ch04-1][^ch04-14] It is not a standard: Cloudflare's individual Internet-Draft was never adopted by the working group, and the IETF datatracker lists it as "Expired & archived" since 4 April 2026.[^ch04-15] And nobody has published whether crawlers obey it. None of the vendor pages in Table 4.1 mentions Content Signals.

So why add it? Two practical reasons. It is the cheapest way to write your training decision in a form that is explicit, dated and machine-readable, which helps if you ever need to show what you asked for. And isitagentready.com requires it: Level 2 ("Bot-Aware") needs both AI bot rules and Content Signals in `robots.txt`.[^ch04-16] The tool that defines the most-cited agent-readiness level is run by the company that wrote the signal. Cloudflare is player and referee here, and I think it is fair to say that out loud while still adding the line.

Where does the line go? The Content Signals text does not define how it interacts with `robots.txt` groups, and a crawler with its own group never sees a line that sits only in the `*` group. To be safe, Nordlys repeats the line in every group. isitagentready.com's `contentSignals` check only looks for at least one `Content-Signal:` line, so it passes either way.[^ch04-16]

## The IETF AI Preferences work

The IETF chartered the AI Preferences working group (aipref) to standardise exactly this. As of November 2026 it has two working-group drafts.[^ch04-17] `draft-ietf-aipref-vocab-08` defines three categories of use, `train-ai`, `ai-use` and `search`, each with a `y` or `n` preference, and warns in its own text that its contents "DO NOT REFLECT CONSENSUS of the Working Group either in whole or part."[^ch04-18] `draft-ietf-aipref-attach-05` attaches them with a `Content-Usage` HTTP header or a `Content-Usage` rule in `robots.txt`.[^ch04-19] An individual draft from Anthropic (30 October 2026) uses an ordinary `robots.txt` group under a reserved token, `User-Agent: __usage_ai-training`,[^ch04-20] and Google says it "intends to support the AIPREF shared machine-readable training preference signal (with " user-agent: __usage_ai-training") in early 2027."[^ch04-6]

There is a practical catch, too. Lighthouse's SEO audit validates every line of `robots.txt` against a safelist of directives, and in Lighthouse 13.6.0 that list includes `content-signal` but not `content-usage`.[^ch04-21] A `robots.txt` with an aipref line therefore fails "robots.txt is valid" today. That is why the Nordlys policy has a switch for it, off by default.

> **Still in flux:** Two drafts with different syntaxes, a vocabulary without consensus, and one vendor's intent for early 2027. Nothing in the aipref work is final as of November 2026, and no crawler documents reading `Content-Usage` today. My advice: keep Content Signals as your deployed signal, follow the working group, and switch on the aipref syntax once the drafts settle and a vendor you care about reads it.

## Google's controls for AI features

Google deserves its own section, because its search engine and its AI features share one crawler, and because Google-Extended, the token many teams reach for first, does not control AI features in Search.

Here is the situation as of November 2026. Googlebot crawls for Google Search, and Google's AI Overviews and AI Mode are features of Search, built on the same index. Blocking Googlebot removes you from Search entirely, which is rarely what anyone wants. Google-Extended, as we saw, controls training and grounding for Gemini apps and Vertex AI, and explicitly not Search. So what controls AI features in Search? Google offers three levers (Table 4.2).

**Table 4.2** Google's controls for AI use of your content (November 2026)

| Control | Where | What it does |
| --- | --- | --- |
| `Google-Extended` token in `robots.txt` | Your site | Opts content out of training and grounding for Gemini apps and Vertex AI. No effect on Search, AI Overviews or AI Mode.[^ch04-6] |
| `nosnippet`, `max-snippet` (robots meta tag or `X-Robots-Tag` header) and the `data-nosnippet` HTML attribute | Your pages | Limit or prevent snippets. Google says `nosnippet` also prevents the content "from being used as a direct input for AI Overviews and AI Mode." `data-nosnippet` does the same for a part of a page.[^ch04-22] |
| "Search generative AI control" toggle | Search Console | Removes the site from appearing in and grounding AI Overviews, AI Mode and AI Overviews in Discover, without affecting classic ranking. Tested from 3 June 2026, available to all websites since 31 August 2026.[^ch04-23] |

The Search Console toggle is the closest thing Google has to an `ai-input=no` for its own products, and opting out means no traffic or impressions from its generative AI features.[^ch04-23] It is invisible from the outside, so write it into the policy document. For Nordlys, all three stay open.

> **Note:** If your legal team asks about a formal reservation of rights for text and data mining in the EU (TDMRep and the EU AI Act's copyright duties), or your business wants to charge crawlers instead of blocking them (pay per crawl, HTTP `402`, RSL licensing), Appendix C covers both. They depend on the same two things as everything else here: a clear policy, and knowing who the crawler really is.

## Beyond the polite request

Everything so far is a request. RFC 9309 says so, Content Signals and aipref are "preferences" by their own definitions, and the vendors describe which requests they honour. For some sites that is not enough, and it helps to see the whole ladder of controls.

**Requests** are `robots.txt` groups, Content Signals and (later) aipref. They work for crawlers that choose to comply, which includes every major vendor crawler in Table 4.1.

**Enforcement at the edge** means rules in your CDN, web application firewall or server that answer requests from certain clients with `403`, `429` or a redirect, regardless of what `robots.txt` says. This is where the 16% of `403` responses in Radar's data come from. Cloudflare's AI Crawl Control, Vercel's AI bots managed ruleset and comparable features in AWS WAF, Akamai and others ship ready-made rules for AI bots, and several of them verify signed agents.[^ch04-24][^ch04-25] Block by verified identity where you can, because anyone can falsely claim to be CCBot,[^ch04-8] and keep `robots.txt` as the statement of intent that compliant crawlers read.

**Authentication** is the only real access control. Member areas, booking details, anything with personal data: these need sign-in or unguessable tokens, and they need it whether the visitor is a person, a crawler or an agent. In Nordlys, `/account/` already requires sign-in and a booking page needs its reference plus a token. The `Disallow` lines for those paths are there to save crawlers a wasted request, not to protect anything.

> **Note:** Blocking is a business decision with a price. A `403` for a user-triggered fetcher means a person who asked an assistant about your site gets "I couldn't access that page". Block the purposes you decided against, not "AI" in general.

## Writing the policy in code

> **Hands-on:** This section turns the Nordlys decision into a layer of the demo app: a policy file, a generator for `robots.txt`, a sitemap, `noindex` headers and tests. If you don't write code, the short version is this: the four answers live in one small file, everything else is generated from it, and a test proves that each kind of crawler gets the answer we decided. Pick up again at "Checking claims: from user agent to signature".

The layer lives in `nordlys-cabins/layers/04-crawler-controls/` in the demos repository.[^ch04-26] It follows the layer contract from Chapter 2: it registers files and headers through hooks and never edits the shared app. It replaces the minimal `robots.txt` and `sitemap.xml` from Chapter 2.

The decision itself lives in `policy.js`: one answer per purpose (search, AI input, agents acting for a person, training), the private and transactional paths, and two experimental switches for the aipref lines, both off. It is the file a product manager can read and review in a pull request. Next to it sits `agents.js`, the vendor table from Table 4.1 as data, starting with `export const CHECKED = '2026-11-02'`, because a table like this is only as good as its date. A small generator, `robots.js`, turns the two into a `robots.txt`.

The generator writes three groups, each complete on its own, as the refresher demanded (Figure 4.2):

- The `*` group covers everyone without a group of their own: Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot and every other search crawler. Public pages are open, private and transactional paths are closed.
- The user-agent group lists the tokens with purpose `user` and opens the booking flow (`/book/`) to them, while keeping private paths closed. This is the group that keeps Claude-User working for a guest who asks it to book.
- The training group lists the training tokens and disallows everything, because the policy says `aiTrain: false`. If the policy said `true`, the group would disappear and training crawlers would fall back to the `*` group.

![Figure 4.2 — Which group each crawler reads. A crawler obeys the one group that names it, or the * group if none does. GPTBot reads the training group and is turned away, Claude-User reads the user-agent group and may open the booking form, and OAI-SearchBot and Googlebot fall back to the * group.](images/figure-4-2.png)

Every group repeats the signals, and the `Sitemap` line goes at the end. Listing 4.1 is the file it generates, real output from the demo:

**Listing 4.1** The generated `robots.txt` (output of the demo, upto Chapter 4)

```text
# robots.txt for Nordlys Cabins, generated from layers/04-crawler-controls/policy.js
# Content signals: https://contentsignals.org/

# Everyone else: search engines and AI search crawlers
User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=no
Allow: /
Disallow: /account/
Disallow: /bookings/
Disallow: /login
Disallow: /book/

# Assistants fetching pages for a person: the booking flow is open
User-agent: ChatGPT-User
User-agent: Claude-User
User-agent: Perplexity-User
User-agent: Amzn-User
User-agent: MistralAI-User
Content-Signal: search=yes, ai-input=yes, ai-train=no
Allow: /
Disallow: /account/
Disallow: /bookings/
Disallow: /login

# Training only: no
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
User-agent: MistralAI-Training
User-agent: Meta-ExternalAgent
Content-Signal: search=yes, ai-input=yes, ai-train=no
Disallow: /

Sitemap: https://nordlys.example/sitemap.xml
```

There is no separate group for AI search crawlers. Their rules are the same as for every other search crawler, so naming them would only add lines that can drift. isitagentready.com's `robotsTxtAiRules` check accepts this: it passes when the file names known AI bots "or" has wildcard rules that apply to all crawlers.[^ch04-16]

The sitemap lists every public page and adds `lastmod` only where the data actually knows a date: guide articles get their publication date, cabins get none. Google ignores `priority` and `changefreq`, and uses `lastmod` only when it is "consistently and verifiably" accurate.[^ch04-27] A sitemap that claims every page changed today trains crawlers to ignore its dates.

The layer registers both files per request, so the absolute URLs use the site's public origin, and sends `X-Robots-Tag: noindex` on private and transactional pages, which covers fetchers that skip `robots.txt` and still feed an index. The test in `nordlys-cabins/tests/ch04-crawler-controls.test.js` parses the served file with `robots-parser` 3.0.1, a widely used RFC 9309 parser on npm,[^ch04-28] and asks it the policy's questions per agent: may GPTBot read a cabin page, may Claude-User open the booking form, may anyone open `/account/`. All seven tests pass (Node.js 22.23.2, Hono 4.13.16, robots-parser 3.0.1 on 2 November 2026). What matters is that the test asks your *policy* questions, in your policy's words.

## Checking claims: from user agent to signature

Most automated traffic that reaches Nordlys never logs in, and many `User-Agent` headers say someone they are not. So there are three questions about every automated request. *Which software is this?* The user agent answers, and it costs nothing to fake. *Which operator runs it?* IP ranges, reverse DNS and signatures answer, with different strength. *Which person is behind it?* Only OAuth answers that, for your own users (Chapter 11). The Web Bot Auth working group left the end user out of its charter,[^ch04-29] and this half of the chapter is about the operator, the question that decides most of your bot policy.

### The user agent is a claim

Anyone can send any user agent — really, anyone. A scraper that wants to look respectable writes `GPTBot` or `Googlebot` into its header with one line of code, and the operators know it. Common Crawl warns site owners that it is "aware of crawlers falsely identifying themselves as CCBot".[^ch04-30] It works the other way too: an agent built into a browser runs in the person's own browser, so its requests carry that person's user agent, cookies and address.

So the user agent is good for one thing: sorting the traffic that is honest. If a request says `Claude-User`, it is probably Anthropic's user-triggered fetcher, and we can label it as a *claimed* agent. We should never give a claim more than we would give an anonymous visitor. That rule is the core of the Nordlys policy later in this chapter.

### Published IP ranges

OpenAI, Anthropic, Perplexity and Google publish the address ranges their crawlers and fetchers use, as small JSON files. OpenAI has one file per agent (`gptbot.json`, `searchbot.json`, `chatgpt-user.json` and one for its ad checker), Anthropic publishes `https://claude.com/crawling/bots.json`, Perplexity has `perplexitybot.json`, and Google has five files, from `common-crawlers.json` to `user-triggered-agents.json`.[^ch04-31][^ch04-32][^ch04-33][^ch04-34] If a request says `GPTBot` and comes from an address inside `gptbot.json`, it is very likely GPTBot. If it says `GPTBot` and comes from anywhere else, it is very likely lying.

The ranges have two weaknesses. They change often, so you have to download them on a schedule and keep the date with each copy (the log classifier from Chapter 2 does exactly that). And they are shared: a cloud browser service used by many people sends all of them from the same addresses.

### Reverse DNS, then forward DNS

Google documents an older method that needs no file at all. You look up the host name of the requesting address (reverse DNS), check that the name ends in one of Google's domains, then look up that name and check that it resolves back to the same address (forward DNS). In Google's words: "Verify that the domain name is either googlebot.com, google.com, or googleusercontent.com."[^ch04-34]

The second lookup is the important one. Whoever controls an IP address controls its reverse DNS record, so a scraper on its own server can make its address resolve to `crawl-1-2-3-4.googlebot.com`. It cannot make Google's DNS servers resolve that name back to its address. Only the round trip proves anything.

Reverse DNS costs two lookups for every new address, so you do it at the edge, or in middleware with a cache, and only for requests that claim to be Google. And please note: network checks tell you a request from `Google-Agent` really came from Google. They don't tell you it will follow your `robots.txt`, because Google says its user-triggered fetchers "generally ignore robots.txt rules".[^ch04-35]

### Web Bot Auth: a signature on every request

In simple words, Web Bot Auth lets an automated client sign each HTTP request with a private key and tell the site where to find the matching public key. A site that checks the signature knows which operator sent the request, whatever the user agent says and whichever network the request came from. It is the first identity mechanism for bots that does not depend on the bot's address.

The Web Bot Auth profile lives in one IETF working group draft, `draft-ietf-webbotauth-httpsig-protocol-01`, published on 29 October 2026 by Thibault Meunier (Cloudflare) and Sandor Major (Google).[^ch04-36] It merged two earlier individual drafts, one for the architecture and one for the key directory.[^ch04-37] Its requirements for a signature are short enough to quote almost in full:

- The signature must cover `@authority` or `@target-uri`, so it is bound to your site.
- `created` and `expires` are required, and "it is RECOMMENDED that expires be no more than 24 hours after created".
- `keyid` must be the JWK SHA-256 thumbprint of the key (RFC 7638, and RFC 8037 for Ed25519 keys).
- `tag` must be `web-bot-auth`.

It also defines a new header, `Signature-Agent`. Its value is a dictionary whose members are HTTPS URLs, one per signature label, and the URL says who signed. The keys for that URL live in a key directory, a JSON Web Key Set served with the media type `application/http-message-signatures-directory+json`, usually at `/.well-known/http-message-signatures-directory` on the agent's own domain.[^ch04-36] The `Signature-Agent` header is itself covered by the signature, so nobody can swap the URL without breaking it.

Listing 4.2 shows a signed request from the test agent we build later in this chapter. It is real output from my run, with the agent's directory on a local port.

**Listing 4.2** A request signed with Web Bot Auth (output of `chapters/15-signing-agent/signer.mjs`)

```http
GET /cabins HTTP/1.1
Host: 127.0.0.1:3015
User-Agent: NordlysTestAgent/1.0
Signature-Agent: sig1="http://127.0.0.1:8977"
Signature-Input: sig1=("@authority" "@method" "@path" "signature-agent";key="sig1");created=1793659269;expires=1793659569;keyid="-LKDDMS1ZfRUbOdIYm8NJfZLEvt2pUgsY-kHzKDrIpw";alg="ed25519";nonce="2kyD1ao2/jRJ6dZyuMQZUEjxbvFdH1hsc3AAGpBaj0c=";tag="web-bot-auth"
Signature: sig1=:wDsjolQasBzTvl0nSqjAuNt+LTKWkSxHxJqSQTBZu3tmsNR1w5Q4kJ2EbXQHHpjiO2LGAedrenKsan8j5bDtDA==:
```

`Signature-Agent` names the agent (a local test address here, which is why it is not HTTPS). `Signature-Input` says that the signature labelled `sig1` covers the authority, the method, the path and the `sig1` member of `Signature-Agent`, and expires five minutes after it was created. The `nonce` is a random value so that two signatures are never identical. Figure 4.3 shows how a verifier turns those three headers into an answer.

![Figure 4.3 — Anatomy of a Web Bot Auth check. The verifier rebuilds the signature base from the covered components of the request, finds the agent URL in Signature-Agent, fetches that agent's key directory (only for agents on its allowlist, and cached), picks the key whose thumbprint equals keyid, and verifies the Ed25519 signature. The result is a label for the request.](images/figure-4-3.png)

### What a signature proves, and what it does not

This is the part I'd ask every security person and product manager on the team to read, because a signature is easy to overestimate.

A valid signature proves that whoever controls the URL in `Signature-Agent` published the key that signed this request. The draft is careful about this: resolving the URL "establishes that the host named in the URL served this key set at fetch time", and that is "all it gives you". It "does not say that the operator of that URL is honest, or that it is the same party everyone knows about".[^ch04-36] So a valid signature from `https://chatgpt.com` is strong evidence, because you know who runs `chatgpt.com`. A valid signature from `https://totally-legit-agent.example` proves only that someone owns that domain.

Two more limits matter in practice. A signature names an operator, and only that: a signed request from an agent service used by thousands of people tells you which service, not which of its users, which Cloudflare's bot directory calls "transitive trust".[^ch04-38] And a signature that covers only `@authority` can be replayed against any path until it expires,[^ch04-36] so short lifetimes and covering `@method` and `@path` matter.

Bottomline: a verified signature is the best answer to "which operator sent this?" that the web has today. Whether to trust what the request *asks for* is a different question, and the Nordlys code below never confuses the two.

> **Still in flux:** Web Bot Auth is still a working group draft, its charter milestones have passed without a submission, and header details changed between drafts: `Signature-Agent` was a plain string before it became a dictionary, and deployments still send the old form.[^ch04-29][^ch04-36] Pin the draft number in your code comments, accept both forms, and keep all signature handling in one module.

### Who signs today

As of November 2026 the list of signers is short, but it includes the agents most likely to visit a booking site. OpenAI signs requests from ChatGPT agent, with a key directory at `https://chatgpt.com/.well-known/http-message-signatures-directory` that held one Ed25519 key when I fetched it on 2 November 2026.[^ch04-39] Google calls its support experimental: "a subset of requests made by the Google-Agent are signed with Web Bot Auth", with `Signature-Agent: g="https://agent.bot.goog"`, and "We don't sign every request of a particular agent. Be sure that you fall back to the established methods of bot verification."[^ch04-40] Visa's Trusted Agent Protocol and Mastercard's Agent Pay use it as their agent authentication layer.[^ch04-41][^ch04-42]

The verifying side is broader, because CDNs and firewalls did the work for their customers. Cloudflare folded signed agents into its Verified bots on 1 July 2026, AWS WAF Bot Control added Web Bot Auth support on 21 November 2025, and Vercel's bot management verifies bots by reverse DNS and Web Bot Auth.[^ch04-43][^ch04-44][^ch04-45] On Radar, 118 of the 115,468 top domains (0.10%) publish a key directory on 2 November 2026.[^ch04-46] Please read that number correctly: a directory is something you publish when *you send* signed requests. It measures operators of bots, not sites that verify them.

### Verify, don't sign

Web Bot Auth has two sides, and most websites only ever need one of them. *Signing* is for whoever sends automated requests. If Nordlys ran a bot that checked competitor prices, it would sign. It doesn't, so it won't, and isitagentready.com agrees: its Web Bot Auth check is informational, and "Failures are shown as neutral and do not affect the score".[^ch04-47] *Verifying* is for whoever receives them, which is every website, and there are three ways to do it:

Let your edge do it, if your site is behind Cloudflare, AWS WAF, Vercel or another provider that verifies signed agents, and write rules that use the result. Use a library, such as Cloudflare's Apache-licensed reference implementation (npm package `web-bot-auth`, version 0.2.0 when I checked), and check which draft it follows.[^ch04-48] Or write a small verifier, which is a few hundred lines with your platform's crypto library. That is what we do for Nordlys, because it lets us see every step.

## Hands-on: verifying signed agents in Nordlys Cabins

> **Hands-on:** This section builds layer `15-bot-identity` in the demo app: a Web Bot Auth verifier with no dependencies, an optional DNS check for Google's crawlers, a label for every request and rate limits per class. The demos keep the first edition's layer numbers, so `--upto=15` also turns on layers 5 to 14 (the table in "About this book" maps them to this edition's chapters). If you don't write code, read the next paragraph for the policy, look at Figure 4.4, and pick up again at "Rate limits that explain themselves".

The policy for Nordlys is simple, and I'd suggest something similar for most small sites. Every request gets exactly one label from the strongest evidence it carries. Nobody is blocked because of a label. The label only decides which rate-limit bucket a request counts against on the agent-facing endpoints (`/mcp` and the booking-session API under `/ucp/`), and what we write into the log for Chapter 12.

| Label | Evidence | Rate limit on agent endpoints |
| --- | --- | --- |
| `verified-agent` | a valid Web Bot Auth signature from an allowlisted agent | 300 requests per minute per agent |
| `verified-network` | an unsigned request whose Google claim passed reverse and forward DNS | 120 per minute per crawler |
| `invalid-signature` | a signature that is present but does not verify | 60 per minute per address |
| `claimed-agent` | a known user agent token, nothing more | 60 per minute per address |
| `unidentified` | nothing | 60 per minute per address |

An invalid signature gets *no* penalty beyond the anonymous limit, because a broken signature is more often a clock or a proxy problem than an attack, but we log it.[^ch04-36] And the limits are per *bucket*: a verified agent shares one bucket named after the agent, while anonymous requests get one bucket per address. That is the whole reward for signing: a verified agent is no longer mixed up with every other client on the same cloud address.

![Figure 4.4 — The Nordlys bot identity layer. A signed request is verified against the agent's key directory. An unsigned request that claims to be Google can be confirmed by reverse and forward DNS. Every request gets one label, the label picks a rate-limit bucket on /mcp and /ucp/, and every response from those endpoints says where the client stands in RateLimit headers.](images/figure-4-4.png)

### One label per request

Listing 4.3 is the policy in code. It takes the result of the signature check, the user agent and the result of the DNS check, and returns one label. The order of the `if` statements *is* the evidence ladder: a signature beats a confirmed network, which beats a claim.

**Listing 4.3** `nordlys-cabins/layers/15-bot-identity/identity.js` — one label per request, and the rate-limit bucket for it

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

The verifier itself, `verify.js`, implements the draft's validation rules and nothing more. It never throws, so a broken header cannot break a page. It looks the key up in *this agent's* directory, never in a global pool, because "Key lookup MUST be keyed on the (URL, key) pair, not on the key alone".[^ch04-36] It computes the thumbprint itself, because Google's directory uses short `kid` values that are not thumbprints.[^ch04-49] And its tests check the signature base against the test vectors in RFC 9421 appendix B.2.6 and the draft's appendix E.2.

### Fetching keys safely

To verify, our server fetches the agent's public keys from a URL that a stranger put in a header. That is a textbook server-side request forgery (SSRF) risk, and the draft lists the precautions.[^ch04-36] The first line of defence is the allowlist: Nordlys fetches keys only for agents it decided to trust (`https://chatgpt.com` and `https://agent.bot.goog` by default, plus anything in the `NORDLYS_WBA_TRUST` setting), and a signature from any other agent comes back as `invalid` without the server ever contacting that URL. The rest follows the draft: HTTPS only, no redirects, five seconds at most, 64 KB at most, 16 keys at most, directories cached for five minutes to a day and failures for one minute. For unsigned requests that claim to be `Googlebot` or `Google-Agent`, the layer can also run the reverse-then-forward DNS check (`NORDLYS_RDNS=1`).

## Rate limits that explain themselves

A `429 Too Many Requests` with no explanation is the most common way sites talk to bots, and the least useful one. An agent that hits it has to guess when to come back, and a polite agent backs off far more than it needs to. There is a better way, and it is close to standard.

The IETF HTTPAPI working group's draft `draft-ietf-httpapi-ratelimit-headers-11` (May 2026) defines two response headers.[^ch04-50] `RateLimit-Policy` describes a quota: `"anonymous";q=60;w=60` means 60 requests in a 60-second window. `RateLimit` says where this client stands right now: `"anonymous";r=59;t=60` means 59 requests remain and the window resets in 60 seconds. With `Retry-After` on the `429`, even clients that don't know the draft can do the right thing. It is a draft, but the cost is two headers, and the benefit is agents that stop guessing.

The Nordlys limiter in `ratelimit.js` is a fixed window per bucket, the simplest algorithm that works, and it returns the headers with every decision. An unsigned request to the booking-session API that only *claims* to be ChatGPT shows them (Listing 4.4).

**Listing 4.4** An unsigned request to `/ucp/` that claims to be ChatGPT-User (response headers, shortened)

```http
HTTP/1.1 404 Not Found
content-type: application/json
ratelimit: "anonymous";r=59;t=60
ratelimit-policy: "anonymous";q=60;w=60
x-nordlys-bot-identity: claimed-agent
```

A fixed window in memory is fine for one server. With several servers, keep the counters in a shared store. And the limit applies only on the two agent-facing endpoints, because a person browsing cabins should never meet a `429` from us.

The tests in `nordlys-cabins/tests/ch15-bot-identity.test.js` sign requests with a small test agent from `chapters/15-signing-agent/`, tamper with them (another path, an expired signature, an unknown key, an agent that is not on the allowlist) and expect `invalid` every time, never `verified`. They also check that the 61st anonymous request in a minute gets a `429` with `Retry-After` while a verified agent still gets through. On Node.js 24.22.1 all 13 tests pass.

## What the graders see

Let's measure, as we do after every layer. Table 4.3 shows the checks that the crawler-controls layer touches, before (the site after Chapter 3) and after.

**Table 4.3** Nordlys Cabins before and after the crawler-controls layer

| Grader and check | After Chapter 3 | After Chapter 4 | Why |
| --- | --- | --- | --- |
| isitagentready `robotsTxt` | pass | pass | Chapter 2 already served a valid file |
| isitagentready `sitemap` | pass | pass | Now with real `lastmod` for the guide |
| isitagentready `robotsTxtAiRules` | pass | pass | It passed on the `User-agent: *` rule alone |
| isitagentready `contentSignals` | fail | pass | The `Content-Signal` line |
| isitagentready level | 1 (Basic Web Presence) | 2 (Bot-Aware) | Level 2 = Level 1 plus AI bot rules plus Content Signals |
| Lighthouse SEO `robots-txt` | pass | pass | `content-signal` is on the safelist |
| Lighthouse Agentic Browsing | no change | no change | No audit in that category reads `robots.txt` rules |

The level went up by one, and all of it came from one line that a single vendor defined. Meanwhile the decision that actually matters for Nordlys's business, the separate group that keeps the booking flow open to assistants acting for a guest, moved no check at all. Track the level, but review the policy.

The bot identity layer moves nothing, and that is correct. isitagentready.com's `webBotAuth` check looks for a key directory, which a site publishes only when it signs.[^ch04-47] If you don't send automated traffic, leave it neutral.

## Summary

- Most AI crawling is for training (Radar, seven days to 2 November 2026), while user-triggered fetches are small in volume and high in value. "Block AI" or "allow AI" is the wrong unit of decision. The right unit is the purpose.
- Answer four questions before touching a file (search, AI answers, agents acting for a person, training), with your own logs open. For most commercial sites the first three are "yes".
- `robots.txt` (RFC 9309) is a request, not access control. Each group must be complete, and errors change the policy.
- Vendors document their tokens per purpose. Control tokens like Google-Extended never crawl, and most user-triggered fetchers may ignore `robots.txt`, while Claude-User honours it.
- Content Signals states search, AI-input and training preferences in one line. It is widely deployed but not a standard, and isitagentready.com requires it for Level 2. The IETF aipref drafts are still in flux, and Google's real controls for AI features are `nosnippet` and a Search Console toggle.
- A user agent is a claim. Published IP ranges and reverse-then-forward DNS confirm the big operators by network. A Web Bot Auth signature (RFC 9421 plus a key directory) proves which operator sent a request, not which person, and only for keys you chose to trust.
- Most sites should verify, not sign. Nordlys gives every request one label from the strongest evidence, blocks nobody for it, and uses it to pick a rate-limit bucket that explains itself in `RateLimit` headers.
- Enforcement belongs at the edge and in authentication. Pay per crawl, TDMRep and licensing are in Appendix C.

[^ch04-1]: "AI Insights," Cloudflare Radar, https://radar.cloudflare.com/ai-insights (data for 26 October to 2 November 2026, including the "Adoption of AI agent standards" widget, retrieved November 2026).
[^ch04-2]: M. Koster, G. Illyes, H. Zeller, L. Sassman, "RFC 9309: Robots Exclusion Protocol," RFC Editor, September 2022, https://www.rfc-editor.org/rfc/rfc9309.html (retrieved November 2026).
[^ch04-3]: "How Google interprets the robots.txt specification," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt (retrieved November 2026).
[^ch04-4]: "Overview of OpenAI crawlers," OpenAI Platform documentation, https://platform.openai.com/docs/bots (retrieved November 2026).
[^ch04-5]: "Does Anthropic crawl data from the web, and how can site owners block the crawler?," Anthropic Help Center, https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler (retrieved November 2026).
[^ch04-6]: "Google's common crawlers," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers (page updated 30 October 2026, retrieved November 2026).
[^ch04-7]: "About Applebot," Apple Support, https://support.apple.com/en-us/119829 (retrieved November 2026).
[^ch04-8]: "CCBot," Common Crawl, https://commoncrawl.org/ccbot (retrieved November 2026).
[^ch04-9]: "Meta Web Crawlers," Meta for Developers, https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers (the page did not load for us on 2 November 2026, so the purposes come from a search engine's snippet of the page and are unverified, retrieved November 2026).
[^ch04-10]: "Amazon Web Search crawlers," Amazon Developer, https://developer.amazon.com/amazonbot (retrieved November 2026).
[^ch04-11]: "Perplexity Crawlers," Perplexity documentation, https://docs.perplexity.ai/guides/bots (retrieved November 2026).
[^ch04-12]: "Google's user-triggered fetchers," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers (retrieved November 2026).
[^ch04-13]: "Giving users choice with Cloudflare's new Content Signals Policy," The Cloudflare Blog, 24 September 2025, https://blog.cloudflare.com/content-signals-policy/ (retrieved November 2026).
[^ch04-14]: André Jesus and Vance Morrison, "Introducing the Agent Readiness score. Is your site agent-ready?," The Cloudflare Blog, 17 April 2026, https://blog.cloudflare.com/agent-readiness/ (retrieved November 2026).
[^ch04-15]: M. Tremante, L. Romm, "Vocabulary For Expressing Content Signals," draft-romm-aipref-contentsignals-00, IETF Datatracker, https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ (retrieved November 2026).
[^ch04-16]: "isitagentready.com: full reference," Cloudflare, https://isitagentready.com/llms-full.txt (retrieved November 2026).
[^ch04-17]: "AI Preferences (aipref) documents," IETF Datatracker, https://datatracker.ietf.org/wg/aipref/documents/ (retrieved November 2026).
[^ch04-18]: P. Keller, M. Thomson, "A Vocabulary For Expressing AI Usage Preferences," draft-ietf-aipref-vocab-08, 14 September 2026, https://www.ietf.org/archive/id/draft-ietf-aipref-vocab-08.txt (retrieved November 2026).
[^ch04-19]: G. Illyes, M. Thomson, "Associating AI Usage Preferences with Content in HTTP," draft-ietf-aipref-attach-05, 19 August 2026, https://www.ietf.org/archive/id/draft-ietf-aipref-attach-05.txt (retrieved November 2026).
[^ch04-20]: K. Kelley, "Machine-Readable Training Preference Signal," draft-kelley-aipref-training-preference-signal-00, 30 October 2026, IETF Datatracker, https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/ (retrieved November 2026).
[^ch04-21]: Lighthouse 13.6.0 source, `core/audits/seo/robots-txt.js`, GitHub, https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/seo/robots-txt.js (read in the npm package lighthouse@13.6.0, retrieved November 2026).
[^ch04-22]: "Robots meta tag, data-nosnippet, and X-Robots-Tag specifications," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag (retrieved November 2026).
[^ch04-23]: "New controls for website owners in Search," Google The Keyword, https://blog.google/products-and-platforms/products/search/new-controls-website-owners/ (retrieved November 2026).
[^ch04-24]: "AI Crawl Control," Cloudflare documentation, https://developers.cloudflare.com/ai-crawl-control/, and "Analyze AI traffic," https://developers.cloudflare.com/ai-crawl-control/features/analyze-ai-traffic/ (retrieved November 2026).
[^ch04-25]: "Bot Management," Vercel documentation, https://vercel.com/docs/bot-management (page updated 10 September 2026, retrieved November 2026).
[^ch04-26]: Demos repository, `nordlys-cabins/layers/04-crawler-controls/`, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch04-27]: "Build and submit a sitemap," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (retrieved November 2026).
[^ch04-28]: "robots-parser" 3.0.1, npm, https://www.npmjs.com/package/robots-parser (retrieved November 2026).
[^ch04-29]: "Web and Internet Transport Bot Authentication (webbotauth): About", IETF Datatracker, https://datatracker.ietf.org/wg/webbotauth/about/ (retrieved November 2026).
[^ch04-30]: "CCBot", Common Crawl, https://commoncrawl.org/ccbot (retrieved November 2026).
[^ch04-31]: "Overview of OpenAI Crawlers", OpenAI Platform documentation, https://platform.openai.com/docs/bots (retrieved November 2026).
[^ch04-32]: "Does Anthropic crawl data from the web, and how can site owners block the crawler?", Claude Help Center, https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler (retrieved November 2026).
[^ch04-33]: "Perplexity Crawlers", Perplexity documentation, https://docs.perplexity.ai/docs/resources/perplexity-crawlers (retrieved November 2026).
[^ch04-34]: "Verifying Google requests", Google Crawling Infrastructure, https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests (retrieved November 2026).
[^ch04-35]: "Google user-triggered fetchers", Google Crawling Infrastructure, https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers (retrieved November 2026).
[^ch04-36]: T. Meunier, S. Major, "HTTP Message Signatures for automated traffic", draft-ietf-webbotauth-httpsig-protocol-01, 29 October 2026, IETF, https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt, sections 4.4, 5.2, 5.2.1, 5.2.3, 5.4, 5.5.1, 6.7, 6.11 and appendix C (retrieved November 2026).
[^ch04-37]: "webbotauth: Documents", IETF Datatracker, https://datatracker.ietf.org/wg/webbotauth/documents/ (retrieved November 2026).
[^ch04-38]: "Signed agents", Cloudflare Bots documentation, https://developers.cloudflare.com/bots/concepts/bot/signed-agents/ (retrieved November 2026).
[^ch04-39]: OpenAI key directory, https://chatgpt.com/.well-known/http-message-signatures-directory, fetched on 2 November 2026 (retrieved November 2026).
[^ch04-40]: "Google's Guide to Authenticating Requests with Web Bot Auth (Experimental)", Google Crawling Infrastructure, https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth (retrieved November 2026).
[^ch04-41]: "Getting Started - Trusted Agent Protocol", Visa Developer, https://developer.visa.com/docs/trusted-agent-protocol (retrieved November 2026).
[^ch04-42]: "Helping AI agents transact with Visa and Mastercard", The Cloudflare Blog, 24 October 2025, https://blog.cloudflare.com/secure-agentic-commerce (retrieved November 2026).
[^ch04-43]: "Verified bots", Cloudflare Bots documentation, https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ (retrieved November 2026).
[^ch04-44]: "AWS WAF announces Web Bot Auth support", AWS What's New, 21 November 2025, https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/ (retrieved November 2026).
[^ch04-45]: "Bot Management", Vercel documentation, https://vercel.com/docs/bot-management (retrieved November 2026).
[^ch04-46]: "AI Insights: Adoption of AI agent standards" and "AI Insights", Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards, data dated 2 November 2026 (retrieved November 2026).
[^ch04-47]: "llms-full.txt", isitagentready.com, https://isitagentready.com/llms-full.txt, Bot Access Control checks and "Levels" (retrieved November 2026).
[^ch04-48]: "web-bot-auth", Cloudflare on GitHub, https://github.com/cloudflare/web-bot-auth (retrieved November 2026).
[^ch04-49]: Google agent key directory, https://agent.bot.goog/.well-known/http-message-signatures-directory, fetched on 2 November 2026 (retrieved November 2026).
[^ch04-50]: R. Polli et al., "RateLimit header fields for HTTP", draft-ietf-httpapi-ratelimit-headers-11, May 2026, https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ (retrieved November 2026).
