# Chapter 17: Privacy, consent and the human in the loop

This chapter covers

- What personal data an agent interaction creates at your site, and the GDPR principles that apply to it
- Why "consent" means three different things when an agent acts for a person
- Cookie banners and agents, an open question with a practical answer
- The EU AI Act's transparency rules, with the dates that matter for a website
- Human-in-the-loop patterns: confirmation pages, MCP multi round-trip requests with form and URL elicitation, and WebMCP's unsettled API
- Telling people what an agent did, giving them their data, and deleting agent logs on time

Chapter 16 was about keeping attackers out of the conversation between a guest, their agent and our site. This chapter is about the people inside that conversation. When an assistant books Fjellro for Astrid, who agreed to what? What does Nordlys learn about Astrid, and how long may it keep it? How does Astrid find out what her assistant did in her name, and how does she stop it? None of these questions is new. Web teams answer them for forms, newsletters and analytics every day. Agents change who clicks the button, and that changes where the answers have to live.

Please note: this chapter is not legal advice. I am a developer and a book author, not a lawyer, and the rules differ between countries. What I can do is show where the well-known principles land in an agent-ready site, cite the texts, and point out the questions to take to whoever handles data protection in your organisation. I say this once, here, and I trust you to remember it in every section that follows.

This chapter is for privacy and legal people, product managers and designers as much as for developers. The privacy officer will find the GDPR and AI Act touchpoints with dates. The product manager will find the decision of which actions an agent may finish alone. The designer will find what the human checkpoint needs to show. The code, marked as usual, builds the Nordlys layer that makes all of this real: a record of every agent booking, a plain-language email to the guest, a page where guests see and export what agents did, retention rules for agent logs, and a booking tool where the guest confirms on our own site.

## Who is who when an agent books a cabin

Let's start with the cast, because most privacy questions get easier once the roles are clear (Figure 17.1).

![Figure 17.1 — Who holds what in an agent booking. Astrid talks to her assistant, which runs on its provider's systems. The assistant calls Nordlys tools. Nordlys controls what it receives and keeps: the booking, the record of how it was made, the email it sends and its own logs. What the assistant keeps is its provider's business.](images/figure-17-1.png)

**The guest** (Astrid) is the person the data is about, the data subject in GDPR terms, and the party to the booking contract. She is the one who wants the cabin and the one who pays.

**The agent** is Astrid's tool. It runs on its provider's systems (an AI lab, a browser vendor, an app developer) under its provider's privacy terms. What the assistant remembers about Astrid, which other sites it visited for her and what it did with Nordlys's answers are the provider's responsibility. As Chapter 16 said about security, we cannot reach into it, and we should not pretend to.

**Nordlys** is the controller for everything that arrives at its servers: the booking, the tool calls, the logs, the emails it sends. For those, the obligations are exactly the ones Nordlys already has for its booking form. The agent does not reduce them, and it does not create a separate regime. It does create new data that a booking form never produced, and new places where data can leak.

Here is what an agent booking creates at Nordlys, compared with a booking through the form.

| Data | Booking form | Agent booking |
| --- | --- | --- |
| The booking (name, email, dates, guests, optional phone and requests) | Yes | Yes |
| Server access logs (IP address, user agent) | Yes | Yes, and the user agent names the agent product |
| Tool-call log (which tool, which client, outcome) | No | Yes (Chapter 16) |
| A record of how the booking was made and confirmed | Implicit, the guest was on the page | Must be explicit |
| Tool inputs and outputs | No | Yes, in transit, and in the agent's own logs |

The last two rows are where an agent-ready site needs new habits. The rest of this chapter works through them.

## GDPR principles on agent channels

The General Data Protection Regulation (GDPR) applies to agent traffic the way it applies to all processing. No regulator has written agent-specific rules for websites as of November 2026. Two data protection authorities have published early analyses of agentic AI. The UK Information Commissioner's Office (ICO) published a Tech Futures report on agentic AI in January 2026, which it says is not intended as guidance.[^ch17-3] Spain's data protection authority, the AEPD, published "Inteligencia Artificial Agéntica desde la perspectiva de Protección de Datos" in February 2026.[^ch17-2] Its warning about agent memories applies to our logs too: in a law firm's summary, keeping lots of data "just in case" or to "optimize performance" can clash with purpose limitation and data minimisation.[^ch17-1] I read both reports through those summaries (the ICO page sat behind a bot challenge for us), so read the originals before you quote them in a policy.

Four GDPR articles do most of the work for an agent-ready site.

**Data minimisation, Article 5(1)(c).** Personal data must be "adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed".[^ch17-4] For agents this has a very concrete meaning: a tool returns the fields the task needs. Chapter 16's `get_booking` tool returns the cabin, dates, guests, total and cancellation deadline, and no name, email, phone or free-text requests. An agent planning a trip needs nothing more. The same article's purpose limitation (5(1)(b)) and storage limitation (5(1)(e)) apply to the tool-call log: it exists for security investigations, so it holds what an investigation needs, for as long as one is plausible.

**Data protection by default, Article 25(2).** "The controller shall implement appropriate technical and organisational measures for ensuring that, by default, only personal data which are necessary for each specific purpose of the processing are processed."[^ch17-5] The words "by default" matter for tool design. A tool with an optional `includeContactDetails: true` parameter is a tool where a manipulated agent can ask for more. If a task really needs contact details, that is a separate tool, behind its own OAuth scope (Chapter 14), with its own entry in the policy table.

