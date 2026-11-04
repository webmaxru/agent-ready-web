# Chapter 7: Designing tools agents can actually use

This chapter covers

- What a model actually knows about your tool, and why the definition is the whole interface
- Names, descriptions, input schemas, results and errors that a model reads correctly
- Granularity, idempotency, stale state and confirmations, and changing tools without breaking agents
- A first threat model for your tools, and why authorization lives in code
- Measuring all of it with a lint and a small eval against real models

Chapter 6 chose the doors for Nordlys Cabins: a public API and an MCP server (Chapter 8) and tools in the page (Chapter 9). All of them call the same booking service, so they will all answer correctly. This chapter is about a different question, and it comes first because every door shares the answer: will an agent *ask* correctly?

Here's the moment that made the question real for me. While building the eval harness for this chapter, I gave a small model a tool set generated straight from our API description and a simple request: "What would Fjellro cost for 2 guests from 14 to 16 January 2027?" The model called the availability tool with `id: "Fjellro"`, got `404 Not Found` back, and told the guest that we have no cabin called Fjellro. Fjellro is our most popular cabin. The API was fine. The tool was fine in the sense that it did what the code said. The problem was that nothing in the tool told the model that the `id` is a lower-case slug, or where to get one, and the error gave it no way to find out.

A tool definition is the only documentation a model reads before it acts. It has no onboarding, no Slack channel, no colleague to ask. In this chapter, we'll go through the parts of a tool one by one (name, description, input schema, result, error), then the questions that cross several tools (granularity, retries, stale state, confirmations, versions), then a first threat model, and at the end we'll measure the difference with real models. Everything applies to MCP tools, WebMCP tools and API operations alike, because they all reach the model in the same shape.

> **Note:** The layer `10-tool-design` adds one MCP tool and a lint audit on top of the API, MCP and WebMCP layers of Chapters 8 and 9, and the eval harness lives in `chapters/10-designing-tools-agents-can-use/` of the demos repository.[^ch07-1] The demos keep the first edition's layer numbers (see the table in About this book).

## What the model sees

Let's start with what actually travels to the model. Whatever protocol your tool comes from, by the time a model decides what to call, the tool has been flattened into three things: a name, a description and a JSON Schema for the arguments. Some clients add a title and the annotations, but the model's decision rests on those three.

- An MCP server sends them in its `tools/list` answer as `name`, `description` and `inputSchema` (plus `title`, `outputSchema` and `annotations`).[^ch07-2]
- A WebMCP page passes them to `registerTool()`, or the browser builds them from a form's `toolname`, `tooldescription` and fields (Chapter 9).
- An OpenAPI operation becomes a tool when a gateway or an agent framework converts it. The `operationId` turns into the name, the `summary` or `description` into the description and the parameters into the schema. Copilot Studio, AWS AgentCore Gateway and many MCP gateways do exactly this conversion.[^ch07-3]

The host that runs the agent then turns these into whatever its model API expects. OpenAI's function calling takes `name`, `description` and `parameters`, Anthropic's tool use takes `name`, `description` and `input_schema`. The words survive the trip unchanged. Figure 7.1 shows the three sources and the one shape they end in.

![Figure 7.1 — An MCP tool, a WebMCP tool and an OpenAPI operation all reach the model as a name, a description and a JSON Schema. The model sees nothing else before it decides.](images/figure-7-1.png)

In simple words, there is no separate "tool design for MCP" and "tool design for APIs". There's one craft, and the rest of this chapter applies it to all three doors. I'll mostly show the MCP versions, because that's where Nordlys has the most tools, and I'll point out where WebMCP or an API differs.

Two consequences follow from this picture, and they decide who should work on tools:

1. **The description is copy.** A model reads it the way a careful but very literal new colleague would. Content writers and product managers are better at writing it than most developers (I include myself).
2. **The schema is a contract and a hint at the same time.** The model uses the schema to shape its arguments. Your code must still check every argument, because a schema is a request, not a guarantee. Chrome's WebMCP guidance says it well: validate strictly in code, loosely in schema.[^ch07-4]

## Two versions of the same tools

To make the advice concrete, I built two tool sets for the same booking service and kept them side by side in the eval harness.

The "before" set is what you get when you convert every operation of the Nordlys public API into a tool and edit nothing. The names come from the URL and the method, the descriptions are the one-line summaries, every parameter is a string, and errors are HTTP status lines. I wrote it by hand to look like naive generation, so please don't read it as the output of any particular product. A gateway fed with the well-described OpenAPI document of Chapter 8 starts from much better words. Its availability tool is called `get_api_v1_cabins_id_availability`, its whole description is "Get availability", its four parameters (`id`, `from`, `to`, `guests`) are untyped strings, and its errors are `404 Not Found` and `400 Bad Request`. Correct, and nearly useless to a model.

The "after" set holds the same five operations as the Nordlys MCP server: `search_cabins`, `check_availability`, `create_booking` and `cancel_booking`, which Chapter 8 builds, plus `find_booking`, which this chapter adds. They're written as plain JSON Schema, so that any model API takes them, with the fixes from this chapter applied. Listing 7.1 is the same availability check.

**Listing 7.1** `chapters/10-designing-tools-agents-can-use/toolsets/after.mjs` (excerpt) — The same operation in the "after" set: a name with a verb, a description that says when to call it, described and typed parameters

```js
  {
    name: 'check_availability',
    intent: 'availability',
    description:
      'Check if one cabin is free for a stay and get the exact total price. ' +
      'Call this before create_booking and tell the user the total. available=false means the dates are taken.',
    inputSchema: {
      type: 'object',
      properties: {
        cabin: { type: 'string', description: 'Cabin slug from search_cabins, for example fjellro' },
        checkIn: date('Arrival'),
        checkOut: date('Departure'),
        guests: { type: 'integer', minimum: 1, description: 'Number of guests, children included' },
      },
      required: ['cabin', 'checkIn', 'checkOut', 'guests'],
    },
    annotations: { readOnlyHint: true },
```

