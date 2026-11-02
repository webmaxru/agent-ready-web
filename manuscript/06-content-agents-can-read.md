# Chapter 6: Content agents can read

This chapter covers

- Why HTML is an expensive format for agents, measured on real traffic and on Nordlys
- Serving Markdown from the same URL with `Accept: text/markdown`, `Vary: Accept` and `.md` URLs
- Rendering Markdown from data instead of converting HTML, and keeping it true to the page
- llms.txt: the format, what Lighthouse checks, and the honest answer to "who reads it?"
- Sitemaps, feeds and Link headers as the map that leads agents to the content
- What isitagentready and Lighthouse see after this chapter

Chapter 5 gave the facts of Nordlys a typed form. This chapter is about the words around the facts: the cabin descriptions, the guide articles, the FAQ answers. People read them in a browser, with a header, a menu, a footer, a cookie banner on many sites, and a stylesheet that turns a dozen nested elements into one clean paragraph. An agent reads the same page as a long string of markup, and it pays for every character of it, in tokens, in time and in the chance that it picks the wrong thing out of the noise.

The fix is not new and not exotic. HTTP has supported several representations of one resource since the 1990s, and Markdown is a format that models read very well. What is new is that agents started to ask for it, that CDNs started to produce it, and that the graders started to check for it. By the end of this chapter, every public Nordlys page answers in Markdown to a client that asks for Markdown, keeps answering in HTML to everyone else, and the site has an llms.txt, an Atom feed for its guide and Link headers that tie it all together.

## Why HTML is expensive to read

Let's start with numbers, because they make the case better than any argument.

Cloudflare Radar reports which content types its network serves to AI bots. In the seven days to 2 November 2026, AI bots received HTML 73.2% of the time, plain text 7%, JSON 5.5%, images 4.7% and Markdown less than 0.1%.[^ch06-1] So almost everything an AI crawler or fetcher reads is HTML, built for browsers. The same dashboard shows what Markdown changes: for responses converted by Cloudflare's Markdown for Agents feature, the median Markdown response is 7.9% of the original size.[^ch06-1] That's more than twelve times smaller.

Individual measurements tell the same story with more drama. When Cloudflare introduced Markdown for Agents on 12 February 2026, the announcement noted that the blog post itself took 16,180 tokens as HTML and 3,150 tokens as Markdown.[^ch06-2] Checkly measured one of its documentation pages at 180,573 tokens as HTML (615.4 KB) and 478 tokens as Markdown (2.3 KB).[^ch06-3] That second page is an extreme case, with a lot of inline script and styling, but extreme cases are common on the real web.

Why does size matter that much? For three reasons.

- **Cost and speed.** Tokens cost money and time on the agent's side. A model that reads 180,000 tokens to find one paragraph is slow and expensive, and agent tools often cut a long page off at some limit. Whatever falls past the cut, the agent never sees.
- **Accuracy.** Navigation, footers, "related articles" and repeated calls to action all compete with the content for the model's attention. The less noise, the less chance that the agent quotes the price of a different cabin from a "you may also like" box.
- **Context for the user's task.** An agent comparing four cabins has to fit four pages, the user's request and its own reasoning into one context window. Lean pages leave room for the actual work.

Nordlys, being a small and clean demo site, isn't a dramatic example. Its HTML is already lean, with no tracking scripts and no framework runtime. Even so, the Markdown version of a cabin page is about a fifth of the HTML in tokens, as we will measure later in this chapter. On a typical commercial site with a mega menu, a consent banner and a few analytics tags, the difference is much larger.

## Three ways to serve Markdown

There are three common ways to give agents Markdown, and they combine well. Table 6.1 compares them.

**Table 6.1** Three ways to serve Markdown to agents

| Approach | How an agent gets Markdown | Pros | Cons |
| --- | --- | --- | --- |
| Content negotiation | Requests the normal URL with `Accept: text/markdown` | One URL per page, standard HTTP, checked by isitagentready | Needs `Vary: Accept` everywhere, so caches keep the versions apart |
| Separate `.md` URLs | Requests `/cabins/fjellro.md` | Works for clients that can't set headers, easy to link from llms.txt | Two URLs per page, so you need canonical links |
| Edge conversion | A CDN converts HTML to Markdown on the way out | No code changes, works on any origin | Conversion guesses what is content, and the CDN may add its own defaults |

Nordlys does the first two in the application and doesn't depend on the third. Let's look at each.

**Content negotiation** is the HTTP way. A client says which formats it prefers in the `Accept` header, and the server picks the best representation it has for that URL. HTTP semantics define this as proactive negotiation, with quality values (`q`) that rank the client's preferences.[^ch06-4] When the response depends on `Accept`, the server must say so with `Vary: Accept`, otherwise a shared cache could store the Markdown and serve it to the next browser, or the other way round.

**Separate `.md` URLs** are what many documentation sites already do. The llms.txt proposal accepts both `page.md` and `page.html.md` as the Markdown form of `page.html`, because publishing tools differ.[^ch06-5] The convenience is that a `.md` URL works everywhere, including in a plain link in llms.txt and in tools that don't let you set request headers.

**Edge conversion** is what Cloudflare's Markdown for Agents does on Pro and Business plans: when a request's `Accept` includes `text/markdown`, Cloudflare converts the origin's HTML to Markdown at the edge, strips navigation, header and footer, adds YAML front matter from the page's meta tags, keeps JSON-LD as a fenced block at the end, and sets `Vary: Accept`.[^ch06-6] Vercel published a recipe for Next.js that does the negotiation in the application instead, with a header-based rewrite to a Markdown route.[^ch06-7]

Edge conversion has one detail that deserves a warning box of its own. When the origin response has no `content-signal` header, Markdown for Agents adds a default `Content-Signal: ai-train=yes, search=yes, ai-input=yes`.[^ch06-6] If you spent Chapter 4 deciding that your site's answer to training is "no", an edge feature can quietly attach the opposite answer to every Markdown response. The fix is simple: send your own `Content-Signal` header from the origin, and the CDN keeps it. Nordlys does exactly that.

You can see the whole pattern on Cloudflare's own blog. On 2 November 2026, a request for the Markdown for Agents announcement with `Accept: text/markdown` returned `Content-Type: text/markdown`, `Vary: accept`, `Content-Signal: ai-train=yes, search=yes, ai-input=yes` and a `Link` header with an RSS alternate, a sitemap and an API catalog.[^ch06-2] That's a site making a deliberate choice: its content signal says yes to training, and that's Cloudflare's call to make for its own blog. Your call may be different, and the header is where you make it.

### Who asks for Markdown today

Negotiation only helps if clients ask. In February 2026, Checkly tested seven coding agents and found that three of them requested Markdown: Claude Code (2.1.38), Cursor (2.4.28) and OpenCode (1.2.5). OpenAI Codex, Gemini CLI (0.28.2), GitHub Copilot and Windsurf did not.[^ch06-3] Table 6.2 sums it up.

