import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import release_policy as policy  # noqa: E402
import validate_release as vr  # noqa: E402

TODAY = datetime.date.today().isoformat()
STEM = "01-the-agent-ready-web"
BOOK = {"title": "Agent-Ready Websites in Action", "version": "2.0.0", "edition": "November 2026",
        "checked_as_of": "November 2026", "year": "2026", "agent_ready": {"feed": True}}
TABLE = ("# Validation: Chapter 1\n\n| # | Claim | Verdict | Source URL | Retrieved | Notes | Origin |\n"
         "| --- | --- | --- | --- | --- | --- | --- |\n"
         "| 1 | llms.txt is a proposal | VERIFIED | https://llmstxt.org/ | 2026-11-02 | | v1 ch1 #1 |\n")
LOG = "# Editorial log: Chapter 1\n\n- 2026-11-02: second edition.\n"
CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [2.0.0] - 2026-11-05\n\n- Second edition.\n"


def git(root, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
           "GIT_AUTHOR_DATE": "2026-11-05T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-05T12:00:00Z"}
    return subprocess.run(["git", "-c", "core.autocrlf=false", *args], cwd=root, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q", "-b", "main")
        self.write({"tools/book.json": json.dumps(BOOK, indent=2) + "\n", "CHANGELOG.md": CHANGELOG,
                    f"manuscript/{STEM}.md": "# The agent-ready web\n\nText.\n",
                    "manuscript/Book.txt": f"{STEM}.md\n", f"validation/{STEM}.md": TABLE,
                    f"editorial/{STEM}-editorial-log.md": LOG, "VALIDATION.md": "# Validation\n",
                    "tools/build.py": "print('build')\n"})
        self.base = self.commit("v2.0.0")
        git(self.root, "tag", "-a", "v1.0.0", "-m", "v1.0.0", self.base)
        git(self.root, "tag", "-a", "v2.0.0", "-m", "v2.0.0", self.base)

    def write(self, files):
        for name, text in files.items():
            path = self.root / name
            if text is None:
                path.unlink()
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")

    def commit(self, message="change"):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "--allow-empty", "-m", message)
        return git(self.root, "rev-parse", "HEAD")

    def book(self, **changes):
        data = json.loads((self.root / "tools/book.json").read_text(encoding="utf-8"))
        data.update(changes)
        self.write({"tools/book.json": json.dumps(data, indent=2) + "\n"})

    def release(self, version="2.1.0", date=TODAY):
        self.book(version=version, checked_as_of="December 2026")
        log = (self.root / "CHANGELOG.md").read_text(encoding="utf-8")
        self.write({"CHANGELOG.md": log.replace("## [Unreleased]\n", f"## [Unreleased]\n\n## [{version}]"
                                                 f"{' - ' + date if date else ''}\n\n- Chapter 1 updated.\n")})

    def chapter(self, *, log=True, row_date=TODAY, summary=True):
        self.write({f"manuscript/{STEM}.md": "# The agent-ready web\n\nUpdated text.\n"})
        if log:
            self.write({f"editorial/{STEM}-editorial-log.md": LOG + f"- {TODAY}: updated the llms.txt status.\n"})
        if row_date:
            self.write({f"validation/{STEM}.md": TABLE + f"| 2 | llms.txt still a proposal | VERIFIED | "
                                                          f"https://llmstxt.org/ | {row_date} | | new |\n"})
        if summary:
            self.write({"VALIDATION.md": f"# Validation\n\nRe-checked {TODAY}.\n"})

    def check(self):
        self.commit()
        return vr.validate_change(self.root, self.base)

    def close(self):
        self.tmp.cleanup()


