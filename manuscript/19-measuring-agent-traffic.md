# Chapter 19: Measuring agent traffic and outcomes

This chapter covers

- The kinds of automated visitor you can find in your logs, and the evidence that tells them apart
- A small, dependency-free classifier that labels every request with who sent it, why and how sure we are
- Referrals from AI products and the crawl-to-refer ratio, with Cloudflare Radar's numbers as context
- Analytics products that already label agent traffic, and what each one shows
- Agent analytics inside Nordlys Cabins, from the request log to bookings, and KPIs for every role

Eighteen chapters in, Nordlys Cabins does a lot for agents. It tells crawlers what they may do with its content, it describes its cabins in structured data, it serves Markdown, it has an API, an MCP server and WebMCP tools, it verifies signed agents and it asks for consent before an agent books on someone's behalf. Chapter 18 gave us tests that keep all of it working.

And then somebody in the planning meeting asks the obvious question. "Does any of this get used?"

It is a fair question, and in my experience it is the one that decides whether agent-readiness work survives the next budget round. A product manager wants to know whether agents book cabins. A content lead wants to know which AI products read the guide articles and whether any readers come back from them. A security engineer wants to know how many requests claim to be GPTBot and are not. The two graders we used all through the book (isitagentready.com and the Lighthouse Agentic Browsing category) tell you whether your site *is ready*. Neither of them tells you what happens on it.

That is the job of this chapter. We sort the automated traffic in a site's logs into groups that mean something, attach to every label the evidence behind it, look at what comes back from AI products (visitors and bookings), and put the numbers that Cloudflare Radar publishes next to our own, so we know which is which. Then we build two things: a log classifier that works on the access log of any server, and an agent-analytics layer for Nordlys Cabins that ties every booking to the kind of visitor that made it.

> **Note:** This chapter never shows traffic numbers from a real site that are not cited. The demo numbers come from a synthetic log that a script generates, and every place they appear says so. The real numbers come from Cloudflare Radar, with the date of the snapshot.

## Three questions worth measuring

Before we open any log file, let's agree on what we want to learn — otherwise every chart looks interesting and none of them changes a decision. I find that every useful agent metric answers one of three questions.

**Who visits?** How many requests come from training crawlers, search crawlers, fetchers acting for one person, browsing agents and the rest, and how that changes over time. This is the question most dashboards stop at.

**What do they get?** The status codes and content types that each group receives. A site that answers 403 to every AI crawler and a site that answers 200 with clean Markdown both have "AI traffic", but they made very different decisions. Chapter 4 was about making those decisions on purpose. This is where you check that the server does what the policy says.

**What comes of it?** The outcomes: people who arrive from an answer in ChatGPT or Perplexity, bookings that an agent completes, tool calls that succeed. Outcomes are what a business cares about, and they are the hardest to measure, because the agent-driven part of the funnel often happens far away from your pages.

Chapter 1 introduced the five kinds of automated visitor, and Chapter 4 wrote a robots.txt policy for each of them. Here we need the same groups in a form a program can count, so the classifier in this chapter uses seven labels:

| Label | Who it is | Examples (November 2026) |
| --- | --- | --- |
| `training` | crawlers that collect content to train models | GPTBot, ClaudeBot |
| `search` | crawlers that build an index for search or AI answers | Googlebot, OAI-SearchBot, Claude-SearchBot, PerplexityBot, bingbot |
| `user-fetch` | fetchers that load a page because one person asked a question | ChatGPT-User, Claude-User, Perplexity-User |
| `browsing-agent` | agents that navigate and act on pages for a person, identified by user agent | Google-Agent |
| `signed-agent` | any agent whose request carries a valid Web Bot Auth signature | ChatGPT agent (signs as `https://chatgpt.com`) |
| `other-bot` | automation we cannot vouch for: unknown bots, scripts, false claims | `python-requests`, a "GPTBot" from a home network |
| `unknown` | everything else: mostly people, plus agents that do not say what they are | an ordinary Chrome user agent |

The difference between the first three matters more than anything else in this chapter. A training crawl and a user-triggered fetch can come from the same company, even from the same cloud region, but one feeds a model and the other answers a question somebody asked a minute ago. The vendors treat them differently too. OpenAI says of ChatGPT-User that "because these actions are initiated by a user, robots.txt rules may not apply", and Google says its user-triggered fetchers "generally ignore robots.txt rules".[^ch19-1] If your dashboard puts them in one bucket called "AI bots", you lose exactly the information you need to make a decision.

## Finding agents in your logs

A request tells you a few things about itself: a user agent string, a source IP address, sometimes a `Referer`, and (more and more often) a signature. Each of these is evidence of a different strength. Let's go through them from the weakest to the strongest, because the order is the whole point.

### The user agent: a claim

Every well-behaved crawler names itself in the `User-Agent` header, and every major AI company documents its tokens. This is what they published as of November 2026:

| Operator | Token | Purpose | Published IP ranges |
| --- | --- | --- | --- |
| OpenAI | `GPTBot` | training | `https://openai.com/gptbot.json` |
| OpenAI | `OAI-SearchBot` | search in ChatGPT | `https://openai.com/searchbot.json` |
| OpenAI | `ChatGPT-User` | user-triggered fetches | `https://openai.com/chatgpt-user.json` |
| Anthropic | `ClaudeBot` | training | `https://claude.com/crawling/bots.json` |
| Anthropic | `Claude-SearchBot` | search quality | same file |
| Anthropic | `Claude-User` | user-triggered fetches | same file |
| Perplexity | `PerplexityBot` | search | `https://www.perplexity.ai/perplexitybot.json` |
| Perplexity | `Perplexity-User` | user-triggered fetches | `https://www.perplexity.ai/perplexity-user.json` |
| Google | `Googlebot` | search | `common-crawlers.json` (with reverse DNS) |
| Google | `Google-Agent` | agents acting on user request | `user-triggered-agents.json` |
| Microsoft | `bingbot` | search | `https://www.bing.com/toolbox/bingbot.json` |