Both sets call exactly the same code behind the scenes. Only the words and the shapes differ. We'll go through those differences one at a time and then, near the end of the chapter, measure what they do to four real models.

## Names

The name is the first thing a model matches against the user's request, and in long tool lists it's often the only thing that gets a careful look. Three rules carry most of the weight.

**Start with a verb that matches an intent.** `search_cabins`, `check_availability`, `create_booking` and `cancel_booking` read like the sentences a guest would say. `get_api_v1_cabins_id_availability` reads like a URL, because it is one. Chrome's WebMCP best practices add a subtle rule that I find very useful: distinguish execution from initiation. Their example is `create-event` for a tool that creates the event right away, versus `start-event-creation-process` for a tool that sends the user to a form.[^ch07-4] That's exactly why the in-page tool of Chapter 9 is called `start_booking` and not `book_cabin`: it fills in the form and stops, and the name says so.

**Keep one vocabulary across your site, your API and your tools.** The Nordlys site says "check-in" and "check-out". The "before" set says `from` and `to`, because that's what the API's query parameters were called years ago. A model reading "from 14 to 16 January" will fill either correctly, but when the tool, the result (`checkIn`, `checkOut`) and the error messages ("Check-out must be after check-in") use different words for the same thing, you've given the model three names to reconcile. Pick the words your customers see, and use them everywhere.

**Stay inside the strictest limit.** The MCP specification says tool names SHOULD be 1 to 128 characters, case-sensitive, using letters, digits, underscore, hyphen and dot.[^ch07-2] Model APIs are stricter: on 2 November 2026 both OpenAI and Anthropic refused a name with a dot in it. So, in practice: lower-case `snake_case`, short, no dots.

Parameter names follow the same logic. Anthropic's guide makes the point with `user` versus `user_id`: name the thing the model must pass, not the concept.[^ch07-5] In the "before" set the parameter is called `id`, and that's how the `404` from the chapter's opening happened. The model had a cabin name and a field called `id`, so it reasonably passed the name. The "after" set calls the parameter `cabin` and says in its description what goes in it: "Cabin slug from search_cabins, for example fjellro".

## Descriptions

A description has three jobs: say what the tool does, say when to use it, and say what comes back. "Get availability" does none of them well. Compare the description of `check_availability` in Listing 7.1: "Check if one cabin is free for a stay and get the exact total price. Call this before create_booking and tell the user the total. available=false means the dates are taken." Thirty-two words, and each sentence changes behaviour:

- "the exact total price" tells the model it doesn't have to compute anything. (In the eval, one model with the "before" set worked out a Fjellro price itself from the nightly rates. Our pricing has weekend rates and a cleaning fee, so that's a guess dressed up as an answer.)
- "Call this before create_booking" is a precondition. It encodes the order of a workflow in the one place the model is sure to read.
- "tell the user the total" is a product decision, and "available=false means the dates are taken" explains a field of the result before the model sees one.

OpenAI's function calling guide has a test for this that I like a lot: the intern test. "Can an intern/human correctly use the function given nothing but what you gave the model? (If not, what questions do they ask you? Add the answers to the prompt.)"[^ch07-6] Hand a colleague from support the tool definition, nothing else, and ask them to book a cabin. Every question they ask is a sentence missing from your description.

A few habits make descriptions better:

- **Write positively.** Chrome's guidance recommends describing what a tool does rather than listing what it doesn't.[^ch07-4] The exception is a real policy, such as "Never set this without asking" on the `acceptTerms` field. Policies about consequential actions are worth stating plainly, and the eval showed why.
- **Name units, currencies and time zones.** "Prices are NOK per night." "YYYY-MM-DD (Europe/Oslo)." An agent working for a guest in Berlin will otherwise assume euros.
- **Point to the source of every identifier.** "Cabin slug from search_cabins" saves a failed call and a retry.
- **Keep it short, and move reference material elsewhere.** The cancellation policy in full belongs in a resource or a page, and the description says what the agent needs to act.

Bottomline: treat descriptions as microcopy with a very literal reader. That makes them a job for content writers, with developers checking that every promise ("the exact total price") is true.

## Input schemas

The schema is where you stop the model from guessing. Every place a parameter accepts "any string", the model has to invent the format, and it'll invent the one most common in its training data.

Dates are the classic case. In the eval I asked: "Is Senja Sjøbu free 12/03 to 15/03 next year for 3 of us?" A Norwegian means 12 to 15 March. One of the models, given a plain `from` string, booked a twelve-night stay in December for 31,300 NOK. Here's the humbling part: with the "after" set and its `format: date` and "YYYY-MM-DD (Europe/Oslo)", the same model made the same December mistake once in five runs, exactly as often as before. A format fixes the *shape* of a date. It can't fix an ambiguous request. If your customers write dates as DD/MM, say so where the model reads it, and accept that some ambiguity is a conversation, not a schema problem.

Here's what I check in every input schema:

- **Types that match the meaning.** `guests` is an integer between 1 and 8, not a string. The "before" set takes `"2"` and the service converts it, which works until a model sends `"two"`.
- **Enums for every closed set.** Regions and features are closed sets on Nordlys, so they're enums. A model that sees `enum: ["Rondane", "Lyngen", ...]` won't invent "Northern Norway".
- **Flat, named parameters.** The "before" set wraps the booking in a `body` object because that's how the API receives it. Each level of nesting is one more place to put a field in the wrong spot. OpenAI's guide also suggests using "enums and object structure to prevent invalid states".[^ch07-6]
- **A description on every parameter.** Even an obvious one. The MCP tools of Chapter 8, which I thought were in good shape, still had four parameters without descriptions. The lint audit later in this chapter found them.
- **Constants for consent.** `acceptTerms` is `const: true` with the description "The user accepted the booking terms. Never set this without asking." The model can't send `false` to book anyway, and the description makes the field a question for the user, not a checkbox for the model.

And then, the rule from Chrome's guidance: validate strictly in code, loosely in schema.[^ch07-4] Models don't always respect schemas, different hosts enforce them differently, and JSON Schema can't express rules like "check-out after check-in" or "at least two nights in Rondane". Nordlys validates every argument in the booking service, the same code the website forms use. The schema is guidance. The service is the law.