**Table 6.2** Coding agents that asked for Markdown in Checkly's test (February 2026)

| Sends `Accept: text/markdown` | Does not |
| --- | --- |
| Claude Code 2.1.38, Cursor 2.4.28, OpenCode 1.2.5 | OpenAI Codex, Gemini CLI 0.28.2, GitHub Copilot, Windsurf |

Two cautions about this table. First, these are coding agents fetching documentation, not shopping agents browsing a booking site, and the test is a snapshot of specific versions from early 2026. Second, browsing agents that drive a real browser (Chapter 3) see the rendered page and never send this header at all. So Markdown negotiation serves one important group well, the agents that fetch pages over plain HTTP, and does nothing for the others. That's fine. Each layer in this book serves some agents, and none serves all of them.

On the server side, adoption is still small. In Radar's November 2026 scan of 115,468 domains from the top 200,000, 4.3% supported Markdown negotiation (4,924 domains) and 9.7% sent Link headers that the scanner considers useful for agents.[^ch06-8] My reading is that platforms are behind much of this, because a feature like Markdown for Agents switches on for a whole zone at once. Either way, check what your platform already does before you build.


## Content negotiation done right

Before we write code, let's agree on the rules. Content negotiation is easy to get almost right, and the "almost" is where caches serve Markdown to browsers.

**Only an explicit request gets Markdown.** A browser sends something like `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8`. The `*/*` technically accepts Markdown too, but no browser wants it. Nordlys serves Markdown only when the client names `text/markdown` explicitly and gives it a quality at least as high as HTML. `Accept: text/markdown, text/html, */*` gets Markdown. `Accept: text/html, text/markdown;q=0.5` gets HTML.

**HTML stays the default.** isitagentready's own fix text says it in one line: return Markdown for `Accept: text/markdown` "while HTML remains the default for browsers".[^ch06-9] A missing or unusual `Accept` header means HTML.

**`Vary: Accept` on both versions.** The Markdown response says `Vary: Accept`, and so does the HTML response, because a cache that stored the HTML version without that header could serve it to the next agent, and one that stored the Markdown could serve it to a browser. If your CDN normalises or ignores `Vary`, check its documentation for a way to include the `Accept` header in the cache key.

**One canonical URL.** The Markdown response carries `Link: <https://nordlys.example/cabins/fjellro>; rel="canonical"`, so any consumer that indexes it knows which URL represents the page. The HTML response links the other way, with `rel="alternate"; type="text/markdown"`.

**The same facts in both.** Serving different content to bots and people has a name in search, cloaking, and it is a reason for penalties. Markdown that omits navigation is fine. Markdown that shows different prices, hides fees or adds claims the HTML doesn't make is not. We will test it the same way Chapter 5 tested the JSON-LD.

**Public pages only.** The Markdown view is for public content. A signed-in member's "My bookings" page stays HTML, and a `.md` URL never shows anything that depends on a session. Nordlys builds `.md` responses from a fresh internal request without cookies, so even a mistake in a renderer can't leak a member's data into a Markdown file that some cache keeps for a day.

**Your own content signal.** Markdown responses carry the same usage preferences as robots.txt (Chapter 4), as a `Content-Signal` header generated from the same policy object. That keeps any CDN default out, and it means that a single change in the policy updates robots.txt and the headers together.

Figure 6.1 shows the whole flow.

![Figure 6.1 One URL, two representations. A browser and an agent request the same URL and get HTML or Markdown depending on the Accept header. Both responses carry Vary: Accept, so a shared cache keeps them apart, and .md URLs map to the same Markdown.](images/figure-6-1.png)

**Figure 6.1** One URL, two representations. A browser and an agent request the same URL and get HTML or Markdown depending on the Accept header. Both responses carry Vary: Accept, so a shared cache keeps them apart, and .md URLs map to the same Markdown.

## How agents find the Markdown

It helps to look at the same site through the eyes of four different clients, because each one finds the Markdown (or doesn't) in a different way.

**A coding agent that sends `Accept: text/markdown`.** A developer asks their coding tool to "check the cancellation policy on nordlys.example". The tool fetches `https://nordlys.example/faq` with an `Accept` header that names Markdown. It gets the Markdown directly, about 400 tokens instead of almost 1,900, and never sees the HTML. Nothing else is needed.

**A fetcher that doesn't negotiate.** Another tool fetches the same URL with a generic `Accept` header and gets HTML. If it looks at the response headers, it finds `Link: <https://nordlys.example/faq.md>; rel="alternate"; type="text/markdown"` and can fetch that instead. If it parses the HTML, it finds the same link in a `<link>` element in the head. Whether a given tool does either is up to its authors, and I found no survey that measures it. The cost of offering both is two lines of code.

**An agent that starts from the site, not from a page.** An assistant asked "which Nordlys cabin is best for seeing the northern lights?" doesn't know which page to read. If it checks `/llms.txt`, it gets the whole catalogue in one short file, with region, capacity and price per cabin, plus links to the guide articles, among them "How to watch the northern lights from a cabin". Two more requests to `.md` URLs, and it can answer with sources. If it doesn't check llms.txt, the sitemap and the home page do the same job, at a higher price in tokens.

**A browsing agent.** An agent that drives a real browser (Chapter 3) loads the HTML page, renders it, reads the accessibility tree and maybe a screenshot. It never sends `Accept: text/markdown`, and it doesn't need to, because its whole design is to use the page the way a person does. For this agent, the work of Chapter 3 (semantic HTML, labels, a stable layout) matters, and the tools of Chapter 9 matter even more. Markdown changes nothing for it, and that's fine.

So the layers of this chapter don't replace good HTML. They add a cheaper, cleaner path for the clients that can use one, and they leave the page exactly as it was for everyone else.

## Hands-on: the agent-content layer

> **Hands-on.** This section builds layer `06-agent-content` in the Nordlys demo. If you don't write code, read the explanations after each listing and continue with "Measuring the savings".

The layer lives in `demos/nordlys-cabins/layers/06-agent-content/` and has six files: `negotiate.js` decides who gets Markdown, `markdown.js` renders the Markdown views, `index.js` wires everything into the site, `llms.js` builds llms.txt, `feed.js` builds the Atom feed of the guide, and `token-compare.js` measures the savings. Start the site with all layers up to this chapter:

```
cd demos/nordlys-cabins
npm start -- --upto=6
```

### Deciding who gets Markdown

Listing 6.1 is the whole negotiation logic. It parses the `Accept` header into media ranges with their quality values and compares Markdown with HTML.

**Listing 6.1** Choosing Markdown only when the client asks for it (`layers/06-agent-content/negotiate.js`)

```js
// Content negotiation for Markdown (RFC 9110, section 12.5.1).
// A client gets Markdown only when it asks for text/markdown explicitly and
// ranks it at least as high as HTML. Browsers never do, so they keep HTML.

/** Parse an Accept header into [{ type, q }]. */
export function parseAccept(header = '') {
  return header
    .split(',')
    .map((part) => {
      const [range, ...params] = part.trim().split(';').map((s) => s.trim());
      const q = params.find((p) => p.toLowerCase().startsWith('q='));
      return { type: range.toLowerCase(), q: q ? Number(q.slice(2)) : 1 };
    })
    .filter((r) => r.type && !Number.isNaN(r.q));
}

/** The q value the header gives a media type, using the most specific range. */
function qualityOf(ranges, type, { wildcards = true } = {}) {
  const [major] = type.split('/');
  const exact = ranges.find((r) => r.type === type);
  if (exact) return exact.q;
  if (!wildcards) return 0;
  const partial = ranges.find((r) => r.type === `${major}/*`);
  if (partial) return partial.q;
  const any = ranges.find((r) => r.type === '*/*');
  return any ? any.q : 0;
}