The sources are in the footnotes.[^ch19-2] OpenAI also documents OAI-AdsBot (it checks ad landing pages), and there are many more crawlers on the web than these eleven. The table covers the operators whose crawl-to-refer ratios Radar publishes, which is what we need later.

Two details are worth knowing. First, the version numbers change. OpenAI's documentation shows `GPTBot/1.4` and `OAI-SearchBot/1.4` and says that the version number may change, so match the token, never the whole string. Second, OpenAI adds a `robots.txt` marker to the user agent when it fetches your robots.txt, which is handy when you want to see how often each crawler rereads your policy.[^ch19-3]

And here is the problem: anyone can send any user agent. A scraper that wants to look respectable writes `GPTBot` into its header in one line of code. A user agent is a claim, nothing more. It is useful for sorting traffic that is honest, and useless for traffic that is not.

### Published IP ranges: the network

The next step up is the network. OpenAI, Anthropic, Perplexity, Google and Microsoft all publish the IP ranges their crawlers use, as JSON files with a `creationTime` and a list of `prefixes`. If a request says `GPTBot` and comes from an address inside `gptbot.json`, it is very likely GPTBot. If it says `GPTBot` and comes from somewhere else, it is very likely lying.

The files change often, and they are small. On 2 November 2026 I downloaded all nine files our classifier uses. Their `creationTime` values ranged from 2 November 2026 (Google's two files) back to January 2026 (OpenAI's search crawler), and one file, Bing's, said January 2024. The ChatGPT-User file listed 235 prefixes, Anthropic's listed 14. So the practical rule is simple: fetch them on a schedule (daily is common), keep the date with each copy, and never hard-code an address you saw once.

Please note one warning from Anthropic: blocking by IP address "may not work correctly or persistently guarantee an opt-out", because the robots.txt fetch itself can come from addresses you block.[^ch19-4] Use the ranges to *verify* a claim. Use robots.txt (Chapter 4) to *express* your policy.

### Reverse DNS: the name

Google documents a second method that predates the JSON files: look up the host name of the address (reverse DNS), check that it ends in the right domain, then look up that name and check that it resolves to the same address (forward DNS). Google's common crawlers resolve to `crawl-***.googlebot.com` or `geo-crawl-***.geo.googlebot.com`, and its user-triggered fetchers to `google.com` or `gae.googleusercontent.com` names.[^ch19-5] It is reliable, but it costs two DNS lookups per new address, so you do it at the edge or cache the result. Chapter 15 does it in middleware. Our log classifier skips it and relies on the published ranges, which carry the same information for Google.

### Signatures: the strongest evidence

The strongest evidence is cryptographic. With Web Bot Auth, an agent signs each request with a private key (HTTP Message Signatures, RFC 9421) and names, in a `Signature-Agent` header, where its public keys live. A site that verifies the signature knows which operator sent the request, whatever the user agent or the network says. Chapter 15 explained the protocol and built the verifier for Nordlys Cabins, so here I only want to make one point: a valid signature beats every other signal, and an *invalid* signature is a strong signal too, in the other direction.

Who signs today? OpenAI signs ChatGPT agent traffic (its key directory lives at `https://chatgpt.com/.well-known/http-message-signatures-directory`), and Google says it is experimenting with Web Bot Auth for some agents under the identity `https://agent.bot.goog`, adding that it does not sign every request of a particular agent.[^ch19-6] So for now a signature is a bonus you can use when it is there, never a requirement you can enforce.

> **Still in flux:** Web Bot Auth is an IETF working group draft (`draft-ietf-webbotauth-httpsig-protocol-01`, 29 October 2026), and Google calls its own use experimental. Keep the signature handling in one place (layer 15 in Nordlys Cabins), so that a change to the protocol touches one file and not your analytics.

There is a practical consequence for logging that surprised me the first time. The classic "combined" log format of Apache and nginx has no field for a signature result. If you verify signatures in middleware and then write a combined log, the evidence is gone by the time anyone analyses it. That is one of the reasons I recommend a JSON log for any site that cares about agents, and it is what we build later in this chapter.

### Agents that do not say who they are

Now the uncomfortable part. Many agents that act for people run inside an ordinary browser. Claude in Chrome, Gemini in Chrome and Copilot in Edge work in the person's own browser,[^ch19-19] so (as far as their documentation shows) their requests carry that person's user agent, cookies and IP address. Cloud browsers that do not sign look like any other Chrome. No log analysis can reliably separate those visits from people, and I would be careful with any product that claims it can from the user agent and IP alone.

So the `unknown` bucket in our classifier is honestly named. It holds mostly people, plus some agents that do not identify themselves. What you *can* measure for that bucket is how it behaves on the agent-facing parts of your site: calls to WebMCP tools (Chapter 9 can count them in the page), visits to `.md` URLs or requests with `Accept: text/markdown`, hits on llms.txt. A person rarely reads your llms.txt.

Figure 19.1 puts the evidence in order.

![Figure 19.1 — The evidence ladder. From the strongest evidence (a verified Web Bot Auth signature) to none at all, with what each kind of evidence proves and the label the Nordlys classifier gives the request.](images/figure-19-1.png)

The classifier we build next follows this ladder from the top. It takes the strongest evidence a request carries, and it records which evidence that was, so that every number in a report can say how sure it is.

## Hands-on: a log classifier for any server

> **Hands-on:** This section builds a command-line tool that reads an access log and prints a report like Listing 19.3. If you do not write code, skip to Listing 19.3 to see what the report contains, then continue with "Referrals: what comes back".

