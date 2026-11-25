"""Read-only check of the upstream sources this book cites (stdlib only).

Reads the baseline (tools/book.json "checked_as_of" and the Retrieved dates in validation/),
then asks each watched upstream whether it changed after that baseline: the latest GitHub
release or commit, or an HTTP Last-Modified date. It maps each source to the chapters whose
validation tables cite it. It writes nothing and never fails on network errors: an
unreachable source is reported as such. Used by .github/prompts/update-book.prompt.md.

  python tools/check_upstream.py              # Markdown report
  python tools/check_upstream.py --json       # machine-readable
  python tools/check_upstream.py --offline    # baseline and source inventory only
"""
from __future__ import annotations

import argparse
import datetime
import email.utils
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = re.compile(r"https?://[^\s|;)<>`,\]]+")
ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

# kind: release = latest GitHub release (falls back to the latest commit), commits = latest
# commit, http = Last-Modified of a page the tables cite. "cites" finds the chapters.
WATCH = [
    {"id": "lighthouse", "title": "Lighthouse (Agentic browsing category)", "kind": "release",
     "repo": "GoogleChrome/lighthouse", "cites": r"GoogleChrome/lighthouse|developer\.chrome\.com/docs/lighthouse"},
    {"id": "mcp", "title": "Model Context Protocol specification", "kind": "commits",
     "repo": "modelcontextprotocol/modelcontextprotocol", "cites": r"modelcontextprotocol\.io"},
    {"id": "webmcp", "title": "WebMCP (W3C Web Machine Learning CG)", "kind": "commits",
     "repo": "webmachinelearning/webmcp", "cites": r"webmachinelearning(\.github\.io|/webmcp)"},
    {"id": "webmcp-polyfill", "title": "WebMCP polyfill", "kind": "release",
     "repo": "webmachinelearning/webmcp-polyfill", "cites": r"webmcp-polyfill"},
    {"id": "ucp", "title": "Universal Commerce Protocol (UCP)", "kind": "release",
     "repo": "Universal-Commerce-Protocol/ucp", "cites": r"ucp\.dev|Universal-Commerce-Protocol"},
    {"id": "schema-org", "title": "schema.org vocabulary", "kind": "release",
     "repo": "schemaorg/schemaorg", "cites": r"schema\.org|schemaorg/schemaorg"},
    {"id": "agent-skills", "title": "Agent skills discovery (/.well-known/agent-skills)", "kind": "commits",
     "repo": "cloudflare/agent-skills-discovery-rfc", "cites": r"agent-skills"},
    {"id": "web-bot-auth", "title": "Web Bot Auth (signed agents)", "kind": "commits",
     "repo": "cloudflare/web-bot-auth", "cites": r"web-bot-auth"},
    {"id": "a2a", "title": "Agent2Agent (A2A) protocol", "kind": "release",
     "repo": "a2aproject/A2A", "cites": r"a2a-protocol\.org|a2aproject"},
    {"id": "acp", "title": "Agentic Commerce Protocol (ACP)", "kind": "commits",
     "repo": "agentic-commerce-protocol/agentic-commerce-protocol", "cites": r"agentic-commerce-protocol|agenticcommerce\.dev"},
    {"id": "x402", "title": "x402 payments", "kind": "release",
     "repo": "x402-foundation/x402", "cites": r"x402"},
    {"id": "playwright-mcp", "title": "Playwright MCP", "kind": "release",
     "repo": "microsoft/playwright-mcp", "cites": r"playwright-mcp"},
    {"id": "llms-txt", "title": "llms.txt proposal", "kind": "http", "cites": r"llmstxt\.org"},
    {"id": "content-signals", "title": "Content Signals (robots.txt)", "kind": "http",
     "cites": r"contentsignals|content-signals", "probe": r"datatracker\.ietf\.org/doc/draft-romm-aipref-contentsignals"},
    {"id": "ard", "title": "Agentic Resource Discovery (ARD)", "kind": "http", "cites": r"agenticresourcediscovery\.org"},
    {"id": "pay-per-crawl", "title": "Cloudflare pay per crawl", "kind": "http",
     "cites": r"developers\.cloudflare\.com/[^ |]*pay-per-crawl"},
]