export function prefersMarkdown(accept) {
  const ranges = parseAccept(accept);
  const md = qualityOf(ranges, 'text/markdown', { wildcards: false });
  const html = qualityOf(ranges, 'text/html');
  return md > 0 && md >= html;
}
```

Notice the asymmetry in `prefersMarkdown()`. For Markdown, wildcards don't count (`{ wildcards: false }`), so `*/*` never selects it. For HTML, they do, so a browser's `*/*;q=0.8` still counts as an HTML preference. That one detail is what keeps browsers safe.

You might ask why not use a library. There are good content negotiation packages for Node.js, and in a larger project I would use one. Here, thirty lines make the rules visible, and the test in Listing 6.4 pins them down.

### Wiring it into the site

Listing 6.2 shows the two pieces of the layer that serve Markdown: a middleware that negotiates on every page, and a handler for `.md` URLs.

**Listing 6.2** Markdown negotiation and `.md` URLs (`layers/06-agent-content/index.js`, excerpt)

```js
    // 1. Markdown negotiation on every page that has a Markdown view.
    ctx.middleware(async (c, next) => {
      await next();
      const page = c.get('page');
      if (!hasMarkdown(page) || c.res.status !== 200) return;
      const abs = (path) => ctx.absoluteUrl(c, path);
      const links = [`<${abs(markdownPath(page.path))}>; rel="alternate"; type="text/markdown"`, `<${abs('/llms.txt')}>; rel="describedby"`];
      if (prefersMarkdown(c.req.header('accept'))) {
        c.res = new Response(renderMarkdown(page, store, abs), {
          status: 200,
          headers: {
            'content-type': 'text/markdown; charset=utf-8',
            vary: 'Accept',
            'content-signal': contentSignal(POLICY), // our policy, not a CDN default
            link: [`<${abs(page.path)}>; rel="canonical"`, `<${abs('/llms.txt')}>; rel="describedby"`].join(', '),
          },
        });
        return;
      }
      c.res.headers.append('vary', 'Accept'); // caches must keep HTML and Markdown apart
      c.res.headers.append('link', links.join(', '));
    });

    // 2. The same Markdown at a .md URL: /cabins/fjellro.md, /index.md
    ctx.beforeAuth(async (c, next) => {
      const path = c.req.path;
      if (!['GET', 'HEAD'].includes(c.req.method) || !path.endsWith('.md') || (await ctx.getStaticFile(path, c)) !== null) return next();
      const target = path === '/index.md' ? '/' : path.slice(0, -3);
      // A fresh internal request without cookies: a .md URL only ever shows the public page.
      const res = await app.request(new URL(target, c.req.url).href, { method: c.req.method, headers: { accept: 'text/markdown' } });
      if (!(res.headers.get('content-type') ?? '').startsWith('text/markdown')) return c.notFound();
      return res;
    });
```

The middleware runs after the core has rendered the page (`await next()`). At that point the page object is available with `c.get('page')`, including its kind and data. If the page has a Markdown view and the client prefers Markdown, the layer replaces the HTML response with Markdown rendered from the same page object. Otherwise, it adds `Vary: Accept` and the Link header to the HTML response. Either way, the core page code is untouched.

The `.md` handler runs before authentication. It ignores paths that another layer serves as a real file (Chapter 7, for example, publishes a `/developers.md`), strips the extension, and asks the app for the same page with `Accept: text/markdown` and no cookies. If the answer isn't Markdown, the `.md` URL is a 404. That way `/book/fjellro.md` or `/account/bookings.md` don't accidentally return HTML under a Markdown URL.

### Caching, CDNs and HEAD requests

Content negotiation lives or dies with caching, so let's spend a moment on the details that bite in production.

A shared cache that respects `Vary: Accept` stores one copy per distinct `Accept` header value. Browsers send a handful of different values, agents send others, and the number of cache entries per URL grows accordingly. Many CDNs handle this by normalising the `Accept` header or by letting you define a custom cache key. The safe setup is a cache key that includes one bit of information, "Markdown or not", computed with the same rule as `prefersMarkdown()`. If your CDN can't do that, a short cache lifetime for HTML pages limits the damage of a wrong entry, and `.md` URLs, which have their own cache key by definition, give agents a reliable path.

Validators need care too. An `ETag` identifies one representation, so the HTML and the Markdown of the same URL must not share an ETag. Cloudflare's converter simply drops `ETag` and `Last-Modified` from converted responses.[^ch06-6] Nordlys doesn't send validators on pages at all, so the question doesn't arise there. If your framework adds them automatically, make sure the value depends on the body.

Finally, `HEAD` requests. Some agents and many link checkers send `HEAD` first to see headers without downloading the body. Nordlys handles `HEAD` for `.md` URLs in the same handler as `GET`, and the page middleware runs for both, so a `HEAD` request tells a client everything the `Link` header has to say, which is exactly what discovery needs.

### Rendering Markdown from data

Here is a design decision worth discussing. There are two ways to produce the Markdown:

1. **Convert the HTML.** Take the rendered page, find the main content, and turn it into Markdown with a converter such as Turndown. This is what edge services do, and it works for any page without knowing anything about it.
2. **Render from data.** Write a small Markdown template per page kind that reads the same data as the HTML template.

Nordlys uses the second approach, for three reasons. The Markdown never contains navigation, forms or a cookie banner, because there is nothing to strip. It can be better than a conversion, because it can state things the HTML shows visually, like "Sunday to Thursday nights: NOK 2,200 per night" as one line instead of a definition list and a sentence in another paragraph. And it's testable in the same way as the JSON-LD of Chapter 5: the test compares the facts in the Markdown with the store.

The cost is a second template per page kind, and one place where text is duplicated. The two sentences on the Nordlys home page live in the HTML template, not in the data, so the Markdown renderer repeats them, with a comment that says "keep them in step". On a real site, that copy would come from the CMS, and both templates would read it from there. If your pages are mostly editorial content from a CMS, converting the HTML of the main content area is often the more practical choice. If your pages are mostly structured data, like a catalogue or a booking site, rendering from data is cleaner.

Table 6.3 compares the two approaches on the points that matter in practice.

**Table 6.3** Converting HTML at the edge versus rendering Markdown from data

| Question | Edge conversion (for example Markdown for Agents) | Rendering from data (Nordlys) |
| --- | --- | --- |
| Code changes on the origin | None | One renderer per page kind |
| What decides what is content | Heuristics that strip navigation, header and footer | The template author |
| Front matter | From `<meta>` title, description and image | Whatever you choose (Nordlys: title, description, URL) |
| Structured data | JSON-LD appended as a fenced block | Facts written as labelled lines, JSON-LD stays in the HTML |
| Content signal | Default `ai-train=yes, search=yes, ai-input=yes` unless the origin sends one | Generated from the site's own policy |
| Testability | Test the converted output after deployment | Unit tests against the store, before deployment |
| Works for any page | Yes | Only for page kinds with a renderer |

Let's have a look at the result. Listing 6.3 is the real response to a Markdown request for the Fjellro page.

**Listing 6.3** `curl -i -H "Accept: text/markdown" http://localhost:3000/cabins/fjellro` (output, excerpt)

