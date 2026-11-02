#!/usr/bin/env python3
"""Summarise a Lighthouse JSON report's Agentic browsing category as Markdown; exit 1 if it fails.

    python3 tools/agentic_report.py lh-index.json [--min 1.0]

Prints the page, the pass ratio and each audit. Fails (exit 1) when the category score is below
--min (default 1.0: every audit passes; informative audits count as passed).
"""
import argparse, json, sys

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("report")
    ap.add_argument("--min", type=float, default=1.0)
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
    print()
    return 0 if (cat["score"] or 0) >= a.min else 1

if __name__ == "__main__":
    sys.exit(main())