**Lawful basis, Article 6.** Every processing needs one of six bases. For a booking that the guest asked for, it is usually Article 6(1)(b): processing "necessary for the performance of a contract to which the data subject is party or in order to take steps at the request of the data subject prior to entering into a contract".[^ch17-6] Note what that implies. A booking made through an agent rests on the same basis as one made through the form, *if* the guest asked for it. Whether the guest asked is the question the next section is about.

**Automated decisions, Article 22.** People have "the right not to be subject to a decision based solely on automated processing" with legal or similarly significant effects.[^ch17-7] Nordlys does not score its guests. But an agent-ready site often adds automation around agents: automatic refusal of bookings from "suspicious" agents (Chapter 15), dynamic pricing per channel, automatic cancellation of unconfirmed requests. If any of these decide something significant about a person with no human involved, check Article 22 with your privacy officer before you ship it.

### A data inventory of the agent interfaces

Minimisation is easier to discuss with a table on the screen than in the abstract. Here is the one I would put in front of Nordlys's privacy officer: every MCP tool after Chapter 17, and the personal data its answer carries.

| Tool (layer) | Personal data in the answer | Comment |
| --- | --- | --- |
| `search_cabins`, `check_availability` (8) | None | Public catalogue and prices |
| `get_cabin_reviews` (16) | Reviewers' first names | Reviewers are data subjects too. First name only, as on the page |
| `find_booking` (10), `get_booking` (16) | None directly: reference, cabin, dates, guests, total | Owner checks decide who gets even this |
| `list_my_bookings` (14) | None directly, for the signed-in member's own bookings | Behind the `bookings:read` scope |
| `create_booking` (8) | The guest's name, echoed back | The agent sent it a moment earlier. Worth trimming in a later version |
| `cancel_booking` (8), `cancel_my_booking` (14) | None directly | Refund amount only |
| `request_booking`, `check_booking_request` (17) | Booking reference only | Name and email go in through form mode, not out |

Two observations come from building this table, and I expect them to repeat on your site. First, the inventory found one tool that returns more than it needs (`create_booking` echoes the name). It is harmless, because the agent already had it, but "harmless because the agent already had it" is the kind of reasoning that quietly turns into "return the full profile". Second, the reviews tool returns personal data about people who are not the user at all. Third-party personal data in tool outputs is easy to forget, and the review authors never agreed to be quoted to AI systems in particular. Showing the same first name that the public page shows is a reasonable line. Showing their full name, city or other reviews would not be.

Keep this table in your record of processing activities, and add a row in the same pull request as every new tool. Chapter 16's policy table already forces that pull request to exist.

## Three kinds of consent

The word "consent" causes more confusion in agent discussions than any other, because it is used for three different things. Let's separate them, using Nordlys as the example.

### Consent as a lawful basis

In GDPR language, consent is one of the six lawful bases, with strict conditions (freely given, specific, informed, unambiguous, as easy to withdraw as to give). For a cabin booking, consent is usually the *wrong* basis: the booking is a contract, and Article 6(1)(b) covers the processing it needs. You do not need a "consent checkbox" for processing the guest's name to book the cabin they asked for, whether a person or an agent sent it.

Consent as a lawful basis does come up for the extras: the marketing newsletter, the "tell me about last-minute deals" checkbox, analytics cookies. An agent filling in a booking should not tick those boxes for the guest, and a site should not accept them through an agent channel. Nordlys's MCP and API booking tools simply have no marketing fields.

### Consent as authority

The second meaning is "did Astrid actually ask for this?". When a booking arrives through the MCP server with a valid token from Chapter 14, Astrid has authorised the assistant to act on Nordlys for her, within the scopes she granted. That is real authority, recorded by the authorisation server. When a booking arrives through the public API or an anonymous MCP call, Nordlys only has the agent's word for it.

This is the core problem of agent consent, and no protocol solves it today. The emerging answer in agent commerce is the signed mandate (AP2 and its relatives, discussed in Chapter 12), where the user's instruction travels with cryptographic proof. Until those are common, a site has two tools: keep a record of what it was told and how (so the question can be answered later), and for consequential steps, bring the person to a page where the site sees their decision with its own eyes. Both are built in this chapter.

### Consent as acceptance of the terms

The third meaning is contractual. A booking includes cancellation terms, and the guest has to accept them. Nordlys's form has a checkbox. Chapter 8's `create_booking` tool requires `acceptTerms` to be the literal value `true`, which means the agent has to state, explicitly, that the user accepted. Chapter 12's checkout handoff goes further: the guest accepts the terms on Nordlys's own page.

Both are legitimate designs, and the choice is a business decision. An agent accepting terms on a user's behalf is like a travel agent doing it, and the agent's provider and the user have their own agreement about that. But it is weaker evidence, and when something goes wrong, the dispute is about who said what. For Nordlys, I recommend this split: flexible-rate stays booked by a signed-in member with a `bookings:write` token may go through `create_booking`, and everything else (first-time guests, non-refundable stays, anything without a verified member) goes through `request_booking`, which ends on our page. You can encode this split in the tool descriptions and enforce it in the handler.

### Cookie banners and agents

One kind of consent deserves its own section, because agents meet it on almost every European site: the cookie banner. Under the ePrivacy rules, non-essential cookies (analytics, advertising) need consent, and consent management platforms (CMPs) collect it through a banner.