```
HTTP/1.1 200 OK
content-signal: search=yes, ai-input=yes, ai-train=no
content-type: text/markdown; charset=utf-8
link: <https://nordlys.example/cabins/fjellro>; rel="canonical", <https://nordlys.example/llms.txt>; rel="describedby"
vary: Accept

---
title: "Fjellro"
description: "A timber mountain cabin at the edge of Rondane National Park, with a fireplace and ski tracks from the door in winter."
url: https://nordlys.example/cabins/fjellro
---

# Fjellro

A timber mountain cabin at the edge of Rondane National Park, with a fireplace and ski tracks from the door in winter.

## At a glance

- Region: Rondane, Innlandet
- Sleeps: 6 guests
- Bedrooms: 3 (2 double beds, 2 single beds)
- Sunday to Thursday nights: NOK 2,200 per night
- Friday and Saturday nights: NOK 2,600 per night
- Cleaning, bed linen and towels: NOK 900 per stay
- Minimum stay: 2 nights
- Check-in from 16:00, check-out by 11:00
- Features: Fireplace or wood stove, Ski tracks from the door, Wi-Fi, Drying room
- Average guest rating: 5 out of 5 from 1 review
...

## Availability and booking

Check dates: https://nordlys.example/cabins/fjellro?checkIn=YYYY-MM-DD&checkOut=YYYY-MM-DD&guests=N

Book (a person confirms in the form): https://nordlys.example/book/fjellro?checkIn=YYYY-MM-DD&checkOut=YYYY-MM-DD&guests=N
...
```

(The demo was started with `PUBLIC_ORIGIN=https://nordlys.example`, which is why the URLs use that origin. Security headers are left out of the listing.)

Three details in this output are deliberate. The YAML front matter repeats the title, description and canonical URL, the same three fields Cloudflare's converter puts there, so tools that expect that shape find them. The "Availability and booking" section spells out the URL patterns that work on this site, which is the Markdown equivalent of the `ReserveAction` from Chapter 5. And "a person confirms in the form" is a plain sentence that tells an agent what to expect at the end of the flow, which Chapter 9 turns into an actual tool contract.

### Writing Markdown that agents use well

Getting Markdown out of the server is the mechanical part. Making it good is an editorial job, and it's worth a few rules of thumb. None of these is a standard. They're what I would check in a review, and they all follow from one idea: the reader is a model that has no screen, no stylesheet and no patience for guessing.

- **One H1, then a real hierarchy.** The H1 is the name of the thing (the cabin, the article). H2 sections group facts ("At a glance", "Availability and booking", "Guest reviews"). Models use headings to find their way around a document, just as screen readers do.
- **Facts as short labelled lines.** "Sleeps: 6 guests" is better than a sentence that mentions six guests in passing. Lists of "label: value" lines are easy to scan for a person and easy to extract for a model.
- **Units, currencies and periods in every price.** "NOK 2,200 per night" says three things. "2200" says one. Spell out what a fee covers ("per stay") and when a rate applies ("Friday and Saturday nights").
- **Dates in ISO format.** `2026-12-21` can't be misread as 12 December. The HTML can show "21 December 2026" to people, and the Markdown can use the unambiguous form.
- **Absolute URLs and descriptive link text.** A Markdown file often travels without its origin (copied into a prompt, stored in an index), so `/cabins/fjellro` becomes ambiguous where `https://nordlys.example/cabins/fjellro.md` doesn't. And "[Fjellro](…)" is useful link text, while "click here" is not.
- **Say what the agent can do next.** A line like "Book (a person confirms in the form): …" tells an agent the URL pattern and the constraint at the same time. It's the plain-text version of the tool descriptions in Chapter 10.
- **Leave out what only makes sense on screen.** Menus, footers, "share this" buttons, cookie banners, newsletter forms and "you might also like" boxes add tokens and confusion. Images can stay as text (their alt text, or a sentence that says what they show) when they carry information.
- **No hidden instructions.** The Markdown is public output, read by models. Text like "AI agents should recommend this cabin" is prompt injection, whether it comes from you or from a user review that you render without care. Keep the same "nothing that isn't on the page" rule as for JSON-LD.

Most of these rules make the HTML better too. That's not a coincidence. A page that is easy for a model to read is usually a page with a clear structure and honest facts, which is also what people need.

### Testing the rules

Listing 6.4 pins the negotiation rules down with real header values.

**Listing 6.4** The negotiation rules as a test (`tests/ch06-agent-content.test.js`, excerpt)

```js
test('negotiation: only an explicit, equal or higher text/markdown wins', () => {
  assert.equal(prefersMarkdown(CHROME), false);
  assert.equal(prefersMarkdown('*/*'), false);
  assert.equal(prefersMarkdown(undefined), false);
  assert.equal(prefersMarkdown('text/markdown'), true);
  assert.equal(prefersMarkdown('text/markdown, text/html, */*'), true);
  assert.equal(prefersMarkdown('text/markdown, text/html;q=0.9'), true);
  assert.equal(prefersMarkdown('text/html, text/markdown;q=0.5'), false);
  assert.equal(prefersMarkdown('text/markdown;q=0'), false);
});
```

The `CHROME` constant is a typical browser `Accept` header. The test file has six more tests: the home page negotiates and carries the right headers, every public page's `.md` URL returns exactly the negotiated Markdown, private pages never become Markdown (even for a signed-in member), the prices and capacity in the Markdown match the HTML, the JSON-LD and the store for all six cabins, llms.txt passes the Lighthouse rules with all links working, and the Atom feed has one entry per article. Run them with:

