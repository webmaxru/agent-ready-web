const controller = new AbortController();
await document.modelContext.registerTool({
  name: "search_cabins",
  description: "Find cabins that are free for the given dates.",
  inputSchema: { type: "object", properties: { from: { type: "string" }, to: { type: "string" } } },
  annotations: { readOnlyHint: true },
  execute: async ({ from, to }) => ({ from, to, cabins: [] }),
}, { signal: controller.signal });