An agent that browses a site sees that banner like a person does, and it can click a button. Is that click consent? A consent-management vendor's guide from 28 October 2026 puts it in one sentence: "the technical ability to click a consent button does not mean the agent has permission to make that decision on behalf of the user".[^ch17-10] I found no regulator guidance on whether an agent's click can be valid consent, so treat this as an open legal question.

What a web team can do today is practical:

- Build the banner in semantic HTML with labelled buttons (Chapter 3), so an agent can find and press "Reject all" as easily as "Accept all". Make both equally prominent for people, too.
- Do not count an agent's "Accept all" as consent for analytics or advertising cookies. If you identify agent traffic (Chapter 15), set only strictly necessary cookies for it.
- Prefer server-side analytics for agent traffic. Chapter 19 measures agents from server logs, which needs no cookies at all.

Nordlys, for what it's worth, sets one cookie: the sign-in session, which is strictly necessary and needs no banner.

## The EU AI Act, for website owners

The EU AI Act is the other regulation people ask about, and here the honest answer is: for most websites, it touches very little. Let's be precise about the parts that do.

The transparency rules in Article 50 have applied since 2 August 2026. The European Commission's AI Act Service Desk timeline lists that date with the words "Transparency rules (Article 50) start to apply."[^ch17-11] The "Digital Omnibus on AI", which a law firm's summary identifies as Regulation (EU) 2026/1744 in force since 27 July 2026, postponed the high-risk system requirements to December 2027 but left the Article 50 date in place, with a grace period until 2 December 2026 for generative AI systems already on the market before 2 August 2026 to implement machine-readable marking.[^ch17-13] I have not checked the regulation number against EUR-Lex, so verify it before citing it in a policy. The same summary puts the maximum fine for Article 50 violations at 15 million euros or 3% of worldwide annual turnover, whichever is higher.

Table 17.1 maps the parts of Article 50 to the situations a website meets.

| Article 50 | Who it binds | Does it apply to Nordlys? |
| --- | --- | --- |
| 50(1): people must be informed that they are interacting with an AI system, unless that is obvious | Providers of AI systems that interact directly with people | Only if Nordlys runs its own chatbot or assistant. A guest's third-party agent visiting Nordlys is its provider's obligation |
| 50(2): synthetic audio, image, video and text output marked in a machine-readable format | Providers of generative AI systems | No, unless Nordlys offers a generative system |
| Disclosure of AI-generated text published to inform the public on matters of public interest, unless human-reviewed with editorial responsibility | Deployers who publish such text | Worth checking for AI-written articles, much less for cabin descriptions |
| Disclosure of deepfakes | Deployers | Not for a booking site that does not publish synthetic media of people |

The text of Article 50(1) is short: providers "shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system".[^ch17-12] So if your site adds a "Ask our assistant" chat window, label it as AI. That is good practice anyway.

What the AI Act does not do is regulate the site that an agent visits. Nordlys does not become a "provider" or "deployer" because an AI agent calls its MCP server. I mention this because it is a common worry that adding agent interfaces brings a site under the AI Act. For the interfaces this book builds, it does not. Your own chatbot does, and AI-generated content you publish might.

## The human in the loop

Now to the design question that sits under all three kinds of consent. Which steps should an agent be allowed to complete alone, and which should bring the person back? And when the person must come back, how does the agent bring them?

The first question is a product decision. Here is how I would frame it for Nordlys, and the same questions work for most sites:

| Step | Agent alone? | Why |
| --- | --- | --- |
| Search cabins, check availability, read reviews | Yes | Read-only, no personal data |
| Look up one's own booking | Yes, with proof of ownership | Read-only, minimal output (Chapter 16) |
| Book a flexible-rate stay as a signed-in member with a write token | Yes | Verified authority, free cancellation as the safety net |
| Book as a first-time guest, or a non-refundable stay | No, the guest confirms on our page | Weak authority, a mistake costs the guest money |
| Pay, or enter card details | Never through the agent | Payment data belongs on our page (MCP requires this, see below) |
| Cancel a booking | Yes with a write token, otherwise with a confirmation | Hard to undo once the cabin is rebooked |

The second question has three answers, one per kind of agent interface.

### On the plain web: the confirmation page

The oldest human checkpoint is a page. Chapter 12 built one: the agent prepares a booking session, the session's `continue_url` points at `/checkout/{id}` on Nordlys's own site, and the guest reviews the stay and confirms it there. "An assistant prepared this booking for you. Nothing is booked until you confirm it here."