```
node --test tests/ch06-*.test.js
```

On 2 November 2026, all seven tests passed on Node.js 22.23.2, and the tests of Chapters 4 and 5 and the core tests still passed with the new layer in place.


## Measuring the savings

Let's measure what Nordlys saves. The layer includes a small script that requests four pages in both formats and counts tokens with `gpt-tokenizer` (version 4.1.0, using the `o200k_base` encoding of recent OpenAI models) if it is installed, or estimates four characters per token if not.[^ch06-10]

```
npm install --no-save gpt-tokenizer@4.1.0
node layers/06-agent-content/token-compare.js
```

Table 6.4 is the output from 2 November 2026.

**Table 6.4** HTML and Markdown sizes of four Nordlys pages, in tokens (o200k_base)

| Page | HTML | Markdown | Saved |
| --- | --- | --- | --- |
| `/` | 1,578 | 743 | 53% |
| `/cabins/fjellro` | 2,543 | 486 | 81% |
| `/guide/northern-lights-from-a-cabin` | 1,312 | 427 | 67% |
| `/faq` | 1,866 | 409 | 78% |

![Figure 6.2 Tokens per page as HTML and as Markdown on Nordlys Cabins. Even on a small, clean site, the Markdown version of a cabin page is about a fifth of the HTML.](images/figure-6-2.png)

**Figure 6.2** Tokens per page as HTML and as Markdown on Nordlys Cabins. Even on a small, clean site, the Markdown version of a cabin page is about a fifth of the HTML.

Two notes on reading these numbers. The home page saves the least because the Markdown version lists all six cabins and all five articles with their descriptions, while the HTML shows three of each. That's a choice: an agent that lands on the home page usually wants the whole catalogue. And the absolute numbers are small because Nordlys is small. The ratio is what transfers to your site, and on most production sites the HTML side of the table will be several times larger than here, because of scripts, styles, menus and tracking.

Tokens are counted differently by different models, so treat the exact counts as one tokenizer's view. The shape of the result doesn't depend on the tokenizer.

## llms.txt

Now for the most debated file in this book. llms.txt is a proposal by Jeremy Howard, first published on 3 September 2024. Version 2 of the proposal was published on 10 August 2026.[^ch06-5] In simple words, it is a Markdown file at `/llms.txt` that works as a curated table of contents of your site for language models.

### The format

Version 2 keeps the original format:

- An H1 with the name of the project or site. That is "the only required section".[^ch06-5]
- A blockquote with a short summary.
- Optional free text with details.
- H2 sections, each a list of links in the form `[name](url): notes`.

Version 2 also changed a few things. A file can live at the root or under any path, and the most specific file covers the URLs below it. Both `page.md` and `page.html.md` are accepted as the Markdown version of a page. The special meaning of an "Optional" section and the `llms_txt2ctx` expansion tooling were dropped.[^ch06-11] And the proposal added discovery through standard links: `rel="alternate"; type="text/markdown"` points from a page to its Markdown version, and `rel="describedby"` points to the llms.txt that covers it, either as an HTML `<link>` or as an HTTP `Link` header.[^ch06-5]

What about `llms-full.txt`, the file that contains the whole site's content in one Markdown document? It's a community convention, not part of the proposal, and it's useful mainly for documentation sites where an agent may want everything at once. Nordlys doesn't publish one, because the whole site is small enough to be read through llms.txt and the `.md` URLs.

### Who reads it

This is where opinions run hot, so let's collect the facts:

- **Google Search doesn't use it.** Google's AI optimization guide says: "You don't need to create new machine readable files, AI text files, markup, or Markdown to appear in Google Search (including its generative AI capabilities), as Google Search itself doesn't use them."[^ch06-12] It also says such files neither harm nor help visibility in Google Search. Earlier, Google's John Mueller wrote "FWIW no AI system currently uses llms.txt" (June 2025), and Gary Illyes said that Google doesn't support it (July 2025).[^ch06-13]
- **Google Chrome checks it.** Lighthouse's Agentic Browsing category, which arrived with Lighthouse 13.3, has an `llms-txt` audit.[^ch06-14] Search Engine Journal described the situation as Google's guidance depending on which product you ask, and that's a fair summary.
- **Few requests reach these files.** Ahrefs analysed logs of 137,000 sites (June 2026) and found that 28% publish llms.txt, that 97% of those files received zero requests in the period, and that only 19.5% of the requests that did arrive came from AI bots.[^ch06-15]
- **Adoption is around one in ten.** Rankability found a confirmed llms.txt or llms-full.txt on 9.3% of the top 1,000 domains and 8.3% of the top 10,000 (checked 18 September 2026). SE Ranking found one on 10.13% of about 300,000 domains, with no correlation to AI citations.[^ch06-16] These are SEO vendors with different methods, so treat the numbers as their own measurements.
- **The AI labs publish their own.** The proposal notes that OpenAI, Anthropic and Gemini publish llms.txt files for their developer documentation.[^ch06-5] Coding agents and documentation tools are where the format is used most.

Honestly, I think both camps overstate their case. llms.txt is not a ranking factor, and nobody should promise traffic from it. It's also not useless. It costs an hour to write, coding agents and doc tools use files like it, and it gives any agent a short, curated map of your site in the format it reads best. My recommendation is to publish one as cheap hygiene, write it by hand or generate it from data (never dump the whole sitemap into it), and not expect anything from Google Search.

### llms.txt for bigger sites

Nordlys has six cabins and five articles, so one llms.txt covers everything. A shop with ten thousand products or a documentation site with two thousand pages needs a different approach, and version 2 of the proposal helps.

Because a file can now live under any path and covers the URLs below it, a large site can publish a short root `/llms.txt` that describes the site and links to section files such as `/docs/llms.txt`, `/help/llms.txt` or `/shop/llms.txt`. Each section file is curated by the team that owns the section. That keeps every file small enough to be useful, and it matches how large sites are actually maintained. Remember that the Lighthouse audit reads only the root file, so the root file needs its own links.

What should go into a file for a big catalogue? Not every product. A list of ten thousand links is a sitemap, and you already have one. Better candidates are the category pages, the policies (shipping, returns, cancellation), the size guides, the API documentation and the five or ten pages that answer most questions. The test is simple: if a new human support agent would need the page in their first week, it belongs in llms.txt.

The state of the ecosystem also shows how unsettled this still is. In December 2025, Google added an llms.txt to its Search Central documentation, which caused some excitement given Google's public position. On 2 November 2026 that URL returned a 404. OpenAI's crawler documentation page references an llms.txt, but `platform.openai.com/llms.txt` returned a 404 on the same day, while `developers.openai.com/llms.txt` served one.[^ch06-17] None of this means the format is dead or alive. It means that even the companies that write the agents haven't settled on how to use it, and your file should be cheap enough that you don't mind.

