"""Structure of the release workflows (text checks; PyYAML is not a test dependency)."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
sys.path.insert(0, str(ROOT / "tools"))
import book_release as br  # noqa: E402


def read(name):
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def triggers(text):
    block = re.search(r"^on:\n(.*?)(?=^\S)", text, re.M | re.S).group(1)
    return re.findall(r"^  ([a-z_]+):", block, re.M)


def top_permissions(text):
    return re.search(r"^permissions:(.*)$", text, re.M).group(1).strip()


class Workflows(unittest.TestCase):
    def test_ci_has_the_book_release_preflight_aggregate(self):
        text = read("ci.yml")
        self.assertEqual(re.search(r"^name: (.+)$", text, re.M).group(1), "Book CI")
        self.assertIn("pull_request", triggers(text))
        job = text[text.index("  book-release-preflight:"):]
        self.assertIn(f"name: {br.CHECK_JOB}", job)
        self.assertIn("if: always()", job)
        self.assertIn("needs: [release-checks, build]", job)
        self.assertIn("python -m unittest discover -s tests", text)
        self.assertIn("validate_release.py change", text)

    def test_no_playwright_system_deps_and_bounded_installs(self):
        for path in WORKFLOWS.glob("*.yml"):
            self.assertNotIn("--with-deps", path.read_text(encoding="utf-8"), path.name)
        for name in ("ci.yml", "release.yml"):
            text = read(name)
            self.assertIn("timeout 300 python -m playwright install chromium", text)
            self.assertRegex(text, r"timeout-minutes: \d+\n\s+working-directory: book\n\s+run: \|\n\s+timeout 420 pip"
                             if name == "release.yml" else r"timeout-minutes: 12")

    def test_tags_come_from_the_checkout_not_an_unauthenticated_fetch(self):
        # persist-credentials: false leaves no token for a later "git fetch" in this private
        # repository; fetch-depth: 0 already fetches every tag.
        for path in WORKFLOWS.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            if "persist-credentials: false" in text:
                self.assertNotRegex(text, r"\bgit (-C \S+ )?fetch\b", path.name)

    def test_approval_signal_has_no_permissions(self):
        text = read("book-approval-signal.yml")
        self.assertEqual(re.search(r"^name: (.+)$", text, re.M).group(1), "Book approval signal")
        self.assertEqual(triggers(text), ["pull_request_review"])
        self.assertEqual(top_permissions(text), "{}")
        self.assertNotIn("checkout", text)
        self.assertNotIn("${{", text)

    def test_approved_book_controller(self):
        text = read("approved-book.yml")
        self.assertEqual(triggers(text), ["workflow_run", "issue_comment", "schedule", "workflow_dispatch"])
        self.assertIn('workflows: ["Book approval signal", "Book CI"]', text)
        self.assertEqual(top_permissions(text), "{}")
        self.assertIn("group: approved-book", text)
        self.assertIn("github.event.comment.user.login == 'webmaxru'", text)
        self.assertIn("startsWith(github.event.comment.body, '/release-book ')", text)
        self.assertNotIn("pull_request_target", text)
        # Code from the pull request never runs with write access: every tool comes from main.
        self.assertEqual(text.count("ref: main"), 3)
        self.assertIn("python trusted/tools/validate_release.py change --root book", text)
        self.assertIn("python trusted/tools/lint_manuscript.py --manuscript book/manuscript", text)
        merge = text[text.index("  merge:"):]
        self.assertIn("needs.preflight.result == 'success'", merge)
        self.assertIn("contents: write", merge)
        self.assertNotIn("contents: write", text[:text.index("  merge:")])

    def test_release_is_dispatch_only_and_never_clobbers(self):
        text = read("release.yml")
        self.assertEqual(triggers(text), ["workflow_dispatch"])
        self.assertEqual(top_permissions(text), "{}")
        for name in ("pr", "head_sha", "base_sha", "merge_sha", "tag"):
            self.assertRegex(text, rf"\n      {name}:\n")
        self.assertIn("group: book-publish", text)
        for path in WORKFLOWS.glob("*.yml"):
            self.assertNotIn("--clobber", path.read_text(encoding="utf-8"), path.name)
            self.assertNotIn("git push", path.read_text(encoding="utf-8"), path.name)
        build = text[text.index("  build:"):text.index("  publish:")]
        self.assertNotIn("contents: write", build)
        self.assertIn("ref: ${{ needs.plan.outputs.merge_sha }}", build)
        self.assertIn("grep -q '^warning:' build.log", build)
        self.assertIn("epubcheck", build)
        self.assertIn("check_site.py", build)
        self.assertLess(text.index("  build:"), text.index("book_release.py publish"))

    def test_deploy_step_names_match_the_controller(self):
        text = read("deploy-swa.yml")
        self.assertIn(f"name: {br.DEPLOY_STEP}", text)
        self.assertIn(f"name: {br.SKIP_STEP}", text)
        self.assertIn("Web edition NOT deployed", text)
        self.assertIn("workflow_dispatch", triggers(text))

    def test_controller_names_existing_workflows(self):
        for name in (br.CHECK_WORKFLOW, br.RELEASE_WORKFLOW, br.DEPLOY_WORKFLOW):
            self.assertTrue((WORKFLOWS / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