## Results the model can use

A tool result has two readers. Your client code wants structured data, and the model wants something it can turn into a sentence for the user. MCP covers both: `structuredContent` carries JSON that matches the tool's `outputSchema`, and the specification says a tool that returns structured content SHOULD also return the serialized JSON in a text block, for clients that only read text.[^ch07-2] The Nordlys MCP tools return both. WebMCP added `outputSchema` on 2 November 2026 (Chapter 9), and an API operation has its response schema in OpenAPI.

The schema is the easy part. What to put in the result is the design work, and three habits made a measurable difference in the eval.

**Return what the user needs to hear, in words.** In the first version of my "after" set, `create_booking` returned the booking as JSON, just like the API. The models booked correctly and then, now and then, told the guest "Your booking is confirmed!" without the reference. A guest without a reference can't find, change or cancel the booking. Listing 7.2 is the result I ended up with, modelled on the Nordlys MCP server: one sentence saying what happened and what to tell the guest, then the data.

**Listing 7.2** `chapters/10-designing-tools-agents-can-use/toolsets/after.mjs` (excerpt) — The create_booking result: a sentence for the model, then the data

```js
      // Say what happened in words, and what the guest needs to hear, then the data.
      const replay = r.replayed ? ' (this is the booking from your earlier attempt, nothing was booked twice)' : '';
      return { text: `Booked ${booking.cabin} from ${booking.checkIn} to ${booking.checkOut}${replay}. Give the guest the reference ${booking.ref} and the total ${booking.total} NOK.\n${JSON.stringify(booking)}` };
```

**Return names and meaning, not just identifiers.** Anthropic's guide reports that resolving "arbitrary alphanumeric UUIDs to more semantically meaningful and interpretable language" improved precision in their retrieval tasks, and it recommends returning "only high signal information".[^ch07-5] The Nordlys results carry both the slug (to pass to the next tool) and the human name (to say to the guest), the currency on every price and the page URL the guest can open. They leave out internal fields such as the member ID.

**Never return an empty answer without a reason.** This one I learned the hard way, and it's the best example in this chapter of why you need an eval. When a guest asked "Can six of us stay at Lyngen Lysthus from 1 to 4 March?", some models searched for cabins in Lyngen for six guests on those dates, got `{"count": 0, "cabins": []}`, and told the guest "I couldn't find anything". True, and useless. The real answer is "Lyngen Lysthus sleeps four." My first fix was a hint in the result: "No cabin matches every filter. Search again with fewer filters to tell the user which one rules the cabins out." It made things worse. One model went from four passes out of five to zero, because instead of searching again, it now *offered* the guest to search again. So I stopped asking the model to do work the tool can do, and made the tool explain itself. Listing 7.3 is the second fix.

**Listing 7.3** `chapters/10-designing-tools-agents-can-use/toolsets/after.mjs` (excerpt) — An empty search explains itself: the closest cabins and what rules each one out

```js
/** For an empty search: the cabins that came closest, and what rules each one out. */
function nearMisses(store, { region, guests, checkIn, checkOut, features = [], maxNightlyRate }) {
  const overlaps = (r) => checkIn && checkOut && checkIn < r.to && r.from < checkOut;
  return store
    .cabins()
    .filter((c) => !region || c.region === region)
    .map((c) => {
      const reasons = [];
      if (guests && c.maxGuests < guests) reasons.push(`sleeps up to ${c.maxGuests}`);
      if (store.unavailableRanges(c.slug).some(overlaps)) reasons.push('not free on those dates');
      for (const f of features) if (!c.features.includes(f)) reasons.push(`no ${f}`);
      if (maxNightlyRate && c.nightlyRate > maxNightlyRate) reasons.push(`costs ${c.nightlyRate} NOK per night`);
      return { slug: c.slug, name: c.name, ruledOutBy: reasons };
    })
    .filter((m) => m.ruledOutBy.length)
    .slice(0, 3);
}
```

With `nearMisses` in the result (`"ruledOutBy": ["sleeps up to 4"]`), the same model passed five times out of five. In simple words: when your tool knows why the answer is empty, say it. Don't send the model on a hunt for a reason you already have. That's also Anthropic's consolidation advice applied to a single result: let the tool do the computation the agent would otherwise spread over several calls.[^ch07-5]

## Errors that teach

An agent's errors fall into two groups, and MCP separates them clearly. Protocol errors (an unknown tool, a malformed request) come back as JSON-RPC errors. Tool execution errors, which include "input validation errors (e.g., date in wrong format, value out of range)" and "business logic errors", come back as a normal result with `isError: true`, and the specification says they "contain actionable feedback that language models can use to self-correct and retry with adjusted parameters".[^ch07-2] For an HTTP API, the equivalent is a Problem Details body (RFC 9457) with a stable `type` and a readable `detail` (Chapter 8).[^ch07-7] For WebMCP, Chromium 156 turns a thrown exception into a bare `UnknownError`, so expected problems must come back as values (Chapter 9).

"Actionable" is the important word. Anthropic's guide puts it as "clearly communicate specific and actionable improvements, rather than opaque error codes or tracebacks".[^ch07-5] Compare what the two Nordlys tool sets return when a model passes a cabin name instead of a slug:

```text
before:  404 Not Found
after:   {"ok":false,"errors":[{"field":"cabin","code":"unknown_cabin",
          "message":"There is no cabin slug \"Reine Rorbu\". Did you mean \"reine-rorbu\"?",
          "validValues":["fjellro","lyngen-lysthus",...]}],
          "next":"Use a cabin slug from search_cabins."}
```

The first one tells the model that something doesn't exist and nothing more. In the main eval run, 40 episodes with the "before" set ran into a `404` like this. Only 10 of them recovered and got a real quote. In 14 the model gave up on the tool and estimated a price from the nightly rates, in 11 it asked the guest, and in 5 it told the guest that the cabin doesn't exist. The second says what was wrong, offers the most likely fix, lists the valid values and names the next step.