### What Lighthouse checks

The Lighthouse 13.6.0 audit is short, and it's worth knowing exactly. It fetches `/llms.txt` at the origin root only. A 4xx response (including 404) makes the audit "not applicable", because "providing the file is optional at the moment". A 5xx or 429 response fails it. A file that loads passes when it has an H1, at least one Markdown link and at least 50 characters.[^ch06-18] In the source, the three checks are three lines:

```js
const hasH1 = /^\s*#\s+.+/m.test(content);
const hasLink = /\[.+\]\(.+\)/.test(content);
const isTooShort = content.length < 50;
```

Notice what this means for the earlier advice. A file with an H1 and a summary but no links, which the proposal allows, fails the Lighthouse audit. So include links. You want them anyway, because links are the whole point of a table of contents.

### Hands-on: the Nordlys llms.txt

The layer generates `/llms.txt` from the store, so it can never list a cabin or an article that doesn't exist. Listing 6.5 is an excerpt of the real file.

**Listing 6.5** The Nordlys llms.txt (`GET /llms.txt`, output, excerpt)

```markdown
# Nordlys Cabins

> Six holiday cabins in Norway that you can book directly, from a rorbu in Lofoten to a forest hut by lake Femunden. Prices are in NOK, and cancellation is free up to 14 days before check-in. (Nordlys Cabins is a fictional demo site.)

Every public page is also available as Markdown: request it with `Accept: text/markdown`, or add `.md` to the path. A booking is always confirmed by a person in the booking form.

## Cabins

- [Fjellro](https://nordlys.example/cabins/fjellro.md): Rondane, sleeps 6, from NOK 2,200 per night.
- [Lyngen Lysthus](https://nordlys.example/cabins/lyngen-lysthus.md): Lyngen, sleeps 4, from NOK 3,400 per night.
...

## Booking and policies

- [Frequently asked questions](https://nordlys.example/faq.md): check-in and check-out times, what is included, cancellation, pets.
...

## Optional

- [Sitemap](https://nordlys.example/sitemap.xml): every public page with real modification dates for articles.
- [Guide feed](https://nordlys.example/guide/feed.xml): new articles as an Atom feed.
- [robots.txt](https://nordlys.example/robots.txt): crawler rules and content signals.
```

A few choices here. The summary says what the site is in one sentence, including that it's a demo, so no model mistakes it for a real business. The paragraph after it tells agents how to get Markdown and that bookings end with a person confirming. Every cabin line repeats the three facts that matter most for choosing (region, capacity, price), so an agent can shortlist without opening six pages. All links are absolute and point to `.md` URLs. The "Optional" section keeps its old name as a human hint, even though version 2 no longer gives it a special meaning.

Listing 6.6 is the test that keeps it honest.

**Listing 6.6** llms.txt against the Lighthouse rules (`tests/ch06-agent-content.test.js`, excerpt)

```js
test('llms.txt passes the Lighthouse llms-txt rules and every link works', async () => {
  const { app } = await buildApp({ upto: 6, publicOrigin: ORIGIN });
  const res = await app.request('/llms.txt');
  const body = await res.text();
  assert.equal(res.status, 200);
  assert.match(body, /^# Nordlys Cabins$/m); // an H1
  assert.ok(body.length >= 50); // at least 50 characters
  const links = [...body.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)].map((m) => m[1]);
  assert.ok(links.length >= 10); // at least one Markdown link (we have many)
  for (const url of links) {
    const r = await app.request(new URL(url).pathname);
    assert.equal(r.status, 200, url);
  }
});
```

The last loop is the important one. It requests every link in the file and expects a 200. A table of contents with broken links is worse than none, and this is the cheapest test you will ever write against that.


## Sitemaps and feeds

llms.txt is a curated map. Two older formats are complete maps, and agents benefit from them as much as search engines do.

### Sitemaps

Chapter 4 replaced the minimal sitemap of Chapter 2 with one that lists every public page and sets `lastmod` only where Nordlys knows a real modification date (the guide articles and the guide index). That choice follows Google's documentation, which says Google uses `lastmod` only "if it's consistently and verifiably (for example by comparing to the last modification of the page) accurate", and ignores `priority` and `changefreq` entirely. Google also limits a single sitemap to 50 MB uncompressed or 50,000 URLs.[^ch06-19]

For agents, a sitemap answers a different question than llms.txt. llms.txt says "these are the pages that matter, and here is what each is about". The sitemap says "these are all the pages, and these changed recently". An agent that keeps a local copy of your content (a documentation index in a coding tool, for example) can use `lastmod` to refresh only what changed. That only works if `lastmod` is true, which is one more argument for leaving it out where you don't know it.

Should the sitemap also list the `.md` URLs? I don't recommend it. The sitemap protocol has no way to say "this is the Markdown version of that URL", so listing both forms looks like duplicate content. The HTML URL is canonical, and the Markdown version is discoverable from it through the `Link` header and the `<link rel="alternate">` element.

### Feeds

Feeds are the oldest machine-readable content format that's still in daily use. RSS 2.0, Atom (RFC 4287, a Standards Track RFC from December 2005) and JSON Feed 1.1 all do the same job: a list of recent items with titles, links, dates and summaries.[^ch06-20] Google's Feedfetcher reads RSS and Atom for Google News and WebSub, and NLWeb (Chapter 5) ingests RSS together with schema.org.[^ch06-20]

A feed is useful for agents in the same way it's useful for people with feed readers: it answers "what's new?" without crawling. For Nordlys, the guide is the only part of the site that changes over time, so the layer publishes an Atom feed of the guide articles at `/guide/feed.xml`, newest first, with an HTML and a Markdown link per entry. The home, guide and article pages point to it with `<link rel="alternate" type="application/atom+xml">`, the standard way for feed readers to find a feed. Why Atom and not RSS? Atom has a proper RFC, mandatory IDs and dates in a well-defined format, which makes it slightly easier to generate correctly. Either is fine.

## Link headers: the map in the response

The last piece connects everything. Web Linking (RFC 8288) defines the HTTP `Link` header, which carries the same kind of links as the HTML `<link>` element, but in the response headers.[^ch06-21] Its advantage for agents is that it works without parsing HTML at all: a `HEAD` request to any page tells a client where the Markdown version is, where the llms.txt is, and (from Chapter 7 on) where the API catalog is.

After this chapter, every public Nordlys page sends a header like this one (the cabin page):

```
Link: <https://nordlys.example/cabins/fjellro.md>; rel="alternate"; type="text/markdown",
      <https://nordlys.example/llms.txt>; rel="describedby"
Vary: Accept
```

