# Chapter 2: Your first agent-ready page

This chapter covers

- Measuring a page with isitagentready.com and Lighthouse's Agentic Browsing category
- A local version of isitagentready's checks that also works on `localhost`
- A first look at your own access logs
- Watching a structure-only agent try to book a cabin, and fail
- Fixing the page with semantic HTML, a robots.txt, a sitemap and one declarative WebMCP tool
- The habit for the rest of the book: measure, change one layer, measure again

Chapter 1 was the map. This chapter is the walk. We take one real page, the booking page of Nordlys Cabins, in its agent-hostile legacy version, and do everything once: measure it with the two graders, take a first look at who already visits, watch an agent try to use the page, fix it in three small steps and measure again. Every topic here has its own chapter later. The point of doing it all once, quickly, is to feel the loop.

## The page we start with

The page is `/cabins/fjellro`, the detail page for Fjellro, a mountain cabin in Rondane. A person who opens it sees a photo, a description, the price per night and a small widget: two date boxes, a guest counter with minus and plus, a "Check" button and, after a successful check, a "Book now" button that opens a booking form in an overlay. It is a perfectly normal-looking booking page. Most of us have built one like it.

Here is the widget as the browser has it in the DOM, after the page's JavaScript has run (I captured it with Playwright and only added line breaks):

```html
<div class="widget">
  <div class="dates">
    <div class="date-wrap"><input class="date-input" placeholder="Check-in" readonly=""></div>
    <div class="date-wrap"><input class="date-input" placeholder="Check-out" readonly=""></div>
  </div>
  <div class="stepper"><div class="step minus">−</div><span class="count">2</span><div class="step plus">+</div></div>
  <div class="btn btn-primary">Check</div>
  <div class="result"></div>
  <div class="btn btn-book hidden">Book now</div>
</div>
```

Let's have a look at what this markup tells a machine. There is no `<form>`, so nothing says "this is something you submit". The two date inputs are read-only and have no label, only placeholder text (clicking them opens a custom calendar built from more `<div>` elements). The guest counter is a `<span>` between two `<div>` elements that happen to contain a minus and a plus sign. The "Check" and "Book now" buttons are `<div>` elements with a CSS class and a click handler. And the whole widget is not in the HTML the server sends at all: the page's script fetches the cabin data and injects it about 400 milliseconds after the page loads.