For designers, three details make such a page work. First, show the facts the agent might have gotten wrong: dates in words ("Mon, 8 Feb 2027 to Fri, 12 Feb 2027"), number of guests, total with fees, cancellation deadline. Second, show what the agent sent and let the guest change it, because the name and email came through a machine. Third, make the page expire (Chapter 12's sessions last 15 minutes) and say so, so a forgotten link cannot be confirmed weeks later at an old price.

This works with every agent, because every agent can hand a link to its user. Its weakness is the gap: after handing over the link, the agent does not know whether the guest confirmed. That is what the protocols below add.

### In MCP: multi round-trip requests

MCP has had a way for servers to ask the user something since 2025: elicitation. In the 2026-07-28 revision, the way it travels changed. Earlier, a server sent an `elicitation/create` request to the client in the middle of a tool call, which needed a stateful connection. The new revision introduced **multi round-trip requests** (MRTR): the tool call itself answers with "input required", the client collects the input, and then it calls the tool again with the answers. The specification is blunt about the change: servers MUST use the MRTR pattern for server-to-client requests, "The previous pattern of server-initiated requests is no longer supported. This is a breaking change."[^ch17-14]

Elicitation has two modes, and the difference is the heart of this chapter.[^ch17-15]

- **Form mode** collects structured data through the client. The server sends a small JSON Schema, and the client shows a form to the user. Contact details such as a name or email address are allowed, "subject to the user's ability to review and decline".
- **URL mode** sends the user to a page outside the client, for "interactions that must not pass through the MCP client". The spec names auth flows and payment processing as the typical uses. URL mode arrived in the 2025-11-25 revision, and the specification warns that its design "may change in future protocol revisions".

The rule that connects the two is a MUST: "Servers MUST NOT use form mode elicitation to request sensitive information such as passwords, API keys, access tokens, or payment credentials" and "Servers MUST use URL mode for interactions involving such sensitive information". Clients have MUSTs too: they make clear which server is asking, offer decline and cancel, let the user review a form before sending, and for URL mode, "clearly display the target domain/host and gather user consent before navigation to the target URL".

Figure 17.2 shows how `request_booking`, the new Nordlys tool, uses both modes in three rounds.

![Figure 17.2 — request_booking in three rounds. Round 1: the tool opens a booking session and answers input_required with a form-mode request for name and email. Round 2: the client calls again with the answers, and the tool answers input_required with a URL-mode request for the checkout page. The guest confirms there, on Nordlys. Round 3: the client calls again, and the tool returns the booking reference only if the guest confirmed.](images/figure-17-2.png)

> **Hands-on:** The next pages build `request_booking` and its tests in `layers/17-consent/`. If you don't write code, here is what they achieve: an agent can prepare a booking, ask its user for a name and email in its own interface, and then hand the user a link to Nordlys's checkout page. The booking exists only after the guest confirms on that page, and the agent finds out when it asks again. Pick up again at "In WebMCP: an open question".

Here is what the first answer looks like on the wire. The agent called `request_booking` for Fjellro, and instead of a result, it got this.

**Listing 17.1** The first `tools/call` answer from `request_booking` (captured from the demo)

```json
{
  "result": {
    "resultType": "input_required",
    "inputRequests": {
      "guest": {
        "method": "elicitation/create",
        "params": {
          "message": "Who is staying at Fjellro? Nordlys sends the confirmation to this email.",
          "requestedSchema": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "Full name of the main guest",
                "minLength": 2
              },
              "email": {
                "type": "string",
                "description": "Email address for the confirmation",
                "format": "email"
              }
            },
            "required": [
              "name",
              "email"
            ],
            "$schema": "https://json-schema.org/draft/2020-12/schema"
          },
          "mode": "form"
        }
      }
    },
    "requestState": "eyJzdGVwIjoiZ3Vlc3QiLCJzZXNzaW9uIjoiYmtzXzZSempIN2xLUTBLZ2cwWlMiLCJiaW5kIjoiZ296RUNNeTE1SnpyY0pfTkxDLVlQeG13bmpIeXJsR0hHZnlZbnllcXhxdyIsImV4cCI6MTc5MzY1ODU3ODQ4M30.XhIPeRHStaYf0w6b_XsxBIw8k5bmX6_0tlQ1duDT8M0",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "nordlys-cabins",
        "title": "Nordlys Cabins",
        "version": "1.0.0"
      }
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

Three fields carry the pattern. `resultType: "input_required"` tells the client this is not the end. `inputRequests` is a map of embedded requests, here one form-mode elicitation keyed `guest` (the key is the server's choice). And `requestState` is an opaque string that the client must echo back, byte for byte, on the next call. It is how a stateless server remembers where it was: the client carries the state, and the server does not need a session store.

The MCP TypeScript SDK v2.4.0 has builders for these answers: `inputRequired()` for the result, `inputRequired.elicit()` for a form request, `inputRequired.elicitUrl()` for a URL request, and `acceptedContent()` to read a validated answer on the next round. Here are rounds two and three of the handler.

**Listing 17.2** `nordlys-cabins/layers/17-consent/request-booking.js` — rounds two and three of request_booking (excerpt)

```js
      // Round 2: store the guest, then send the user to our own page to confirm.
      if (state.step === 'guest') {
        const guest = acceptedContent(responses, 'guest', Guest);
        if (!guest) return done({ status: 'not_requested', reason: 'The user did not share their name and email.' });
        const [first, ...rest] = guest.name.trim().split(/\s+/);
        const res = await ucp(`/ucp/v1/booking-sessions/${state.session}`, {
          method: 'PUT',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ booker: { first_name: first, last_name: rest.join(' ') || first, email: guest.email } }),
        });
        const session = await res.json();
        return inputRequired({
          inputRequests: {
            confirm: inputRequired.elicitUrl({
              message: 'Review the stay and accept the terms on nordlys.example. Nothing is booked until you confirm there.',
              url: session.continue_url,
            }),
          },
          requestState: sealState({ step: 'confirm', session: state.session }, bound),
        });
      }

      // Round 3: the user saw the page (or declined). The booking exists only if they confirmed.
      const answer = responses?.confirm?.action;
      const session = await status(state.session);
      if (session.status === 'completed') {
        return done({ status: 'confirmed', ref: session.confirmation?.id ?? null, cabin: session.property.id });
      }
      if (answer !== 'accept') {
        await ucp(`/ucp/v1/booking-sessions/${state.session}/cancel`, { method: 'POST' });
        return done({ status: 'not_booked', reason: 'The user declined to open the confirmation page.' });
      }
      return done({
        status: 'awaiting_guest',
        checkout: state.session,
        continue_url: session.continue_url,
        next: 'The user has the confirmation page. Call check_booking_request with this checkout id later.',
      });
    },
