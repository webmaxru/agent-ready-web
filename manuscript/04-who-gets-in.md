# Chapter 4: Who gets in: robots.txt, AI crawlers and content signals

This chapter covers

- The three kinds of automated visitors that arrive from AI companies, and why each one needs its own answer
- Turning a business decision about AI into a policy that product, legal, content and engineering agree on
- Writing that policy into `robots.txt` with groups per purpose, Content Signals and a sitemap
- The IETF AI Preferences drafts, TDMRep and Google's own controls for AI features, with their status as of November 2026
- Where `robots.txt` stops and enforcement at the CDN or in your code begins
- Testing the policy in CI and watching which grader checks it moves

Part 1 was about the page itself: how an agent perceives it, and how a few honest fixes in HTML make it usable. Part 2 steps back to the front door. Before an agent can read your cabin descriptions or book anything, it has to arrive, and before it arrives someone at your company has (or hasn't) decided whether it is welcome.

Most teams never made that decision on purpose. The `robots.txt` file was written years ago by whoever set up the site, it says `Allow: /` to everyone, and it has not been touched since. Then, sometime in 2024 or 2025, a headline about AI training made someone nervous, and a block of `Disallow: /` lines for "the AI bots" appeared at the bottom. Sometimes that block also locks out the very assistants that send customers. Honestly, I don't blame anyone: the vocabulary for talking about this became clear only quite recently, when the vendors started to document their crawlers per purpose.

This chapter gives you that vocabulary. We start with who actually visits (with numbers), turn that into four decisions a team can make in one meeting, and then write the result into files: a `robots.txt` with groups per purpose, the Content Signals line that one of our two graders requires for Level 2, and a sitemap with honest dates. Along the way we look at the standards work that is still moving (the IETF AI Preferences drafts) and at the controls Google offers for its own AI features, which are not the ones most people think. At the end, Nordlys Cabins has a policy in code, tested with a real parser, and isitagentready.com's level goes from 1 to 2.

This is a policy chapter as much as a technical one. Product managers, legal, content and SEO people decide here, and developers implement. The code sections are marked, and you can skip them without losing the thread.

## Who knocks on the door

Let's start with data rather than opinions. Cloudflare Radar publishes AI crawler traffic for its network, and the "crawl purpose" chart is the most useful single picture I know of what arrives at a website from AI companies. For the seven days ending 2 November 2026, Radar classified AI crawler traffic like this: 41.4% for training, 41.3% for mixed training and search, 12.3% for search, 3.7% for user actions and 1.3% undeclared.[^ch04-1]

Two things stand out. First, most AI crawling is about training models, either purely or mixed with search. Second, the slice that most directly represents a person using an assistant right now ("user action") is small in volume. Small in volume does not mean small in value, of course. A single request from an assistant that a traveller just asked "find me a cabin with a sauna in Lofoten for the first week of March" can be worth more to Nordlys than ten thousand training fetches.

Radar also shows what this traffic gives back. Its crawl-to-refer ratio divides the HTML requests from a platform's crawlers by the requests that arrive with a referrer from that platform. In the same week, the ratios were roughly 4,900 to 1 for Perplexity, 1,400 to 1 for OpenAI, 541 to 1 for Anthropic and 4.8 to 1 for Google.[^ch04-1] These numbers swing a lot from week to week (Perplexity's moved by about 25% in that single week), so please treat them as an order of magnitude and always quote them with a date. The direction is clear, though: for most AI platforms, many pages are read for every visitor sent back.

And sites are reacting. Sixteen percent of all responses that Radar saw going to AI bots in that week were `403 Forbidden`.[^ch04-1] Among the top 10,000 domains, Radar found 4,387 `robots.txt` files, and 708 of them disallow OpenAI's training crawler, GPTBot, at least partly (509 of them completely).[^ch04-1] So a lot of websites are already making some decision. The question is whether it is the decision they meant.

### Three kinds of visitors

The vendors' own documentation now splits their automated traffic by purpose, and that split is the key to everything in this chapter. In simple words, there are three kinds of visitors:

- **Training crawlers** collect content to train or fine-tune models. GPTBot (OpenAI), ClaudeBot (Anthropic) and CCBot (Common Crawl, a dataset many models are trained on) are examples.
- **Search crawlers** build an index that an AI product (or a classic search engine) uses to answer questions and link back to sources. OAI-SearchBot, Claude-SearchBot and PerplexityBot belong here, and so does Googlebot, because Google's AI Overviews and AI Mode are built on normal Search crawling.
- **User-triggered fetchers and agents** fetch a page because one person asked an assistant to, right now. ChatGPT-User, Claude-User, Perplexity-User and Google-Agent are examples. Browsing agents that read and click in a real browser (Chapter 3) are the same idea in a different form.

Each kind costs you something different and gives back something different. Training gives back little that you can measure. Search can send visitors and citations. User-triggered fetches are, quite literally, customers using a different interface. That is why "block AI" or "allow AI" is the wrong unit of decision. The right unit is the purpose.

> **Note:** A fourth kind, browsing agents that drive a real browser on the user's device (Claude in Chrome, Gemini in Chrome, Comet and similar), usually arrives with the browser's normal user agent string. `robots.txt` does not see them as anything special. Chapters 3 and 9 cover how they perceive and act on your pages, and Chapter 15 covers how agents can prove who they are.

## Four decisions before any file

Here is the framework I suggest. Before anybody edits a file, the people who own the business answer four questions, one per purpose (Figure 4.1):

1. **Search.** Do we want to appear in classic search results and in AI search indexes that link back to us?
2. **AI answers.** May our content be used as input for AI-generated answers (grounding, retrieval-augmented generation, summaries in an assistant), assuming the answer cites us?
3. **Agents acting for a person.** May an assistant fetch and use our pages, including transactional ones, when a user asks it to?
4. **Training.** May our content be used to train or fine-tune generative AI models?