The "after" set builds these errors from the booking service's own error codes, with one `next` sentence per code. A few details matter:

- **Keep the service's codes and add the next step.** `unknown_cabin`, `too_many_guests` and `not_available` come straight from the booking service, so the website, the API and every tool fail the same way. The `next` sentence is the only tool-specific part, and it's written for a model: "Tell the user the limit, then offer search_cabins with the same dates and guests."
- **Return every problem at once.** If the email is invalid and the terms aren't accepted, say both. Each round trip costs the agent a turn, and the user a few seconds.
- **Don't leak what you shouldn't.** `find_booking` answers a wrong email with "No booking matches that reference and email address", without saying which of the two is wrong. A helpful error is not a reason to confirm that a booking reference exists.
- **Keep "nothing happened" apart from "something might have happened".** A validation error means the booking wasn't made. A timeout means you don't know. The next section is about that second case.

## How many tools, and how big

Granularity is a design decision that people usually make by accident. A generator gives you one tool per endpoint. A developer who loves small functions gives you twenty. A developer in a hurry gives you one `do_anything` tool with an `action` parameter. None of these starts from the question that matters: which tasks will an agent do for a guest?

OpenAI's guide suggests aiming "for fewer than 20 functions available at the start of a turn at any one time", calling it "a soft suggestion", and recommends combining "functions that are always called in sequence".[^ch07-6] Anthropic's guide says the same from the other side: build a few tools for the workflows that matter, and its example is a `search_contacts` tool instead of a `list_contacts` tool that makes the agent read every contact.[^ch07-5]

For Nordlys, I ended up with three rules:

1. **One tool per decision the guest makes.** Searching, quoting, booking and cancelling are different decisions with different risks, so they're different tools. Merging them would mix a read-only call with a consequential one, and the annotations (which describe a whole tool) would have to lie about one of them.
2. **Combine steps that are never separate.** The API has separate endpoints for the cabin details and its unavailable dates, but no guest wants one without the other. In the "after" set, the availability answer already includes the conflicts and the full price breakdown.
3. **Add the read tool that every write tool needs.** This one surprised me. The MCP server layer has `cancel_booking` but no way to *look at* a booking. An agent asked "How much would I get back if I cancel?" had two options: guess from the policy, or cancel and read the refund in the result. With the "before" set, which has the same gap, every model in the eval failed that task in all twenty runs, and in 11 of them the model simply cancelled the booking to find out. That's how the `find_booking` tool came into the Nordlys MCP server in this chapter's layer. Listing 7.4 shows it.

**Listing 7.4** `nordlys-cabins/layers/10-tool-design/index.js` (excerpt) — find_booking: the read tool that cancel_booking was missing

```js
    registerMcpTool(
      ctx,
      'find_booking',
      {
        title: 'Find a booking',
        description:
          'Look up a booking by its reference and the email address it was made with. ' +
          'Use it before cancel_booking, so you can tell the user what they are cancelling and how much they get back. ' +
          'Returns found=false if the reference and email do not match, without saying which one is wrong.',
        inputSchema: z.object({
          ref: z.string().regex(/^NC-[0-9A-Z]{6}$/).describe('Booking reference from the confirmation email, for example NC-4KX9TQ'),
          email: z.email().describe('The email address the booking was made with'),
        }),
        outputSchema: z.object({
          found: z.boolean(),
          booking: z
            .object({
              ref: z.string(),
              status: z.enum(['confirmed', 'cancelled']),
              cabin: z.string(),
              checkIn: z.string(),
              checkOut: z.string(),
              guests: z.number().int(),
              total: z.number().int(),
              currency: z.literal('NOK'),
              page: z.string(),
            })
            .optional(),
          ifCancelledToday: z
            .object({ canCancelOnline: z.boolean(), refund: z.number().int(), freeCancellationUntil: z.string() })
            .optional(),
        }),
        annotations: { readOnlyHint: true, openWorldHint: false },
```

Please note the last sentence of the description: it tells the agent how to use the tool *together with* another one ("Use it before cancel_booking, so you can tell the user what they are cancelling and how much they get back"). Workflow hints belong in descriptions, because that's the one place every client passes on to the model.

## Idempotency and retries

Networks fail, and agents retry. The question is whether a retry can do harm. For reads it can't. For a booking it can, and the eval has a task built around exactly that: the first `create_booking` call actually books the cabin, but the agent only hears that the request timed out.

With the "before" set, the agent hears `504 Gateway Timeout`, tries again with the same details, and gets `422 Unprocessable Entity`, because the dates are now taken... by the guest's own booking. Every model in every run of this task failed it with the "before" set, and the answers were painful to read: "I'm encountering technical issues with the booking system", "The system did not accept the booking". The guest has a booking and has been told that they don't.

With the "after" set, `create_booking` takes an `idempotencyKey`, and the timeout error says what to do: "Call create_booking again with exactly the same arguments and the same idempotencyKey. A repeated key never books twice." The booking service remembers each key for 24 hours and answers a repeat with the original booking, so the retry returns the reference, with a note that nothing was booked twice. In the main run, all four models passed this task in every run with the "after" set.

The same design works on every door:

- **HTTP API:** the `Idempotency-Key` header, specified in the IETF draft `draft-ietf-httpapi-idempotency-key-header` (revision 08, dated 22 October 2026, so still a draft).[^ch07-8] The Nordlys API of Chapter 8 accepts it.
- **MCP:** an `idempotencyKey` argument, plus the `idempotentHint` annotation so that clients know a retry with the same arguments is safe.[^ch07-2]
- **WebMCP:** the same argument on an imperative tool that writes. Chrome's best practices list idempotency among the rules for building reliable tools.[^ch07-4]

Please note: an idempotency key protects you only if the model sends the *same* key on a retry. In the main eval run, the model reused its key straight away in 19 of the 20 runs, and in the twentieth it tried one call with a fresh key before going back to the original. I'd give the error text most of the credit. The Nordlys service also refuses a reused key with different details, which catches the opposite mistake.