```

Round two stores the guest on the Chapter 12 booking session and asks for a URL-mode interaction with the session's `continue_url`. Note the message: it tells the user what will happen and that nothing is booked yet. The client shows it, with the target domain, before it opens anything.

Round three contains the subtle part. When the user accepts a URL-mode request, the specification says the response "indicates that the user has consented to the interaction. It does not mean that the interaction is complete."[^ch17-15] The user may have opened the page and closed it again. So the tool does not trust `accept`. It asks the booking session. If the guest confirmed, the result has the booking reference. If the user declined, the session is cancelled. And if the user accepted but has not confirmed yet, the tool says so and offers `check_booking_request` for later. The specification also allows a server to answer with another `input_required` in that case. I chose a plain result instead, because a model handles "awaiting_guest, check later" well, and an endless loop of the same link does not help anyone.

One more detail in that listing matters for security: the `requestState` comes back from the client, so the server must not trust it either. The specification is explicit. Servers "MUST treat `requestState` as an attacker-controlled input", and if it influences business logic, they "MUST protect its integrity (e.g. HMAC or AEAD) and MUST reject state that fails verification". To prevent replay, it says servers SHOULD bind the state to the authenticated principal, a short expiry and the originating request.[^ch17-14] Without that, an agent could edit the state to point at someone else's booking session. Here is the signing.

**Listing 17.3** `nordlys-cabins/layers/17-consent/request-booking.js` — signing and checking requestState (excerpt)

```js
// requestState travels through the client and comes back as attacker-controlled
// input. The spec says to integrity-protect it when it drives business logic: we sign it.
// Following the spec's replay advice, the state is bound to a short expiry, to this
// tool and its arguments, and to the signed-in member when there is one.
const mac = (body) => createHmac('sha256', SECRET).update(body).digest('base64url');
const bindingOf = (args, member) => mac(JSON.stringify(['request_booking', args, member ?? null]));

export function sealState(payload, { args, member = null, minutes = 15 }) {
  const body = Buffer.from(JSON.stringify({ ...payload, bind: bindingOf(args, member), exp: Date.now() + minutes * 60_000 }))
    .toString('base64url');
  return `${body}.${mac(body)}`;
}
export function openState(state, { args, member = null }) {
  const [body, sig] = String(state ?? '').split('.');
  if (!body || !sig) return null;
  const expected = Buffer.from(mac(body));
  const given = Buffer.from(sig);
  if (expected.length !== given.length || !timingSafeEqual(expected, given)) return null;
  const payload = JSON.parse(Buffer.from(body, 'base64url').toString());
  if (payload.exp <= Date.now() || payload.bind !== bindingOf(args, member)) return null;
  return payload;
}
```

The SDK leaves this to you on purpose. Its own type documentation says it "applies no integrity protection by default", and it ships an HMAC codec that a server can plug in through its options. Nordlys signs by hand, because the Chapter 8 layer creates the MCP server and this layer only adds tools, and because I want the mechanism visible in the book. The state is signed, not encrypted: anyone can base64-decode it and read the session id. That is fine here. If your state carries anything confidential, use an AEAD construction instead.

Here is the second round's request, as the client receives it, and the final result after the guest confirmed.

**Listing 17.4** The URL-mode request of round two, and the result of round three (from the demo)

```json
{
  "mode": "url",
  "message": "Review the stay and accept the terms on nordlys.example. Nothing is booked until you confirm there.",
  "url": "https://nordlys.example/checkout/bks_CVvdK-EBTRp1rTDG"
}
```

```json
{
  "status": "confirmed",
  "ref": "NC-UW2KMJ",
  "cabin": "fjellro"
}
```

The tests drive the whole flow with the SDK's own client, which fulfils `input_required` answers automatically through the handler you register for `elicitation/create`. The test's handler plays the user: it answers the form with Astrid's name and email, and for the URL request it submits the checkout page the way Astrid would, then answers `accept`. Other tests cover a user who declines (nothing is booked), a user who accepts but confirms later (`awaiting_guest`, then `confirmed` from `check_booking_request`), and a forged or replayed `requestState`.

### In WebMCP: an open question

What about tools inside the page, with WebMCP (Chapter 9)? Here the honest answer is that the human-in-the-loop API is not settled. The WebMCP specification draft of 27 October 2026 has no method for it in its interface definitions.[^ch17-17] An open pull request, "Replace requestUserInteraction with requestUserInput", proposes three modes (interactive, form and url) aligned with MCP elicitation.[^ch17-16] Meanwhile, Chrome's page on WebMCP tool security, updated 1 September 2026, still says "the spec draft includes `requestUserInteraction()`".[^ch17-18] I would not write production code against either name yet.

The good news is that WebMCP needs it less than MCP does. A WebMCP tool runs in a page the user has open, in their browser. The user is already there. So the human-in-the-loop pattern for WebMCP today is the page itself:

- Mark the tool with `consequentialHint: true`, so the agent or browser can ask the user before it runs.
- Let the tool *prepare* the action and show it in the page's own UI (a filled-in booking summary with a "Confirm" button), and return a result that says "waiting for the user to confirm on the page".
- Or return the URL of the confirmation page, exactly like `continue_url`, and let the agent navigate there.

The hint alone leaves the asking to the agent or browser. In the other two, the confirmation is a real page element the person clicks, which is the strongest evidence a site can have that they agreed.

## Telling the guest what happened

Transparency is the cheapest privacy measure and the one guests notice. When an agent books for Astrid, she should hear about it from Nordlys, not only from her assistant. If her assistant misunderstood ("book Fjellro for the winter break" became the wrong week), the email is how she finds out in time to cancel for free.

### A record of every agent booking

The layer starts by recording, for every booking that arrives through an agent channel, what happened.

**Listing 17.5** `nordlys-cabins/layers/17-consent/consent.js` — a record of every agent booking (excerpt)

```js
/** Record every agent-channel booking. Called once per app from the layer. */
export function recordAgentBookings(ctx, { onRecord = () => {} } = {}) {
  ctx.events.on('booking.created', (booking, meta = {}) => {
    const via = meta.via;
    if (!AGENT_CHANNELS[via]) return; // our own form: the guest was on the page
    const record = bookingRecords(ctx).add({
      ref: booking.ref,
      at: new Date().toISOString(),
      email: booking.email,
      memberId: booking.memberId ?? null,
      channel: via,
      agent: meta.agent ?? null,
      what: AGENT_CHANNELS[via],
      confirmedBy: via === 'ucp-checkout' ? 'you, on nordlys.example' : 'the assistant, which accepted the terms for you',
      termsVersion: TERMS_VERSION,
      dataReceived: ['name', 'email', 'dates', 'guests', ...(booking.phone ? ['phone'] : []), ...(booking.requests ? ['requests'] : [])],
    });
    onRecord(record, booking);
  });
}
```

It listens to the `booking.created` event, which every booking path emits with a `via` value: `form` for the website, `api` for the public API, `mcp` for the MCP server's `create_booking`, and `ucp-checkout` for the Chapter 12 checkout page (where `request_booking` also ends). Form bookings get no record, because the guest was on the page. Every other channel gets one: when, through which channel, which agent (as the agent identified itself, or as Chapter 15 verified it), who confirmed, which version of the terms applied, and which categories of data we received. It records the *categories*, not the values. The values are in the booking already.

This record is the answer to "who agreed to what?" when a guest disputes a booking, and it is the evidence a privacy officer needs for the record of processing activities.

### The email

On each record, the layer sends the guest a short notice. In the demo, mail goes to an in-memory outbox so the tests can read it. In production, it would go to your mailer, in the same template as your confirmation email.

**Listing 17.6** The notice Astrid receives (from the demo outbox)

```text
To: astrid@example.no
Subject: Your Nordlys booking NC-UW2KMJ was made with an AI assistant

