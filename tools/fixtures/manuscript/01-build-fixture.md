# Chapter 1: Everything the Build Has to Handle

This chapter covers

- A figure with a caption, rendered from an SVG source
- A numbered listing that points at a file in the demos repository
- Every kind of callout, a footnote and a table
- A section for readers who write code, opened by a Hands-on callout

The build turns this Markdown into a web page, an EPUB chapter and PDF pages. If any of the elements below stops rendering, CI fails before a real chapter is affected.

## A figure

Figure 1.1 shows the pipeline from one manuscript to every edition.

![Figure 1.1 — One manuscript, every edition: the build reads the Markdown and writes the web edition, its Markdown twins and agent files, the EPUB and both PDFs.](images/figure-1-1.png)

## A listing

> **Hands-on:** This section shows a short JavaScript file. If you don't write code, the point is simple: the page registers one read-only tool. Pick up again at "Callouts and a table".

**Listing 1.1** `tools/fixtures/register-tool.js` — a read-only tool, registered with an AbortSignal

```js
const controller = new AbortController();
await document.modelContext.registerTool({
  name: "search_cabins",
  description: "Find cabins that are free for the given dates.",
  inputSchema: { type: "object", properties: { from: { type: "string" }, to: { type: "string" } } },
  annotations: { readOnlyHint: true },
  execute: async ({ from, to }) => ({ from, to, cabins: [] }),
}, { signal: controller.signal });
```

The label above the listing names the file it is copied from. In the book, that file lives in the demos repository.[^fx01-1]

## Callouts and a table

> **Note:** A note adds context the reader may want.

> **Tip:** A tip is a shortcut.

> **Warning:** A warning is about something that breaks or costs money.

> **Still in flux:** This marks a standard that is still a draft, with the date it was checked.

| File | Who reads it | Built from |
| --- | --- | --- |
| `llms.txt` | Language models and agents | `Book.txt` and each chapter's first paragraph |
| `robots.txt` | Crawlers | `tools/book.json` |
| `sitemap.xml` | Search engines | Every page |

## Summary

- The fixture exercises figures, listings, callouts, footnotes and tables.
- CI builds it while the real manuscript is empty.

[^fx01-1]: The demos live in the repository webmaxru/agent-ready-web-demos, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