class Change(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def assertFails(self, pattern):
        with self.assertRaisesRegex(policy.PolicyError, pattern):
            self.repo.check()

    def test_tooling_only_passes(self):
        self.repo.write({"tools/build.py": "print('build 2')\n"})
        self.repo.book(agent_ready={"feed": False})
        self.assertEqual(self.repo.check()[0], "tooling")

    def test_tooling_must_not_bump_the_version(self):
        self.repo.write({"tools/build.py": "print('build 2')\n"})
        self.repo.release()
        self.assertFails("tooling-only change must not change release metadata")

    def test_tooling_must_not_add_a_changelog_version(self):
        self.repo.write({"CHANGELOG.md": CHANGELOG.replace("## [Unreleased]\n", "## [Unreleased]\n\n## [2.0.1] - 2026-12-01\n")})
        self.assertFails(r"must not add the CHANGELOG version section \[2.0.1\]")

    def test_unreleased_notes_are_allowed_in_tooling(self):
        self.repo.write({"CHANGELOG.md": CHANGELOG.replace("## [Unreleased]\n", "## [Unreleased]\n\n- CI tweak.\n")})
        self.assertEqual(self.repo.check()[0], "tooling")

    def test_content_with_evidence_passes(self):
        self.repo.chapter()
        self.repo.release()
        kind, summary = self.repo.check()
        self.assertEqual(kind, "content")
        self.assertIn("v2.1.0", summary)

    def test_content_needs_a_version_bump(self):
        self.repo.chapter()
        self.assertFails("must be higher than the latest release v2.0.0")

    def test_version_must_exceed_latest_stable(self):
        self.repo.chapter()
        self.repo.release("1.5.0")
        self.assertFails("must be higher than the latest release v2.0.0")

    def test_tag_must_not_exist(self):
        git(self.repo.root, "tag", "v2.1.0", self.repo.base)
        self.repo.chapter()
        self.repo.release()
        self.assertFails("tag v2.1.0 already exists")

    def test_changelog_section_must_be_dated(self):
        self.repo.chapter()
        self.repo.release(date="")
        self.assertFails("no release date")

    def test_changelog_section_must_exist(self):
        self.repo.chapter()
        self.repo.book(version="2.1.0")
        self.assertFails(r"no '## \[2.1.0\]' section")

    def test_changed_chapter_needs_its_editorial_log(self):
        self.repo.chapter(log=False)
        self.repo.release()
        self.assertFails(f"editorial/{STEM}-editorial-log.md did not")

    def test_changed_chapter_needs_its_validation_table(self):
        self.repo.chapter(row_date=None)
        self.repo.release()
        self.assertFails(f"validation/{STEM}.md did not")

    def test_validation_rows_need_a_fresh_retrieved_date(self):
        self.repo.chapter(row_date="2026-01-01")
        self.repo.release()
        self.assertFails("no added or updated row with a Retrieved date")

    def test_future_retrieved_dates_fail(self):
        self.repo.chapter(row_date="2099-01-01")
        self.repo.release()
        self.assertFails("in the future")

    def test_validation_change_needs_the_summary(self):
        self.repo.chapter(summary=False)
        self.repo.release()
        self.assertFails("VALIDATION.md did not")

    def test_image_only_change_needs_no_chapter_evidence(self):
        self.repo.write({"manuscript/resources/images/fig.svg": "<svg/>\n"})
        self.repo.release()
        self.assertEqual(self.repo.check()[0], "content")

    def test_mixed_change_is_reported(self):
        self.repo.chapter()
        self.repo.release()
        self.repo.write({"tools/build.py": "print('x')\n"})
        kind, summary = self.repo.check()
        self.assertEqual(kind, "mixed")
        self.assertIn("never merges mixed changes automatically", summary)

    @unittest.skipIf(os.name == "nt", "symlinks need privileges on Windows")
    def test_symlinks_in_content_fail(self):
        self.repo.chapter()
        self.repo.release()
        os.symlink("../tools/build.py", self.repo.root / "manuscript" / "link.md")
        self.assertFails("symlinks and submodules")


class Release(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.repo.chapter()
        self.repo.release()
        self.sha = self.repo.commit("v2.1.0")

    def tearDown(self):
        self.repo.close()

    def test_release_passes(self):
        self.assertIn("previous release: v2.0.0", vr.validate_release(self.repo.root, "v2.1.0", self.sha))

    def test_head_must_be_the_sha(self):
        with self.assertRaisesRegex(policy.PolicyError, "check out"):
            vr.validate_release(self.repo.root, "v2.1.0", self.repo.base)

    def test_tag_must_match_book_json(self):
        with self.assertRaisesRegex(policy.PolicyError, "version is '2.1.0', the tag is v2.2.0"):
            vr.validate_release(self.repo.root, "v2.2.0", self.sha)

    def test_existing_tag(self):
        git(self.repo.root, "tag", "-a", "v2.1.0", "-m", "v2.1.0", self.sha)
        with self.assertRaisesRegex(policy.PolicyError, "already exists"):
            vr.validate_release(self.repo.root, "v2.1.0", self.sha)
        vr.validate_release(self.repo.root, "v2.1.0", self.sha, allow_existing_tag=True)
        git(self.repo.root, "tag", "-f", "-a", "v2.1.0", "-m", "moved", self.repo.base)
        with self.assertRaisesRegex(policy.PolicyError, "never moved"):
            vr.validate_release(self.repo.root, "v2.1.0", self.sha, allow_existing_tag=True)

    def test_previous_release_must_be_an_ancestor(self):
        git(self.repo.root, "checkout", "-q", "--orphan", "other")
        other = self.repo.commit("unrelated")
        git(self.repo.root, "tag", "-f", "-a", "v2.0.0", "-m", "forged", other)
        git(self.repo.root, "checkout", "-q", "main")
        with self.assertRaisesRegex(policy.PolicyError, "not an ancestor"):
            vr.validate_release(self.repo.root, "v2.1.0", self.sha)

    def test_dirty_checkout_fails(self):
        (self.repo.root / "VALIDATION.md").write_text("edited\n", encoding="utf-8")
        with self.assertRaisesRegex(policy.PolicyError, "local changes"):
            vr.validate_release(self.repo.root, "v2.1.0", self.sha)

    def test_cli_notes(self):
        out = subprocess.run([sys.executable, str(Path(vr.__file__)), "notes", "--root", str(self.repo.root),
                              "--tag", "v2.1.0", "--repo", "webmaxru/agent-ready-web"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertEqual(out.strip(), "- Chapter 1 updated.")


if __name__ == "__main__":
    unittest.main()