The tool lives in the demos repository under `chapters/19-measuring-agent-traffic/`. It has no dependencies, so it runs anywhere Node.js runs, against the logs of any server (nginx, Apache, a CDN export or the JSON log of a Node app). It has four parts: a rules file, a parser, the classifier and the report.

### The rules: operators, purposes, ranges

The rules file is plain data. Each entry names a user-agent token, the operator, the platform it belongs to (for referrals later), its purpose and the file with its published IP ranges. Listing 19.1 shows the start of it.

**Listing 19.1** `chapters/19-measuring-agent-traffic/agents.json` (excerpt) — the first two rules (OpenAI)

```json
{
  "asOf": "2026-11-02",
  "note": "User-agent tokens, purposes and IP range files as each operator documents them on 2 November 2026. Tokens are matched case-insensitively as substrings, so version numbers in the user agent do not matter.",
  "agents": [
    {
      "token": "GPTBot",
      "operator": "OpenAI",
      "platform": "openai",
      "purpose": "training",
      "ipRanges": "openai-gptbot.json",
      "docs": "https://platform.openai.com/docs/bots"
    },
    {
      "token": "OAI-SearchBot",
      "operator": "OpenAI",
      "platform": "openai",
      "purpose": "search",
      "ipRanges": "openai-searchbot.json",
      "docs": "https://platform.openai.com/docs/bots"
    },
```

The file has one entry per row of the table in the previous section, plus three small maps: the referrer host names of each platform (`chatgpt.com` and `chat.openai.com` for OpenAI, `perplexity.ai`, `claude.ai` and so on), the `utm_source` values we recognise, and the Web Bot Auth identities (`https://chatgpt.com` and `https://agent.bot.goog`). Next to it, the folder `ip-ranges/2026-11-02/` holds the nine range files exactly as I downloaded them on that day, with a `SOURCES.md` that lists each URL and `creationTime`. A second script, `fetch-ip-ranges.mjs`, saves today's copies in a new dated folder when you run it. I deliberately did not make the classifier fetch them on the fly: a report should be reproducible, and "which version of the ranges did we use?" is a question you will be asked.

### The parser: two formats

The parser reads two formats. The first is the combined log format that nginx and Apache write by default: address, time, request line, status, size, referrer and user agent. The second is JSON lines, one object per request, with the same fields plus `contentType`, `signature` and `signatureAgent` for servers that verify Web Bot Auth. It also decides what counts as an HTML page, because both our ratios and Cloudflare's count HTML page requests only. A JSON log says so in `contentType`. For the combined format, the parser treats a successful `GET` of a path without a file extension (or ending in `.html`) as a page, and it skips `/api/` and `/mcp`, which you may need to adjust for your own site.

### The classifier: the ladder in code

Listing 19.2 is the heart of the tool. Read the four numbered comments and you have the evidence ladder from Figure 19.1.

**Listing 19.2** `chapters/19-measuring-agent-traffic/lib/classify.mjs` (excerpt) — the classify function

```js
/**
 * Returns { class, agent, operator, platform, evidence }.
 *   class:    signed-agent | training | search | user-fetch | browsing-agent | other-bot | unknown
 *   evidence: signature | ip-range | ua-only (no range file to check) | spoofed (UA claims an
 *             agent, the IP is outside its published ranges) | invalid-signature | none
 */
export function classify(req, rules) {
  const ua = req.userAgent ?? '';
  const claimed = rules.agents.find((a) => ua.toLowerCase().includes(a.token.toLowerCase()));

  // 1. A verified Web Bot Auth signature beats everything a request says about itself.
  if (req.signature === 'verified' && req.signatureAgent) {
    const platform = rules.signatureAgents[req.signatureAgent] ?? null;
    return { class: 'signed-agent', agent: req.signatureAgent, operator: claimed?.operator ?? req.signatureAgent,
      platform, evidence: 'signature' };
  }

  if (claimed) {
    const compiled = rules.ranges.get(claimed.ipRanges);
    let evidence = 'ua-only';
    if (req.signature === 'invalid') evidence = 'invalid-signature';
    else if (compiled) evidence = inRanges(req.ip, compiled) ? 'ip-range' : 'spoofed';
    // 2. A user agent we can disprove is not that agent. Count it as an unknown bot.
    if (evidence === 'spoofed' || evidence === 'invalid-signature') {
      return { class: 'other-bot', agent: claimed.token, operator: null, platform: null, evidence };
    }
    // 3. A documented agent, confirmed by its IP range or (weaker) by its user agent alone.
    return { class: claimed.purpose, agent: claimed.token, operator: claimed.operator,
      platform: claimed.platform, evidence };
  }

  // 4. Self-declared automation we have no rule for, then everything else.
  if (BOT_HINT.test(ua) || !ua) return { class: 'other-bot', agent: null, operator: null, platform: null, evidence: 'none' };
  return { class: 'unknown', agent: null, operator: null, platform: null, evidence: 'none' };
}
```

A few decisions in this function deserve a word.

A claim we can disprove becomes `other-bot`, not the crawler it claims to be. That keeps a spoofed "GPTBot" out of OpenAI's numbers, which matters as soon as anyone computes a ratio per platform. It still keeps the claimed token and the evidence `spoofed`, because "how many requests pretend to be GPTBot?" is a good question for the security team.

A documented agent with no range file to check gets its purpose but the evidence `ua-only`. Every report line carries the evidence, so `training / ua-only` and `training / ip-range` never add up silently.

Self-declared automation (anything with "bot", "crawl", "spider", `curl`, `python-requests` and similar in the user agent, or no user agent at all) is `other-bot`. Everything else is `unknown`, for the reasons we discussed above.

The IP matching itself is in `lib/ip.mjs`: about sixty lines that compare IPv4 and IPv6 prefixes with BigInt arithmetic. Google publishes many IPv6 ranges, so IPv4-only matching would quietly miss real Googlebot traffic.