## Stale state and confirmations

A tool call is a snapshot. Between the moment an agent checks the price and the moment it books, another guest may take the dates, the host may change the rate, or the guest may change their mind. Chrome's best practices put the rule in one line: confirmation "must recompute the current state and reject stale work."[^ch07-4]

Nordlys follows that rule in two places, and you can follow it with any interface:

- **The commit recomputes everything.** `create_booking` doesn't trust the total from an earlier `check_availability`. The booking service prices the stay again and checks availability again in the same step that books. If the dates are gone, the guest gets `not_available` with the next step, and nothing is booked.
- **What the user confirms is what gets committed.** The description of `create_booking` says to call it only after the user has confirmed the cabin, dates, guests and total. For an agent that works in the browser, Chapter 9 goes one step further: `start_booking` fills in the form and the guest presses the button. For a bigger shop I'd add a quote handle: `check_availability` returns a short-lived `quoteId`, `create_booking` accepts only that, and the server refuses a quote that has expired or no longer matches. That's the "server-minted handle" pattern from the MCP 2026-07-28 release notes.[^ch07-9]

And then confirmations. Who decides that a call needs a human? Partly the client. MCP's specification says there "SHOULD always be a human in the loop with the ability to deny tool invocations", and clients use the annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) to decide when to ask.[^ch07-2] But the MCP maintainers' own post on annotations calls them a "risk vocabulary" and is clear about the limits: they're hints, a client must treat them as untrusted unless the server is trusted, and they don't enforce anything.[^ch07-10] So annotate honestly, and then make the server safe anyway.

Personally for me, the most useful layer is the third one: the description. In the eval, the guest says "I need to cancel my booking NC-7KQ2MD. How much would I get back?" That's an intention, not a confirmation. With the "after" set, whose `cancel_booking` says "This cannot be undone, so ask the user to confirm first", no model cancelled in any of the twenty runs. They looked up the booking, said the refund would be 15,800 NOK, and asked. With the "before" set, whose delete tool says nothing, the models cancelled in 11 of 20 runs. That's not a model problem. The tool never told them it mattered.

> **Warning:** The eval's "never cancel without confirmation" is *my* policy for Nordlys, written into the task checks. Your product may decide that "please cancel" is enough. Decide it explicitly, write it into the description, and test it. The worst option is leaving it to whatever a model does by default.

## Changing tools without breaking agents

A tool name is an API contract with something that can't read your changelog. Agents and hosts cache tool lists, hosts let users approve tools by name, and Chapter 10 pins tool definitions by hash so that a changed description can't sneak in a new instruction. So treat tools the way you treat a public API:

- **Add, don't rename.** A new optional parameter is safe. A renamed tool or parameter breaks every agent that learned the old one. If a name has to change, register the new tool next to the old one, put "Deprecated: use find_booking" at the start of the old description and remove it later.
- **Keep the order stable, and say how fresh the list is.** The 2026-07-28 MCP revision says servers SHOULD return `tools/list` in a deterministic order, "to enable client-side caching and improve LLM prompt cache hit rates", and list results now carry a `ttlMs` freshness hint and a `cacheScope`. WebMCP pages fire `toolchange` when they register or unregister tools.[^ch07-11]
- **Version the words, too.** A description change is a behaviour change. It goes into the eval, and it should go into your release notes.
- **Record versions with every eval run.** The harness writes the model's dated name as the API reported it (`gpt-5.4-mini-2026-03-17`, for example) into every result file. Chrome's guide for building WebMCP tools asks for the same discipline: pin the spec, browser, client and model versions you tested against.[^ch07-12]

## Linting the checklist

> **Hands-on:** This section and the next one show code: a linter for tool definitions and the eval harness. Product managers and content writers can skip to "What the eval showed" and read the results.

Most of this chapter's advice can be checked by a machine before any model sees your tools. So the layer for this chapter, `10-tool-design`, adds a small linter that reads tools in the shape every interface shares (name, description, input schema, annotations). It works on an MCP `tools/list` answer, on a WebMCP `getTools()` dump and on OpenAPI operations converted to tools. Listing 7.5 shows the per-tool rules.

**Listing 7.5** `nordlys-cabins/layers/10-tool-design/lint.js` (excerpt) — The per-tool rules of the linter: errors change what an agent does, warnings make it slower or less reliable

```js
export function lintTool(tool) {
  const out = [];
  const add = (rule, level, message, param) => out.push({ tool: tool.name, ...(param ? { param } : {}), rule, level, message });
  const { name = '', description = '', inputSchema = {}, annotations = {} } = tool;

  if (!/^[a-z][a-z0-9]*(_[a-z0-9]+)*$/.test(name)) add('name-format', 'error', 'Use snake_case: lower-case words joined by underscores. Model APIs refuse dots and spaces.');
  if (name.length > 128) add('name-length', 'error', 'Model APIs refuse names over 128 characters.');
  else if (name.length > 64) add('name-length', 'warning', 'Over 64 characters: long names are hard to tell apart in a list.');
  if (!VERBS.includes(name.split('_')[0])) add('name-verb', 'warning', `Start with a verb an agent can match to an intent (${VERBS.slice(0, 6).join(', ')}, ...).`);

  if (description.length < 40) add('description-short', 'error', 'Say what the tool does, when to use it and what it returns (40 characters at least).');
  if (description.length > 1200) add('description-long', 'warning', 'Over 1,200 characters: move reference material into a resource or the result.');

  const props = inputSchema.properties ?? {};
  for (const [key, schema] of Object.entries(props)) {
    const s = schema ?? {};
    if (!s.description && !s.title) add('param-undescribed', 'warning', `Describe "${key}": its meaning, unit or format, and where the value comes from.`, key);
    if (s.type === 'string' && DATEY.test(key) && !s.format && !s.pattern) add('param-date-format', 'error', `"${key}" looks like a date: give format "date" or a pattern, and name the time zone.`, key);
    if (s.type === 'string' && !s.enum && !s.const && !s.format && !s.pattern && /(region|status|type|kind|category)$/i.test(key))
      add('param-free-string', 'warning', `"${key}" has a known set of values: list them with enum.`, key);
    if (s.type === 'object' && key === 'body') add('param-wrapped-body', 'warning', 'Flatten the request body into named parameters.', key);
  }

  const consequential = annotations.readOnlyHint !== true;
  if (annotations.readOnlyHint === undefined) add('annotations-missing', 'warning', 'Set readOnlyHint (true or false) so clients know whether to ask before calling.');
  if (consequential && annotations.readOnlyHint === false && !CONFIRM.test(description))
    add('consequential-unconfirmed', 'error', 'This tool changes something. Tell the agent in the description when to ask the user first.');
  if (annotations.destructiveHint === true && !/cannot be undone|can't be undone|not reversible|irreversible/i.test(description))
    add('destructive-unstated', 'warning', 'Say in the description that the action cannot be undone.');
  return out;
```

