{sample: false}
# Chapter 3: How agents see a page

This chapter covers

- The three views an agent can have of a page: the server's HTML, the accessibility tree and a screenshot
- How the browser builds the accessibility tree, and what an agent finds in it
- Semantic HTML as the zero-cost baseline, and where ARIA helps or hurts
- The 33 axe rules behind Lighthouse's agent audit, what they catch and what they skip
- A perception contract for every page of Nordlys Cabins, checked in tests

In Chapter 2 a structure-only agent failed every step on the legacy booking page and finished every step on the clean one. The two pages look almost the same to a person. So what exactly did the agent see that we did not? This chapter answers that question, and it gives you the tools to see your own pages the way agents do.

This is the perception layer from Chapter 1, the second from the bottom. It is the cheapest layer in the book, because most of it is HTML that the web platform has supported for decades, and it pays twice, because people who use assistive technology read the same structure. It is also the layer where I see the most confusion — mostly because "ARIA for AI" has become a marketing phrase. Let's look at what is really there.

## Three ways to look at a page

An agent that wants to understand a page has three raw materials. web.dev's guide to agent-friendly websites names the same three: screenshots, the raw HTML and the accessibility tree, and it notes that modern agents combine them.[^ch03-1] Each view has different strengths, and different agents lean on different ones.