### The report

Let's have a look at what it prints. The report counts requests per label, the HTML pages among them and the 403 and 429 responses, lists every named agent with its evidence, and computes per platform the crawls, user-triggered fetches, agent visits, referrals and the crawl-to-refer ratio. To try it without a production log, generate the synthetic week first:

```sh
cd chapters/19-measuring-agent-traffic
node make-synthetic-log.mjs
node report.mjs fixtures/synthetic-access.jsonl
```

The generator writes 2,000 requests from 26 October to 1 November 2026, in both formats, with a mix of visitors I invented for the demo: people with referrers from Google, ChatGPT, Perplexity, Claude and Bing, crawlers from inside their published ranges, a signed ChatGPT agent, a fake GPTBot from a documentation address range and a Python script that gets rate-limited. Listing 19.3 is the report.

**Listing 19.3** Output of `node report.mjs fixtures/synthetic-access.jsonl` (synthetic data, not real traffic)

```text
Requests: 2000 (2026-10-26T00:00:05.839Z to 2026-11-01T23:55:37.275Z)

By class                requests   share   HTML   403  429
  signed-agent                55    2.8%     33     0    0
  training                   578   28.9%    565     0    0
  search                     429   21.4%    417     0    0
  user-fetch                 100    5.0%     96     0    0
  browsing-agent              51    2.5%     50     0    0
  other-bot                  146    7.3%    112     0   29
  unknown                    641   32.0%    376     0    0

Agents by evidence
  GPTBot                 training        ip-range              329
  ClaudeBot              training        ip-range              249
  Googlebot              search          ip-range              179
  OAI-SearchBot          search          ip-range              101
  bingbot                search          ip-range               77
  GPTBot                 other-bot       spoofed                76
  PerplexityBot          search          ip-range               72
  ChatGPT-User           user-fetch      ip-range               71
  https://chatgpt.com    signed-agent    signature              55
  Google-Agent           browsing-agent  ip-range               51
  Perplexity-User        user-fetch      ip-range               29

Platforms (HTML pages)  crawls  user fetches  agent visits  referrals  crawl-to-refer
  anthropic                242             0             0          5  48.4 : 1
  google                   176             0            50        107  1.6 : 1
  microsoft                 74             0             0         11  6.7 : 1
  openai                   421            67            33         22  19.1 : 1
  perplexity                69            29             0          6  11.5 : 1
```

Let's read it as a team would. The training crawlers made 28.9% of the requests and the search crawlers 21.4%. 76 requests (almost 4% of the week) claimed to be GPTBot from the wrong network, and the classifier filed them under `other-bot`. The signed ChatGPT agent made 55 requests, and some of them were booking form posts. And the platform table shows the number every product manager eventually asks for: how much each platform takes compared with what it sends back.

Now run the same report on the combined-format copy of the same week (`node report.mjs fixtures/synthetic-access.log`). The `signed-agent` row drops to zero and `unknown` grows by the same 55 requests, because the combined format had nowhere to keep the signature result. Same traffic, weaker evidence. That one comparison is the best argument I know for logging JSON.

> **Tip:** The test suite (`npm run test:unit` in the same folder, nine tests with `node:test`) checks each rule of the ladder, both log formats, IPv4 and IPv6 matching, the referral detection and the totals of the synthetic report. Run it after you add your own crawlers to `agents.json`.

## What they get: checking the policy against the log

Chapter 4 wrote a policy for Nordlys Cabins: search crawlers may read the public pages, training crawlers may read nothing, assistants acting for a person may use the booking flow but not the account pages. A policy in robots.txt is a request, so the log is where you find out whether it is respected and whether your own server enforces what it should.

Three patterns are worth checking every month.

**Training crawlers fetching pages.** With `Disallow: /` for GPTBot and ClaudeBot, a compliant training crawler should fetch your robots.txt and little else. If the report shows them on cabin pages, either the policy changed recently (OpenAI says robots.txt changes take about 24 hours to take effect for search, and Perplexity says up to 24 hours), or the request is not who it claims to be, or a crawler is ignoring the rule.[^ch19-17] The evidence column tells you which of the last two you are looking at. With the JSON output of the classifier, one `jq` line lists the pages:

```sh
node report.mjs fixtures/synthetic-access.jsonl --json \
  | jq -c '.classes[] | select(.name=="training") | .topPaths[:3]'
[["/faq",55],["/cabins/hardanger-hytte",54],["/guide/northern-lights-from-a-cabin",49]]
```

The synthetic generator ignores robots.txt on purpose, so this output is what a violation looks like. On a real site you hope for an empty list.

**Refusals you did not intend.** A 403 to a verified search crawler means your pages drop out of that platform's answers. It usually comes from a WAF rule or a CDN bot setting that is stricter than your robots.txt. Compare the 403 column for `search` with your intent. For context, Radar showed 16% of requests from AI bots answered with 403 across Cloudflare's network in the week to 2 November 2026.

**Rate limits that hit the wrong group.** Chapter 15 gave verified agents their own rate-limit bucket. If the 429 column grows for `user-fetch` or `signed-agent`, people who asked an assistant about your cabins are getting errors. If it grows for `other-bot`, the limits are doing their job, which is what the synthetic week shows for the Python script.

None of these checks needs a dashboard product. They need a log that keeps the evidence and a report you actually read.

## Counting tool calls, not only pages

Pages are only part of the story on an agent-ready site. Agents that use the API from Chapter 7 or the MCP server from Chapter 8 never request an HTML page, and for them the useful unit is the tool call: which tool, how often, how many errors.