Hello Astrid,

An AI assistant prepared this booking and you confirmed it on nordlys.example.
The assistant identified itself as "mcp:example-agent".
Fjellro, Mon, 8 Feb 2027 to Fri, 12 Feb 2027, 3 guests.
We received: name, email, dates, guests.

If you did not ask for this booking, cancel it free of charge until 2027-01-25:
https://nordlys.example/bookings
See everything agents did with your bookings: https://nordlys.example/account/agent-activity
```

Each line has a job. The subject says what happened. The first lines say how, and what the assistant called itself. The data line is the minimisation promise made visible. The last lines give the two ways out: cancel for free (with the deadline), and look at everything agents did.

### What agents did, on one page

The page at `/account/agent-activity` shows a guest the records of their bookings and, for signed-in members, the tool calls made with their account from the Chapter 16 log. A guest without an account proves ownership the same way as on the bookings page, with a reference and its email address.

**Listing 17.7** `nordlys-cabins/layers/17-consent/activity.js` — the activity page and its JSON export (excerpt)

```js
  // Everyone else proves the booking is theirs, the same way as on /bookings.
  ctx.route('POST', '/account/agent-activity', async (c) => {
    const { ref, email, format } = await c.req.parseBody();
    const booking = store.findBooking(String(ref ?? ''), String(email ?? ''));
    if (!booking) return page(c, ask('No booking matches that reference and email address.'), 404);
    const data = activityFor(ctx, { email: booking.email });
    if (format === 'json') {
      c.header('content-disposition', 'attachment; filename="nordlys-agent-activity.json"');
      c.header('cache-control', 'no-store');
      return c.json(data);
    }
    return page(c, show(data));
  });