# ---------------------------------------------------------------- baseline

def cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())]


def read_baseline(root):
    """Baseline facts and every cited source: {url: {"tables": set, "retrieved": [dates]}}."""
    root = Path(root)
    book = json.loads((root / "tools" / "book.json").read_text(encoding="utf-8"))
    sources = {}
    dates = []
    for table in sorted((root / "validation").glob("*.md")):
        retrieved_at = None
        for line in table.read_text(encoding="utf-8").splitlines():
            if not line.lstrip().startswith("|"):
                continue
            row = cells(line)
            if "Retrieved" in row:
                retrieved_at = row.index("Retrieved")
                continue
            if re.fullmatch(r"[|\s:-]+", line.strip()):
                continue
            date = None
            if retrieved_at is not None and retrieved_at < len(row):
                m = ISO.search(row[retrieved_at])
                date = m.group(1) if m else None
            if date:
                dates.append(date)
            for url in URL.findall(line):
                url = url.rstrip(".")
                entry = sources.setdefault(url, {"tables": set(), "retrieved": []})
                entry["tables"].add(table.stem)
                if date:
                    entry["retrieved"].append(date)
    lighthouse = None
    ci = root / ".github" / "workflows" / "ci.yml"
    if ci.is_file():
        m = re.search(r"lighthouse@([0-9][0-9A-Za-z.\-]*)", ci.read_text(encoding="utf-8"))
        lighthouse = m.group(1) if m else None
    return {
        "version": book.get("version"),
        "checked_as_of": book.get("checked_as_of"),
        "last_retrieved": max(dates) if dates else None,
        "first_retrieved": min(dates) if dates else None,
        "rows_with_dates": len(dates),
        "lighthouse_pinned": lighthouse,
        "sources": sources,
    }


def cited_by(pattern, sources):
    rx = re.compile(pattern, re.I)
    tables = set()
    retrieved = []
    for url, entry in sources.items():
        if rx.search(url):
            tables |= entry["tables"]
            retrieved += entry["retrieved"]
    return sorted(tables), (max(retrieved) if retrieved else None)


# ---------------------------------------------------------------- network (read-only)

def fetch(url, timeout):
    """GET url; returns (status, headers, body). Raises on network errors."""
    headers = {"User-Agent": "agent-ready-web-check-upstream", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and urllib.parse.urlsplit(url).netloc == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read(2_000_000)
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers or {}), b""


def _github(path, timeout):
    status, _, body = fetch(f"https://api.github.com/{path}", timeout)
    if status == 404:
        return None
    if status != 200:
        raise RuntimeError(f"HTTP {status}")
    return json.loads(body)


def probe(item, sources, timeout):
    if item["kind"] == "http":
        pattern = item.get("probe", item["cites"])
        url = next((u for u in sorted(sources) if re.search(pattern, u, re.I)), None)
        if not url:
            return {"state": "not cited", "detail": "no cited URL matches"}
        status, headers, _ = fetch(url, timeout)
        if status != 200:
            return {"state": "error", "detail": f"HTTP {status}", "url": url}
        modified = headers.get("Last-Modified") or headers.get("last-modified")
        date = None
        if modified:
            try:
                date = email.utils.parsedate_to_datetime(modified).date().isoformat()
            except (TypeError, ValueError):
                date = None
        return {"state": "ok", "date": date, "detail": f"Last-Modified {date}" if date else "no Last-Modified header",
                "url": url}
    repo = item["repo"]
    if item["kind"] == "release":
        release = _github(f"repos/{repo}/releases/latest", timeout)
        if release:
            return {"state": "ok", "date": (release.get("published_at") or "")[:10] or None,
                    "detail": f"latest release {release.get('tag_name')}", "version": release.get("tag_name"),
                    "url": release.get("html_url")}
    commits = _github(f"repos/{repo}/commits?per_page=1", timeout)
    if not commits:
        return {"state": "error", "detail": "no releases or commits visible"}
    commit = commits[0]
    date = ((commit.get("commit") or {}).get("committer") or {}).get("date", "")[:10] or None
    return {"state": "ok", "date": date, "detail": f"latest commit {commit.get('sha', '')[:7]}",
            "url": f"https://github.com/{repo}/commits"}