The MCP revision of 28 July 2026 made this much easier at the HTTP layer. It requires two request headers on every Streamable HTTP POST, `Mcp-Method` (for example `tools/call`) and `Mcp-Name` (for a `tools/call`, the name of the tool).[^ch19-18] Before that, counting MCP tool calls meant parsing JSON-RPC bodies. Now a web server can log them like any other header. Here is an nginx log format that writes the JSON variant our classifier reads, plus the two MCP headers:

```nginx
log_format agents escape=json
  '{"time":"$time_iso8601","ip":"$remote_addr","method":"$request_method",'
  '"path":"$request_uri","status":$status,"referer":"$http_referer",'
  '"ua":"$http_user_agent","contentType":"$sent_http_content_type",'
  '"mcpMethod":"$http_mcp_method","mcpName":"$http_mcp_name"}';
access_log /var/log/nginx/agents.jsonl agents;
```

The classifier ignores the two extra fields, and a `jq` group-by on `mcpName` gives you calls per tool. What nginx cannot write is a signature result, unless the verification happens at the edge before the request reaches it. So for the full picture, log in the application (as the Nordlys layer below does) or at a CDN that verifies Web Bot Auth.

WebMCP tool calls happen inside the page, so the server never sees them as separate requests. If you want to count them, the tool's handler can send a small event to your analytics endpoint, the same way you would count a button click. Chapter 9 registers the Nordlys tools, and that is the place to add it. Keep the event free of personal data: the tool name, the outcome and the page are enough.

## Referrals: what comes back

So far we counted what agents take. The other half is what they give back, and the main signal is old and humble: the `Referer` header.

When a person clicks a link in an AI answer, the browser usually sends the address of the page they came from. With the default policy most sites and browsers use (`strict-origin-when-cross-origin`, which is also what Nordlys sends) a cross-site request carries only the origin, such as `https://chatgpt.com/`, but the origin is all we need to name the platform. Our classifier matches referrer host names against a short list per platform. A real deployment will want a longer list (regional Google domains, Copilot, Gemini) and should keep it as data, as we did.

Some AI products also tag their outbound links. Many publishers and analytics vendors report that ChatGPT adds `utm_source=chatgpt.com` to links in its answers. I could not find it in OpenAI's own documentation, so treat it as an observed convention, not a promise.[^ch19-7] The classifier counts it as a referral from OpenAI when it appears, because it survives where the `Referer` does not (in apps, for example).

Google Analytics 4 now does part of this work for you. Its default channel group has an "AI Assistant" channel for "users arrive at your site from sources like ChatGPT, Gemini, Deepseek, Copilot, or Grok". Please note what it leaves out: Google's own AI Overviews and AI Mode count as Organic Search, not as AI Assistant.[^ch19-8] So a GA4 report of "AI traffic" says nothing about Google's AI features, which for many sites are the biggest of them all.

And here is the honest limit of referrals. They measure the part of the agentic web that still ends with a person on your page. A user-triggered fetch answers a question and sends nobody. An agent that books through your API or MCP server never loads a page at all. For those visitors, the outcome is not a referral. It is a booking, a quote, a completed tool call, and you measure it at the place where it happens, which we do in Nordlys Cabins below.

## Crawl-to-refer: the ratio everyone quotes

In July 2025 Cloudflare added a metric to Radar that put a number on a feeling many publishers had: the crawl-to-refer ratio. In Cloudflare's definition, it is the number of HTML page requests from a platform's crawler user agents divided by the number of HTML page requests whose `Referer` header contains a host name of that platform.[^ch19-9] In simple words: how many pages a platform takes for every visitor it sends back.

The ratios were dramatic from the start. For July 2025, Cloudflare reported 38,065.7 to 1 for Anthropic (down from 286,930.1 to 1 in January), 1,091.4 to 1 for OpenAI, 194.8 to 1 for Perplexity and 40.7 to 1 for Microsoft.[^ch19-10] On 2 November 2026, the week shown on Radar's AI Insights page had Perplexity at 4.9K to 1, OpenAI at 1.4K to 1, Anthropic at 540.8 to 1 and Google at 4.8 to 1 (Figure 19.2).[^ch19-11]

![Figure 19.2 — Crawl-to-refer ratios on Cloudflare Radar for the week to 2 November 2026, on a logarithmic scale. Google sends a visitor back for about every five pages its crawlers request. The AI platforms crawl hundreds to thousands of pages per visitor.](images/figure-19-2.png)

Two cautions before you put these numbers on a slide. First, they move a lot. The same Radar page showed Perplexity down 24.9% and OpenAI down 24% from the week before, and Anthropic up 8.4%. Always give the date and the period. Second, they describe Cloudflare's network, which is large but not the web, and the platforms' own mix of crawlers. Your site is not an average.

That is why the classifier computes the same idea on your own logs. My version counts as "crawls" only the HTML pages requested by a platform's training and search crawlers, and reports user-triggered fetches and agent visits in their own columns next to it. I made that choice on purpose: a user-triggered fetch exists because a person asked about your site, so lumping it in with training crawls would make an engaged audience look like extraction. Keep whichever definition you choose stable, write it next to the number, and compare a platform with itself over time.

What do you do with the ratio? Mostly, you use it in the conversation Chapter 4 started. If a platform takes thousands of pages per visitor and you never agreed to train its models, the `ai-train=no` Content Signal and a training-crawler block are easy decisions. If a platform's search crawler sends real visitors, keep it in. The ratio turns "AI is stealing our content" and "AI is our future traffic" into a number per platform, which is a much better place for a team to argue from.

## Radar as context, not as your numbers

Cloudflare Radar's AI Insights page is the largest public, regularly updated view of AI traffic, and I quote it a lot in this book. It is also easy to misuse, so here is how I suggest a team uses it.[^ch19-11]