```

The same form with "Download JSON" returns the data as a file. This serves two GDPR rights at once: the right of access in Article 15 ("the right to obtain from the controller confirmation as to whether or not personal data concerning him or her are being processed, and ... access to the personal data")[^ch17-8] and, for data processed under a contract, the right to data portability in Article 20, which asks for "a structured, commonly used and machine-readable format".[^ch17-9] Here is the export for Astrid's booking.

**Listing 17.8** The agent-activity export (from the demo)

```json
{
  "generatedAt": "2026-11-02T22:14:38.556Z",
  "bookings": [
    {
      "ref": "NC-UW2KMJ",
      "at": "2026-11-02T22:14:38.534Z",
      "channel": "ucp-checkout",
      "agent": "mcp:example-agent",
      "what": "An AI assistant prepared this booking and you confirmed it on nordlys.example",
      "confirmedBy": "you, on nordlys.example",
      "termsVersion": "2026-09-01",
      "dataReceived": [
        "name",
        "email",
        "dates",
        "guests"
      ]
    }
  ],
  "toolCalls": []
}
```

The export leaves out what the guest gave us directly (her email is in the booking itself) and the internal member id. It answers the question the guest actually has: what did agents do with my bookings?

Two more pieces belong next to the code. The privacy notice should get a short paragraph about agents, for example: "You can book with an AI assistant through our API and MCP server. We receive the same booking details as through our website, plus the name the assistant gives itself. We record how each such booking was made and confirmed, email you about it, and show it at /account/agent-activity. We keep technical logs of assistant activity for 30 days." And customer support should know the page exists, because it is the first thing to open when a guest says "I never booked that".

## Keeping less, for less time

Chapter 16's agent action log already leaves out tool arguments. This chapter adds the time dimension. Here is the retention module, all of it.

**Listing 17.9** `nordlys-cabins/layers/17-consent/retention.js` — retention rules for agent data (a proposal)

```js
// Retention for agent data. PROPOSAL: the periods below are the defaults this
// book suggests for a small booking site, not legal advice. Set yours with
// whoever is responsible for data protection, write them in the privacy notice,
// and make the code match the notice.
import { createHmac } from 'node:crypto';

export const RETENTION = {
  agentActionLog: { days: 30, why: 'security investigations; no arguments are logged' },
  bookingRecords: { keep: 'as long as the booking record itself', why: 'evidence of who agreed to what' },
  ipAddresses: { days: 0, why: 'stored only as a keyed hash that changes every day' },
};

/** Entries older than `days` are dropped. Entries need an ISO `at`. */
export function pruneOlderThan(entries, days, now = new Date()) {
  const cutoff = now.getTime() - days * 86_400_000;
  return entries.filter((e) => Date.parse(e.at) >= cutoff);
}

/** A daily-rotating keyed hash: the same IP is linkable within one day, not across days. */
export function hashIp(ip, secret, now = new Date()) {
  const day = now.toISOString().slice(0, 10);
  return createHmac('sha256', `${secret}:${day}`).update(String(ip)).digest('hex').slice(0, 16);
}