> **Hands-on:** The rest of this section and the next three sections run commands against the demo site. You need Node.js 24 or later, the demos repository (https://github.com/webmaxru/agent-ready-web-demos) and about ten minutes. If you do not run code, read the outputs in the text and pick up again at "What a screenshot agent would do". The numbers in this chapter were measured on 2 November 2026 with Chromium 156.0.8078.4, Playwright 1.64.1 and Lighthouse 13.6.0.

Start the baseline, which is the legacy front end with no chapter layers:

```sh
cd agent-ready-web-demos
npm install
npm run start:baseline -w nordlys-cabins
```

The site runs at http://127.0.0.1:3000. Open http://127.0.0.1:3000/cabins/fjellro in a browser, play with the widget, and then let's measure it.

## Measuring the baseline

We use three instruments in this chapter, and the rest of the book uses the same three. Two of them are the graders from Chapter 1. The third is an agent, or rather a small, honest stand-in for one. Each instrument answers a different question (Figure 2.1), and you will see that you need all three.

![Figure 2.1 — The loop this book follows for every layer. Measure the page with three instruments (a server-side scan in the style of isitagentready.com, Lighthouse's Agentic Browsing category and a scripted agent walk), change one layer, then measure again and record which checks moved.](images/figure-2-1.png)

### Scanning a public site with isitagentready

The real isitagentready.com scanner runs on Cloudflare's servers, so it can only scan sites on the public internet. For a public site you can use the web page, or call its API directly. This is the request:

```sh
curl -s -X POST https://isitagentready.com/api/scan \
  -H 'content-type: application/json' \
  -d '{"url":"https://salnikov.no"}'
```

The response is JSON with a `level`, a `levelName`, the result of every check with a status and a message, and a `nextLevel` object that says what to fix first. The research for this book scanned my own site, salnikov.no, on 2 November 2026. This is the top of the response, shortened to four of the checks:

```json
{
  "scannedAt": "2026-11-02T20:59:58.009Z",
  "level": 1,
  "levelName": "Basic Web Presence",
  "nextLevel": { "target": 2, "name": "Bot-Aware", "requirements": ["contentSignals"] },
  "checks": {
    "robotsTxt": { "status": "pass", "message": "robots.txt exists with valid format" },
    "linkHeaders": { "status": "fail", "message": "No Link headers found on target page" },
    "markdownNegotiation": { "status": "fail", "message": "Site does not support Markdown for Agents" },
    "contentSignals": { "status": "fail", "message": "No Content Signals found in robots.txt" }
  }
}
```

robots.txt and the sitemap passed. The robots.txt even names a long list of AI crawlers (GPTBot, ClaudeBot, PerplexityBot and others), so "AI bot rules" passed too. Link headers, Markdown negotiation, Content Signals and every discovery file failed, and the next-level hint says exactly one thing: `contentSignals`.[^ch02-1] So my own site is one robots.txt line away from Level 2. The shoemaker's children, as they say :)

If you work with a coding agent, the same scanner is available as a tool: isitagentready.com runs a stateless MCP server at `https://isitagentready.com/mcp` with one tool, `scan_site`, which takes a URL and returns the same result. Chapter 12 uses the API in CI.

### A local scanner for localhost

Our site runs on `127.0.0.1`, which Cloudflare's servers cannot reach. You could deploy every change to a public preview, or open a tunnel, and some teams will. For this book I wanted something faster: a small script that performs the checks isitagentready documents, against any origin, with the same check ids and the same level rules.

isitagentready publishes its rules in plain language in its full documentation file, https://isitagentready.com/llms-full.txt. Each check has a "Pass criteria" line, and the level system is spelled out. So the companion script, `agent-ready-check.mjs` in the folder `chapters/02-your-first-agent-ready-page/` of the demos repository, is mostly those sentences turned into code. It needs Node.js 20 or later (for the global `fetch`) and no dependencies. Listing 2.1 shows the first two checks. Each one is a couple of HTTP requests and a test against the pass criteria.

**Listing 2.1** `chapters/02-your-first-agent-ready-page/agent-ready-check.mjs` — the robots.txt and sitemap checks (excerpt)

```js
  r.robotsTxt = robots.ok && robots.type.startsWith('text/plain') && /^\s*user-agent\s*:/im.test(robots.text)
    ? pass('robots.txt returns 200 text/plain with a User-agent line')
    : fail(`robots.txt: HTTP ${robots.status} ${robots.type || ''}`.trim());

  const sitemapRes = await get(at('/sitemap.xml'));
  const sitemapXml = sitemapRes.ok && /<(urlset|sitemapindex)[\s>]/.test(sitemapRes.text);
  const sitemapLine = /^\s*sitemap\s*:\s*\S+/im.test(robotsText);
  r.sitemap = sitemapXml || sitemapLine
    ? pass(sitemapXml ? '/sitemap.xml is valid XML' : 'Sitemap directive in robots.txt')
    : fail('no /sitemap.xml and no Sitemap line in robots.txt');
```

Listing 2.2 is the level ladder from Table 1.2 in Chapter 1, almost word for word. When a level is not met, the function returns the failing check ids as the requirements for the next level, the way the real scanner does.

**Listing 2.2** `chapters/02-your-first-agent-ready-page/agent-ready-check.mjs` — the level rules (excerpt)

```js
/** The level rules, as isitagentready.com documents them. `next` names the failing checks. */
export function computeLevel(r) {
  const ok = (id) => r[id]?.status === 'pass';
  const failing = (ids) => ids.filter((id) => !ok(id));
  const integration = ['mcpServerCard', 'a2aAgentCard', 'agentSkills', 'apiCatalog'];
  const auth = ['oauthDiscovery', 'oauthProtectedResource', 'authMd'];
  const basics = ['robotsTxt', 'sitemap', 'linkHeaders'];
  const steps = [
    { target: 1, met: basics.filter(ok).length >= 2, needs: failing(basics) },          // 2 of 3
    { target: 2, met: ok('robotsTxtAiRules') && ok('contentSignals'), needs: failing(['robotsTxtAiRules', 'contentSignals']) },
    { target: 3, met: ok('markdownNegotiation'), needs: ['markdownNegotiation'] },
    { target: 4, met: integration.some(ok), needs: integration },                          // 1 of 4
    {
      target: 5,                                                                           // 2 of 3
      met: [ok('webBotAuth'), integration.every(ok), auth.some(ok)].filter(Boolean).length >= 2,
      needs: ['webBotAuth', ...failing(integration), ...(auth.some(ok) ? [] : auth)],
    },
  ];
  let level = 0;
  for (const step of steps) {
    if (!step.met) return { level, next: { target: step.target, name: LEVELS[step.target], requirements: step.needs } };
    level = step.target;
  }
  return { level, next: null };
}
```

Two checks cannot work exactly as the real ones do. DNS-AID needs a public hostname with DNSSEC, so on `127.0.0.1` the script answers `unableToCheck`. And the real scanner finds WebMCP tools by loading the page in a headless browser. A script without a browser can only look for declarative forms in the HTML and for `registerTool()` calls in the page's own script files, and it says so. For the browser view we have Lighthouse.

> **Note:** A re-implementation is only as good as its last comparison with the original. On 2 November 2026 the script gave the same level as the real scanner for all six public sites I compared (salnikov.no, isitagentready.com, vercel.com, developer.chrome.com, docs.stripe.com and allbirds.com), with individual checks differing in three expected places. When the two disagree, the real scanner wins.

Run it against the baseline:

```sh
node chapters/02-your-first-agent-ready-page/agent-ready-check.mjs http://127.0.0.1:3000/cabins/fjellro
```

```text
http://127.0.0.1:3000/cabins/fjellro

discoverability       robotsTxt               fail           robots.txt: HTTP 404 text/html; charset=UTF-8
discoverability       sitemap                 fail           no /sitemap.xml and no Sitemap line in robots.txt
discoverability       linkHeaders             fail           no agent-useful Link header on /
discoverability       dnsAid                  unableToCheck  DNS-AID needs a public hostname
contentAccessibility  markdownNegotiation     fail           Accept: text/markdown on / returns text/html; charset=UTF-8
botAccessControl      robotsTxtAiRules        fail           no AI bot rules in robots.txt
botAccessControl      contentSignals          fail           no Content-Signal line in robots.txt
botAccessControl      webBotAuth              neutral        no key directory (informational, does not affect the level)

Level 0: Not Ready
Next: Level 1 (Basic Web Presence), work on: robotsTxt, sitemap, linkHeaders
```

(I kept the first nine checks and the summary. Every discovery check fails and the commerce checks are neutral.) Level 0. No robots.txt, no sitemap, nothing for agents at all. The interesting result is the next one.

### Lighthouse's Agentic Browsing category

The second grader looks at the page from inside a real browser. Lighthouse has shipped the Agentic Browsing category since version 13.2.0, and it runs only that category with one flag:

```sh
npx lighthouse@13.6.0 http://127.0.0.1:3000/cabins/fjellro \
  --only-categories=agentic-browsing \
  --chrome-flags="--headless=new --enable-features=WebMCPTesting" \
  --output=json --output-path=./baseline.json
```

Please note: the category needs Chrome 150 or later, and the WebMCP audits only see tools when WebMCP is switched on, through the origin trial on your own origin or with the `WebMCPTesting` feature flag shown here.[^ch02-2]

Here is what Lighthouse 13.6.0 said about the baseline page:

| Audit | Result on the baseline |
|---|---|
| `agent-accessibility-tree` | Passed ("All audits passed") |
| `cumulative-layout-shift` | 0.116, failed (the good threshold is 0.1) |
| `webmcp-form-coverage` | Not applicable, no `<form>` on the page |
| `webmcp-registered-tools` | Informative, no tools |
| `webmcp-schema-validity` | Not applicable |
| `llms-txt` | Not applicable, no /llms.txt |
| `ard-schema` | Not applicable, no ARD manifest |
| Category | 1 of 2 scored audits passed |

Look at the first row again. The page we just described, with fake buttons, unlabelled inputs and no form, passes the agent accessibility audit.

This is not a bug in Lighthouse — and it is the most important thing to understand about the audit. The audit runs 33 axe-core rules that matter to agents, and every one of them asks whether the elements that *are* in the accessibility tree are correct: does this button have a name, does this ARIA role exist, is this `aria-*` attribute valid, does this form field have a label.[^ch02-3] A `<div>` with a click handler is not a button as far as the tree is concerned. It is generic text. So it cannot be a button without a name, and no rule fails. The read-only date inputs have placeholder text, and axe accepts a placeholder as a last-resort name for the `label` rule. In simple words, the audit checks the quality of what the page exposes. It cannot know what the page *should* have exposed.

The CLS failure is real, though. The widget arrives 400 milliseconds after the first paint and pushes the content below it down. For a person that is a small annoyance. For an agent that took a screenshot or a snapshot a moment too early, the button it wanted to click has moved. Chapter 3 shows why that matters more for agents than for people.

So, after two graders: Level 0 from one, a near pass from the other. Neither tells us the simple fact we care about, which is whether an agent can book Fjellro on this page. For that we need the third instrument.

### A first look at your own logs

The graders and the walk measure what your site offers. Your access log measures who already comes, and it answers a question no grader can: which of the five kinds of visitor from Chapter 1 are already here, and what do they get?

> **Hands-on:** The demos repository has a small log classifier in `chapters/12-testing-and-measuring-in-production/measuring/`, the folder of Chapter 12. It has no dependencies, so it runs anywhere Node.js runs, against the logs of any server: nginx, Apache, a CDN export or the JSON log of a Node app. Chapter 12 explains how it decides each label. If you do not run code, read Listing 2.3 and continue with "Watching an agent struggle".

To try it without a production log, generate the synthetic week first. The generator writes 2,000 requests from 26 October to 1 November 2026, with a mix of visitors I invented for the demo, including a fake GPTBot from a documentation address range and a signed ChatGPT agent. On your own server, point `report.mjs` at your access log instead.

```sh
cd chapters/12-testing-and-measuring-in-production/measuring
node make-synthetic-log.mjs
node report.mjs fixtures/synthetic-access.jsonl
```

**Listing 2.3** Output of `node report.mjs fixtures/synthetic-access.jsonl`, the first table (synthetic data, not real traffic)

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
```

Read it the way you read Table 1.1 in Chapter 1, but for your own site. The training crawlers made 28.9% of the requests and the search crawlers 21.4%. The full report goes on to list every named agent with its evidence: 76 requests claimed to be GPTBot from the wrong network and were filed under `other-bot`, and the signed ChatGPT agent made 55 requests. On your own log, write down the share of `user-fetch` and `browsing-agent` requests (the visitors that act for a person), the 403 and 429 responses they got, and the share of `unknown`. One warning: the combined log format has nowhere to keep a signature result, so the same week logged that way shows zero signed agents. Chapter 4 turns these numbers into access decisions, and Chapter 12 builds the full measurement.

## Watching an agent struggle

The most honest test of an agent-ready page is an agent. But real agents are not repeatable: a browsing agent built on a large language model takes a different path each time, depends on the model version and costs money per run. For a measurement we can repeat in CI, I built something smaller.

### A structure-only agent

`booking-walk.mjs` is a scripted stand-in for an agent that works from the accessibility tree. It has a fixed task (book Fjellro from 2 to 5 December 2026 for three guests, as the guest Ingrid Berg) and it may only find things the way such an agent does: by role and accessible name ("the link called Cabins", "the button called Check availability") or by label ("the field labelled Check-in"). It never uses CSS selectors, element ids or pixel coordinates. Playwright's `getByRole()` and `getByLabel()` locators work exactly this way, on top of the browser's accessibility tree.

Listing 2.4 shows the first six of the thirteen steps.

**Listing 2.4** `chapters/02-your-first-agent-ready-page/booking-walk.mjs` — the first steps of the booking task (excerpt)

```js
export function bookingSteps(page, base, task = TASK) {
  return [
    { name: 'Open "Cabins" from the home page', recover: `${base}/cabins`,
      run: () => page.getByRole('link', { name: 'Cabins', exact: true }).first().click() },
    { name: `Open the ${task.cabin} cabin page`, recover: `${base}/cabins/${task.slug}`,
      run: () => page.getByRole('link', { name: task.cabin, exact: true }).first().click() },
    { name: 'Fill in "Check-in"', run: () => page.getByLabel('Check-in', { exact: true }).fill(task.checkIn) },
    { name: 'Fill in "Check-out"', run: () => page.getByLabel('Check-out', { exact: true }).fill(task.checkOut) },
    { name: 'Fill in "Guests"', run: () => page.getByLabel('Guests', { exact: true }).fill(task.guests) },
    { name: 'Press "Check availability"', blocks: true, run: () => page.getByRole('button', { name: 'Check availability' }).click() },
```

Two small details make the walk fair. Navigation steps carry a `recover` URL, so if the agent cannot find the "Cabins" link it goes to `/cabins` directly, the way a real agent would guess a URL. And when a blocking step fails, the steps that depend on it are skipped, because there is no availability result to read if the check never ran.

> **Hands-on:** Run the walk against the baseline. The script uses Playwright's Chromium. If you have not used Playwright on this machine before, install the browser once with `npx playwright install chromium`.

```sh
node chapters/02-your-first-agent-ready-page/booking-walk.mjs http://127.0.0.1:3000
```

### What it found on the legacy page

```text
 1. FAILED  Open "Cabins" from the home page  (nothing with that role and name)
 2. FAILED  Open the Fjellro cabin page  (nothing with that role and name)
 3. FAILED  Fill in "Check-in"  (nothing with that role and name)
 4. FAILED  Fill in "Check-out"  (nothing with that role and name)
 5. FAILED  Fill in "Guests"  (nothing with that role and name)
 6. FAILED  Press "Check availability"  (nothing with that role and name)
 7. skipped Read the availability result
 8. skipped Open "Book these dates"
 9. skipped Fill in "Full name"
10. skipped Fill in "Email"
11. skipped Accept the terms
12. skipped Press "Confirm booking"
13. skipped Read the booking reference

0 of 13 steps completed
```

Zero of thirteen — not even the first click. The navigation links are `<div>` elements, so even the first step has nothing with the role "link" and the name "Cabins". The recovery URLs get the agent to the cabin page, and there it finds no field labelled "Check-in", no field labelled "Guests" (only a number in a `<span>`) and no button called "Check availability" (only a `<div>` that says "Check"). Step 6 blocks, so the rest is skipped.

The date fields are almost there. Chrome's accessibility tree calls each read-only input a textbox and borrows the placeholder as its name. Playwright's `getByLabel()` does not count a placeholder as a label, and even the more forgiving `getByRole('textbox', { name: 'Check-in' })` ends with "element is not editable", because the input is read-only. An agent that types gets nowhere.

I want to be careful about what this result means. It does not mean that no agent could ever book this cabin. It means that an agent that relies on the page's structure, which is what Chrome calls the agent's "primary data model", gets nothing to work with.[^ch02-4] Several of the agents from Chapter 1 work this way, and the ones that do not still use the structure first when it is there.

### What a screenshot agent would do

A screenshot agent is the other kind. It looks at a picture of the page and clicks at pixel coordinates. Such an agent could probably click the "Check" div, because it looks like a button, and might get through the custom calendar, one click, one screenshot and one model call at a time.

So the legacy page is not impossible for every agent. It is slow, expensive and fragile for all of them, and impossible for some. Anthropic's documentation for its browser tool recommends element references from the page's structure over coordinates, because "a reference survives layout shifts and reflows that make pixel coordinates fragile".[^ch02-5] Our 0.116 layout shift is exactly that kind of reflow.

If you have access to a browsing agent, try it: give it the same task in plain words against a public copy of the baseline, count the steps, the time and the retries, and do it again after the fixes. I did not put such a run in a table, because the numbers change with every model release. Chapter 12 shows how to turn this into a proper evaluation with real models.

## The fix, part 1: semantic HTML

The first fix costs nothing but attention. Nordlys Cabins has a clean front end next to the legacy one, built from plain semantic HTML. It renders the same pages with the same data, and the server sends complete HTML, so nothing waits for JavaScript. Stop the baseline (Ctrl+C) and start the clean version, still with no chapter layers:

```sh
npm start -w nordlys-cabins -- --upto=0
```

Here is the availability form as the clean front end sends it (reformatted for print, the server's output has more whitespace):

```html
<form id="availability" method="get" action="/cabins/fjellro#availability-title">
  <div class="field">
    <label for="availability-checkIn">Check-in</label>
    <input id="availability-checkIn" name="checkIn" required type="date" value="" min="2026-11-10">
  </div>
  <div class="field">
    <label for="availability-checkOut">Check-out</label>
    <input id="availability-checkOut" name="checkOut" required type="date" value="" min="2026-11-10">
  </div>
  <div class="field">
    <label for="availability-guests">Guests</label>
    <p class="hint" id="availability-guests-hint">Up to 6 guests.</p>
    <input id="availability-guests" name="guests" required aria-describedby="availability-guests-hint" type="number" value="2" min="1" max="6" inputmode="numeric">
  </div>
  <button type="submit">Check availability</button>
</form>
```

Nothing in it is clever. It is the HTML that every web developer learned once, and Table 2.1 lists what changed compared to the legacy widget.

**Table 2.1** Legacy widget vs semantic HTML

| Legacy page | Clean page | What the agent gains |
|---|---|---|
| `<div class="nav-item" data-href="/cabins">` | `<a href="/cabins">` | A link with a name, and a URL it can follow or remember |
| No `<form>` | `<form method="get" action="…">` | A unit it can fill in and submit, and that works without JavaScript |
| Read-only input with a placeholder and a custom calendar | `<input type="date">` with a `<label>` | A named field it can fill with a date string |
| `<span>` between minus and plus divs | `<input type="number" min="1" max="6">` | A named field with limits it can read |
| `<div class="btn">Check</div>` | `<button type="submit">Check availability</button>` | A real button with a descriptive name |
| Booking form in a `<div>` overlay | A separate booking page with its own URL | A step it can reach directly and return to |
| Widget injected 400 ms after load | Complete HTML from the server | Nothing moves, nothing to wait for |

Of course, every row in this table also helps people. Screen reader users, keyboard users and people on a slow connection get the same benefits. This is the cheapest argument you will ever make to a product manager: the work for agents is accessibility work that was overdue anyway.

### Three fixes that look right and are not

When teams fix a page like this one under time pressure, I see the same shortcuts again and again. They all make some checker happier and leave the agent where it was.

**`role="button"` on the div.** Adding the role gives the element the right name in the tree, but none of the behaviour. A real `<button>` is focusable, reacts to Enter and Space, and submits its form. A `<div role="button">` does none of that until you write the JavaScript yourself. The W3C's first rule of ARIA use says it plainly: if a native HTML element with the semantics and behaviour you need exists, use it "instead of re-purposing an element and adding an ARIA role".[^ch02-6] Chapter 3 shows what ARIA is good for, and it is a lot, but replacing a button is not it.

**Placeholder as label.** As we saw, axe accepts it, so the audit passes. But the placeholder disappears as soon as the field has a value, so a screenshot agent that checks its own work, or a person who comes back to the form, no longer sees what the field was for. And our structure-only agent, which asks for "the field labelled Check-in", did not find it.

**Keeping the custom date picker.** Custom calendars are where agents go to die — every extra click is another screenshot and another guess. A native `<input type="date">` takes a date string, which is exactly what an agent has. If your design team insists on a custom calendar, keep a real date input underneath it that the calendar writes to, so the form still works when someone (or something) types.

> **Hands-on:** Run the three instruments against the clean page.

```sh
node chapters/02-your-first-agent-ready-page/booking-walk.mjs http://127.0.0.1:3000
node chapters/02-your-first-agent-ready-page/agent-ready-check.mjs http://127.0.0.1:3000/cabins/fjellro
npx lighthouse@13.6.0 http://127.0.0.1:3000/cabins/fjellro --only-categories=agentic-browsing \
  --chrome-flags="--headless=new --enable-features=WebMCPTesting" --output=json --output-path=./clean.json
```

The walk now goes all the way through:

```text
 1. ok      Open "Cabins" from the home page
 2. ok      Open the Fjellro cabin page
 3. ok      Fill in "Check-in"
 4. ok      Fill in "Check-out"
 5. ok      Fill in "Guests"
 6. ok      Press "Check availability"
 7. ok      Read the availability result  (Fjellro is available from Wed, 2 Dec 2026 to Sat, 5 Dec 2026.)
 8. ok      Open "Book these dates"
 9. ok      Fill in "Full name"
10. ok      Fill in "Email"
11. ok      Accept the terms
12. ok      Press "Confirm booking"
13. ok      Read the booking reference  (NC-JDUMYP)

13 of 13 steps completed
```

The booking reference at the end is random, so yours will differ. Lighthouse moves too. The layout shift is now 0, so both scored audits pass. And the WebMCP form coverage audit, which had no form to look at before, now reports one form without tool annotations. That is informative only, not a failure, and it is the hint for part 3.

The server-side scan, on the other hand, does not move at all. It is still Level 0, with the same failures, because it never looks at the page's markup. That is the disagreement from Chapter 1, now in your own terminal: one grader measures files and headers, the other measures the page, and only the agent measures the task.

### The same widget in the accessibility tree

Why did the walk succeed now? Playwright can print the part of the accessibility tree it works with as a compact YAML "ARIA snapshot", which is close to what several browsing agents read (Chapter 3 compares them). Here is the legacy widget:

```yaml
- textbox "Check-in"
- textbox "Check-out"
- text: − 2 + Check
```

And here is the clean availability form:

```yaml
- text: Check-in
- textbox "Check-in"
- text: Check-out
- textbox "Check-out"
- text: Guests
- paragraph: Up to 6 guests.
- spinbutton "Guests": "2"
- button "Check availability"
```

Three lines against eight — and the count is the smaller part of the story. In the legacy tree, the guest counter and the "Check" button have dissolved into one line of text, "− 2 + Check", and there is no way to tell from the tree which part of it can be clicked. In the clean tree every control has a role and a name, the guests field is a `spinbutton` with its current value, and the hint "Up to 6 guests." sits right before it. That is everything an agent needs to fill the form without guessing, and it came from plain HTML.

## The fix, part 2: robots.txt and a sitemap

The next two fixes are files at the root of the site. They are tiny, and they move the server-side grader.

Nordlys Cabins adds features in layers, one folder per chapter. The layer for this chapter is `layers/02-first-steps/`, and when you start the server with `--upto=2` (or with no `--upto` at all) it is switched on. Listing 2.5 is the first part of it.

> **Hands-on:** Restart the server with this chapter's layer: `npm start -w nordlys-cabins -- --upto=2`. The listing below is already in the repository, so there is nothing to type.

**Listing 2.5** `nordlys-cabins/layers/02-first-steps/index.js` — robots.txt and sitemap.xml (excerpt)

```js
    // robots.txt: everyone may crawl the public pages, nobody needs the private ones.
    ctx.staticFile('/robots.txt', (c) =>
      [
        'User-agent: *',
        'Allow: /',
        'Disallow: /account/',
        'Disallow: /bookings/',
        '',
        `Sitemap: ${ctx.absoluteUrl(c, '/sitemap.xml')}`,
        '',
      ].join('\n')
    );

    // sitemap.xml: every public page the site can render, with absolute URLs.
    ctx.staticFile(
      '/sitemap.xml',
      (c) => {
        const paths = [
          '/',
          '/cabins',
          ...store.cabins().map((cabin) => `/cabins/${cabin.slug}`),
          '/guide',
          ...store.articles().map((article) => `/guide/${article.slug}`),
          '/faq',
          '/contact',
        ];
        const urls = paths.map((path) => `  <url><loc>${ctx.absoluteUrl(c, path)}</loc></url>`);
        return [
          '<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
          ...urls,
          '</urlset>',
          '',
        ].join('\n');
      },
      { contentType: 'application/xml; charset=utf-8' }
    );
```

The robots.txt allows everything public and keeps crawlers out of two private areas, the member account and the booking management pages. It also points to the sitemap. The sitemap lists every public page the site can render, with absolute URLs, because the sitemap protocol requires them.[^ch02-7]

Please note what this robots.txt does *not* do. It has only a wildcard group, and it says nothing about AI crawlers or how content may be used. That is enough for isitagentready's "AI bot rules" check, which passes when "wildcard rules that apply to all crawlers" are present.[^ch02-8] But it is not a decision. Who may train on your content and who may cite it are business decisions, and Chapter 4 makes them properly.

Run the local scanner again and the level moves for the first time:

```text
discoverability       robotsTxt               pass           robots.txt returns 200 text/plain with a User-agent line
discoverability       sitemap                 pass           /sitemap.xml is valid XML
discoverability       linkHeaders             fail           no agent-useful Link header on /
botAccessControl      robotsTxtAiRules        pass           robots.txt has wildcard rules that apply to all crawlers
botAccessControl      contentSignals          fail           no Content-Signal line in robots.txt

Level 1: Basic Web Presence
Next: Level 2 (Bot-Aware), work on: contentSignals
```

(I kept only the lines that changed plus the summary. Level 1 needs two of the three basics, so the missing Link headers do not hold us back.)

One thing surprised me while measuring. The same layer also works on the legacy front end, because robots.txt and the sitemap do not depend on the markup. With layer 02 on the legacy page, the server-side scan said Level 1 and the booking walk still said 0 of 13. A site can climb the server-side ladder while every agent that depends on the page structure still fails. That is the best argument I know for never using one grader alone.

## The fix, part 3: one declared tool

The last fix is the first step into capabilities, the layer where the site tells agents what they can *do* instead of letting them work it out from the page. We go deep on WebMCP in Chapter 9. Here we use its simplest form, which needs no JavaScript at all.

WebMCP is a browser API, incubated in the W3C Web Machine Learning Community Group, that lets a page register tools an agent in the browser can call.[^ch02-9] Its declarative form turns an existing HTML form into a tool with a few attributes: `toolname` and `tooldescription` on the `<form>`, `toolparamdescription` on each field, and optionally `toolautosubmit`, which lets the agent submit the form without the person pressing the button. The browser builds the tool's input schema from the form's own fields: their names, types, `required` and limits. If a field has no `toolparamdescription`, Chrome falls back to the text of its label.[^ch02-10]

Please note: in October 2026 the declarative attributes moved out of the WebMCP specification text into a separate explainer in the same repository, while Chrome kept shipping them in its origin trial. So this is the least settled thing in the chapter — keep an eye on it. I use it anyway, because it costs six attributes, it degrades to a plain form, and it shows the idea of a declared tool better than anything else I know. Chapter 9 follows its status.

Listing 2.6 adds these attributes to the availability form. The layer system's `formAttributes()` and `fieldAttributes()` helpers put them on the form the page already renders, so the HTML stays in one place.

**Listing 2.6** `nordlys-cabins/layers/02-first-steps/index.js` — the availability form as a declarative WebMCP tool (excerpt)

```js
    // One declarative WebMCP tool: the availability form becomes check_availability.
    // It only reads data, so the agent may submit it without asking (toolautosubmit).
    ctx.formAttributes('availability', (page) => ({
      toolname: 'check_availability',
      tooldescription: `Check whether the cabin ${page.data.cabin.name} is free for a stay and get the total price in NOK.`,
      toolautosubmit: true,
    }));
    ctx.fieldAttributes('availability', 'checkIn', { toolparamdescription: 'Arrival date' });
    ctx.fieldAttributes('availability', 'checkOut', { toolparamdescription: 'Departure date, after the arrival date' });
    ctx.fieldAttributes('availability', 'guests', { toolparamdescription: 'Number of guests, including children' });
```

The form now starts like this in the HTML the server sends (again reformatted):

```html
<form id="availability" method="get" action="/cabins/fjellro#availability-title"
      toolname="check_availability"
      tooldescription="Check whether the cabin Fjellro is free for a stay and get the total price in NOK."
      toolautosubmit>
  <div class="field">
    <label for="availability-checkIn">Check-in</label>
    <input id="availability-checkIn" name="checkIn" required type="date" value="" min="2026-11-10"
           toolparamdescription="Arrival date">
```

Why only this form, and not the booking form on the next page? Because checking availability only reads data, so letting the agent submit it on its own (`toolautosubmit`) is safe. Booking a cabin creates a reservation and, in a real business, a charge. That form should stay something the person confirms, and Chapters 9 and 11 show how to declare consequential tools with confirmation built in. In simple words: start with tools that read, and add tools that write when you have thought about consent.

To see the tool, open the page in a Chrome that runs with the testing flag (`--enable-features=WebMCPTesting` on the command line, or "WebMCP for testing" in `chrome://flags`) and ask the page for its tools in the DevTools console. The Model Context Tool Inspector extension shows the same list in a panel, if you prefer clicking.[^ch02-11]

```js
await document.modelContext.getTools()
```

This is the tool Chromium 156 generated from our form, printed as JSON:

```json
{
  "name": "check_availability",
  "description": "Check whether the cabin Fjellro is free for a stay and get the total price in NOK.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "checkIn": {
        "type": "string",
        "format": "date",
        "description": "Arrival date (Dates MUST be provided in 'YYYY-MM-DD' format.)"
      },
      "checkOut": {
        "type": "string",
        "format": "date",
        "description": "Departure date, after the arrival date (Dates MUST be provided in 'YYYY-MM-DD' format.)"
      },
      "guests": {
        "type": "number",
        "minimum": 1,
        "maximum": 6,
        "multipleOf": 1,
        "description": "Number of guests, including children"
      }
    },
    "required": [
      "checkIn",
      "checkOut",
      "guests"
    ]
  }
}
```

Look at what the browser added on its own. The `date` inputs became strings with `"format": "date"`, and Chrome appended its own instruction about the format to our descriptions. The number input became a number with the `min` and `max` from the HTML and `"multipleOf": 1` from the default step. And all three fields are required, because the HTML says so. We wrote three short descriptions, and the browser did the rest from markup we already had (Figure 2.2).

![Figure 2.2 — How a declarative WebMCP tool is built. Attributes on the form and its fields become the tool's name, description and parameter descriptions, and the browser derives the input schema (types, formats, limits, required) from the HTML form itself.](images/figure-2-2.png)

The same console can call the tool. `executeTool()` takes the tool and an object with the arguments:

```js
const [tool] = await document.modelContext.getTools();
await document.modelContext.executeTool(tool, { checkIn: '2026-12-09', checkOut: '2026-12-12', guests: 2 });
```

Chrome fills in the form, submits it (because of `toolautosubmit`) and the page shows the result for three nights, NOK 7,900 in our demo data. The repository's Playwright tests do exactly this.

Please note: these console calls are testing hooks behind a flag, and Chapter 9 covers the API surface. What matters here is the measurement. Run Lighthouse once more: form coverage passes, because the only form on the page is annotated, schema validity passes, and the category reports 4 of 4 scored audits passed. The local scanner reports the declarative tool too, though, as on the real scanner, WebMCP does not change the level.

And in every browser without WebMCP the attributes are ignored and the form is just a form. On 2 November 2026 no browser exposes WebMCP by default. Chrome exposes it on origins that joined the origin trial, which runs to Chrome 162, or with the testing flag.[^ch02-12] Nothing breaks. That is the nice property of the declarative form: it is progressive enhancement in the most literal sense.

## Before and after

Table 2.2 puts the three runs side by side. All numbers come from the same machine on 2 November 2026, with the versions named in the Hands-on note at the start of the chapter.

**Table 2.2** The Fjellro page, measured three times

| Instrument | Legacy page | Semantic HTML | Plus layer 02 |
|---|---|---|---|
| Booking walk (structure-only agent) | 0 of 13 steps | 13 of 13 | 13 of 13 |
| Server-side scan (local, isitagentready rules) | Level 0 | Level 0 | Level 1 |
| Next level needs | robotsTxt, sitemap, linkHeaders | robotsTxt, sitemap, linkHeaders | contentSignals |
| Lighthouse `agent-accessibility-tree` | Pass | Pass | Pass |
| Lighthouse `cumulative-layout-shift` | 0.116 (fail) | 0 | 0 |
| Lighthouse WebMCP form coverage | Not applicable | 1 form without annotations (informative) | Pass |
| Lighthouse WebMCP schema validity | Not applicable | Not applicable | Pass |
| Lighthouse category | 1 of 2 | 2 of 2 | 4 of 4 |

Read the table by row, not by column. The agent walk moved with the markup, the server-side scan moved with the files, and Lighthouse moved a little with each. With only one of them, we would have told a different story about the same afternoon of work.

Bottomline: a page an agent can use is mostly a page that was built well in the first place. Semantic HTML did the heavy lifting here, and two small files and three attributes did the rest. The total change is one layer file of 78 lines, comments included, and a front end that uses the elements HTML already has.

## A first pass on your own site

You can run this whole chapter on your own site in an afternoon, without the demo. This is the order I use with teams:

1. **Pick three tasks** that matter to the business and that an agent might do for a customer, each written as a sentence with concrete values, like our `TASK` object.
2. **Scan and audit.** Scan the public site with isitagentready.com (or the companion script on a staging origin), run Lighthouse's Agentic Browsing category with a pinned version on the page where each task starts, and save the JSON.
3. **Walk each task by structure.** Copy `booking-walk.mjs`, change the steps to your task and run it. Each failing step is a concrete, reproducible bug report: "there is no button called Add to cart on the product page".
4. **Sort the findings by layer and by owner.** Chapter 1's six layers make a good set of labels for the backlog.

If your site runs on a platform like Shopify, some of the server-side checks may already pass without anyone on your team doing anything, as we saw in Chapter 1. The markup in your theme is still yours, so steps 3 and 4 matter just as much.

## The habit: measure, change one layer, measure again

This chapter was small on purpose, because I wanted the loop to be visible. Every remaining chapter in the book follows it, and I suggest your team does too:

1. **Baseline.** Run all three instruments on the pages that matter and save the raw output (the Lighthouse JSON, the scanner's JSON, the walk's log). Nordlys Cabins keeps a "before" switch for every chapter (`--upto`) so you can always go back.
2. **Change one layer.** One chapter's worth of change at a time. If you change the markup and robots.txt and add a tool in one release, you will not know which change moved which number, and you will not know what to roll back.
3. **Measure again**, with the same versions of the tools. Lighthouse changed its agentic category in every minor release from 13.2 to 13.6, so pin the version in your scripts and write it next to every result.
4. **Record the deltas per check**, not only the level. "Level 1" hides the fact that `robotsTxtAiRules` passes only because of a wildcard group. A table like Table 2.2, kept in your repository, is worth more than any single score.

The agent walk deserves a special word. A scripted walk like ours is not a real agent, and it never will be. But it is cheap, deterministic and exactly as strict as the accessibility tree, which makes it a good regression test. Chapter 12 puts the three instruments into CI and adds evaluations with real models on top.

## Summary

- Three instruments, three questions. A server-side scan in the style of isitagentready.com checks files and headers. Lighthouse's Agentic Browsing category checks the page in a real browser. A scripted agent walk checks whether the task can be done. They disagree, and that is useful.
- A first look at your own access log, with the demos' log classifier, shows which kinds of visitor already come and what they get, before any grader result.
- Lighthouse's `agent-accessibility-tree` audit checks the quality of what a page exposes, not what it is missing. The legacy page with no form and no real buttons passed it.
- A structure-only agent completed 0 of 13 booking steps on the legacy page and 13 of 13 after the switch to semantic HTML: real links, a `<form>`, labelled inputs, a real `<button>` and content that is in the HTML from the start.
- A robots.txt and a sitemap moved the server-side scan from Level 0 to Level 1. They also did that on the legacy page, where the agent still failed every step.
- Three attributes on a form and three on its fields made a declarative WebMCP tool, `check_availability`. Chrome built the input schema from the form itself, and browsers without WebMCP ignore the attributes.
- Measure, change one layer, measure again, and record per-check deltas with pinned tool versions.

[^ch02-1]: isitagentready.com, "Scan API" and MCP server, documented in https://isitagentready.com/llms-full.txt (retrieved 2 November 2026). Scan of https://salnikov.no on 2 November 2026 at 20:59 UTC, stored with the book's research data.
[^ch02-2]: Chrome for Developers, "Agentic Browsing scoring", https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring (retrieved 2 November 2026).
[^ch02-3]: Lighthouse 13.6.0 source, `core/audits/agentic/agent-accessibility-tree.js`, the list of 33 axe-core rules, https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 (retrieved 2 November 2026). Chapter 3 lists the rules.
[^ch02-4]: Chrome for Developers blog, "Get your site agent ready", 22 June 2026, https://developer.chrome.com/blog/agent-ready-toolkit (retrieved 2 November 2026).
[^ch02-5]: Anthropic, "Browser use tool", https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool (retrieved 2 November 2026).
[^ch02-6]: W3C, "Using ARIA", section 2.1 "First Rule of ARIA Use", https://www.w3.org/TR/using-aria/ (retrieved 2 November 2026).
[^ch02-7]: sitemaps.org, "Sitemaps XML format", https://www.sitemaps.org/protocol.html (retrieved 2 November 2026).
[^ch02-8]: isitagentready.com, check "AI bot rules", pass criteria, https://isitagentready.com/llms-full.txt (retrieved 2 November 2026).
[^ch02-9]: W3C Web Machine Learning Community Group, "WebMCP", Draft Community Group Report, https://webmachinelearning.github.io/webmcp/ (retrieved 2 November 2026).
[^ch02-10]: Chrome for Developers, "Declarative API", last updated 25 September 2026, https://developer.chrome.com/docs/ai/webmcp/declarative-api, and "WebMCP declarative API" explainer, https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md (both retrieved 2 November 2026).
[^ch02-11]: François Beaufort, "Model Context Tool Inspector", https://github.com/beaufortfrancois/model-context-tool-inspector (retrieved 2 November 2026).
[^ch02-12]: Chrome Platform Status, "WebMCP", https://chromestatus.com/feature/5117755740913664 (retrieved 2 November 2026). The origin trial runs from Chrome 149 to Chrome 162.