![Figure 3.1 — Three views of the same page. The server's HTML is what a fetch-only agent reads. The accessibility tree, built by the browser after rendering, is what most browsing agents read first. The screenshot is what vision-based agents and fallbacks look at.](images/figure-3-1.png)

Table 3.1 lists what the vendors themselves say about the agents you met in Chapter 1. I only list what is documented or, in one case, published by a third party that took the product apart. This changes from month to month, so please treat the table as a snapshot of 2 November 2026.

**Table 3.1** What browsing agents read, as documented on 2 November 2026

| Agent or tool | What it reads | Source |
|---|---|---|
| Anthropic browser use tool (Claude API) | The accessibility tree as text with references such as `[ref_2]`, plus screenshots and coordinates | Vendor documentation[^ch03-2] |
| Perplexity Comet | A YAML accessibility tree from Chrome's `Accessibility.getFullAXTree`, plus the page as Markdown | Third-party reverse engineering[^ch03-3] |
| Playwright MCP | Accessibility snapshots, with coordinate-based input only as an opt-in | Project README[^ch03-4] |
| ChatGPT Atlas agent | "ARIA tags", the labels and roles that screen readers use | OpenAI help page, quoted by others[^ch03-5] |
| Microsoft Edge, Browse with Copilot | Screenshots of the page it acts on | Vendor documentation[^ch03-6] |
| Computer-use models (OpenAI, Google) | A loop of screenshot, then action | Vendor documentation[^ch03-7] |

Two things stand out. First, the accessibility tree is the common denominator. Chrome's own words are that agents rely on it "as their primary data model".[^ch03-8] Second, even the screenshot-first agents get the page's structure for free when they run inside a browser, and the hybrid ones switch to pixels only when the structure is missing or confusing. web.dev puts it bluntly: screenshot analysis "can be slow and expensive (in terms of used tokens), making it better as a backup when the structure is confusing".[^ch03-1]

### View 1: the HTML the server sends

The simplest agents never run your JavaScript. The search and answer crawlers from Chapter 1, the "fetch this URL" tools of chat assistants and coding agents, and many retrieval pipelines download the HTML, strip it to text or Markdown, and hand that to a model. What they get is whatever your server sends in the first response.

For a server-rendered page that is everything. For a page that builds itself in the browser, it can be almost nothing. Our legacy Fjellro page sends 2.1 KB of HTML: the site name and menu as plain text, three images, the cabin's name, a footer and a script tag. The description, the price and every control arrive later, from JavaScript.

### View 2: the accessibility tree

Browsing agents run a real browser, so they get the page after rendering. The browser keeps a second tree next to the DOM, the accessibility tree, built for screen readers and other assistive technology. It drops everything that is only there for layout and keeps what a person (or an agent) needs to understand and operate the page: the roles of elements, their names, their states and how they relate to each other. We look at how it is built in the next section.

### View 3: the screenshot

A screenshot is the page as pixels. It carries everything a person sees, including visual cues that no tree has: which button is the primary one, where the price is, which image is the cabin. And it carries nothing that is not visible: no roles, no names, no hidden hints, no URLs behind links. An agent that works from screenshots has to recognise a button by its look, aim at it with coordinates and take another screenshot to see what happened.

### The three views of Fjellro

> **Hands-on:** The script for this section is `three-views.mjs` in the folder `chapters/03-how-agents-see-a-page/` of the demos repository. It needs Playwright's Chromium (`npx playwright install chromium` once). Start the site as in Chapter 2, then run the script against the legacy and the clean front end. All numbers in this chapter come from Chromium 156.0.8078.4, Playwright 1.64.1 and axe-core 4.14.0 on 2 November 2026.

Listing 3.1 is the core of the script. It opens the page twice: once with JavaScript switched off, to see what a fetch-only agent gets, and once normally, to read the accessibility tree and take a screenshot. For the tree it uses two sources. Playwright's ARIA snapshot is a compact YAML view of the tree, close to what several agents send to their model.[^ch03-9] Chrome DevTools Protocol's `Accessibility.getFullAXTree` is the full tree as Chromium has it, the same call Comet uses.

**Listing 3.1** `chapters/03-how-agents-see-a-page/three-views.mjs` — capturing the three views (excerpt)

```js
/** Capture the three views of one URL. */
export async function threeViews(browser, url, { settle = 1000 } = {}) {
  // View 1: the server's HTML, as a fetch-only agent sees it (no JavaScript).
  const noJs = await browser.newContext({ javaScriptEnabled: false });
  const raw = await noJs.newPage();
  const response = await raw.goto(url, { waitUntil: 'load' });
  const html = await response.text();
  const htmlSnapshot = await raw.locator('body').ariaSnapshot();
  await noJs.close();

  // Views 2 and 3: the rendered page, as a browsing agent sees it.
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(settle);
  const snapshot = await page.locator('body').ariaSnapshot();
  const cdp = await context.newCDPSession(page);
  const { nodes } = await cdp.send('Accessibility.getFullAXTree');
  const domElements = await page.evaluate(() => document.querySelectorAll('*').length);
  const screenshot = await page.screenshot({ fullPage: false });
```

Run it against both front ends:

```sh
npm run start:legacy -w nordlys-cabins     # in one terminal, port 3000
node chapters/03-how-agents-see-a-page/three-views.mjs http://127.0.0.1:3000/cabins/fjellro --out=views-legacy
```

Then stop the server, start the clean front end with `npm start -w nordlys-cabins -- --upto=2`, and run the script again with `--out=views-clean`. These are my results:

```text
http://127.0.0.1:3000/cabins/fjellro

1. Server HTML, no JavaScript
   2.1 KB of HTML, 0 interactive elements in the ARIA snapshot
2. Rendered page, accessibility tree
   54 DOM elements, 81 accessibility nodes (67 not ignored)
   2 interactive nodes, 0 of them without a name
   0 headings, 0 landmarks
   ARIA snapshot: 0.6 KB, 2 interactive lines
3. Screenshot
   1280x800 PNG, 61.6 KB

Saved the three views to views-legacy/
```

```text
http://127.0.0.1:3000/cabins/fjellro

1. Server HTML, no JavaScript
   4.8 KB of HTML, 15 interactive elements in the ARIA snapshot
2. Rendered page, accessibility tree
   100 DOM elements, 233 accessibility nodes (214 not ignored)
   23 interactive nodes, 0 of them without a name
   5 headings, 9 landmarks
   ARIA snapshot: 3.1 KB, 15 interactive lines
3. Screenshot
   1280x800 PNG, 66.3 KB

Saved the three views to views-clean/
```

Table 3.2 puts the two side by side.

**Table 3.2** The three views of `/cabins/fjellro`

| View | Legacy | Clean |
|---|---|---|
| Server HTML | 2.1 KB, 0 interactive elements | 4.8 KB, 15 interactive elements |
| DOM after rendering | 54 elements | 100 elements |
| Accessibility tree | 81 nodes, 2 interactive, 0 headings, 0 landmarks | 233 nodes, 23 interactive, 5 headings, 9 landmarks |
| ARIA snapshot | 0.6 KB, 2 interactive lines | 3.1 KB, 15 interactive lines |
| Screenshot, 1280 by 800 | 61.6 KB | 66.3 KB |

Look at the last row first — it is the most important one. The two screenshots are almost the same size, because the two pages look almost the same. If you only ever look at your pages, which is what most of us do, you will never notice the difference. Every other row shows it.

The legacy page sends no controls in its HTML, so a fetch-only agent learns nothing about booking. After rendering, its tree has two interactive nodes, the two read-only date fields, and no headings or landmarks at all. In simple words, the agent sees a wall of text with two boxes in it. The clean page sends all 15 controls in its first response, and its tree has every link, field and button with a name, five headings to navigate by and nine landmarks (banner, navigation, main, regions and so on) that say which part of the page is which.

Here is the complete server-HTML view of the legacy page, as the script saved it. This is all a fetch-only agent gets:

```yaml
- text: NORDLYS Cabins Guide FAQ Contact
- img
- img
- img
- text: Fjellro © Nordlys Cabins (fictional) Find a booking · Terms · Contact
```

Please note: the clean page has 23 interactive nodes in the full tree but only 15 lines in the ARIA snapshot, because Chromium's full tree exposes the parts inside each native date field, while Playwright's snapshot shows each date field as one textbox. Different tools give an agent different granularity of the same tree.

### Seeing your own pages the way agents do

**Chrome DevTools.** The Accessibility pane in the Elements panel shows the role, name, description and states of the selected element, and where the name came from. Chrome DevTools also has a full-page accessibility tree: "when you toggle the new tree, it replaces the DOM tree view and allows you to see the full accessibility tree for the page".[^ch03-10] It is the closest you get to reading the page with an agent's eyes.

**Switching JavaScript off.** In DevTools, the command menu has "Disable JavaScript". Reload the page and you see View 1. If your main content or your forms disappear, so do they for fetch-only agents. The section "Rendering for client-rendered apps" later in this chapter is about that case.

**Playwright ARIA snapshots.** `await page.locator('body').ariaSnapshot()` gives you the YAML view we used above, and `expect(locator).toMatchAriaSnapshot()` turns it into a test. Playwright's documentation shows how to match only parts of the tree, by leaving out names or attributes you do not care about.[^ch03-9] A snapshot test for the availability form of a cabin page could look like this:

```js
await expect(page.getByRole('region', { name: 'Check availability' })).toMatchAriaSnapshot(`
  - heading "Check availability" [level=2]
  - textbox "Check-in"
  - textbox "Check-out"
  - spinbutton "Guests"
  - button "Check availability"
`);
```

## How the browser builds the accessibility tree

Every node in the accessibility tree has four kinds of information. MDN lists them as name, description, role and state.[^ch03-11] The role says what the thing is (a link, a button, a text box, a heading). The name is what it is called ("Check availability"). The description is extra help ("Up to 6 guests."). The state says what is going on with it right now (checked, expanded, required, invalid, disabled).

Chromium's renderer, Blink, builds the tree from the DOM, the CSS and any ARIA attributes. Elements that exist only for layout become ignored generic containers, and the useful ones get a role from the HTML element or from ARIA.[^ch03-10] The rules for how each HTML element maps to a role are standardised in HTML-AAM, and the name and description come from an algorithm with its own specification, the Accessible Name and Description Computation (accname).[^ch03-12] You do not need to read those specifications to build good pages. You do need to know that the browser follows them, and that it can only work with what your markup gives it.

Let's look at one real node. The clean booking page validates the form on the server and sends it back with error messages when something is wrong. Here is the email field after a submit with the incomplete address `ingrid@` (rendered HTML, reformatted):

```html
<div class="field has-error">
  <label for="booking-email">Email</label>
  <p class="hint" id="booking-email-hint">We send the booking confirmation here.</p>
  <p class="error-message" id="booking-email-error">Enter an email address like name@example.com.</p>
  <input id="booking-email" name="email" required
         aria-describedby="booking-email-hint booking-email-error" aria-invalid="true"
         autocomplete="email" type="email" value="ingrid@">
</div>
```

And here is the node Chromium built for that input, read with `Accessibility.getPartialAXTree` and shortened to the properties we care about:

```json
{
  "role": { "type": "role", "value": "textbox" },
  "name": { "type": "computedString", "value": "Email" },
  "description": {
    "type": "computedString",
    "value": "We send the booking confirmation here. Enter an email address like name@example.com."
  },
  "properties": [
    { "name": "invalid", "value": { "type": "token", "value": "true" } },
    { "name": "required", "value": { "type": "boolean", "value": true } },
    { "name": "describedby", "value": { "type": "idrefList", "value": "booking-email-hint booking-email-error" } },
    { "name": "labelledby", "value": { "type": "nodeList", "relatedNodes": [ { "text": "Email" } ] } }
  ]
}
```

All four kinds of information are there. The role comes from `type="email"`. The name "Email" comes from the `<label>`. The description joins the hint and the error message, in the order of `aria-describedby`. And the states say the field is required and its value is invalid. An agent that reads this node knows what the field is, what went wrong and what a correct value looks like, without seeing the red border or reading the error summary at the top of the page. A screenshot agent has to find the red text and work out which field it belongs to.

Now the legacy widget again, as a snapshot:

```yaml
- textbox "Check-in"
- textbox "Check-out"
- text: − 2 + Check
```

The two date fields have a name only because Chromium falls back to the placeholder when nothing better exists. The guest counter and the "Check" button do not exist as controls at all. They are one line of text, "− 2 + Check". The `<div>` elements with click handlers are ignored generic containers, exactly as the Blink rules say, and the text inside them is all that is left.

### Reading the tree like an agent

To feel the difference, read the clean availability form the way an agent's model reads it. This is the part of the ARIA snapshot for the "Check availability" section of the Fjellro page:

```yaml
- region "Check availability":
  - heading "Check availability" [level=2]
  - text: Check-in
  - textbox "Check-in"
  - text: Check-out
  - textbox "Check-out"
  - text: Guests
  - paragraph: Up to 6 guests.
  - spinbutton "Guests": "2"
  - button "Check availability"
  - status
  - group: Dates that are already taken
```

Try to plan the task "check Fjellro for 2 to 5 December, three guests" from these lines alone. The region name tells you that you are in the right place. Two textboxes are named for the two dates you have. The spinbutton is named "Guests". There is one button, and its name says what it does, and below it sits an empty `status` element, where the result will appear. A model needs no screenshot and no guessing to plan four actions, and after the fourth it knows where to look for the answer. With the legacy snapshot, two textboxes named by their placeholders and the text "− 2 + Check", every step is a guess, and every guess costs a screenshot, a coordinate and a check of the result.

Anthropic's browser tool makes this explicit. Its `read_page` action returns the accessibility tree as text, with each element tagged with a reference such as `[ref_2]`, and it can filter the tree to interactive elements only.[^ch03-2] The model then says "type into ref_5" instead of "click at 412, 388". Every name in the tree becomes something the model can talk about, and every missing name becomes something it has to guess.

![Figure 3.2 — From markup to tree. On the left, the legacy widget: div elements with click handlers become ignored containers and their text collapses into one line. On the right, the semantic form: each element maps to a role, the label gives the name, the hint gives the description and attributes give states.](images/figure-3-2.png)

## Semantic HTML first, ARIA second

The cheapest way to get a good tree is to use the HTML element that already means what you want. Table 3.3 lists the elements that matter most on a booking site and the role each one gets in Chromium, together with what that gives an agent.

**Table 3.3** HTML elements and the roles they bring

| HTML | Role in the tree | What the agent gets |
|---|---|---|
| `<a href="…">` | link | A name and a URL it can follow or remember |
| `<button>` | button | Something it can press, with a name |
| `<label for>` plus `<input>` | textbox, spinbutton, checkbox and so on | A named field of a known type |
| `<input type="number" min max>` | spinbutton | A number with limits |
| `<input type="date">` | a date field (textbox in Playwright's snapshot) | A field that takes `YYYY-MM-DD` |
| `<select>` | combobox | A list of allowed values |
| `<fieldset>` with `<legend>` | group | A named group of fields ("Lead guest") |
| `<header>`, `<nav>`, `<main>`, `<footer>` | banner, navigation, main, contentinfo | The parts of the page, to jump between |
| `<section aria-labelledby="…">` pointing at its heading | region | A named part ("Check availability") |
| `<h1>` to `<h6>` | heading with a level | An outline of the page |
| `<dialog>` | dialog | A modal step with a name |

None of this is new. What is new is that a second kind of reader depends on it. That is why I call semantic HTML the zero-cost baseline of agent readiness: you pay nothing extra for it, because you should be writing it anyway.

### What ARIA is for

WAI-ARIA is the W3C vocabulary of roles, states and properties for the cases HTML cannot express on its own. Version 1.2 is the current W3C Recommendation, published 6 June 2023, and version 1.3 is still a Working Draft (the latest one dated 4 June 2026), so I stick to 1.2 features in this book.[^ch03-13]

ARIA is excellent at three things that HTML alone does not do well:

- **Names for elements with no visible text.** An icon-only button gets `aria-label="Close"`. A second navigation gets `aria-label="Footer"` so it can be told apart from the main one, as Nordlys does.
- **Relationships.** `aria-describedby` connects a field to its hint and its error message, as in the email example above. `aria-current="page"` marks the current item in a breadcrumb or menu.
- **States that change.** `aria-expanded` on a button that opens a panel, `aria-invalid` on a field that failed validation, `aria-busy` while a region reloads.

Live regions deserve a word too. Nordlys puts the availability result in an element with `role="status"`, so a screen reader announces "Fjellro is available from…" when the result appears. Whether agents watch live regions, I could not find in any vendor documentation, so I do not claim it. For people the value is clear, and an agent that reads the tree after the update finds the result in a clearly named place anyway.

### What ARIA is not for

ARIA changes what the tree says, never what the element does. The W3C's first rule of ARIA use is to use a native element whenever one exists, "instead of re-purposing an element and adding an ARIA role".[^ch03-14] A `<div role="button">` looks right in the tree, but it is not focusable, does not react to the keyboard and does not submit a form until you write all of that yourself. And ARIA in HTML asks authors to avoid redundant roles, like `role="button"` on a `<button>`.[^ch03-15]

This matters more than ever, because the advice "add ARIA for AI" is spreading. OpenAI's help page for the ChatGPT Atlas agent says it "uses ARIA tags — the same labels and roles that support screen readers — to interpret page structure and interactive elements".[^ch03-5] The accessibility consultant Adrian Roselli answered with a post titled "OpenAI, ARIA, and SEO: Making the Web Worse", warning that such advice pushes teams to sprinkle ARIA instead of fixing their HTML.[^ch03-16] I agree with him. The tree is built from your HTML first. ARIA is the correction fluid, not the pen :)

> **Note:** Bad ARIA is worse than no ARIA. A wrong role, a misspelled attribute or `aria-hidden="true"` on a container with a link inside produce a tree that lies. Several of the 33 rules in the next section exist exactly to catch those lies.

### Forms: where booking sites win or lose

Most agent tasks on a business site end in a form, so forms get extra attention. The checklist I use:

- **A visible `<label for>` for every field**, with words the user would say ("Check-in", not "Field 1"). The label becomes the name.
- **The right input type**: `date`, `number`, `email`, `tel`, `password`. Each one brings a role and constraints the agent can read.
- **`autocomplete` tokens** from the HTML standard (`name`, `email`, `tel`, `username`, `current-password`, `one-time-code` and so on).[^ch03-17] They tell browsers and agents what a field is for, independently of its label or language. Nordlys sets them on every personal-data field.
- **Hints and errors connected with `aria-describedby`**, and `aria-invalid="true"` on fields that failed. The email example shows the result.
- **Groups with `<fieldset>` and `<legend>`** when a form has parts ("Your stay", "Lead guest").
- **Buttons that say what they do.** "Confirm booking" is better than "Submit", and an agent that is about to make a reservation for a person should know it.
- **Real dialogs.** Use `<dialog>` with a name for modal steps. HTML can now open one without JavaScript, with `<button command="show-modal" commandfor="…">`, and `closedby` on the dialog controls how it can be closed.[^ch03-18] Both keep the behaviour in markup that an agent can see.

### Patterns that break perception

Beyond forms, these are the patterns I find most often when I look at the trees of real sites. None of them is exotic, and each has a plain fix.

- **Click handlers on cards.** A whole product or cabin card is clickable through JavaScript, and the card contains no real link. In the tree it is text. Put an `<a href>` around the card's title (and make the card clickable with CSS if you like).
- **"Read more" and "Click here".** Five links called "Read more" are five identical names. An agent that lists the links on a page cannot tell them apart. Write link texts that make sense alone, or give each link a unique accessible name.
- **Icon-only buttons.** A heart, a cross, a magnifying glass. Without `aria-label` they have no name, and `button-name` catches them. With a label they are perfectly clear.
- **Custom selects and comboboxes.** A styled list that opens on click is a cluster of `<div>` elements unless it follows the ARIA Authoring Practices pattern exactly. A native `<select>` is almost always the better trade.
- **Text in images and canvas.** A price or a date drawn into an image or a `<canvas>` is not in the tree at all. Keep text as text.
- **Content that appears only on hover or scroll.** An action that shows up only when the mouse is over a card, or a list that loads more items only on scroll, may not exist at the moment the agent reads the tree. Make actions visible by default and give long lists real pagination links.
- **`aria-hidden` in the wrong place.** Teams sometimes hide a whole section from the tree to "clean up" what screen readers announce. Agents lose it too.

One more pattern belongs to security more than to perception, and Chapter 10 treats it properly: text that is in the DOM but not visible. Anthropic tells developers who build agents to read pages from "what the page renders (the accessibility tree or visible text), not raw DOM source, so hidden text doesn't reach Claude".[^ch03-2] The rendered tree is what careful agents read, so that is the view to get right.

## The 33 rules behind Lighthouse's agent audit

In Chapter 2 the legacy page passed Lighthouse's `agent-accessibility-tree` audit, and I promised to explain the audit properly. Here it is.

The audit reuses the axe-core run that Lighthouse already does for its accessibility category and fails if any of 33 rules has a violation. The list lives in the Lighthouse source, and Listing 3.2 is a copy of it from version 13.6.0.[^ch03-19] Chrome's documentation describes the checks in three groups: names and labels, tree integrity, and visibility.[^ch03-20]

**Listing 3.2** `chapters/03-how-agents-see-a-page/agent-axe.mjs` — the 33 rules (excerpt)

```js
export const AGENT_RULES = [
  'button-name',
  'input-button-name',
  'input-image-alt',
  'label',
  'link-name',
  'select-name',
  'document-title',
  'aria-allowed-attr',
  'aria-allowed-role',
  'aria-command-name',
  'aria-conditional-attr',
  'aria-dialog-name',
  'aria-hidden-body',
  'aria-hidden-focus',
  'aria-input-field-name',
  'aria-prohibited-attr',
  'aria-required-attr',
  'aria-required-children',
  'aria-required-parent',
  'aria-roles',
  'aria-text',
  'aria-toggle-field-name',
  'aria-tooltip-name',
  'aria-treeitem-name',
  'aria-valid-attr',
  'aria-valid-attr-value',
  'duplicate-id-aria',
  'definition-list',
  'table-duplicate-name',
  'tabindex',
  'autocomplete-valid',
  'presentation-role-conflict',
  'svg-img-alt',
];
```

Table 3.4 sorts them into four groups of my own, which I find easier to remember when I fix pages.

**Table 3.4** The 33 agent rules, grouped by what they protect

| Group | Rules | A typical failure |
|---|---|---|
| Every control has a name | `button-name`, `input-button-name`, `input-image-alt`, `label`, `link-name`, `select-name`, `aria-command-name`, `aria-dialog-name`, `aria-input-field-name`, `aria-toggle-field-name`, `aria-tooltip-name`, `aria-treeitem-name`, `svg-img-alt`, `document-title` | An icon-only button, a field with no label, a dialog with no title |
| ARIA is valid | `aria-allowed-attr`, `aria-allowed-role`, `aria-conditional-attr`, `aria-prohibited-attr`, `aria-required-attr`, `aria-roles`, `aria-valid-attr`, `aria-valid-attr-value`, `presentation-role-conflict` | A misspelled role, `aria-expanded="yes"`, a checkbox role without `aria-checked` |
| The tree holds together | `aria-hidden-body`, `aria-hidden-focus`, `aria-required-children`, `aria-required-parent`, `aria-text`, `duplicate-id-aria`, `definition-list`, `table-duplicate-name` | A list item outside a list, a duplicated id that a label points to, focusable content hidden from the tree |
| Keyboard and autofill | `tabindex`, `autocomplete-valid` | `tabindex="3"`, `autocomplete="full-name"` |

The common thread is that every rule checks something that *is* in the tree. Does this button have a name? Is this role a real role? Does this hidden container hide something focusable? None of them asks whether something *should* be in the tree and is not. That is why a page made of `<div>` elements passes: there are no buttons, so there are no buttons without names.

Please note what the list leaves out. Colour contrast, heading order, landmark rules, `image-alt` for ordinary images and `html-has-lang` are not part of it.[^ch03-19] For an agent that reads the tree, contrast does not matter. For a person it matters a lot. So the agent subset is a floor, not a target, and I recommend you run the full accessibility audit next to it.

### Running the rules yourself

> **Hands-on:** `agent-axe.mjs` in `chapters/03-how-agents-see-a-page/` injects axe-core into a page and runs exactly these 33 rules. With `--all` it runs the WCAG 2.x A and AA rules and axe's best practices instead. It works on any URL or local file.

The folder has a small fixture, `fixtures/broken-booking.html`, a booking form with one common mistake per line: a field with no label, a checkbox made of a `<span>`, a misspelled role, an icon-only submit button, a link around an image without `alt`, `aria-expanded="yes"`, a dialog without a name, an invalid `autocomplete` token and a positive `tabindex`. Run it:

```sh
node chapters/03-how-agents-see-a-page/agent-axe.mjs chapters/03-how-agents-see-a-page/fixtures/broken-booking.html
```

```text
file:///…/fixtures/broken-booking.html  (axe-core 4.14.0, 33 agent rules)
  aria-dialog-name         serious   ARIA dialog and alertdialog nodes should have an accessible name
      div[role="dialog"]
  aria-required-attr       critical  Required ARIA attributes must be provided
      .fake-check
  aria-roles               critical  ARIA roles used must conform to valid values
      span[role="buton"]
  aria-toggle-field-name   serious   ARIA toggle fields must have an accessible name
      .fake-check
  aria-valid-attr-value    critical  ARIA attributes must conform to valid values
      button[type="button"]
  autocomplete-valid       serious   autocomplete attribute must be used correctly
      #name
  button-name              critical  Buttons must have discernible text
      button[type="submit"]
  label                    critical  Form elements must have labels
      input[name="email"]
      input[name="guests"]
  link-name                serious   Links must have discernible text
      a[href$="help"]
  tabindex                 serious   Elements should not have tabindex greater than zero
      input[name="guests"]
  needs review: aria-hidden-focus (1 element)
```

Ten rules fail, and each one names the element, so the fixes are mechanical — a `<label>` for each field, a real `<input type="checkbox">`, `role="button"` spelled right or better a `<button>`, an `aria-label` on the icon button, `alt` on the image, `aria-expanded="true"` or `"false"`, an `aria-label` on the dialog, `autocomplete="name"` and no positive `tabindex`.

The last line is interesting — and easy to miss. The fixture also has a link inside a container with `aria-hidden="true"`, which hides a focusable element from the tree. axe did not report it as a violation. It reported it as "needs review", which axe's documentation describes as nodes that "could neither be determined to definitively pass or definitively fail".[^ch03-21] Lighthouse's audit only counts violations, so this one would pass. If you rely on Lighthouse alone, review items disappear. The script prints them for that reason.

Now the same with `--all`, which adds the rules for people:

```sh
node chapters/03-how-agents-see-a-page/agent-axe.mjs --all chapters/03-how-agents-see-a-page/fixtures/broken-booking.html
```

The full run adds `color-contrast` (the grey paragraph), `html-has-lang`, `image-alt` and `region` (content outside landmarks) to the list. None of those would have shown up in the agent audit.

### Both Nordlys front ends pass

I ran the 33 rules on six pages of each front end: the home page, the cabin list, Fjellro, the booking page, the contact page and the sign-in page. Both front ends had no violations on any page. Then I ran the full rule set on the Fjellro page:

```text
http://127.0.0.1:3000/cabins/fjellro  (axe-core 4.14.0, WCAG 2.x A/AA and best practices)
  no violations
http://127.0.0.1:3000/cabins/fjellro  (axe-core 4.14.0, WCAG 2.x A/AA and best practices)
  landmark-one-main        moderate  Document should have one main landmark
      html
  page-has-heading-one     moderate  Page should contain a level-one heading
      html
  region                   moderate  All page content should be contained by landmarks
      .brand
      .nav
      .page-title
      ... and 6 more
  needs review: color-contrast (1 element)
```

(Both runs used port 3000 in turn. The first block is the clean front end, the second the legacy one.)

The clean page has no violations at all. The legacy page fails three rules for people that are not in the agent set: no main landmark, no level-one heading and content outside landmarks. This is the honest summary of the audit. It is good at catching broken ARIA and unnamed controls, which is exactly where a well-meaning team that just added ARIA goes wrong. It cannot tell a page with no structure from a page with good structure. For that you need the other instruments: the agent walk from Chapter 2, the three views from this chapter and the perception contract that comes next. Figure 3.3 shows which instrument catches which kind of problem.

![Figure 3.3 — Which instrument catches which perception problem. The 33 agent rules catch unnamed controls and broken ARIA. The full accessibility rules add contrast, headings and landmarks. The perception contract checks the server's HTML on every page. Only the agent walk and the three views notice controls that are missing altogether.](images/figure-3-3.png)

## The perception layer: a contract for every page

The clean Nordlys front end already does everything this chapter recommends. So the layer for this chapter, `layers/03-perception/`, adds no markup. It adds checks that keep the markup that way, on every public page, every time the tests run. I call it a perception contract.

The checks read the HTML the server sends, before any JavaScript, for two reasons. First, that is View 1, the view of fetch-only agents. Second, it makes the checks fast enough to run in a unit test without a browser. They also deliberately cover what the 33 axe rules skip: one main landmark, one level-one heading, the page language and the absence of click-handler `<div>` elements.

> **Hands-on:** The layer is already in the repository. Start the site with `npm start -w nordlys-cabins -- --upto=3` and open http://127.0.0.1:3000/__audit to see the result of every layer's audit as JSON.

Listing 3.3 shows the first half of the check function.

**Listing 3.3** `nordlys-cabins/layers/03-perception/index.js` — the perception contract (excerpt)

```js
/** Check one page's HTML. Returns the ids of the rules it breaks. */
export function perceptionProblems(html) {
  const problems = [];
  if (!/<html\b[^>]*\slang="[a-z]{2}/i.test(html)) problems.push('html-lang');
  if (!/<title>[^<]+<\/title>/i.test(html)) problems.push('title');
  if (tags(html, 'main').length !== 1) problems.push('one-main');
  if (tags(html, 'h1').length !== 1) problems.push('one-h1');
  if (/\sdata-href="/i.test(html)) problems.push('no-click-divs');
```

The second half checks that every form control is labelled (by `<label for>`, by sitting inside a `<label>`, or by `aria-label`), that every button has text or an `aria-label`, and that every image has an `alt` attribute and both `width` and `height`. The last one is about stable layout, which we come back to in a moment. The audit runs the function on every public page: the home page, the cabin list, all six cabins, the guide, the FAQ, the contact page, the sign-in page and a booking page.

On the clean front end every check passes on all 13 pages. To see the contract fail, start the legacy front end with the same layer, `npm run start:legacy -w nordlys-cabins -- --upto=3`, and open `/__audit` again. This is the perception part of the response, with the page lists shortened:

```json
{
  "name": "perception",
  "layer": "03-perception",
  "ok": false,
  "checks": [
    { "id": "html-lang", "ok": true, "message": "passes on all 12 pages" },
    { "id": "title", "ok": true, "message": "passes on all 12 pages" },
    { "id": "one-main", "ok": false, "message": "fails on 12 of 12 pages: /, /cabins, /cabins/fjellro, …" },
    { "id": "one-h1", "ok": false, "message": "fails on 8 of 12 pages: /, /cabins, /cabins/fjellro, …" },
    { "id": "no-click-divs", "ok": false, "message": "fails on 12 of 12 pages: /, /cabins, /cabins/fjellro, …" },
    { "id": "labelled-controls", "ok": true, "message": "passes on all 12 pages" },
    { "id": "named-buttons", "ok": true, "message": "passes on all 12 pages" },
    { "id": "image-alt-and-size", "ok": true, "message": "passes on all 12 pages" }
  ]
}
```

The legacy front end has no booking page, only an overlay, so the audit checks 12 pages there. Three checks fail across the site. And three pass that perhaps should not: the legacy HTML has labelled controls and named buttons only because it has no controls and no buttons at all before the script runs. That is why I keep View 1 in the three-views script and the agent walk from Chapter 2 in the tests. A contract that checks "every control has a label" says nothing about a page with no controls.

The tests for this chapter, `tests/ch03-perception.test.js` and `tests/ch03-perception.spec.js`, check the contract on both front ends, run the 33 axe rules on both, compare the full rule set, run the broken fixture and capture the three views. If someone on the team replaces a button with a styled `<div>` next month, a test fails before the change reaches users or agents.

## Rendering for client-rendered apps

Most of this chapter looked at the rendered page, because browsing agents run a real browser. But View 1 deserves its own section, because it is where many modern front ends lose agents before any tree is built. The legacy Fjellro page is a small model of a client-rendered app: the server sends a shell of 2.1 KB, and the page's own script fetches the cabin data and injects the widget about 400 milliseconds after the page loads. A person never notices. Three kinds of visitor do.

The first is every agent that never runs JavaScript: the crawlers, the user-triggered fetchers and the "fetch this URL" tools from View 1. For them the legacy page is a name, three images and a footer. The second is a browsing agent that reads too early. If it takes its snapshot before the widget arrives it sees the same shell, and if it acts just after, the layout shift we measured in Chapter 2 moves the target under it. The third waits, and then meets a widget built from `<div>` elements, which is the perception problem from the rest of this chapter.

The clean front end avoids the first two problems with one decision: the server sends complete HTML. Its first response carries all 15 interactive elements (Table 3.2), so a fetch-only agent already sees the form and a browsing agent has nothing to wait for. The decision comes in three shapes.

### Server-side rendering

With server-side rendering (SSR), the server runs your components for each request, or once at build time for pages that rarely change, and sends finished HTML. For agents the rule is simple: the content a page exists for and the controls for its key task belong in the first response. Personal parts, such as a "my bookings" badge, can arrive later.

### Hydration

SSR alone gives you a page that a fetch-only agent can read but nobody can use until JavaScript attaches its behaviour. That step is hydration: the client-side framework takes over the server's HTML, attaches event handlers and keeps the state. Two things go wrong with agents here. First, a page that renders one thing on the server and something different after hydration (a different layout, a different set of buttons, a skeleton that is replaced) shows the agent two pages, and the swap between them is a layout shift. Keep the server output and the hydrated output the same, and reserve space for anything that changes. Second, controls that look ready but do nothing until hydration finishes are a trap for an agent that acts quickly. A native form avoids the trap, because the browser can submit it before any script runs.

### No-JavaScript fallbacks

That leads to the most robust pattern, which is also the oldest one: progressive enhancement. Build the key task so that it works with plain HTML (a real `<form>` with a `method` and an `action`, real links with real URLs), and let JavaScript make it nicer. The clean availability form from Chapter 2 is exactly that: a `GET` form with an `action` on the cabin page, complete in the HTML the server sends. The declarative WebMCP tool in Chapter 2 builds on the same form, and that is no coincidence. A form that works without script is also a form a browser can turn into a tool.

Where a full fallback is too expensive (a map, a rich editor, a seat picker), give the task a plain route next to it: a list view, a form with the same fields, or an API (Part 2).

> **Tip:** Test View 1 in CI, not only in a browser. `three-views.mjs` already opens the page with JavaScript switched off, and an assertion that the server's HTML contains the key form catches the day someone moves the widget into a client-only component.

## Stable layout: the part of perception that moves

There is one more thing agents perceive that no tree shows: time. A page that moves while it loads can make an agent act on something that is no longer there.

For a screenshot agent this is literal. It takes a picture, decides to click at a coordinate, and by the time the click arrives a late banner has pushed the button down. The click lands on something else. Anthropic's browser tool documentation recommends references from the tree over coordinates for exactly this reason: "A reference survives layout shifts and reflows that make pixel coordinates fragile".[^ch03-2] Tree-based agents are safer, but they are not immune: an agent that read the tree a moment too early may hold a reference to an element that was replaced.

Lighthouse puts `cumulative-layout-shift` into its agentic category for this reason, and we saw the legacy page fail it with 0.116 in Chapter 2. The fixes are the usual performance work:

- Give every image `width` and `height` (or a CSS aspect ratio), so the browser reserves its space. Our perception contract checks this.
- Render important content and controls on the server, so nothing arrives late and pushes things around.
- Reserve space for anything that does arrive late, such as a result panel or a banner.
- Do not cover actions with overlays. web.dev's guide warns about "ghost" elements and transparent overlays that sit on top of the real controls, and it recommends interactive targets that are big enough to hit.[^ch03-1] A cookie banner over the "Book" button is the most common example I see.

## What to take back to your team

Perception work touches more roles than any other layer. Developers use native elements and label every field. Designers put visible labels and clear button texts into the design system. Content people write link texts and alt texts that stand on their own. QA runs the 33 agent rules and keeps an agent walk for the main tasks. Product managers add "an agent can complete the task by the accessibility tree" to the definition of done.

Bottomline: everything in this chapter is accessibility work. If your team already takes accessibility seriously, most of your perception layer is done. If it does not, agents are a new and very concrete reason to start.

## Summary

- An agent can see a page in three ways: the HTML the server sends, the accessibility tree after rendering and a screenshot. Most browsing agents read the tree first and use screenshots as a fallback. Fetch-only agents never run your JavaScript.
- Two Nordlys pages that look the same produced screenshots of 61.6 and 66.3 KB, but trees with 2 and 23 interactive nodes. Looking at your pages does not tell you how agents perceive them.
- Every node in the tree has a role, a name, a description and states. The browser derives them from HTML first, then from ARIA. A labelled email field with a connected error message tells an agent what went wrong without any pixels.
- Semantic HTML is the zero-cost baseline. ARIA is for names, relationships and states that HTML cannot express, never a replacement for native elements. "ARIA for AI" advice is a reason to be careful, not a shortcut.
- Lighthouse's agent audit runs 33 axe rules that check what is in the tree. It catches unnamed controls and broken ARIA, it skips contrast, headings and landmarks, and it ignores axe's "needs review" items. A page with no structure passes it.
- The perception layer adds a contract for every public page, read from the server's HTML: one main landmark, one `h1`, a language, labelled controls, named buttons, sized images and no click-handler `<div>` elements. It runs in the tests.
- Client-rendered apps lose fetch-only agents and early readers. Render the key content and controls on the server, keep hydration from changing the page, and make the key task work as a plain HTML form.
- Stable layout is part of perception. Sized images, server-rendered content and no overlays over actions keep an agent's view valid between reading and acting.

[^ch03-1]: web.dev, "Build agent-friendly websites", updated 1 April 2026, https://web.dev/articles/ai-agent-site-ux (retrieved 2 November 2026).
[^ch03-2]: Anthropic, "Browser use tool", https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool (retrieved 2 November 2026).
[^ch03-3]: Zenity Labs, "Perplexity Comet: a reversing story", 11 February 2026, https://labs.zenity.io/post/perplexity-comet-a-reversing-story (retrieved 2 November 2026). This is a third-party analysis, not vendor documentation.
[^ch03-4]: Microsoft, "Playwright MCP", README, https://github.com/microsoft/playwright-mcp (retrieved 2 November 2026).
[^ch03-5]: OpenAI's ChatGPT Atlas help page, quoted by Simon Willison, "Introducing ChatGPT Atlas", 21 October 2025, https://simonwillison.net/2025/Oct/21/introducing-chatgpt-atlas/ (retrieved 2 November 2026). The help page itself could not be fetched for verification.
[^ch03-6]: Microsoft Support, "Browse with Copilot", https://support.microsoft.com/en-us/edge/copilot/browse-with-copilot (retrieved 2 November 2026).
[^ch03-7]: OpenAI, "Computer use", https://platform.openai.com/docs/guides/tools-computer-use, and Google, "Introducing the Gemini 2.5 Computer Use model", 7 October 2025, https://blog.google/technology/google-deepmind/gemini-computer-use-model/ (both retrieved 2 November 2026).
[^ch03-8]: Chrome for Developers blog, "Get your site agent ready", 22 June 2026, https://developer.chrome.com/blog/agent-ready-toolkit (retrieved 2 November 2026).
[^ch03-9]: Playwright, "Aria snapshots", https://playwright.dev/docs/aria-snapshots (retrieved 2 November 2026).
[^ch03-10]: Chrome for Developers blog, "Full accessibility tree in Chrome DevTools", https://developer.chrome.com/blog/full-accessibility-tree (retrieved 2 November 2026).
[^ch03-11]: MDN Web Docs, "Accessibility tree", https://developer.mozilla.org/en-US/docs/Glossary/Accessibility_tree (retrieved 2 November 2026).
[^ch03-12]: W3C, "HTML Accessibility API Mappings 1.0", Working Draft 26 October 2026, https://www.w3.org/TR/html-aam-1.0/, and "Accessible Name and Description Computation 1.2", Working Draft 21 October 2026, https://www.w3.org/TR/accname-1.2/ (both retrieved 2 November 2026).
[^ch03-13]: W3C, "Accessible Rich Internet Applications (WAI-ARIA) 1.2", Recommendation 6 June 2023, https://www.w3.org/TR/wai-aria-1.2/, and "WAI-ARIA 1.3", Working Draft 4 June 2026, https://www.w3.org/TR/wai-aria-1.3/ (status read from the W3C API, 2 November 2026).
[^ch03-14]: W3C, "Using ARIA", section 2.1 "First Rule of ARIA Use", https://www.w3.org/TR/using-aria/ (retrieved 2 November 2026).
[^ch03-15]: W3C, "ARIA in HTML", https://w3c.github.io/html-aria/ (retrieved 2 November 2026).
[^ch03-16]: Adrian Roselli, "OpenAI, ARIA, and SEO: Making the Web Worse", October 2025, https://adrianroselli.com/2025/10/openai-aria-and-seo-making-the-web-worse.html (retrieved 2 November 2026).
[^ch03-17]: WHATWG, "HTML Living Standard", section "Autofill", https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill (retrieved 2 November 2026).
[^ch03-18]: MDN Web Docs, "`<button>`: the Button element" (the `command` and `commandfor` attributes), https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button, and "`<dialog>`: the Dialog element" (the `closedby` attribute), https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog (both retrieved 2 November 2026).
[^ch03-19]: Lighthouse 13.6.0 source, `core/audits/agentic/agent-accessibility-tree.js`, the `TARGET_RULES` list, https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/agentic/agent-accessibility-tree.js (retrieved 2 November 2026).
[^ch03-20]: Chrome for Developers, "Agentic Browsing scoring", https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring (retrieved 2 November 2026).
[^ch03-21]: Deque, "axe-core API documentation", section on result types, https://github.com/dequelabs/axe-core/blob/develop/doc/API.md (retrieved 2 November 2026).