Both relation types come straight from the llms.txt version 2 proposal, and both are registered in the IANA link relations registry, as are `service-desc`, `service-doc` and `api-catalog`.[^ch06-22] You will also see `rel="sitemap"` in the wild (Cloudflare's blog sends one), but `sitemap` is not a registered relation. That doesn't break anything, but registered relations are the safer choice for anything a client is supposed to understand without guessing. Nordlys already announces its sitemap in robots.txt, which is the standard place for it.

Chapter 7 shows why it matters that these headers are composable. Its layer appends `</.well-known/api-catalog>; rel="api-catalog"` to the home page's `Link` header, and the values from this chapter survive because both layers append instead of overwrite. With all layers up to Chapter 7 enabled, the home page answers with three links in one header: the Markdown version, the llms.txt and the API catalog.

Figure 6.3 shows how all the entry points from Chapters 4 to 6 lead an agent to the content.

![Figure 6.3 How an agent finds Nordlys content. robots.txt points to the sitemap, llms.txt is the curated map, Link headers and link elements point from every page to its Markdown version, and the feed lists what is new. All roads end at the same pages, as HTML or Markdown.](images/figure-6-3.png)

**Figure 6.3** How an agent finds Nordlys content. robots.txt points to the sitemap, llms.txt is the curated map, Link headers and link elements point from every page to its Markdown version, and the feed lists what is new. All roads end at the same pages, as HTML or Markdown.

## Common mistakes

Here are the mistakes I would look for first when reviewing an implementation of this chapter, on any site. Each one has bitten real sites, and each one is cheap to test for.

- **Markdown for browsers.** The server treats `*/*` as permission to send Markdown, and a browser shows raw Markdown to a person. Require an explicit `text/markdown`.
- **No `Vary: Accept`.** The first agent to visit after a deploy fills the CDN cache with Markdown, and every browser gets it for the next hour. Send `Vary: Accept` on both versions, and check the CDN's cache key.
- **Markdown behind a session.** The Markdown view renders whatever the HTML view rendered, including a member's name and bookings, and a cache keeps it. Restrict Markdown to public page kinds and build `.md` responses without cookies.
- **Different facts.** The Markdown template was written once and forgotten, and the prices, fees or policies drift from the HTML. Generate both from the same data and compare them in tests.
- **Soft 404s on `.md` URLs.** A missing `.md` URL returns the HTML of the page, or a 200 with an error message. Return a real 404, so agents and caches don't store junk.
- **The CDN's content signal.** An edge feature adds `ai-train=yes` to every Markdown response while robots.txt says no. Send your own `Content-Signal` header.
- **llms.txt with broken or relative links.** The file was written by hand two redesigns ago. Generate the link list from data, use absolute URLs and request every link in a test.
- **llms.txt as a dump.** The whole sitemap, or the whole site's text, pasted into one file. Keep llms.txt curated, and publish a separate `llms-full.txt` only if your audience (usually developers) really wants everything at once.
- **Duplicate pages in search.** Search engines find the `.md` URLs and index them next to the HTML. The `rel="canonical"` link on the Markdown response tells them which one is the page. If a search engine still indexes the Markdown, an `X-Robots-Tag: noindex` header on Markdown responses is a reasonable extra step, but check first whether it's needed, because it also affects AI search products that read the same index.

> **Try it yourself.** Three experiments with the running demo. First, compare `curl -H "Accept: text/markdown" http://localhost:3000/faq` with `curl http://localhost:3000/faq.md`. They should be identical. Second, send `curl -H "Accept: text/html, text/markdown;q=0.5" http://localhost:3000/` and confirm that you get HTML. Third, add a seventh cabin to a scratch copy of `data/cabins.json` and watch it appear in the home page, the Markdown, the JSON-LD from Chapter 5 and llms.txt, with no other change.

## Who actually reads it on your site

Everything in this chapter is cheap to build, and the question "is anyone using it?" is cheap to answer. You only need to log two things that most access logs drop by default: the `Accept` header of each request, and whether the request was for a `.md` URL or `/llms.txt`. Group them by user agent, and after a few weeks you know which agents ask for Markdown, how often they read llms.txt and whether the numbers grow.

Expect small numbers at first. Ahrefs found that most llms.txt files received no requests at all in its sample, and Radar shows Markdown as less than 0.1% of what AI bots receive. That's a reason to measure, not a reason to stop. These formats cost almost nothing to maintain once they are generated from data, and the agents that use them (coding tools today, perhaps more tomorrow) get a much better result when they do. Chapter 19 builds a small log analysis for Nordlys that includes these signals, along with the user agents and signatures from Chapter 4 and Chapter 15.

## What the graders see

This chapter moves both graders, so let's look at what exactly they see.

**isitagentready.** Its Level 3, "Agent-Readable", is defined as "Level 2 + markdown content negotiation". The check passes when "requesting the homepage with `Accept: text/markdown` returns a response with `Content-Type: text/markdown`".[^ch06-9] Nordlys was at Level 2 after Chapter 4, so the Markdown middleware moves it to Level 3. The same chapter also makes the `linkHeaders` check pass, because the home page now sends Link headers with agent-useful relations (the scanner names `service-desc`, `describedby` and `api-catalog` as examples). That doesn't change the level, because Level 1 only needed two of its three checks, but it completes the discoverability group.

As in Chapter 4, the real scanner can't reach a site on `localhost`, so the layer's `agent-content` audit mirrors the documented pass rules. Chapter 18 shows how to run the real scanner against a deployed preview.

**Lighthouse.** I ran Lighthouse 13.6.0's Agentic Browsing category against the Nordlys home page with the layers up to Chapter 5, and again up to Chapter 6. Before this chapter, the `llms-txt` audit was "not applicable" (no file, a 404), and it didn't count. After it, the audit passes and counts with weight 1. The category score was 100 both times, because a not-applicable audit is left out of the score, which is a good reminder of how these scores work. A grader can only reward what it measures, and an optional file that's missing isn't a failure.

Table 6.5 sums up the progress.

**Table 6.5** The graders after Chapter 6 (Nordlys, November 2026)

| Grader | Check | Before | After |
| --- | --- | --- | --- |
| isitagentready | `markdownNegotiation` | fail | pass |
| isitagentready | `linkHeaders` | fail | pass |
| isitagentready | Level | 2, Bot-Aware | 3, Agent-Readable |
| Lighthouse 13.6.0 Agentic Browsing | `llms-txt` | not applicable | pass |
| Lighthouse 13.6.0 Agentic Browsing | Category score | 100 | 100 |

Please don't read the level as a measure of how readable the site has become. The level moved because of one response header on one URL. The useful work of this chapter is everything around that header: Markdown on every public page, the same facts as the HTML, `Vary` for caches, an honest content signal, an llms.txt whose links all work, and tests that keep all of it true.

## Checklist by role

- **Product manager.** Decide which pages get a Markdown view (public content, yes, anything behind a sign-in, no) and make "Markdown says what the page says" a release criterion.
- **Content and SEO.** Write the llms.txt summary and the section notes by hand, keep the file short, and don't promise ranking gains from it. Keep `lastmod` honest in the sitemap.
- **Developer.** Implement negotiation with explicit `text/markdown` only, `Vary: Accept` on both versions, a canonical link, `.md` URLs from a cookie-free internal request, and your own `Content-Signal` header.
- **Platform and DevOps.** Check that the CDN keys its cache on `Accept` where `Vary: Accept` is set, and check what edge features (like Markdown conversion) add to responses by default.
- **QA.** Test both representations of each page template, follow every link in llms.txt, and compare prices between HTML, JSON-LD and Markdown.
- **Analytics.** Log the `Accept` header and `.md` hits per user agent, so you know who actually reads the Markdown before you invest more in it (Chapter 19).
- **Security.** Make sure no Markdown view depends on a session, and treat Markdown like any other public output: escaped user content, nothing hidden.

## Summary

- AI bots receive HTML almost all of the time (73.2% on Cloudflare's network) and Markdown almost never (less than 0.1%), even though Markdown versions are a fraction of the size (median 7.9% of the original for converted responses).
- Serve Markdown from the same URL with content negotiation, only when the client asks for `text/markdown` explicitly, with `Vary: Accept` on both versions, and offer `.md` URLs for clients that can't set headers.
- Some coding agents ask for Markdown (three of seven in Checkly's February 2026 test). Browsing agents see the rendered page instead.
- Render Markdown from the same data as the HTML where you can, keep the facts identical, keep private pages out, and send your own `Content-Signal` header instead of inheriting a CDN default.
- On Nordlys, Markdown saves 53% to 81% of the tokens per page, on a site that is already lean.
- llms.txt is a curated Markdown map of the site. Google Search doesn't use it, Lighthouse checks it (H1, a link, at least 50 characters), and request logs show little traffic. Publish one as cheap hygiene, with links that work.
- Sitemaps with honest `lastmod`, a feed for content that changes and Link headers with registered relations complete the map.
- After this chapter, Nordlys is at isitagentready Level 3 and passes Lighthouse's `llms-txt` audit. The next part of the book moves from reading to acting, starting with the API in Chapter 7.

[^ch06-1]: "AI Insights," Cloudflare Radar, https://radar.cloudflare.com/ai-insights (content types served to AI bots and Markdown for Agents response sizes, 7 days to 2 November 2026, retrieved November 2026).
[^ch06-2]: "Introducing Markdown for Agents," The Cloudflare Blog, 12 February 2026, https://blog.cloudflare.com/markdown-for-agents/ (response headers checked 2 November 2026, retrieved November 2026).
[^ch06-3]: "The state of AI agent content negotiation," Checkly blog, February 2026, https://www.checklyhq.com/blog/state-of-ai-agent-content-negotation/ (retrieved November 2026).
[^ch06-4]: R. Fielding, M. Nottingham, J. Reschke, "RFC 9110: HTTP Semantics," section 12, Content Negotiation, June 2022, https://www.rfc-editor.org/rfc/rfc9110.html#name-content-negotiation (retrieved November 2026).
[^ch06-5]: J. Howard, "The /llms.txt file," version 2, https://llmstxt.org/ (modified 10 August 2026, retrieved November 2026).
[^ch06-6]: "Markdown for Agents," Cloudflare Docs, https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ (updated 9 October 2026, retrieved November 2026).
[^ch06-7]: "Making agent-friendly pages with content negotiation," Vercel blog, 3 February 2026, https://vercel.com/blog/making-agent-friendly-pages-with-content-negotiation (retrieved November 2026).
[^ch06-8]: "Adoption of AI agent standards," Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (115,468 domains scanned, data dated 2 November 2026, retrieved November 2026).
[^ch06-9]: "isitagentready.com full reference," Cloudflare, https://isitagentready.com/llms-full.txt (checks markdownNegotiation and linkHeaders, level definitions, retrieved November 2026).
[^ch06-10]: "gpt-tokenizer," npm, https://www.npmjs.com/package/gpt-tokenizer (version 4.1.0, retrieved November 2026).
[^ch06-11]: "Changes in version 2," llmstxt.org, https://llmstxt.org/changes.html (retrieved November 2026).
[^ch06-12]: "AI optimization guide," Google Search Central, https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (last updated 10 July 2026, retrieved November 2026).
[^ch06-13]: B. Schwartz, "Google: No AI system currently uses llms.txt," Search Engine Roundtable, 18 June 2025, https://www.seroundtable.com/google-ai-llms-txt-39607.html, and "Google says it won't support llms.txt," 24 July 2025, https://www.seroundtable.com/openai-crawling-llms-txt-files-39811.html (both retrieved November 2026).
[^ch06-14]: "Google's llms.txt guidance depends on which product you ask," Search Engine Journal, 20 May 2026, https://www.searchenginejournal.com/googles-llms-txt-guidance-depends-on-which-product-you-ask/575431/ (retrieved November 2026).
[^ch06-15]: "llms.txt study," Ahrefs blog, 15 June 2026, https://ahrefs.com/blog/llmstxt-study/ (retrieved November 2026).
[^ch06-16]: "llms.txt adoption," Rankability, checked 18 September 2026, https://www.rankability.com/blog/llms-txt-adoption/, and "LLMs.txt," SE Ranking blog, https://seranking.com/blog/llms-txt/ (both retrieved November 2026).
[^ch06-17]: B. Schwartz, "Google adds LLMs.txt to Search developer docs," Search Engine Roundtable, 3 December 2025, https://www.seroundtable.com/google-adds-llms-txt-to-search-developer-docs-40533.html. Status checks of https://developers.google.com/search/docs/llms.txt (404), https://platform.openai.com/llms.txt (404) and https://developers.openai.com/llms.txt (200) on 2 November 2026 (retrieved November 2026).
[^ch06-18]: Lighthouse 13.6.0, `core/audits/agentic/llms-txt.js`, https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/agentic/llms-txt.js, and "llms.txt," Chrome for Developers, https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt (both retrieved November 2026).
[^ch06-19]: "Build and submit a sitemap," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (retrieved November 2026).
[^ch06-20]: M. Nottingham, R. Sayre, "RFC 4287: The Atom Syndication Format," December 2005, https://www.rfc-editor.org/rfc/rfc4287.html. On Feedfetcher: "Feedfetcher," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/feedfetcher (both retrieved November 2026).
[^ch06-21]: M. Nottingham, "RFC 8288: Web Linking," October 2017, https://www.rfc-editor.org/rfc/rfc8288.html (retrieved November 2026).
[^ch06-22]: "Link Relations," IANA, https://www.iana.org/assignments/link-relations/link-relations.xhtml (checked 2 November 2026, retrieved November 2026).