For the week to 2 November 2026, Radar showed that AI bots made 6% of HTML requests, with "Mixed Purpose" bots at another 4.1%, people at 35.5% and other (non-AI) bots at 54.4%. By declared purpose, AI crawling was 41.4% training, 41.3% training and search, 12.3% search, 3.7% user action and 1.3% undeclared. The status codes AI bots received were 200 for 59.6% of requests, 403 for 16%, 404 for 7.5%, 301 for 5.9% and 429 for 2.6%. And of the content types served to AI bots, 73.2% was HTML and Markdown less than 0.1%.

These numbers are useful in three ways. They give your own report a baseline ("our 403 share to AI bots is twice Radar's"), they show the direction of the market, and they settle arguments about orders of magnitude. They are not a forecast for your site, and they are not your traffic. Radar sees Cloudflare's network, and its adoption figures depend on how isitagentready.com scores each check. So the rule I follow in this book: a Radar number always travels with its date, the widget it came from and the words "on Cloudflare's network".

If you want the series in your own dashboard, the same data is on the Radar API (it needs a free API token, and unauthenticated calls are refused), and the "Adoption of AI agent standards" data is updated weekly on Mondays.[^ch19-12] A small weekly job that stores the numbers next to your own is a nice way to make the comparison routine.

## Tools you may already have

You do not have to build a classifier to start. Several products that sit in front of many sites already label agent traffic. They differ in what they show, and I suggest you look at at least two before you decide.

**Cloudflare AI Crawl Control** (formerly AI Audit) shows requests over time, allowed and unsuccessful requests, crawlers grouped by operator (OpenAI, Microsoft, Google, ByteDance, Anthropic, Meta), the most common status codes and paths, and whether your managed robots.txt is in place. Referral counts are on paid plans only.[^ch19-13] Since 1 July 2026 Cloudflare also folds signed agents into its Verified bots, with a field that says whether the access is "Direct" or "Intermediary".[^ch19-14]

**Vercel Bot Management** has an AI bots managed ruleset that separates training, search and user-initiated bots, and a directory of verified bots with categories (for example, `chatgpt-user` and `chatgpt-operator` are in the `ai_assistant` category). Vercel verifies bots by reverse DNS and by Web Bot Auth signatures.[^ch19-15]

**AWS WAF Bot Control** verifies Web Bot Auth signatures on CloudFront distributions and regional resources, and since 21 November 2025 allows verified Web Bot Auth bots by default.[^ch19-16] Its logs carry the bot labels, so the same classification lands in whatever you already use for log analysis on AWS.

**Google Analytics 4** has the AI Assistant channel we discussed. It sees people who arrive, not bots, so it complements the others rather than replacing them.

What none of them gives you out of the box is the outcome: which bookings came from which kind of visitor. That needs your application, which brings us back to Nordlys Cabins.

## Hands-on: agent analytics inside Nordlys Cabins

> **Hands-on:** This section adds the `19-agent-analytics` layer to Nordlys Cabins: a request log in the JSON format of the classifier, labels for every request and booking, and a dashboard at `/__agents`. If you do not write code, look at Figure 19.3 for the flow and continue with "Outcomes and KPIs per role".

The layer reuses the classifier from the previous section (it imports `lib/classify.mjs` and `lib/report.mjs` from `chapters/19-measuring-agent-traffic/`), so the dashboard and a report on exported logs always agree. Figure 19.3 shows where it sits in the request pipeline.

![Figure 19.3 — Where the analytics layer sits. Layer 15 verifies a Web Bot Auth signature, layer 19 classifies the request before the site handles it, and after the response it writes a JSON log record. A booking made during the request is attributed to the class of the visitor that made it.](images/figure-19-3.png)

Listing 19.4 is the middleware and the booking listener.

**Listing 19.4** `nordlys-cabins/layers/19-agent-analytics/index.js` (excerpt) — the request log and the booking listener

```js
    ctx.beforeAuth(async (c, next) => {
      if (c.req.path.startsWith('/__')) return next(); // do not count the dashboards themselves
      const url = new URL(c.req.url);
      const record = {
        time: new Date().toISOString(),
        ip: clientIp(c),
        method: c.req.method,
        path: url.pathname + url.search,
        referer: c.req.header('referer') ?? '',
        ua: c.req.header('user-agent') ?? '',
        ...signatureFrom(c.get('botIdentity')), // set by layer 15 when it runs
      };
      const who = classify({ ...record, userAgent: record.ua }, rules);
      c.set('agentClass', who); // read by the booking listener below
      await next();
      record.status = c.res.status;
      record.contentType = c.res.headers.get('content-type');
      records.push(record);
      if (records.length > MAX_RECORDS) records.shift();
      if (env.NORDLYS_AGENT_LOG) await appendFile(env.NORDLYS_AGENT_LOG, JSON.stringify(record) + '\n');
    });

    // The outcome that matters: which kind of visitor actually booked a cabin.
    ctx.events.on('booking.created', (booking, meta = {}) => {
      const who = meta.c?.get('agentClass') ?? { class: 'unknown', agent: null, evidence: 'none' };
      bookings.push({ ref: booking.ref, cabin: booking.cabin, total: booking.quote?.total ?? null,
        via: meta.via ?? null, class: who.class, agent: who.agent, evidence: who.evidence });
    });
```

The middleware runs in `ctx.beforeAuth()`, after layer 15 (which runs earlier because its chapter number is lower) has put its verdict into `c.get('botIdentity')`. A small helper, `signatureFrom()`, turns that verdict into the `signature` and `signatureAgent` fields of the log record. If layer 15 is off, the fields stay empty and the classifier falls back to the next rung of the ladder.

The order inside the middleware matters. The request is classified *before* `await next()`, and the result goes into the Hono context as `agentClass`. Every route that creates a booking (the booking form, the public API from Chapter 7 and whatever is built on it, and the commerce checkout from Chapter 12) emits a `booking.created` event with the request context. The listener reads `agentClass` from that context, so each booking is attributed to the kind of visitor whose request created it. After the response, the middleware completes the record with the status and content type and keeps it in memory (the last 10,000 records), and optionally appends it to a file.