def check(root=ROOT, *, offline=False, timeout=20):
    baseline = read_baseline(root)
    since = baseline["last_retrieved"]
    results = []
    for item in WATCH:
        chapters, retrieved = cited_by(item["cites"], baseline["sources"])
        result = {"id": item["id"], "title": item["title"], "chapters": chapters, "retrieved": retrieved}
        if offline:
            result.update(state="skipped", detail="offline")
        else:
            try:
                result.update(probe(item, baseline["sources"], timeout))
            except Exception as error:  # network or parse failure: report, never crash
                result.update(state="error", detail=f"{type(error).__name__}: {error}")
        changed = None
        if result.get("state") == "ok" and result.get("date") and (retrieved or since):
            changed = result["date"] > (retrieved or since)
        if item["id"] == "lighthouse" and result.get("version") and baseline["lighthouse_pinned"]:
            changed = result["version"].lstrip("v") != baseline["lighthouse_pinned"]
            result["detail"] += f" (CI pins {baseline['lighthouse_pinned']})"
        result["changed"] = changed
        results.append(result)
    watched = [re.compile(i["cites"], re.I) for i in WATCH]
    others = {}
    for url, entry in baseline["sources"].items():
        if not any(rx.search(url) for rx in watched):
            host = urllib.parse.urlsplit(url).netloc
            o = others.setdefault(host, {"urls": 0, "tables": set()})
            o["urls"] += 1
            o["tables"] |= entry["tables"]
    return {
        "baseline": {k: v for k, v in baseline.items() if k != "sources"},
        "sources_cited": len(baseline["sources"]),
        "watched": results,
        "other_hosts": {h: {"urls": o["urls"], "tables": sorted(o["tables"])}
                        for h, o in sorted(others.items(), key=lambda kv: -kv[1]["urls"])},
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }


def markdown(report):
    b = report["baseline"]
    lines = [
        "# Upstream check",
        "",
        f"Book {b['version']}, checked as of {b['checked_as_of']}; validation rows retrieved "
        f"{b['first_retrieved']} to {b['last_retrieved']} ({b['rows_with_dates']} dated rows, "
        f"{report['sources_cited']} cited URLs).",
        "",
        "| Source | State | Upstream | Changed after the book's check? | Chapters citing it |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in report["watched"]:
        changed = {True: "**yes, review**", False: "no", None: "unknown"}[r["changed"]]
        upstream = (r.get("detail") or "") + (f", {r['date']}" if r.get("date") else "")
        lines.append(f"| {r['title']} | {r['state']} | {upstream} | {changed} | {', '.join(r['chapters']) or '-'} |")
    errors = [r for r in report["watched"] if r["state"] == "error"]
    if errors:
        lines += ["", f"{len(errors)} source(s) could not be reached; check them by hand: "
                  + ", ".join(r["id"] for r in errors) + "."]
    lines += ["", "Other cited hosts (not watched automatically; re-check the rows by hand when a chapter changes):", ""]
    for host, o in list(report["other_hosts"].items())[:25]:
        lines.append(f"- {host}: {o['urls']} URLs in {', '.join(o['tables'])}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args(argv)
    report = check(args.root, offline=args.offline, timeout=args.timeout)
    text = json.dumps(report, indent=2) + "\n" if args.json else markdown(report)
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
