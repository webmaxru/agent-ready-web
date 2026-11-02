#!/usr/bin/env python3
"""Summarise a Lighthouse JSON report's Agentic browsing category as Markdown; exit 1 if it fails.

    python3 tools/agentic_report.py lh-index.json [--min 1.0]

Prints the page, the pass ratio and each audit. Fails (exit 1) when the category score is below
--min (default 1.0: every audit passes; informative audits count as passed), or when fewer than
--min-tools WebMCP tools are registered (the WebMCP audits pass vacuously when WebMCP is off).
"""
import argparse, json, sys

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("report")
    ap.add_argument("--min", type=float, default=1.0)
    ap.add_argument("--min-tools", type=int, default=0, help="fail when fewer WebMCP tools are registered (0 = no check)")
    a = ap.parse_args(argv)
    r = json.load(open(a.report, encoding="utf-8"))
    cat = r["categories"].get("agentic-browsing")
    if not cat:
        print(f"{a.report}: no agentic-browsing category (Lighthouse {r.get('lighthouseVersion')})")
        return 1
    print(f"### Agentic browsing: {r.get('finalDisplayedUrl', r.get('requestedUrl'))}\n")
    print(f"Lighthouse {r.get('lighthouseVersion')}, score {cat['score']}\n")
    print("| Audit | Score | Mode | Value |\n| --- | --- | --- | --- |")
    for ref in cat["auditRefs"]:
        au = r["audits"][ref["id"]]
        print(f"| {au.get('title', ref['id'])} | {au.get('score')} | {au.get('scoreDisplayMode')} | {au.get('displayValue', '') or ''} |")
    tools = []
    for sec in ((r["audits"].get("webmcp-registered-tools") or {}).get("details") or {}).get("items", []):
        for it in (sec.get("value") or {}).get("items", []):
            if it.get("tool"):
                tools.append(f"{it['tool']} ({sec.get('title', '').split()[0].lower()})")
    print(f"\nWebMCP tools registered: {len(tools)}" + (": " + ", ".join(tools) if tools else ""))
    print()
    ok = (cat["score"] or 0) >= a.min and len(tools) >= a.min_tools
    if len(tools) < a.min_tools:
        print(f"::error::{len(tools)} WebMCP tools registered, expected at least {a.min_tools} (is WebMCP enabled in this Chrome?)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