The client address needs care. Behind a proxy or CDN, the socket address is the proxy, and the real client is in `X-Forwarded-For`. But that header is trivial to forge when there is no proxy, which would let anyone place themselves inside OpenAI's ranges. So the layer reads it only when you say the site is behind a proxy you control (`NORDLYS_TRUST_PROXY=1`).

Run the site and look at the dashboard:

```sh
cd nordlys-cabins
npm start -- --upto=19
# in another terminal
curl -s -A "Mozilla/5.0 (compatible; GPTBot/1.4; +https://openai.com/gptbot)" http://127.0.0.1:3000/cabins/fjellro > /dev/null
curl -s http://127.0.0.1:3000/__agents.json
```

Requests from your own machine come from `127.0.0.1`, which is not in OpenAI's ranges, so that curl request shows up as a spoofed GPTBot. That is exactly right. The page at `/__agents` shows the same numbers as four plain tables (requests by kind of visitor, named agents with their evidence, platforms with their crawl-to-refer ratio, and bookings by kind of visitor), server-rendered, with no scripts, an `X-Robots-Tag: noindex` header and `Cache-Control: no-store`.

> **Warning:** An analytics page lists IP addresses, paths and booking references. In the demo it is open on purpose. On any real deployment, set `NORDLYS_ANALYTICS_TOKEN`, and the layer will answer 401 to every request without `Authorization: Bearer` and that token. Better still, put it behind your normal admin sign-in.

The tests in `tests/ch19-agent-analytics.test.js` (seven tests with `node:test`) cover the important behaviour: a GPTBot request from a published range is counted as training with evidence `ip-range`, the same user agent from another network is labelled spoofed, a ChatGPT referral is counted against OpenAI's crawling, a booking posted by ChatGPT-User is attributed to `user-fetch`, the dashboard has no scripts and is not indexed, the token works, and layer 15's labels map correctly. I also ran them with the Chapter 15 layer present, and they pass both ways.

### Reading the dashboard as a team

A dashboard earns its place when people with different jobs read the same table and each takes something away. Here is how I would walk a Nordlys team through `/__agents` after a week in production.

The **requests by kind of visitor** table is the security engineer's first stop. A growing `other-bot` row is normal on any public site, but a sudden jump, especially one that comes with many spoofed claims in the second table, is worth an alert. The product manager reads the same table for the `user-fetch`, `browsing-agent` and `signed-agent` rows, because those are people using an assistant to look at Nordlys right now.

The **named agents** table is for the architect. The share of rows with evidence `signature` or `ip-range` says how much of the agent traffic you could treat differently (a higher rate limit, a richer response) with confidence. Rows with `ua-only` are a to-do item: find the operator's range file, or accept that the label is a guess.

The **platforms** table belongs to content and SEO. It shows, per platform, how much is crawled and how much comes back, and it is the table to bring to the next review of the robots.txt policy from Chapter 4.

The **bookings** table is the one I would put on the wall. If, after a month, it shows a handful of bookings from `signed-agent` and `user-fetch`, that is the first real evidence that the work of Chapters 7 to 17 reaches customers. If it shows none while the other tables show plenty of agent visits, the agents look but do not book, and the eval suite from Chapter 18 is the place to find out where they fail.

### Logs are personal data

One more thing before we look at KPIs. An access log with IP addresses and booking references is personal data under the GDPR, and Chapter 17 covered what that means for retention, purpose and transparency. For agent analytics, two habits keep you on the safe side. Keep the raw log only as long as you need it for security and debugging, and keep the aggregates (counts per class, per platform, per day) for the long-term charts. And do not use the analytics log to build profiles of people: the point of this layer is to understand agents, and the `unknown` bucket, which is mostly people, only needs to be counted.

## Outcomes and KPIs per role

A dashboard full of request counts is easy to build and easy to ignore. What makes agent analytics useful is a small set of numbers that each role on the team owns. The list below is my proposal, not an industry standard, and it reuses what earlier chapters built: the graders from Chapter 2 on, the eval suite from Chapter 18, the identity labels from Chapter 15 and the bookings from this chapter.

| Role | KPI | Where it comes from | Why it matters |
| --- | --- | --- | --- |
| Product manager | Agent-originated bookings per week, and their cancellation rate compared with other bookings | layer 19 bookings by class | the only number that ties agent-readiness to revenue |
| Product manager | Task success rate of the eval suite per agent type | Chapter 18 evals | whether agents can actually do the job |
| Content and SEO | Referrals per AI platform, and crawl-to-refer per platform over time | classifier report, GA4 AI Assistant channel | which platforms send readers back, input for the Chapter 4 policy |
| Content and SEO | Most-fetched pages by user-triggered fetchers | classifier report, top paths | these pages are your de facto answers, so keep them accurate |
| Developers | Error rate and p95 latency of agent-facing endpoints (`/api/v1`, `/mcp`, WebMCP tools), rate-limit hits | server metrics, 429 counts | agents give up quickly on slow or failing tools |
| Architects | Share of agent traffic with strong evidence (signature or IP range) | classifier evidence column | how much of the agent traffic you can trust and serve differently |
| Security | Spoofed claims and invalid signatures per day, with alerts on spikes | `other-bot` with evidence `spoofed` or `invalid-signature` | false claims are the first sign of scraping that hides behind good names |
| QA | Lighthouse agentic score per key template, and the isitagentready level | Chapter 18 CI | readiness should not regress between releases |
| Analytics | 403 and 429 share per class, compared with Radar's baseline | classifier report, Radar | whether the server enforces the policy you wrote |
| Designers | Completion rate of agent-assisted forms (declarative WebMCP submissions that succeed) | Chapter 9 tool events | forms that agents fail are often forms people fail too |

