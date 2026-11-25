import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import release_policy as policy  # noqa: E402


class Classify(unittest.TestCase):
    def test_content_with_release_metadata_is_content(self):
        result = policy.classify(["manuscript/01-the-agent-ready-web.md", "validation/01-the-agent-ready-web.md",
                                  "VALIDATION.md", "CHANGELOG.md", "tools/book.json"], ["version", "checked_as_of"])
        self.assertEqual(result["kind"], "content")
        self.assertEqual(result["release"], ["CHANGELOG.md", "tools/book.json"])

    def test_book_json_build_key_is_tooling(self):
        result = policy.classify(["manuscript/01-x.md", "tools/book.json"], ["version", "agent_ready"])
        self.assertEqual(result["kind"], "mixed")
        self.assertEqual(result["tooling"], ["tools/book.json"])

    def test_tooling_paths(self):
        for path in ["tools/build.py", ".github/workflows/ci.yml", "theme/book.css", "infra/deploy.sh",
                     "README.md", "RELEASING.md", "tests/test_x.py", "manuscript2/x.md"]:
            self.assertEqual(policy.classify([path])["kind"], "tooling", path)

    def test_content_prefixes_and_files(self):
        for path in ["manuscript/Book.txt", "manuscript/resources/images/a.png", "editorial/01-log.md",
                     "validation/01.md", "figures/fig-1.svg", "VALIDATION.md"]:
            self.assertEqual(policy.classify([path])["kind"], "content", path)

    def test_release_files_alone_are_tooling(self):
        self.assertEqual(policy.classify(["CHANGELOG.md"])["kind"], "tooling")
        self.assertEqual(policy.classify([])["kind"], "none")

    def test_unsafe_paths_are_not_content(self):
        for path in ["manuscript/../tools/build.py", "/manuscript/x.md", "manuscript\\x.md", "manuscript/./x.md"]:
            self.assertFalse(policy.is_content(path), path)

    def test_changed_keys(self):
        self.assertEqual(policy.changed_keys('{"version": "1.0.0", "a": 1}', '{"version": "1.1.0", "a": 1, "b": 2}'),
                         ["b", "version"])
        with self.assertRaises(policy.PolicyError):
            policy.changed_keys("[]", "{}")

    def test_evidence_stem(self):
        self.assertEqual(policy.evidence_stem("manuscript/09-in-page-tools-with-webmcp.md"),
                         "09-in-page-tools-with-webmcp")
        self.assertEqual(policy.evidence_stem("manuscript/appendix-c-pay-per-crawl-and-licensing.md"),
                         "appendix-c-pay-per-crawl-and-licensing")
        self.assertIsNone(policy.evidence_stem("manuscript/Book.txt"))
        self.assertIsNone(policy.evidence_stem("manuscript/resources/images/x.png"))


class Versions(unittest.TestCase):
    def test_semver_precedence(self):
        ordered = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11",
                   "1.0.0-rc.1", "1.0.0", "1.0.1", "1.10.0", "2.0.0"]
        self.assertEqual(sorted(reversed(ordered), key=policy.version_key), ordered)

    def test_invalid_versions(self):
        for bad in ["1.0", "01.0.0", "v1.0.0", "1.0.0-", "1.0.0-01", None]:
            with self.assertRaises(policy.PolicyError):
                policy.parse_version(bad)

    def test_latest_and_previous(self):
        names = ["v1.0.0", "v2.0.0", "v2.1.0-rc.1", "v10.0.0-beta", "notes", "v1.9.9"]
        self.assertEqual(policy.latest_stable(names), "v2.0.0")
        self.assertEqual(policy.previous_release(names, "2.1.0"), "v2.0.0")
        self.assertEqual(policy.previous_release(names, "2.0.1-rc.1"), "v2.0.0")
        self.assertEqual(policy.previous_release(names, "1.5.0"), "v1.0.0")
        self.assertIsNone(policy.previous_release(names, "0.9.0"))

    def test_latest_label(self):
        self.assertTrue(policy.is_newest_stable("2.1.0", ["v1.0.0", "v2.0.0", "v3.0.0-rc.1"]))
        self.assertFalse(policy.is_newest_stable("2.0.1", ["v2.0.0", "v3.0.0"]))
        self.assertFalse(policy.is_newest_stable("3.0.0-rc.2", ["v2.0.0"]))
        self.assertTrue(policy.is_newest_stable("1.0.0", []))


class Changelog(unittest.TestCase):
    TEXT = ("# Changelog\n\n## [Unreleased]\n\n## [2.1.0] - 2026-12-01\n\n### Changed\n\n- See [the table]"
            "(VALIDATION.md) and [site](https://example.com).\n\n[x]: https://example.com\n\n"
            "## [2.0.0] - 2026-11-05\n\n- Second edition.\n\n## [1.9.0]\n\n- Undated.\n")

    def test_sections(self):
        self.assertEqual(policy.changelog_versions(self.TEXT), ["Unreleased", "2.1.0", "2.0.0", "1.9.0"])
        self.assertEqual(policy.dated_section(self.TEXT, "2.1.0")[0], "2026-12-01")
        with self.assertRaisesRegex(policy.PolicyError, "no release date"):
            policy.dated_section(self.TEXT, "1.9.0")
        with self.assertRaisesRegex(policy.PolicyError, "no '## \\[3.0.0\\]'"):
            policy.dated_section(self.TEXT, "3.0.0")

    def test_notes_point_relative_links_at_the_tag(self):
        notes = policy.release_notes(self.TEXT, "2.1.0", "webmaxru/agent-ready-web", "v2.1.0")
        self.assertIn("(https://github.com/webmaxru/agent-ready-web/blob/v2.1.0/VALIDATION.md)", notes)
        self.assertIn("(https://example.com)", notes)
        self.assertNotIn("[x]:", notes)
        self.assertNotIn("Second edition", notes)


class Assets(unittest.TestCase):
    def test_expected_and_missing(self):
        names = policy.expected_assets("v2.1.0")
        self.assertEqual(names, [
            "Agent-Ready-Websites-in-Action-Maxim-Salnikov-v2.1.0.pdf",
            "Agent-Ready-Websites-in-Action-Maxim-Salnikov-v2.1.0-print-7.5x9.25.pdf",
            "Agent-Ready-Websites-in-Action-Maxim-Salnikov-v2.1.0.epub",
            "Agent-Ready-Websites-in-Action-HTML-v2.1.0.zip",
            "SHA256SUMS.txt"])
        assets = [{"name": n, "state": "uploaded", "size": 10} for n in names]
        self.assertEqual(policy.missing_assets("v2.1.0", assets), [])
        assets[0]["size"] = 0
        assets[1]["state"] = "starter"
        self.assertEqual(policy.missing_assets("v2.1.0", assets[:-1]), [names[0], names[1], "SHA256SUMS.txt"])

    def test_asset_names_match_the_build(self):
        build = (Path(__file__).resolve().parent.parent / "tools" / "book.json").read_text(encoding="utf-8")
        self.assertIn(policy.FILE_STEM, build)
        self.assertIn(policy.HTML_ZIP_STEM, build)


if __name__ == "__main__":
    unittest.main()