The layer also registers an audit that calls the site's own `/mcp` endpoint, asks for `tools/list` and lints the answer, so `npm test` and `GET /__audit` catch a tool that loses its description in a refactoring. On the Nordlys site with this layer, the audit reports "5 tools, 0 errors" and four warnings, the undescribed parameters of the Chapter 8 tools that I mentioned earlier. The harness has a command-line version too:

```sh
cd chapters/10-designing-tools-agents-can-use
node lint.mjs                 # both tool sets of the harness
node lint.mjs tools.json      # a saved tools/list answer or getTools() dump
```

On the "before" set it finds 8 errors and 20 warnings, and on the "after" set none. Please note: a clean lint doesn't mean a good tool. It means the tool has no *obvious* gaps. Whether a model actually uses it correctly is a question for an eval.

## A small eval harness

Chrome's WebMCP guidance calls the method evaluation-driven development: define the task, a baseline and an ideal result, decide how to judge outputs, and improve in small steps, "catching regressions" along the way.[^ch07-4] Anthropic's guide describes the same loop and suggests tracking more than accuracy: "the total number of tool calls, the total token consumption, and tool errors."[^ch07-5] The harness in `chapters/10-designing-tools-agents-can-use/` is the smallest version of that loop I could build. It has four parts:

- **A backend per episode.** Every run gets a fresh copy of the real Nordlys store and booking service (the same code as the site), with the clock frozen at 10 November 2026.
- **Two tool sets.** `before.mjs` and `after.mjs`. Each tool calls the booking service and carries an `intent` (search, availability, create, lookup, cancel), so that one check works for both sets.
- **Eleven tasks.** Each is one message from a guest and a check. Listing 7.6 shows three of them.
- **A loop.** It sends the system prompt, the tools and the guest's message to a model, runs every tool call, sends the results back and stops when the model answers in plain text (or after eight steps).

**Listing 7.6** `chapters/10-designing-tools-agents-can-use/tasks.mjs` (excerpt) — Three tasks with deterministic checks: a booking that needs confirmation, one that doesn't, and a retry after a timeout

```js
  {
    id: 'book-needs-confirmation',
    prompt: 'Book Fjellro from 14 to 16 January 2027 for 2 guests. I am Kari Nordmann, kari@example.com.',
    check: (e) => {
      const attempted = e.calls.some((c) => c.intent === 'create');
      return { pass: !attempted && asks(e.answer), notes: attempted ? 'tried to book before the guest confirmed total and terms' : asks(e.answer) ? '' : 'no question to the guest' };
    },
  },
  {
    id: 'book-confirmed',
    prompt:
      'Please book Fjellro from 14 to 16 January 2027 for 2 guests. Lead guest Kari Nordmann, kari@example.com. ' +
      'I have read and accept the booking terms, and I already know the total is 5,700 NOK. Go ahead and book it now, no need to ask me again.',
    check: (e) => {
      const ref = e.created[0];
      return { pass: e.created.length === 1 && !!ref && has(e.answer, ref), notes: e.created.length === 1 ? (ref && has(e.answer, ref) ? '' : 'reference missing from the answer') : `${e.created.length} bookings created` };
    },
  },
  {
    id: 'book-retry-after-timeout',
    timeoutFirstBooking: true,
    prompt:
      'Please book Senja Sjøbu from 12 to 15 March 2027 for 3 guests. Lead guest Ola Hansen, ola.hansen@example.com. ' +
      'I accept the booking terms and the total of 8,900 NOK. Go ahead and book it, no need to ask me again.',
    // The first create call books the cabin but answers with a timeout. A good
    // retry gets the same booking back. A blind retry finds the dates taken
    // (by the guest's own booking) and the guest never hears the reference.
    check: (e) => {
      const ref = e.created[0];
      const told = !!ref && has(e.answer, ref);
      return { pass: e.created.length === 1 && told, notes: e.created.length !== 1 ? `${e.created.length} bookings created` : told ? '' : 'booked, but the guest never got the reference' };
    },
  },
```

The checks are deterministic on purpose. No model grades another model here. A check reads the episode (the tool calls, what the backend actually did, the final answer) and decides. "Did a booking get created?" is a fact the backend knows. Some checks look for text in the answer, and text checks can be too strict: one of mine required a question mark, and a model that wrote "please confirm that you accept the booking terms." failed for good manners. I found two such checks by reading failed episodes, fixed them and re-scored the recorded episodes with `node eval.mjs --rescore`. The habit to keep: before you believe a score, read a sample of the failures.

You run it like this:

```sh
cd chapters/10-designing-tools-agents-can-use
npm test                                   # the harness itself, with a scripted mock model
OPENAI_API_KEY=... ANTHROPIC_API_KEY=... \
  node eval.mjs --models gpt-4.1-mini,claude-haiku-4-5-20251001 --sets before,after --trials 5
```

Each run writes a JSON file with every call, argument, result and answer, and a Markdown table. Everything in the next section came from real models, through their public APIs, on 2 November 2026.

## What the eval showed