![Figure 4.1 — Four purposes, four decisions. Each kind of automated visitor maps to one business question, and each answer maps to a different control: robots.txt groups for crawlers, Content Signals for usage, Google's own settings for its AI features, and authentication for anything private.](images/figure-4-1.png)

For most commercial sites, the first three answers are "yes". A booking site, a shop or a SaaS product wants to be found, quoted and used. The fourth answer is where companies genuinely differ. A news publisher whose business is the text itself may say no to training and also restrict AI answers. A documentation site for a developer tool may say yes to everything, because the more models know about its API, the easier its product is to adopt. A small booking site may not care much either way, or may say no on principle.

### Who decides what

This is also a question of who sits in the meeting. Very often the developer who owns the server ends up editing `robots.txt`, but almost none of these questions are technical. Table 4.1 is the split that works for most teams.

**Table 4.1** Who owns which part of the access policy

| Role | Owns |
| --- | --- |
| Product manager | The four answers, and the trade-off between reach and control |
| Legal | Whether a training "no" needs a formal reservation of rights (EU text-and-data-mining law, licence terms), and what the policy page says |
| Content and SEO | Which sections are public, which pages must stay out of search, Google's AI feature settings in Search Console |
| Developers and platform | The files, the headers, the CDN rules and the tests |
| Security | Making sure nothing private relies on `robots.txt` |
| Analytics | Measuring what each kind of visitor actually brings, so the answers can be revisited |

The last row matters more than it seems. These answers are not forever. If Chapter 19's numbers show that an AI search platform sends real bookings, the team may want to be more open there. If a training crawler turns out to hammer the site, a stricter rule at the CDN may be needed.

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

Three details from the RFC and from Google's documentation cause most of the surprises I see:

- **One group per crawler.** A crawler that has its own group ignores the `*` group completely. If you write rules for `*` and then add a group for GPTBot with a single `Disallow: /private/` line, GPTBot is now allowed everywhere else, including paths you disallowed for `*`. Every group has to be complete on its own.
- **Errors mean something.** Google treats a `4xx` response for `robots.txt` (except `429`) as "no restrictions" and a `5xx` as a reason to stop crawling the site for 12 hours. It caches the file for up to 24 hours and enforces a 500 KiB size limit, the minimum the RFC requires parsers to handle.[^ch04-3] A broken deploy that turns `robots.txt` into an error page can quietly change your policy for a day.
- **Disallow is not noindex.** A crawler that may not fetch a page cannot see a `noindex` instruction on it. A disallowed URL can still appear in an index (without content) if other pages link to it. To keep a page out of search results, let crawlers fetch it and send `noindex`, or protect it with authentication.

And the most important sentence in the whole RFC, quoted exactly: "These rules are not a form of access authorization."[^ch04-2] `robots.txt` is a request. Well-behaved crawlers honour it, and the vendors in the next section document that they do. Anything else is free to ignore it, and some kinds of agents ignore it on purpose. We come back to that in "Beyond the polite request".

> **Tip:** Keep the file small, serve it with `200 OK` and `text/plain`, and test it in CI like any other contract. isitagentready.com's `robotsTxt` check fails on anything else: it wants a `200` response, `text/plain` and at least one `User-agent` line.


## Who is who: the AI user agents

Now the part that changes fastest. Each major AI vendor publishes a page listing its crawlers and fetchers, what each one is for and how it treats `robots.txt`. Table 4.2 summarises those pages as I read them on 2 November 2026. Please read it as a dated snapshot: tokens are added, renamed and retired, and the vendor pages are the source of truth.

**Table 4.2** AI user agents and control tokens by purpose, as documented by their vendors (checked 2 November 2026)

| Token | Vendor | Purpose | What the vendor says about robots.txt |
| --- | --- | --- | --- |
| GPTBot | OpenAI | Training | Honours it[^ch04-4] |
| ClaudeBot | Anthropic | Training | Honours it[^ch04-5] |
| Google-Extended | Google | Training and grounding for Gemini (not Search) | A control token with no crawler of its own[^ch04-6] |
| Applebot-Extended | Apple | Training Apple's models | A control token, "does not crawl webpages"[^ch04-7] |
| CCBot | Common Crawl | Public dataset, widely used for training | Honours it, and warns about spoofed CCBot user agents[^ch04-8] |
| MistralAI-Training | Mistral AI | Training | "Webmasters can disallow this user agent"[^ch04-9] |
| Meta-ExternalAgent | Meta | Training and indexing | Documented on a page we could not load (unverified)[^ch04-10] |
| Amazonbot | Amazon | Mixed: may train Amazon models and improve Amazon products | Honours it, using a cached copy up to 30 days old[^ch04-11] |
| OAI-SearchBot | OpenAI | Search in ChatGPT | Honours it[^ch04-4] |
| Claude-SearchBot | Anthropic | Search quality | Honours it[^ch04-5] |
| PerplexityBot | Perplexity | Search index, "not used to crawl content for AI foundation models" | Honours it[^ch04-12] |
| Amzn-SearchBot | Amazon | Search (for example Alexa), not training | Honours it[^ch04-11] |
| MistralAI-Index | Mistral AI | Search index, not training | Listed as a robots.txt tag[^ch04-9] |
| Googlebot | Google | Search, including AI Overviews and AI Mode | Honours it[^ch04-6] |
| ChatGPT-User | OpenAI | Fetches for a user's request | "robots.txt rules may not apply"[^ch04-4] |
| Claude-User | Anthropic | Fetches for a user's request | Honours it[^ch04-5] |
| Perplexity-User | Perplexity | Fetches for a user's request | "generally ignores robots.txt rules"[^ch04-12] |
| Google-Agent and other user-triggered fetchers | Google | Fetches and actions for a user's request | "generally ignore robots.txt rules"[^ch04-13] |
| Amzn-User | Amazon | Fetches for a user's request | "may not follow all robots.txt directives"[^ch04-11] |
| MistralAI-User | Mistral AI | Fetches for a user in Mistral's assistant | The token "governs which sites these user requests can be made to"[^ch04-9] |

Some rows deserve a comment.

**Control tokens are not crawlers.** Google-Extended and Applebot-Extended never appear in your access logs. They exist only as names in `robots.txt`: Google's crawlers and Apple's crawlers fetch the page under their normal names, and the vendor checks whether you disallowed the `-Extended` token before using the content for model training (and, for Google, for grounding answers in Gemini apps). Google says it plainly: Google-Extended "does not impact a site's inclusion in Google Search nor is it used as a ranking signal in Google Search."[^ch04-6] So blocking Google-Extended does *not* take you out of AI Overviews. We come back to Google's real controls for that below.

**Mixed purposes are a trade-off.** Amazon says Amazonbot "is used to improve our products and services" and "may be used to train Amazon AI models", with Amzn-SearchBot as the separate search crawler.[^ch04-11] Blocking Amazonbot says no to training and to whatever else "improve our products" covers, in one line. When one token covers two purposes you care about differently, you have to choose, and the choice belongs in the policy document.

**User-triggered fetchers mostly don't ask.** This is the row that surprises people. OpenAI, Perplexity, Google and Amazon all document that their user-triggered fetchers may ignore `robots.txt`, and the reasoning is the same everywhere: a person asked for this page, so the fetcher acts like that person's browser. Anthropic is the clearest exception (Mistral's MistralAI-User token also "governs which sites these user requests can be made to"). Anthropic says all three of its bots, including Claude-User, honour `robots.txt`, and that disabling Claude-User "prevents our system from retrieving your content in response to a user query."[^ch04-5] Read this the other way round: if your `robots.txt` blocks everything that looks like AI, the one assistant that actually listens to you is the one you have locked out of your booking pages.

**Some bots are undocumented.** ByteDance's Bytespider has no official documentation that I could find, and community sources report it as non-compliant. For such crawlers `robots.txt` is a wish, and enforcement (later in this chapter) is the only real tool.

**Old names linger.** Tokens get retired, and `robots.txt` files keep them for years. For example, on 2 November 2026 the `robots.txt` of www.cloudflare.com still listed `Anthropic-AI` and `Claude-Web`,[^ch04-14] neither of which appears on Anthropic's current page (ClaudeBot, Claude-User and Claude-SearchBot). A rule for a name that no crawler uses does nothing. If you don't want to track vendor pages by hand, the community-maintained ai.robots.txt list on GitHub collects AI user agents in one place, with a ready-made `robots.txt` and server configs.[^ch04-15] It blocks rather than classifies, so take the names from it and the purposes from the vendors.

> **Warning:** A user agent string is a claim, not an identity. Anyone can send `User-Agent: GPTBot`. OpenAI, Anthropic, Perplexity and Google publish the IP ranges of their crawlers as JSON files, and some agents now sign their requests cryptographically (Web Bot Auth). Chapter 15 shows how to verify both. In this chapter, the user agent is only used to choose which `robots.txt` group applies, which is exactly what it was designed for.


## Content Signals: saying what your content may be used for

`robots.txt` answers one question: may this crawler fetch this path? It says nothing about what happens to the content afterwards. A search crawler that fetched your page could, in principle, feed it to a model. For years the only way to say "index me, but don't train on me" was to know which token each vendor uses for which purpose, as in Table 4.2.

In September 2025 Cloudflare proposed a more direct way, the Content Signals Policy.[^ch04-16] It adds one line to `robots.txt` that states your preference for three uses:

- `search`: building a search index and providing search results, meaning hyperlinks and short excerpts. Search, in this definition, "does not include providing AI-generated search summaries."
- `ai-input`: "inputting content into one or more AI models (e.g., retrieval augmented generation, grounding, or other real-time taking of content for generative AI search answers)."
- `ai-train`: training or fine-tuning AI models.

Each signal is `yes` or `no`, and a missing signal means you neither grant nor restrict anything. For Nordlys the line reads:

```text
Content-Signal: search=yes, ai-input=yes, ai-train=no
```

The policy also comes with a block of comments for the top of `robots.txt` that explains the three signals in plain words and states that any restriction is an express reservation of rights under Article 4 of the EU Directive on Copyright in the Digital Single Market (the text-and-data-mining exception).[^ch04-16] Cloudflare released the policy text under CC0, so anyone can use it, Cloudflare customer or not.

Three facts help you judge how much weight to put on this line.

**It is widely deployed, by one company.** Cloudflare turned on managed `robots.txt` for over 3.8 million domains by September 2025, and managed files carry `Content-Signal: search=yes, ai-train=no` with no `ai-input` signal.[^ch04-16] On Radar's November 2026 snapshot of the top 200,000 domains, 10,279 of the 115,468 successfully scanned domains (8.9%) declared Content Signals, up from about 4% in April 2026.[^ch04-1][^ch04-17] That makes it the most adopted AI-specific signal on the web, almost entirely thanks to one CDN.

**It is not a standard.** Cloudflare submitted the vocabulary to the IETF as an individual Internet-Draft, `draft-romm-aipref-contentsignals-00`, on 1 October 2025. That draft was never adopted by the working group, and the IETF datatracker lists it as "Expired & archived" since 4 April 2026.[^ch04-18] The real standards work is the AI Preferences working group, in the next section.

**Nobody has published whether crawlers obey it.** None of the vendor pages in Table 4.2 mentions Content Signals. I found no vendor statement that a crawler reads the line, and no measurement of compliance. It is a clearly stated preference with a legal framing, and that is all it is today.

So why add it? Two practical reasons. It is the cheapest way to write your training decision in a form that is explicit, dated and machine-readable, which helps if you ever need to show what you asked for. And isitagentready.com requires it: Level 2 ("Bot-Aware") needs both AI bot rules and Content Signals in `robots.txt`.[^ch04-19] The tool that defines the most-cited agent-readiness level is run by the company that wrote the signal. Cloudflare is player and referee here, and I think it is fair to say that out loud while still adding the line.

> **Warning:** Cloudflare's Markdown for Agents feature (Chapter 6) adds its own default header, `Content-Signal: ai-train=yes, search=yes, ai-input=yes`, to every Markdown response it converts, unless your origin sends its own `content-signal` header.[^ch04-20] If your `robots.txt` says `ai-train=no` and your CDN says `ai-train=yes` on the Markdown version of the same page, you are sending two opposite answers. Chapter 6 sets the header explicitly.

### Where to put the line

The Content Signals text does not define how the line interacts with `robots.txt` groups. Cloudflare's own files put it inside the `User-agent: *` group (blog.cloudflare.com) or after the last group (www.cloudflare.com).[^ch04-14] Remember the rule from the refresher: a crawler reads only the group that matches it best. A crawler with its own group never sees a line that sits only in the `*` group. To be safe, Nordlys repeats the line in every group. It costs a few bytes and leaves nothing to interpretation. isitagentready.com's `contentSignals` check only looks for at least one `Content-Signal:` line with one of the three keys, so it passes either way.[^ch04-19]

> **Tip:** Lighthouse 13.6.0 includes a `robots-txt` audit in its SEO category that flags unknown directives. Its safelist already contains `content-signal`, so the line does not cost you SEO points.[^ch04-21] We come back to this audit in a moment, because the IETF's syntax is not on that list.


## The IETF AI Preferences work

The IETF chartered the AI Preferences working group (aipref) to standardise exactly this: a vocabulary for how content may be used by AI systems, and ways to attach that vocabulary to content. As of November 2026 the group has two working-group drafts, both aimed at Proposed Standard.[^ch04-22]

**The vocabulary.** `draft-ietf-aipref-vocab-08` (14 September 2026) defines three categories of use, each with a short label and a `y` or `n` preference:[^ch04-23]

- `train-ai` (AI Training): "Using an asset to modify the learned parameters of a generative AI model."
- `ai-use` (AI Use): "Using an asset as input to a generative AI model, where the asset is not directly provided by the user."
- `search` (Search): using an asset in an application whose primary purpose is to select assets and direct users to their location, with excerpts that help users judge relevance. It "does not include the use of assets to generate summaries."

The draft serialises preferences as an HTTP structured-field dictionary, for example `train-ai=n, search=y`. One detail is worth knowing: the draft says that a `search=y` preference overrides the other categories for processing that serves search only, which includes training models whose outputs are used exclusively for search. And the draft carries an honest warning in its own text: its contents "DO NOT REFLECT CONSENSUS of the Working Group either in whole or part."[^ch04-23]

**The attachment.** `draft-ietf-aipref-attach-05` (19 August 2026, by Gary Illyes of Google and Martin Thomson of Mozilla) defines two ways to attach those preferences: a `Content-Usage` HTTP response header, and a `Content-Usage` rule inside `robots.txt` groups, optionally scoped to a path.[^ch04-24] The draft's own example looks like this:

```text
User-Agent: *
Allow: /
Disallow: /never/
Content-Usage: train-ai=n
Content-Usage: /ai-ok/ train-ai=y
```

**A third approach.** On 30 October 2026, K. Kelley of Anthropic submitted an individual draft, `draft-kelley-aipref-training-preference-signal-00`, which takes a different route: express the training preference with an ordinary `robots.txt` group under a reserved token, `User-Agent: __usage_ai-training`, followed by normal `Allow` and `Disallow` lines.[^ch04-25] Its appeal is obvious. Every existing parser already understands groups, and path scoping comes for free. Google's crawler documentation, updated the same day, says that Google "intends to support the AIPREF shared machine-readable training preference signal (with " user-agent: __usage_ai-training") in early 2027."[^ch04-6]

> **Still in flux:** Two drafts with different syntaxes, a vocabulary without consensus, and one vendor's intent for early 2027. Nothing in the aipref work is final as of November 2026, and no crawler documents reading `Content-Usage` today. My advice: keep Content Signals as your deployed signal, follow the working group, and switch on the aipref syntax once the drafts settle and a vendor you care about reads it.

Table 4.3 puts the two vocabularies side by side, so your policy can be written once and expressed in both.

**Table 4.3** Content Signals and the aipref vocabulary (November 2026)

| Your decision | Content Signals (Cloudflare policy) | aipref vocab-08 label | Notes |
| --- | --- | --- | --- |
| Appear in search results with links | `search=yes` | `search=y` | Both exclude AI-generated summaries from "search" |
| Content as input to AI answers | `ai-input=yes` | `ai-use=y` | aipref's "not directly provided by the user" wording is still under discussion |
| Training generative models | `ai-train=yes` | `train-ai=y` | Note the reversed word order of the two labels |

There is one more reason to be careful with the aipref syntax right now, and it is a very practical one. The Lighthouse SEO audit we just mentioned validates every line of `robots.txt` against a safelist of directives. In Lighthouse 13.6.0 that safelist includes `content-signal` and a few non-standard directives "used in the wild", but not `content-usage`.[^ch04-21] A `robots.txt` with an aipref line therefore fails "robots.txt is valid" in Lighthouse's SEO category today. That is why the Nordlys policy has a switch for it, off by default.

### TDMRep and the European legal angle

If your organisation operates in the European Union (or the wider European Economic Area), your legal team may ask about a reservation of rights for text and data mining. Article 4 of the EU Directive on Copyright in the Digital Single Market allows text and data mining of lawfully accessible content unless the rightholder has reserved that right "in an appropriate manner, such as machine-readable means". The EU AI Act then requires providers of general-purpose AI models to have a copyright policy that identifies and complies with such reservations, "including through state-of-the-art technologies" (Article 53(1)(c)).[^ch04-26] The voluntary General-Purpose AI Code of Practice, published on 10 July 2025, adds commitments for signatories' crawlers, including honouring `robots.txt`.[^ch04-27]

Whether a given line in a given file counts as an "appropriate" reservation is a legal question, and this book is not legal advice. What I can describe is the technical menu:

- The Content Signals comment block frames `ai-train=no` as an Article 4 reservation.
- The W3C TDM Reservation Protocol (TDMRep), a Community Group report from 2024, expresses the reservation as a JSON file at `/.well-known/tdmrep.json` (registered with IANA), as an HTTP header or as an HTML meta tag. The opt-out is `tdm-reservation` set to `1`, for example `[{"location": "/", "tdm-reservation": 1}]`, optionally with a `tdm-policy` URL pointing to your licensing terms.[^ch04-28]
- `robots.txt` rules for training crawlers, which the Code of Practice commits signatories to respect.

TDMRep covers text and data mining in general, not only AI training, so check with legal what you actually want to reserve before you publish it. Nordlys does not publish a `tdmrep.json`. The team's "no" to training is a preference, not a licensing business, and the `robots.txt` groups plus Content Signals express it well enough for its purposes.

### Dead ends to skip

You may meet two other ideas in older articles. The `noai` and `noimageai` values for the robots meta tag were introduced by DeviantArt in November 2022, and no major AI vendor documents honouring them.[^ch04-29] And `ai.txt` exists both as a generator for a permissions file by Spawning and as an individual IETF draft from June 2026 proposing `/.well-known/ai.txt`. None of the vendor pages in Table 4.2 mentions either.[^ch04-30] Neither is harmful, but neither does anything you can verify, so I would spend the time on the controls in this chapter instead.


## Google's controls for AI features

Google deserves its own section, because its search engine and its AI features share one crawler, and because Google-Extended, the token many teams reach for first, does not control AI features in Search.

Here is the situation as of November 2026. Googlebot crawls for Google Search, and Google's AI Overviews and AI Mode are features of Search, built on the same index. Blocking Googlebot removes you from Search entirely, which is rarely what anyone wants. Google-Extended, as we saw, controls training and grounding for Gemini apps and Vertex AI, and explicitly not Search. So what controls AI features in Search? Google offers three levers (Table 4.4).

**Table 4.4** Google's controls for AI use of your content (November 2026)

| Control | Where | What it does |
| --- | --- | --- |
| `Google-Extended` token in `robots.txt` | Your site | Opts content out of training and grounding for Gemini apps and Vertex AI. No effect on Search, AI Overviews or AI Mode.[^ch04-6] |
| `nosnippet`, `max-snippet` (robots meta tag or `X-Robots-Tag` header) and the `data-nosnippet` HTML attribute | Your pages | Limit or prevent snippets. Google says `nosnippet` also prevents the content "from being used as a direct input for AI Overviews and AI Mode." `data-nosnippet` does the same for a part of a page.[^ch04-31] |
| "Search generative AI control" toggle | Search Console | Removes the site from appearing in and grounding AI Overviews, AI Mode and AI Overviews in Discover, without affecting classic ranking. Tested from 3 June 2026, available to all websites since 31 August 2026.[^ch04-32] |

The Search Console toggle is the closest thing Google has to an `ai-input=no` for its own products, and Google is clear about the consequence: "Sites that opt out will not receive traffic or impressions from our generative AI features."[^ch04-32] Because it lives in Search Console, it is also invisible from the outside. No scanner, including the two graders this book uses, can tell whether a site has switched it on. If your organisation uses it, write it into the policy document, so that the person reading `robots.txt` next year knows the whole picture.

For Nordlys, all three stay open: AI Overviews that recommend a cabin with a link are exactly what the team wants. The SEO owner adds one item to the checklist: review the Search Console setting when the policy is reviewed.

## Beyond the polite request

Everything so far is a request. RFC 9309 says so, Content Signals and aipref are "preferences" by their own definitions, and the vendors describe which requests they honour. For many sites that is enough. For some it is not, and it helps to see the whole ladder of controls (Figure 4.2).

![Figure 4.2 — From request to enforcement. robots.txt and usage signals ask, CDN and server rules decide per request, and authentication protects what must stay private. Each step up costs more effort and catches more traffic that ignores the step below.](images/figure-4-2.png)

**Requests** are `robots.txt` groups, Content Signals and (later) aipref. They work for crawlers that choose to comply, which includes every major vendor crawler in Table 4.2.

**Enforcement at the edge** means rules in your CDN, web application firewall or server that answer requests from certain clients with `403`, `429` or a redirect, regardless of what `robots.txt` says. This is where the 16% of `403` responses in Radar's data come from. Most CDNs now ship ready-made rules for AI bots:

- Cloudflare offers managed `robots.txt` (with Content Signals) and AI Crawl Control, which shows requests per AI crawler and operator, status codes and popular paths, and lets you allow or block each crawler (referral counts are on paid plans only).[^ch04-33]
- Vercel's Bot Management has an AI bots managed ruleset that separates training, search and user-initiated bots, and a verified bots directory that classifies, for example, ChatGPT's user and operator agents as `ai_assistant`.[^ch04-34]
- Other CDNs and firewalls (AWS WAF, Akamai and others) have comparable bot features, and several of them verify signed agents, which Chapter 15 covers.

Two warnings from the vendors are worth repeating before you build blocking rules. Anthropic writes that blocking its IP addresses instead of using `robots.txt` "may not work correctly or persistently guarantee an opt-out".[^ch04-5] And Common Crawl warns that other crawlers falsely identify themselves as CCBot.[^ch04-8] So block by verified identity where you can (published IP lists, signatures), and keep `robots.txt` as the statement of intent that compliant crawlers read.

**Authentication** is the only real access control. Member areas, booking details, anything with personal data: these need sign-in or unguessable tokens, and they need it whether the visitor is a person, a crawler or an agent. In Nordlys, `/account/` already requires sign-in and a booking page needs its reference plus a token. The `Disallow` lines for those paths are there to save crawlers a wasted request, not to protect anything.

Pay per crawl (HTTP `402` with a price) and licensing schemes for crawlers are a further step, from "no" to "yes, for a fee". They depend on knowing who the crawler really is, so Chapter 15 covers them together with Web Bot Auth.

> **Note:** Blocking is a business decision with a price. A `403` for an AI search crawler means your cabins don't appear in that assistant's answers. A `403` for a user-triggered fetcher means a person who asked an assistant about your site gets "I couldn't access that page". Measure before and after (Chapter 19), and block the purposes you decided against, not "AI" in general.


## Writing the policy in code

> **Hands-on:** This section turns the Nordlys decision into a layer of the demo app: a policy file, a generator for `robots.txt`, a sitemap, `noindex` headers and tests. If you don't write code, the short version is this: the four answers live in one small file, everything else is generated from it, and a test proves that each kind of crawler gets the answer we decided. Pick up again at "What the graders see".

The layer lives in `nordlys-cabins/layers/04-crawler-controls/` in the demos repository.[^ch04-35] It follows the layer contract from Chapter 2: it registers files and headers through hooks and never edits the shared app. It replaces the minimal `robots.txt` and `sitemap.xml` from Chapter 2.

### The policy as data

Listing 4.1 is the whole decision from earlier in the chapter, as data. It is the file a product manager can read and review in a pull request.

**Listing 4.1** `nordlys-cabins/layers/04-crawler-controls/policy.js` — the access policy

```js
// Nordlys Cabins' access policy, decided by people before anyone writes robots.txt.
// One answer per purpose. The robots.txt and the headers are generated from it.
export const POLICY = {
  search: true, // classic search and AI search indexes: yes, bookings come from them
  aiInput: true, // content as input to AI answers (grounding, RAG): yes, with a link back
  aiTrain: false, // training generative models: no
  userAgents: true, // assistants fetching a page for a person right now: yes, incl. the booking flow

  // Paths no crawler needs. They are protected by sign-in or tokens anyway,
  // because robots.txt is a request, not access control.
  privatePaths: ['/account/', '/bookings/', '/login'],
  // Transactional pages: closed to crawlers, open to agents acting for a person.
  transactionalPaths: ['/book/'],

  // Drafts (November 2026). Off by default, see Chapter 4 "Still in flux".
  experimental: {
    contentUsage: false, // IETF aipref Content-Usage rule and header (draft-ietf-aipref-attach-05)
    trainingGroup: false, // User-Agent: __usage_ai-training (draft-kelley-aipref-training-preference-signal-00)
  },
};
```

The two experimental switches are off. They turn on the aipref `Content-Usage` line and header, and the `__usage_ai-training` group, so that switching later is a one-line change that the tests already cover.

Next to the policy sits `agents.js`, the vendor table from Table 4.2 as an array of objects with a token, a vendor, a purpose, what the vendor says about `robots.txt` and a link to the vendor page. It starts with `export const CHECKED = '2026-11-02'`, because a table like this is only as good as its date. When you update the table, you update the date, and the reviewer can see both.

### Generating robots.txt

Listing 4.2 turns the policy and the agent table into a `robots.txt`.

**Listing 4.2** `nordlys-cabins/layers/04-crawler-controls/robots.js` — the generator

```js
import { tokensFor } from './agents.js';

const yn = (v) => (v ? 'yes' : 'no');

/** Content Signals (Cloudflare's policy, also read by isitagentready.com). */
export const contentSignal = (p) =>
  `search=${yn(p.search)}, ai-input=${yn(p.aiInput)}, ai-train=${yn(p.aiTrain)}`;

/** The IETF aipref vocabulary (draft-ietf-aipref-vocab-08): y or n per category. */
export const contentUsage = (p) =>
  `train-ai=${p.aiTrain ? 'y' : 'n'}, ai-use=${p.aiInput ? 'y' : 'n'}, search=${p.search ? 'y' : 'n'}`;

/** Build robots.txt from the policy. Every group repeats the signals, because a
 *  crawler reads only the one group that matches it best (RFC 9309, section 2.2.1). */
export function buildRobotsTxt(policy, { sitemapUrl }) {
  const signals = [`Content-Signal: ${contentSignal(policy)}`];
  if (policy.experimental?.contentUsage) signals.push(`Content-Usage: ${contentUsage(policy)}`);
  const disallow = (paths) => paths.map((p) => `Disallow: ${p}`);
  const groups = [];

  groups.push(['# Everyone else: search engines and AI search crawlers', 'User-agent: *', ...signals,
    'Allow: /', ...disallow([...policy.privatePaths, ...policy.transactionalPaths])]);

  if (policy.userAgents) {
    groups.push(['# Assistants fetching pages for a person: the booking flow is open',
      ...tokensFor('user').map((t) => `User-agent: ${t}`), ...signals, 'Allow: /', ...disallow(policy.privatePaths)]);
  }
  if (!policy.aiTrain) {
    groups.push(['# Training only: no', ...tokensFor('training').map((t) => `User-agent: ${t}`), ...signals, 'Disallow: /']);
    if (policy.experimental?.trainingGroup) groups.push(['# IETF aipref training preference (draft)', 'User-Agent: __usage_ai-training', 'Disallow: /']);
  }
  const header = ['# robots.txt for Nordlys Cabins, generated from layers/04-crawler-controls/policy.js',
    '# Content signals: https://contentsignals.org/', ''];
  return [...header, groups.map((g) => g.join('\n')).join('\n\n'), '', `Sitemap: ${sitemapUrl}`, ''].join('\n');
}
```

Let's have a look at what it does. There are three groups, each complete on its own, as the refresher demanded (Figure 4.3):

- The `*` group covers everyone without a group of their own: Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot and every other search crawler. Public pages are open, private and transactional paths are closed.
- The user-agent group lists the tokens with purpose `user` and opens the booking flow (`/book/`) to them, while keeping private paths closed. This is the group that keeps Claude-User working for a guest who asks it to book.
- The training group lists the training tokens and disallows everything, because the policy says `aiTrain: false`. If the policy said `true`, the group would disappear and training crawlers would fall back to the `*` group.

![Figure 4.3 — Which group each crawler reads. A crawler obeys the one group that names it, or the * group if none does. GPTBot reads the training group and is turned away, Claude-User reads the user-agent group and may open the booking form, and OAI-SearchBot and Googlebot fall back to the * group.](images/figure-4-3.png)

Every group repeats the signals. The `Sitemap` line goes at the end of the file. Google documents that the sitemap field "isn't tied to any specific user agent and may be followed by all crawlers".[^ch04-3]

Here is the file it generates for `https://nordlys.example`. This is real output from the demo, not a hand-written example:

**Listing 4.3** The generated `robots.txt` (output of the demo, upto Chapter 4)

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

There is no separate group for AI search crawlers. Their rules are the same as for every other search crawler, so naming them would only add lines that can drift. isitagentready.com's `robotsTxtAiRules` check accepts this: it passes when the file names known AI bots "or" has wildcard rules that apply to all crawlers.[^ch04-19]

### A sitemap with honest dates

The sitemap (Listing 4.4) lists every public page and adds `lastmod` only where the data actually knows a date. Guide articles have a publication date, so they get one, and the guide index gets the newest of them. Cabins have no "last changed" field in the Nordlys data, so they get no `lastmod` at all.

**Listing 4.4** `nordlys-cabins/layers/04-crawler-controls/sitemap.js` — the sitemap from the data

```js
const escapeXml = (s) => s.replace(/[<>&'"]/g, (ch) => `&#${ch.charCodeAt(0)};`);

/** Every public page, with lastmod only where the data really knows the date. */
export function sitemapEntries(store) {
  const articles = store.articles();
  const newest = articles.map((a) => a.updated ?? a.published).sort().at(-1);
  return [
    { path: '/' },
    { path: '/cabins' },
    ...store.cabins().map((c) => ({ path: `/cabins/${c.slug}` })),
    { path: '/guide', lastmod: newest },
    ...articles.map((a) => ({ path: `/guide/${a.slug}`, lastmod: a.updated ?? a.published })),
    { path: '/faq' },
    { path: '/contact' },
  ];
}

export function buildSitemap(entries, absoluteUrl) {
  const urls = entries.map(({ path, lastmod }) =>
    `  <url>\n    <loc>${escapeXml(absoluteUrl(path))}</loc>${lastmod ? `\n    <lastmod>${lastmod}</lastmod>` : ''}\n  </url>`);
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`;
}
```

Why leave the date out rather than use today's date? Google ignores `priority` and `changefreq`, and uses `lastmod` only when it is "consistently and verifiably" accurate.[^ch04-36] A sitemap that claims every page changed today trains crawlers to ignore its dates. When Nordlys adds an "updated" field to cabins, the sitemap starts using it with a one-line change. Chapter 6 links the sitemap from the homepage's `Link` header as well, for agents that look there first.

### Registering the layer

Listing 4.5 wires everything into the app.

**Listing 4.5** `nordlys-cabins/layers/04-crawler-controls/index.js` — the layer

```js
import { POLICY } from './policy.js';
import { buildRobotsTxt, contentUsage } from './robots.js';
import { sitemapEntries, buildSitemap } from './sitemap.js';
import { tokensFor } from './agents.js';

export default {
  chapter: 4,
  name: 'Crawler controls',
  description: 'robots.txt with AI crawler groups and content signals, a sitemap with lastmod, noindex on private pages',
  register(app, ctx, policy = POLICY) {
    // 1. robots.txt and sitemap.xml (they replace the minimal ones from Chapter 2)
    ctx.staticFile('/robots.txt', (c) => buildRobotsTxt(policy, { sitemapUrl: ctx.absoluteUrl(c, '/sitemap.xml') }), { replace: true });
    ctx.staticFile('/sitemap.xml', (c) => buildSitemap(sitemapEntries(ctx.store), (p) => ctx.absoluteUrl(c, p)), { replace: true });

    // 2. Private and transactional pages stay out of every index, even for
    //    crawlers that skip robots.txt
    const noindex = [...policy.privatePaths, ...policy.transactionalPaths].map((p) => (p.endsWith('/') ? `${p}*` : p));
    ctx.headers(noindex, { 'x-robots-tag': 'noindex' });

    // 3. Optional: the IETF aipref header on every response (a draft in November 2026)
    if (policy.experimental?.contentUsage) ctx.headers('*', { 'content-usage': contentUsage(policy) });

    // 4. Checks that mirror the documented isitagentready.com pass rules
    ctx.audit('crawler-controls', async ({ request }) => {
      const res = await request('/robots.txt');
      const text = await res.text();
      const sitemap = await (await request('/sitemap.xml')).text();
      return [
        { id: 'robotsTxt', ok: res.status === 200 && /^text\/plain/.test(res.headers.get('content-type')) && /^user-agent:/im.test(text) },
        { id: 'sitemap', ok: /<urlset[\s>]/.test(sitemap) && /^sitemap:/im.test(text) },
        { id: 'robotsTxtAiRules', ok: tokensFor('training').every((t) => text.includes(`User-agent: ${t}`)) },
        { id: 'contentSignals', ok: /^content-signal:\s*\S/im.test(text) },
      ];
    });
  },
};
```

Four things happen. `robots.txt` and `sitemap.xml` are generated per request, so the absolute URLs use the site's public origin (`PUBLIC_ORIGIN` in production, the request origin in development). Private and transactional pages get `X-Robots-Tag: noindex`, which covers crawlers and fetchers that skip `robots.txt` and still feed an index. The aipref header is added only if the experimental switch is on. And an audit mirrors the documented pass rules of the four isitagentready.com checks this layer is responsible for, so the app can check itself without a network connection.

> **Note:** The `noindex` header and the `Disallow` lines on the same paths look like the conflict from the refresher ("Disallow is not noindex"). Here they are deliberate: compliant crawlers never fetch these pages, and anything that fetches them anyway gets told not to index them. Neither is the protection, sign-in and tokens are.

### Testing the policy

A policy that nobody tests drifts. Someone adds a group for one crawler, forgets that groups don't inherit, and opens the booking flow to a training bot. The test in Listing 4.6 parses the served file with `robots-parser` 3.0.1, a widely used RFC 9309 parser on npm,[^ch04-37] and asks it the questions the policy answers.

**Listing 4.6** `nordlys-cabins/tests/ch04-crawler-controls.test.js` (excerpt) — the policy, asked per agent

```js
test('the policy holds for each kind of agent (robots-parser 3.0.1)', async () => {
  const { text } = await robots();
  const r = robotsParser(at('/robots.txt'), text);
  // Search engines and AI search crawlers: public pages yes, booking flow no
  for (const ua of ['Googlebot', 'OAI-SearchBot', 'Claude-SearchBot', 'PerplexityBot']) {
    assert.equal(r.isAllowed(at('/cabins/fjellro'), ua), true, ua);
    assert.equal(r.isAllowed(at('/book/fjellro'), ua), false, ua);
  }
  // Training crawlers and control tokens: nothing
  for (const ua of ['GPTBot', 'ClaudeBot', 'Google-Extended', 'Applebot-Extended', 'CCBot']) {
    assert.equal(r.isAllowed(at('/'), ua), false, ua);
    assert.equal(r.isAllowed(at('/guide/northern-lights-from-a-cabin'), ua), false, ua);
  }
  // Assistants acting for a person: the booking flow is open, accounts are not
  for (const ua of ['ChatGPT-User', 'Claude-User', 'Perplexity-User']) {
    assert.equal(r.isAllowed(at('/book/fjellro'), ua), true, ua);
    assert.equal(r.isAllowed(at('/account/bookings'), ua), false, ua);
  }
  assert.deepEqual(r.getSitemaps(), [at('/sitemap.xml')]);
});
```

The rest of the file checks the content type and the `Sitemap` line, that every group carries the signals, that the sitemap has `lastmod` only for articles, that private pages send `noindex`, that the experimental lines appear only when switched on, and that the layer's own audit passes. Run it with:

```text
node --test tests/ch04-*.test.js
```

All seven tests pass (Node.js 22.23.2, Hono 4.13.16, robots-parser 3.0.1 on 2 November 2026).

> **Tip:** The Robots Exclusion Protocol is simple, but parsers differ in edge cases (wildcards, `$`, case, the order of groups). Google's own C++ parser is open source, and the Lighthouse SEO audit validates syntax. In CI, one parser plus a syntax check is enough. What matters is that the test asks your *policy* questions, in your policy's words.


## What the graders see

Let's measure, as we do after every layer. Table 4.5 shows the checks that this chapter touches in our two graders, before (the site after Chapter 3) and after this layer.

**Table 4.5** Nordlys Cabins before and after the crawler-controls layer

| Grader and check | After Chapter 3 | After Chapter 4 | Why |
| --- | --- | --- | --- |
| isitagentready `robotsTxt` | pass | pass | Chapter 2 already served a valid file |
| isitagentready `sitemap` | pass | pass | Now with real `lastmod` for the guide |
| isitagentready `robotsTxtAiRules` | pass | pass | It passed on the `User-agent: *` rule alone |
| isitagentready `contentSignals` | fail | pass | The `Content-Signal` line |
| isitagentready level | 1 (Basic Web Presence) | 2 (Bot-Aware) | Level 2 = Level 1 plus AI bot rules plus Content Signals |
| Lighthouse SEO `robots-txt` | pass | pass | `content-signal` is on the safelist |
| Lighthouse Agentic Browsing | no change | no change | No audit in that category reads `robots.txt` rules |

The isitagentready rows come from the scanner's documented pass rules, which the layer's audit mirrors locally (a site on `127.0.0.1` cannot be scanned from Cloudflare's servers). Chapter 18 shows how to run the real scanner from CI against a deployed preview.

Look closely at the table, because it teaches something about scores. The level went up by one, and all of it came from one line that a single vendor defined. Meanwhile the decision that actually matters for Nordlys's business, the separate group that keeps the booking flow open to assistants acting for a guest, moved no check at all. `robotsTxtAiRules` passed before we wrote a single AI-specific rule, because a wildcard is enough. I don't say this to criticise the scanner (it has to measure something it can see from the outside). I say it so that your team does not mistake the level for the policy. Track the level, but review the policy.

The Lighthouse Agentic Browsing category is about the page an agent sees, so it has nothing to say about crawler access, with one exception that belongs to Chapter 11: its ARD audit reads an `Agentmap:` line from `robots.txt` to find an agent resource manifest. That line is not on the SEO audit's safelist either, so the same file can please one Lighthouse category and annoy another. `robots.txt` is slowly becoming a discovery file as well as an access file, and that is one more reason to generate and test it rather than edit it by hand.

## A checklist per role

Here is the chapter as a list you can take into the meeting.

- **Product manager:** answer the four questions (search, AI answers, agents acting for a person, training), write them down with a date, and set a review date.
- **Legal:** decide whether a training "no" needs a formal reservation (Content Signals comment block, TDMRep, licence terms), and what the public policy page says.
- **Content and SEO:** list private and transactional paths, decide on Google's Search Console AI setting and `nosnippet` use, and keep the sitemap's dates honest.
- **Developers:** generate `robots.txt` from the policy, complete groups only, `Content-Signal` in every group, the `Sitemap` line, `200` and `text/plain`, and a test per purpose.
- **Security:** confirm that every private path is protected by authentication, and that blocking rules at the edge use verified identities (Chapter 15).
- **Analytics:** segment traffic by purpose (training, search, user) and measure referrals, so the next review is based on data (Chapter 19).

## Summary

- AI traffic comes in three kinds with different costs and value: training crawlers, search crawlers and user-triggered fetchers or agents. Radar's November 2026 data shows most AI crawling is for training, while user actions are a small but valuable share.
- Decide per purpose, not per vendor: search, AI answers, agents acting for a person, and training. Product, legal, content and SEO own the decision, developers implement it.
- `robots.txt` (RFC 9309) is a request, not access control. Groups do not inherit, so every group must be complete. Errors and size limits have real effects on crawling.
- Vendors document separate tokens per purpose. Control tokens such as Google-Extended and Applebot-Extended have no crawler, and most user-triggered fetchers may ignore `robots.txt` by design, with Anthropic's Claude-User as a documented exception.
- Content Signals (`search`, `ai-input`, `ai-train`) is a Cloudflare-defined line on 8.9% of top domains, required for isitagentready.com Level 2, and not a standard. The IETF aipref drafts (`train-ai`, `ai-use`, `search`, the `Content-Usage` header and rule) are still in flux, and Google intends to support a `__usage_ai-training` group in early 2027.
- Google-Extended does not affect Search or AI Overviews. Google's AI feature controls are `nosnippet` and the Search Console generative AI toggle.
- Enforcement happens at the CDN or server with verified identities, and private data needs authentication.
- In code, Nordlys keeps the policy as data, generates `robots.txt` and the sitemap from it, sends `noindex` on private pages and tests the policy per agent with `robots-parser`. The layer moves isitagentready.com from Level 1 to Level 2.

[^ch04-1]: "AI Insights," Cloudflare Radar, https://radar.cloudflare.com/ai-insights (data for 26 October to 2 November 2026, including the "Adoption of AI agent standards" widget, retrieved November 2026).
[^ch04-2]: M. Koster, G. Illyes, H. Zeller, L. Sassman, "RFC 9309: Robots Exclusion Protocol," RFC Editor, September 2022, https://www.rfc-editor.org/rfc/rfc9309.html (retrieved November 2026).
[^ch04-3]: "How Google interprets the robots.txt specification," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt (retrieved November 2026).
[^ch04-4]: "Overview of OpenAI crawlers," OpenAI Platform documentation, https://platform.openai.com/docs/bots (retrieved November 2026).
[^ch04-5]: "Does Anthropic crawl data from the web, and how can site owners block the crawler?," Anthropic Help Center, https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler (retrieved November 2026).
[^ch04-6]: "Google's common crawlers," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers (page updated 30 October 2026, retrieved November 2026).
[^ch04-7]: "About Applebot," Apple Support, https://support.apple.com/en-us/119829 (retrieved November 2026).
[^ch04-8]: "CCBot," Common Crawl, https://commoncrawl.org/ccbot (retrieved November 2026).
[^ch04-9]: "Mistral crawlers," Mistral AI documentation, https://docs.mistral.ai/robots (retrieved November 2026).
[^ch04-10]: "Meta Web Crawlers," Meta for Developers, https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers (the page did not load for us on 2 November 2026, so the purposes come from a search engine's snippet of the page and are unverified, retrieved November 2026).
[^ch04-11]: "Amazon Web Search crawlers," Amazon Developer, https://developer.amazon.com/amazonbot (retrieved November 2026).
[^ch04-12]: "Perplexity Crawlers," Perplexity documentation, https://docs.perplexity.ai/guides/bots (retrieved November 2026).
[^ch04-13]: "Google's user-triggered fetchers," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers (retrieved November 2026).
[^ch04-14]: The robots.txt files of www.cloudflare.com and blog.cloudflare.com, https://www.cloudflare.com/robots.txt and https://blog.cloudflare.com/robots.txt (both fetched on 2 November 2026, retrieved November 2026).
[^ch04-15]: "ai.robots.txt: A list of AI agents and robots to block," GitHub, https://github.com/ai-robots-txt/ai.robots.txt (retrieved November 2026).
[^ch04-16]: "Giving users choice with Cloudflare's new Content Signals Policy," The Cloudflare Blog, 24 September 2025, https://blog.cloudflare.com/content-signals-policy/ (retrieved November 2026).
[^ch04-17]: André Jesus and Vance Morrison, "Introducing the Agent Readiness score. Is your site agent-ready?," The Cloudflare Blog, 17 April 2026, https://blog.cloudflare.com/agent-readiness/ (retrieved November 2026).
[^ch04-18]: M. Tremante, L. Romm, "Vocabulary For Expressing Content Signals," draft-romm-aipref-contentsignals-00, IETF Datatracker, https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ (retrieved November 2026).
[^ch04-19]: "isitagentready.com: full reference," Cloudflare, https://isitagentready.com/llms-full.txt (retrieved November 2026).
[^ch04-20]: "Markdown for Agents," Cloudflare Fundamentals documentation, https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ (retrieved November 2026).
[^ch04-21]: Lighthouse 13.6.0 source, `core/audits/seo/robots-txt.js`, GitHub, https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/seo/robots-txt.js (read in the npm package lighthouse@13.6.0, retrieved November 2026).
[^ch04-22]: "AI Preferences (aipref) documents," IETF Datatracker, https://datatracker.ietf.org/wg/aipref/documents/ (retrieved November 2026).
[^ch04-23]: P. Keller, M. Thomson, "A Vocabulary For Expressing AI Usage Preferences," draft-ietf-aipref-vocab-08, 14 September 2026, https://www.ietf.org/archive/id/draft-ietf-aipref-vocab-08.txt (retrieved November 2026).
[^ch04-24]: G. Illyes, M. Thomson, "Associating AI Usage Preferences with Content in HTTP," draft-ietf-aipref-attach-05, 19 August 2026, https://www.ietf.org/archive/id/draft-ietf-aipref-attach-05.txt (retrieved November 2026).
[^ch04-25]: K. Kelley, "Machine-Readable Training Preference Signal," draft-kelley-aipref-training-preference-signal-00, 30 October 2026, IETF Datatracker, https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/ (retrieved November 2026).
[^ch04-26]: "Article 53: Obligations for Providers of General-Purpose AI Models," EU Artificial Intelligence Act, https://artificialintelligenceact.eu/article/53/, and "Directive (EU) 2019/790 on copyright and related rights in the Digital Single Market," Article 4(3), EUR-Lex, https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0790 (both retrieved November 2026).
[^ch04-27]: "The General-Purpose AI Code of Practice," European Commission, https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai (retrieved November 2026).
[^ch04-28]: "TDM Reservation Protocol (TDMRep)," W3C Community Group, https://w3c-cg.github.io/tdm-reservation-protocol/spec/ (retrieved November 2026).
[^ch04-29]: "UPDATE All Deviations Are Opted Out of AI Datasets," DeviantArt Team, November 2022, https://www.deviantart.com/team/journal/UPDATE-All-Deviations-Are-Opted-Out-of-AI-Datasets-934500371 (retrieved November 2026).
[^ch04-30]: draft-car-ai-txt-wellknown-00, IETF Datatracker, https://datatracker.ietf.org/doc/draft-car-ai-txt-wellknown/00/ (retrieved November 2026).
[^ch04-31]: "Robots meta tag, data-nosnippet, and X-Robots-Tag specifications," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag (retrieved November 2026).
[^ch04-32]: "New controls for website owners in Search," Google The Keyword, https://blog.google/products-and-platforms/products/search/new-controls-website-owners/ (retrieved November 2026).
[^ch04-33]: "AI Crawl Control," Cloudflare documentation, https://developers.cloudflare.com/ai-crawl-control/, and "Analyze AI traffic," https://developers.cloudflare.com/ai-crawl-control/features/analyze-ai-traffic/ (retrieved November 2026).
[^ch04-34]: "Bot Management," Vercel documentation, https://vercel.com/docs/bot-management (page updated 10 September 2026, retrieved November 2026).
[^ch04-35]: Demos repository, `nordlys-cabins/layers/04-crawler-controls/`, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch04-36]: "Build and submit a sitemap," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (retrieved November 2026).
[^ch04-37]: "robots-parser" 3.0.1, npm, https://www.npmjs.com/package/robots-parser (retrieved November 2026).
