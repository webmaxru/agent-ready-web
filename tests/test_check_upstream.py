import io
import json
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import check_upstream as cu  # noqa: E402

TABLE = """# Validation: Chapter 9

| # | Claim | Verdict | Source URL | Retrieved | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | WebMCP is a CG draft | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-03 | |
| 2 | Tool shape \\| detail | VERIFIED | https://github.com/webmachinelearning/webmcp/blob/main/docs/x.md | 2026-11-04 | |
| 3 | llms.txt | VERIFIED | https://llmstxt.org/. | 2026-11-02 | |
| 4 | Lighthouse | VERIFIED | https://developer.chrome.com/docs/lighthouse/overview | 2026-11-01 | |
| 5 | Unrelated | VERIFIED | https://example.org/page | 2026-11-01 | |
"""


def make_root():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "tools").mkdir()
    (root / "tools" / "book.json").write_text(json.dumps({"version": "2.0.0", "checked_as_of": "November 2026"}),
                                             encoding="utf-8")
    (root / "validation").mkdir()
    (root / "validation" / "09-in-page-tools-with-webmcp.md").write_text(TABLE, encoding="utf-8")
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "ci.yml").write_text("run: npx -y lighthouse@13.6.0 x\n", encoding="utf-8")
    return tmp, root


def fake_fetch(responses):
    def fetch(url, timeout):
        for pattern, value in responses.items():
            if pattern in url:
                if isinstance(value, Exception):
                    raise value
                status, headers, body = value
                return status, headers, json.dumps(body).encode() if not isinstance(body, bytes) else body
        raise urllib.error.URLError("no route")
    return fetch


class Baseline(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = make_root()

    def tearDown(self):
        self.tmp.cleanup()

    def test_read_baseline(self):
        b = cu.read_baseline(self.root)
        self.assertEqual((b["first_retrieved"], b["last_retrieved"], b["rows_with_dates"]), ("2026-11-01", "2026-11-04", 5))
        self.assertEqual(b["lighthouse_pinned"], "13.6.0")
        self.assertIn("https://llmstxt.org/", b["sources"])
        self.assertEqual(cu.cited_by(r"webmachinelearning", b["sources"]), (["09-in-page-tools-with-webmcp"], "2026-11-04"))

    def test_offline_needs_no_network(self):
        with mock.patch.object(cu, "fetch", side_effect=AssertionError("network used")):
            report = cu.check(self.root, offline=True)
        self.assertTrue(all(r["state"] == "skipped" for r in report["watched"]))
        self.assertIn("example.org", report["other_hosts"])
        self.assertNotIn("llmstxt.org", report["other_hosts"])


class Probe(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = make_root()

    def tearDown(self):
        self.tmp.cleanup()

    def by_id(self, report):
        return {r["id"]: r for r in report["watched"]}

    def test_changes_and_failures_are_reported_without_crashing(self):
        responses = {
            "repos/GoogleChrome/lighthouse/releases/latest": (200, {}, {"tag_name": "v13.7.0", "published_at": "2026-11-20T00:00:00Z"}),
            "repos/webmachinelearning/webmcp/commits": (200, {}, [{"sha": "abcdef123", "commit": {"committer": {"date": "2026-11-10T00:00:00Z"}}}]),
            "llmstxt.org": (200, {"Last-Modified": "Mon, 01 Sep 2025 00:00:00 GMT"}, b""),
            "repos/schemaorg": (403, {}, b""),
            "repos/modelcontextprotocol": urllib.error.URLError("dns failure"),
            "repos/x402": TimeoutError("timed out"),
            "repos/microsoft/playwright-mcp/releases/latest": (200, {}, b"not json"),
        }
        with mock.patch.object(cu, "fetch", fake_fetch(responses)):
            report = cu.check(self.root, timeout=1)
        r = self.by_id(report)
        self.assertTrue(r["lighthouse"]["changed"])
        self.assertIn("CI pins 13.6.0", r["lighthouse"]["detail"])
        self.assertTrue(r["webmcp"]["changed"])
        self.assertEqual(r["webmcp"]["chapters"], ["09-in-page-tools-with-webmcp"])
        self.assertFalse(r["llms-txt"]["changed"])
        self.assertEqual(r["schema-org"]["state"], "error")
        self.assertIn("HTTP 403", r["schema-org"]["detail"])
        self.assertIn("dns failure", r["mcp"]["detail"])
        self.assertEqual(r["x402"]["state"], "error")
        self.assertEqual(r["playwright-mcp"]["state"], "error")
        self.assertEqual(r["ard"]["state"], "not cited")
        text = cu.markdown(report)
        self.assertIn("**yes, review**", text)
        self.assertIn("could not be reached", text)

    def test_same_lighthouse_version_is_unchanged(self):
        responses = {"lighthouse/releases/latest": (200, {}, {"tag_name": "v13.6.0", "published_at": "2026-12-01T00:00:00Z"})}
        with mock.patch.object(cu, "fetch", fake_fetch(responses)):
            self.assertFalse(self.by_id(cu.check(self.root, timeout=1))["lighthouse"]["changed"])

    def test_cli_never_crashes_on_network_errors(self):
        out = io.StringIO()
        out.buffer = io.BytesIO()
        with mock.patch.object(cu, "fetch", side_effect=OSError("offline")), redirect_stdout(out):
            self.assertEqual(cu.main(["--root", str(self.root), "--json", "--timeout", "1"]), 0)
        report = json.loads(out.buffer.getvalue())
        self.assertTrue(all(r["state"] in {"error", "not cited"} for r in report["watched"]))


if __name__ == "__main__":
    unittest.main()