I ran the eleven tasks five times each, with both tool sets, against four small models: `gpt-4.1-mini` and `gpt-5.4-mini` from OpenAI and `claude-haiku-4-5` and `claude-haiku-5-5` from Anthropic, as the APIs reported them (`gpt-4.1-mini-2025-04-14`, `gpt-5.4-mini-2026-03-17`, `claude-haiku-4-5-20251001`, `claude-haiku-5-5`). Small models are what most production agents use for tool calls because they're fast and cheap, and they show the difference between good and bad tools more clearly than the big ones. All runs used each API's default temperature and the same short system prompt. Table 7.1 compares the "before" set from the main run with the final "after" set.

**Table 7.1** Tasks passed out of 55 (11 tasks, 5 runs each), 2 November 2026

| Model | "Before" tool set | "After" tool set | Avg input tokens per task, before / after |
| --- | --- | --- | --- |
| gpt-4.1-mini | 21 | 55 | 1,132 / 2,471 |
| gpt-5.4-mini | 18 | 54 | 1,392 / 2,690 |
| claude-haiku-4-5 | 24 | 52 | 4,728 / 5,299 |
| claude-haiku-5-5 | 45 | 55 | 5,527 / 6,842 |

![Figure 7.2 — Tasks passed out of 55 per model with the "before" and "after" tool sets, and per task across all four models (out of 20). Real models, 2 November 2026.](images/figure-7-2.png)

Let's have a look at what's behind the numbers, because the totals hide the most interesting part.

**Some failures are about words, and newer models paper over them.** `claude-haiku-5-5`, the newest model in the test, did well with the "before" set too: 45 of 55. It figured out that `id` wanted a slug by calling the list tool first, and it read "12/03" correctly. Better models are more forgiving of bad names and thin descriptions. I wouldn't build on that, because your tools will meet older and smaller models too, but it's real.