/** Apply the agent-log period to the Chapter 16 log. Returns how many entries were dropped. */
export function pruneAgentLog(log, now = new Date()) {
  return log.keepOnly((e) => pruneOlderThan([e], RETENTION.agentActionLog.days, now).length === 1);
}
```

The periods are a proposal, not a legal requirement, and the file says so in its first line. Thirty days of raw tool-call logs covers most security investigations at a small site. Booking records live as long as the booking itself, because they are part of its evidence. IP addresses, if you log them for agent traffic at all, become a keyed hash that changes every day: the same address is linkable within a day (enough to spot a burst of reference guessing), and not across days (so the log does not become a movement profile).

The layer prunes the log once an hour, and a test checks that an entry from 40 days ago disappears while one from 3 days ago stays. Whatever periods you choose, three things must agree: the privacy notice, the configuration and the test. When they drift apart, the notice is the one that is wrong in public.

Analytics deserve one sentence too. Chapter 19 counts agent traffic from server logs by agent class (published user agents, verified signatures, IP ranges). That is aggregate data about software, not about people, and it can be kept much longer than raw logs.

## What each role takes away

Privacy work fails when everybody assumes somebody else did it. Here is the split I would propose for a team like Nordlys's.

**Privacy and legal.** Add the agent channels to the record of processing activities: which tools and APIs agents can call, the data inventory above, the lawful basis (usually the contract), and the retention periods. Decide the cookie position for agent traffic. If the site runs its own assistant, own the Article 50(1) disclosure.

**Product managers.** Own the table of steps an agent may finish alone, and revisit it when the data changes (for example, when cancellations of agent bookings turn out to be frequent). Decide which bookings go through `create_booking` and which through `request_booking`.

**Designers.** Design the confirmation page and the transparency email as one experience. The email's facts should match the page's facts, word for word, so a guest who reads both sees the same story.

**Developers.** Keep tool outputs minimal, keep arguments out of logs, sign `requestState`, and keep the retention configuration in code with a test. Add a row to the data inventory with every new tool.

**Customer support.** Know the agent-activity page, and use it first when a guest says "I never booked that".

## Testing it

The layer's tests are in `nordlys-cabins/tests/ch17-consent.test.js` (node:test, seven tests):

- `request_booking` with form and URL rounds, a confirmed booking, its record and its email
- a declined URL request books nothing, and an accepted one that the guest confirms later shows up through `check_booking_request`
- a forged `requestState` is rejected, and a sealed state does not open with different arguments, a different member, or one changed character
- form bookings create no record and no email
- the activity page shows records to the owner only, and the JSON export has no email address
- raw log entries expire after 30 days, and IP hashes rotate daily

Run them with `node --test tests/ch17-*.test.js` in `nordlys-cabins/`. They passed on 2 November 2026 with Node 22.23 and Node 24.22 and the MCP TypeScript SDK v2.4.0 (`@modelcontextprotocol/server` and `@modelcontextprotocol/client`).

As in Chapter 16, the two graders do not move. isitagentready.com and Lighthouse's Agentic Browsing category measure discovery and perception, and none of their checks asks whether a site records agent bookings or deletes its logs. The measure of this chapter is a guest who gets an email, opens a page, and understands what happened.

## Summary

- An agent is the guest's tool. The site is the controller for everything it receives and keeps, with the same obligations as for its booking form, plus new data: tool-call logs, records of how a booking was made, and tool inputs and outputs. This chapter is not legal advice, so check the details with whoever handles data protection.
- Data minimisation (GDPR Art. 5(1)(c)) and protection by default (Art. 25) mean tools return only what the task needs, and no "include everything" switches.
- "Consent" means three things. The lawful basis for a booking is usually the contract, not consent. Authority (did the person ask?) is the hard part, answered today with records and confirmations. Acceptance of terms can happen through the agent or on your page, and that is a business choice.
- An agent's click on a cookie banner is not known to be valid consent. Build banners agents can use, and set only necessary cookies for agent traffic.
- The EU AI Act's Article 50 transparency rules have applied since 2 August 2026. For a website they matter for its own chatbot and AI-generated public-interest content, not for third-party agents that visit it.
- Decide which steps an agent may finish alone. For the rest, bring the person to a page: a confirmation page on the plain web, MCP URL-mode elicitation through multi round-trip requests, and in WebMCP the page the user already has open.
- In MCP, form mode may collect contact details. Passwords, tokens and payment data MUST use URL mode. An accepted URL request means the user agreed to open the page, not that they finished. Treat `requestState` as attacker-controlled: sign it and bind it to the request and the principal.
- Tell guests what agents did: a record per agent booking, an email with a way out, and a page with a machine-readable export.
- Keep agent logs without arguments, for a defined period, hash IP addresses with a rotating key, and make the privacy notice, the configuration and the tests agree.

[^ch17-1]: "Spanish Supervisory Authority Issues Detailed Guidance on Agentic AI and GDPR Compliance," Inside Privacy (Covington), https://www.insideprivacy.com/artificial-intelligence/spanish-supervisory-authority-issues-detailed-guidance-on-agentic-ai-and-gdpr-compliance/ (retrieved November 2026).
[^ch17-2]: "Innovación y tecnología," Agencia Española de Protección de Datos, listing "Inteligencia Artificial Agéntica desde la perspectiva de Protección de Datos [feb 2026]," https://www.aepd.es/areas-de-actuacion/innovacion-y-tecnologia (retrieved November 2026).
[^ch17-3]: "ICO Shares Early Views on Agentic AI & Data Protection," Global Policy Watch, February 2026, https://www.globalpolicywatch.com/2026/02/ico-shares-early-views-on-agentic-ai-data-protection/ (retrieved November 2026).
[^ch17-4]: "Art. 5 GDPR – Principles relating to processing of personal data," gdpr-info.eu, https://gdpr-info.eu/art-5-gdpr/ (retrieved November 2026).
[^ch17-5]: "Art. 25 GDPR – Data protection by design and by default," gdpr-info.eu, https://gdpr-info.eu/art-25-gdpr/ (retrieved November 2026).
[^ch17-6]: "Art. 6 GDPR – Lawfulness of processing," gdpr-info.eu, https://gdpr-info.eu/art-6-gdpr/ (retrieved November 2026).
[^ch17-7]: "Art. 22 GDPR – Automated individual decision-making, including profiling," gdpr-info.eu, https://gdpr-info.eu/art-22-gdpr/ (retrieved November 2026).
[^ch17-8]: "Art. 15 GDPR – Right of access by the data subject," gdpr-info.eu, https://gdpr-info.eu/art-15-gdpr/ (retrieved November 2026).
[^ch17-9]: "Art. 20 GDPR – Right to data portability," gdpr-info.eu, https://gdpr-info.eu/art-20-gdpr/ (retrieved November 2026).
[^ch17-10]: "AI Agent Readiness: Websites, Cookie Consent & GDPR," CookieScript, 28 October 2026, https://cookie-script.com/guides/ai-agent-readiness-cookie-consent (retrieved November 2026).
[^ch17-11]: "Timeline for the Implementation of the EU AI Act," AI Act Service Desk, European Commission, https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act (retrieved November 2026).
[^ch17-12]: "Article 50: Transparency Obligations for Providers and Deployers of Certain AI Systems," EU Artificial Intelligence Act, https://artificialintelligenceact.eu/article/50/ (retrieved November 2026).
[^ch17-13]: "EU AI Act Article 50 Transparency Obligations Go Live," Baker Botts, September 2026, https://www.bakerbotts.com/thought-leadership/publications/2026/september/eu-ai-act-article-50-transparency-obligations-go-live (retrieved November 2026).
[^ch17-14]: "Multi Round-Trip Requests," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr (retrieved November 2026).
[^ch17-15]: "Elicitation," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation (retrieved November 2026).
[^ch17-16]: "Replace requestUserInteraction with requestUserInput," webmachinelearning/webmcp pull request 204, GitHub, updated 29 October 2026, https://github.com/webmachinelearning/webmcp/pull/204 (retrieved November 2026).
[^ch17-17]: "WebMCP," Draft Community Group Report, 27 October 2026, https://webmachinelearning.github.io/webmcp/ (retrieved November 2026).
[^ch17-18]: "WebMCP tool security," Chrome for Developers, updated 1 September 2026, https://developer.chrome.com/docs/ai/webmcp/secure-tools (retrieved November 2026).