Bottomline: pick three or four KPIs, not ten. In my experience the first one (agent-originated bookings) does more for the budget conversation than all the others together, because it answers the question from the planning meeting with a number of bookings. If it is small today, that is fine. It is a baseline, and Chapter 20 is about what happens to all these numbers as the standards underneath them move.

## Summary

- Agent analytics answers three questions: who visits, what they get and what comes of it. Most dashboards stop at the first.
- Keep training crawlers, search crawlers, user-triggered fetchers, browsing agents and signed agents apart. They come from the same companies but are controlled and valued differently.
- Evidence has an order: a verified Web Bot Auth signature, then an IP address inside the operator's published ranges, then reverse DNS, then the user agent alone. Record which evidence each label rests on.
- A user agent from outside its operator's published ranges is a false claim. Count it as an unverified bot, never as the crawler it names.
- The combined log format cannot keep a signature result. Log JSON if you care about agents.
- Referrals come from the `Referer` header and tags such as `utm_source=chatgpt.com` (widely observed, not documented by OpenAI). GA4's AI Assistant channel excludes Google's AI Overviews and AI Mode.
- The crawl-to-refer ratio compares what a platform takes with what it sends back. Radar's values for the week to 2 November 2026 ranged from 4.8 to 1 (Google) to 4.9K to 1 (Perplexity). Always cite the date, and compute your own.
- Cloudflare AI Crawl Control, Vercel Bot Management, AWS WAF Bot Control and GA4 each show part of the picture. None of them shows which bookings agents made.
- The Nordlys layer attributes every booking to the kind of visitor that made it. Agent-originated bookings are the KPI that ties agent-readiness to the business.

[^ch19-1]: OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots, and Google Crawling Infrastructure, "Google User-Triggered Fetchers", https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers (both retrieved November 2026).
[^ch19-2]: OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots, Claude Help Center, "Does Anthropic crawl data from the web, and how can site owners block the crawler?", https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler, Perplexity, "Perplexity Crawlers", https://docs.perplexity.ai/docs/resources/perplexity-crawlers, Google Crawling Infrastructure, "Verify Requests from Google Crawlers and Fetchers", https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests, and the Bing range file at https://www.bing.com/toolbox/bingbot.json (all retrieved November 2026).
[^ch19-3]: OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots (retrieved November 2026).
[^ch19-4]: Claude Help Center, "Does Anthropic crawl data from the web, and how can site owners block the crawler?", https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler (retrieved November 2026).
[^ch19-5]: Google Crawling Infrastructure, "Verify Requests from Google Crawlers and Fetchers", https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests (retrieved November 2026).
[^ch19-6]: OpenAI's key directory, https://chatgpt.com/.well-known/http-message-signatures-directory, and Google Crawling Infrastructure, "Google's Guide to Authenticating Requests with Web Bot Auth (Experimental)", https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth (both retrieved November 2026).
[^ch19-7]: For example Profound, "How to get your product discovered by ChatGPT", https://www.tryprofound.com/articles/get-your-product-discovered-in-chatgpt-shopping (retrieved November 2026). I found no statement about the parameter in OpenAI's documentation.
[^ch19-8]: Analytics Help, "Default channel group", https://support.google.com/analytics/answer/9756891 (retrieved November 2026).
[^ch19-9]: Cloudflare blog, "The crawl before the fall… of referrals: understanding AI's impact on content providers", https://blog.cloudflare.com/ai-search-crawl-refer-ratio-on-radar (retrieved November 2026).
[^ch19-10]: Cloudflare blog, "The crawl-to-click gap: Cloudflare data on AI bots, training, and referrals", 29 August 2025, https://blog.cloudflare.com/crawlers-click-ai-bots-training (retrieved November 2026).
[^ch19-11]: Cloudflare Radar, "AI Insights", https://radar.cloudflare.com/ai-insights, traffic widgets for 26 October to 2 November 2026 (retrieved 2 November 2026).
[^ch19-12]: Cloudflare changelog, "AI Insights updates on Cloudflare Radar", 17 April 2026, https://developers.cloudflare.com/changelog/post/2026-04-17-radar-ai-insights-updates/ (retrieved November 2026).
[^ch19-13]: Cloudflare AI Crawl Control docs, "Analyze AI traffic", https://developers.cloudflare.com/ai-crawl-control/features/analyze-ai-traffic/ (retrieved November 2026).
[^ch19-14]: Cloudflare Docs, "Verified bots", https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ (retrieved November 2026).
[^ch19-15]: Vercel Docs, "Bot Management", https://vercel.com/docs/bot-management (retrieved November 2026).
[^ch19-16]: AWS, "AWS WAF announces Web Bot Auth support", 21 November 2025, https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/, and AWS WAF Developer Guide, "AWS WAF Bot Control", https://docs.aws.amazon.com/waf/latest/developerguide/waf-bot-control.html (both retrieved November 2026).
[^ch19-17]: OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots, and Perplexity, "Perplexity Crawlers", https://docs.perplexity.ai/docs/resources/perplexity-crawlers (both retrieved November 2026).
[^ch19-18]: Model Context Protocol, "Key Changes" for revision 2026-07-28 (SEP-2243), https://modelcontextprotocol.io/specification/2026-07-28/changelog (retrieved November 2026).
[^ch19-19]: Claude Help Center, "Get started with Claude in Chrome", https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome, Google, "The new era of browsing: Putting Gemini to work in Chrome", https://blog.google/products-and-platforms/products/chrome/gemini-3-auto-browse/, and Microsoft Support, "Browse with Copilot", https://support.microsoft.com/en-us/edge/copilot/browse-with-copilot (all retrieved November 2026).