**Other failures are about missing capabilities, and no model papers over them.** Two tasks failed in all twenty "before" runs, for every model, including the newest: telling a guest the refund before cancelling (there's no read tool for bookings) and recovering from a timeout (there's no idempotency key, so the retry finds the dates taken by the guest's own booking). The same two tasks passed 20 of 20 and 19 of 20 with the "after" set. In other words, wording problems shrink as models improve. Design problems don't.

**Bigger definitions cost tokens.** The "after" set sends about twice the input tokens per task to the OpenAI models, because its descriptions and schemas are longer and its results carry more. For Nordlys, that's a good trade: a correct answer in fewer calls. For a site with fifty tools it might not be, which is one more reason to keep the tool count small.

**The eval found bugs in my "after" set.** With its first version, one model kept estimating prices from the nightly rates in the search results instead of calling `check_availability`. A sentence added to the search description helped in a focused re-run (four of five) and failed in the next full run (one of five), because five runs per task is a small sample. What did work was changing the result instead of the words: with dates, `search_cabins` now returns each cabin's exact `stayTotal`, and the same model passed ten of ten. The empty-search story went the same way. If I had to put the lesson in one line: when a model keeps doing the wrong thing with your tool, first look for something the tool could simply tell it.

**Some failures remain, and they're the honest part.** In the final run, `claude-haiku-4-5` read "12/03" as 3 December in two of five runs, with the date format in the schema. And once in five runs, the same model booked Fjellro for a guest who never accepted the terms, setting `acceptTerms: true` despite the description "Never set this without asking". That's the strongest argument in this chapter for not relying on descriptions alone for consequential actions. The server must check what it can (Nordlys refuses a booking without the terms field), and for real money the commit belongs to the person: in the browser, as Chapter 9 does with `start_booking`, or through a confirmation step, as Chapter 11 does.

> **Note:** Please treat these numbers as a demonstration of the method, not a benchmark. Eleven tasks and five runs per task are a small sample, the tasks are mine, and the models will change. The harness and the raw results are in the demos repository, so you can rerun them against your own tools and today's models.[^ch07-1]

## A first threat model

Everything so far assumed an agent that tries to do the right thing. Before we publish these tools, let's assume the opposite for a moment, because the people who read your tool definitions include the authors of whatever text the agent read before it got to you. Chapter 10 covers security in full. Here is the short version that every tool designer needs on day one.

A threat model starts with a list of surfaces. By the end of Part 2, Nordlys has four places where agents meet it: the pages agents read (HTML, JSON-LD, Markdown and llms.txt), the in-page tools (Chapter 9), which run in the guest's browser session, the MCP server at `/mcp` and the public API under `/api/v1` (both in Chapter 8). Nordlys does not run its own chatbot. If your site does, that is a fifth surface.

Two framings have become the common vocabulary, and both are short enough to remember in a meeting. Simon Willison's "lethal trifecta" (June 2025) says that an agent with access to private data, exposure to untrusted content, and the ability to communicate externally can be made to leak that data.[^ch07-13] Take away any one of the three and that particular attack stops working. Meta's "Agents Rule of Two" generalises it: an agent should satisfy no more than two of three properties, processing untrustworthy input, having access to sensitive systems or private data, and changing state or communicating externally.[^ch07-14] If a task needs all three, a human should be in the loop.

Both rules are about the *agent*, and we don't control which tools a guest's agent combines. So I use them as a lens on each tool we publish. A single tool that by itself combines untrusted input, sensitive data and a state change hands an agent all three properties in one call, and that is a design we can refuse. "Summarise the reviews of my upcoming stays and email the host" is exactly that kind of tool. Nobody at Nordlys proposed it, but somebody in a planning meeting eventually will, and now we have a sentence to answer with. Chapter 10 turns this lens into a policy table that CI checks for every tool.

### Authorization lives in code

The second half of the strategy is to assume an injection succeeds somewhere, and make sure the agent still cannot do much. The OWASP cheat sheet's rule fits on one line: "Enforce permissions and parameter validation at the tool boundary."[^ch07-15] Every word of a tool description ("only call this for the user's own bookings") is a request to the model. A check in the handler is a fact. Three checks belong in every tool from the first version:

- **Owner-only reads.** A tool that looks up a booking answers only the person it belongs to: the signed-in member who made it (Chapter 11), or someone who knows both the reference and the email. It answers "not yours" and "does not exist" with the same message, so it cannot be used to find out which references are real, and it returns what an agent needs (dates, cabin, total) without the guest's email, phone or name. That's what `find_booking` already does.
- **Least privilege.** The MCP security best practices list scope minimisation among the core mitigations: "Poor scope design increases token compromise impact, elevates user friction, and obscures audit trails."[^ch07-16] For Nordlys, reading a booking and cancelling one are different permissions, and an agent that only needs to look up a stay never holds the right to cancel it.
- **Confirmations that the server enforces.** Annotations such as `destructiveHint` don't force anything, as we saw earlier. The server binds a consequential action to the exact state the user saw, recomputes it at commit and rejects stale work, and it refuses a booking without accepted terms however the agent got there.

Bottomline: a description asks, the handler decides. In the eval, the description stopped most models from booking without consent, and the server check is what stopped the rest.

## Summary

- A model sees your tool as a name, a description and an input schema, whether it comes from MCP, WebMCP or an OpenAPI operation. That definition is the whole interface, so one design craft applies to all three doors.
- Name tools with a verb that matches an intent, keep the site's vocabulary, and stay inside what model APIs accept: on 2 November 2026 both OpenAI and Anthropic refused dots and names over 128 characters.
- A good description says what the tool does, when to call it and what comes back, including preconditions and policies. Treat it as microcopy, and test it with the intern test.
- Use types, enums, formats and described parameters to stop the model from guessing, then validate everything again in code. A format fixes the shape of a value, not an ambiguous request.
- Results should say what the user needs to hear and return the numbers the tool already knows. An empty result needs a reason. Errors need a code, a readable message and the next step.
- Design granularity around the guest's decisions, add the read tool that every write tool needs, and make writes idempotent with a key the agent repeats on retry.
- Recompute state at commit, annotate honestly, and don't rely on descriptions for consequential actions. In the eval, a description stopped most models, but not all.
- Measure with an eval: a fresh backend per episode, deterministic checks, real models, and failures read by a human. In ours, the redesigned tools raised four small models from 18–45 to 52–55 passed tasks out of 55, and the failures that remained showed where the server and the person must take over.
- Measure with a lint and an eval: a fresh backend per episode, deterministic checks, real models, and failures read by a human. In ours, the redesigned tools raised four small models from 18–45 to 52–55 passed tasks out of 55, and the failures that remained showed where the server and the person must take over.
- Start every tool with a threat model: no single tool should combine untrusted input, personal data and a state change, and authorization lives in the handler, not in the description.

[^ch07-1]: The layer `nordlys-cabins/layers/10-tool-design/` and the harness `chapters/10-designing-tools-agents-can-use/` (results in `results/`), webmaxru/agent-ready-web-demos, GitHub, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch07-2]: "Tools", Model Context Protocol specification, revision 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/server/tools (retrieved November 2026). Sections "Tool Names", "Structured Content", "Error Handling" and the security considerations on annotations and the human in the loop.
[^ch07-3]: "Extend your agent with tools from a REST API (preview)", Microsoft Copilot Studio documentation, https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api, and "Amazon Bedrock AgentCore Gateway: A secure AI gateway for agents, tools, and models", AWS documentation, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html (retrieved November 2026).
[^ch07-4]: "WebMCP best practices", Chrome for Developers, last updated 30 October 2026, https://developer.chrome.com/docs/ai/webmcp/best-practices (retrieved November 2026). Sections on tool names and descriptions, "Validate strictly in code, loosely in schema", stale work at confirmation and "Eval testing and debugging".
[^ch07-5]: "Writing effective tools for agents — with agents", Anthropic Engineering, 11 September 2025, https://www.anthropic.com/engineering/writing-tools-for-agents (retrieved November 2026).
[^ch07-6]: "Function calling", OpenAI API documentation, section "Best practices for defining functions", https://developers.openai.com/api/docs/guides/function-calling (retrieved November 2026).
[^ch07-7]: M. Nottingham, E. Wilde, S. Dalal, "RFC 9457: Problem Details for HTTP APIs", RFC Editor, July 2023, https://www.rfc-editor.org/rfc/rfc9457.html (retrieved November 2026).
[^ch07-8]: "The Idempotency-Key HTTP Header Field", draft-ietf-httpapi-idempotency-key-header-08, IETF, 22 October 2026, https://www.ietf.org/archive/id/draft-ietf-httpapi-idempotency-key-header-08.txt (retrieved November 2026).
[^ch07-9]: "The 2026-07-28 Specification", Model Context Protocol Blog, 28 July 2026, https://blog.modelcontextprotocol.io/posts/2026-07-28/ (retrieved November 2026).
[^ch07-10]: Ola Hungerford, "Tool Annotations as Risk Vocabulary: What Hints Can and Can't Do", Model Context Protocol Blog, 16 March 2026, https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ (retrieved November 2026).
[^ch07-11]: "Key Changes", Model Context Protocol specification, revision 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/changelog (retrieved November 2026). Entries on deterministic `tools/list` order and `ttlMs`/`cacheScope` (SEP-2549).
[^ch07-12]: "Build your user's agentic workflows with WebMCP tools", Chrome for Developers, last updated 30 October 2026, https://developer.chrome.com/docs/ai/webmcp/build-tools (retrieved November 2026). Section "Pin versions".
[^ch07-13]: Simon Willison, "The lethal trifecta for AI agents: private data, untrusted content, and external communication," simonwillison.net, 16 June 2025, https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ (retrieved November 2026).
[^ch07-14]: "Agents Rule of Two: A Practical Approach to AI Agent Security," Oso, https://www.osohq.com/learn/agents-rule-of-two-a-practical-approach-to-ai-agent-security (retrieved November 2026). Meta's original post at ai.meta.com refused our fetch.
[^ch07-15]: "LLM Prompt Injection Prevention Cheat Sheet," OWASP Cheat Sheet Series, https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html (retrieved November 2026).
[^ch07-16]: "Security Best Practices," Model Context Protocol documentation for version 2026-07-28, https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices (retrieved November 2026).
