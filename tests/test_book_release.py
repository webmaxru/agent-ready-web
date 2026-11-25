import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
sys.path.insert(0, str(HERE))
import book_release as br  # noqa: E402
import release_policy as policy  # noqa: E402
from github_fake import OWNER, FakeGitHub  # noqa: E402

PR = 7
CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [2.0.0] - 2026-11-05\n\n- Second edition.\n"


def book(version="2.0.0", **extra):
    return json.dumps({"title": "Agent-Ready Websites in Action", "version": version, "edition": "November 2026",
                       "checked_as_of": "November 2026", "agent_ready": {"feed": True}, **extra}, indent=2)


BASE_FILES = {"tools/book.json": book(), "CHANGELOG.md": CHANGELOG, "tools/build.py": "build\n",
              "manuscript/01-the-agent-ready-web.md": "Text.\n", "validation/01-the-agent-ready-web.md": "rows\n",
              "editorial/01-the-agent-ready-web-editorial-log.md": "log\n", "VALIDATION.md": "summary\n"}


def update_files(version="2.1.0", **extra):
    files = dict(BASE_FILES)
    files.update({"tools/book.json": book(version, checked_as_of="December 2026"),
                  "CHANGELOG.md": CHANGELOG.replace("## [Unreleased]\n", f"## [Unreleased]\n\n## [{version}] - 2026-12-01\n\n- Updated.\n"),
                  "manuscript/01-the-agent-ready-web.md": "Updated text.\n",
                  "validation/01-the-agent-ready-web.md": "rows\nnew row\n",
                  "editorial/01-the-agent-ready-web-editorial-log.md": "log\nentry\n",
                  "VALIDATION.md": "summary 2\n"})
    files.update(extra)
    return files


def pr_dict(head, author=OWNER):
    return {"head": {"sha": head}, "user": {"login": author}}


def review(i, state, commit, at, user=OWNER):
    return {"id": i, "user": {"login": user}, "state": state, "commit_id": commit, "submitted_at": at}


def comment(body, at, user=OWNER):
    return {"user": {"login": user}, "body": body, "created_at": at}


HEAD = "a" * 40
OLD = "b" * 40


class Approval(unittest.TestCase):
    def test_contributor_pr_needs_owner_approval_of_the_exact_head(self):
        pr = pr_dict(HEAD, "contributor")
        self.assertTrue(br.approval(pr, [review(1, "APPROVED", HEAD, "2026-12-01T10:00:00Z")], []))
        self.assertFalse(br.approval(pr, [review(1, "APPROVED", OLD, "2026-12-01T10:00:00Z")], []))
        self.assertFalse(br.approval(pr, [review(1, "APPROVED", HEAD, "2026-12-01T10:00:00Z", "someone")], []))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {HEAD}", "2026-12-01T10:00:00Z")]))

    def test_changes_requested_and_dismissal_revoke_approval(self):
        pr = pr_dict(HEAD, "contributor")
        approved = review(1, "APPROVED", HEAD, "2026-12-01T10:00:00Z")
        self.assertFalse(br.approval(pr, [approved, review(2, "CHANGES_REQUESTED", HEAD, "2026-12-01T11:00:00Z")], []))
        self.assertFalse(br.approval(pr, [dict(approved, state="DISMISSED")], []))
        self.assertTrue(br.approval(pr, [review(2, "CHANGES_REQUESTED", HEAD, "2026-12-01T09:00:00Z"), approved], []))
        self.assertTrue(br.approval(pr, [approved, review(3, "COMMENTED", HEAD, "2026-12-01T12:00:00Z")], []))

    def test_owner_pr_needs_the_exact_release_comment(self):
        pr = pr_dict(HEAD)
        at = "2026-12-01T10:00:00Z"
        self.assertTrue(br.approval(pr, [], [comment(f"/release-book {HEAD}", at)]))
        self.assertTrue(br.approval(pr, [], [comment(f"  /release-book {HEAD}\n", at)]))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {OLD}", at)]))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {HEAD[:12]}", at)]))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {HEAD} please", at)]))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {HEAD}", at, "someone")]))
        self.assertFalse(br.approval(pr, [], []))

    def test_owner_comment_must_follow_any_barrier(self):
        pr = pr_dict(HEAD)
        barrier = review(1, "CHANGES_REQUESTED", HEAD, "2026-12-01T11:00:00Z")
        self.assertFalse(br.approval(pr, [barrier], [comment(f"/release-book {HEAD}", "2026-12-01T10:00:00Z")]))
        self.assertTrue(br.approval(pr, [barrier], [comment(f"/release-book {HEAD}", "2026-12-01T12:00:00Z")]))
        dismissed = review(2, "APPROVED", HEAD, "2026-12-01T09:00:00Z")
        timeline = [{"event": "review_dismissed", "created_at": "2026-12-01T11:30:00Z",
                     "dismissed_review": {"review_id": 2}}]
        self.assertFalse(br.approval(pr, [dismissed], [comment(f"/release-book {HEAD}", "2026-12-01T11:00:00Z")], timeline))
        self.assertTrue(br.approval(pr, [dismissed], [comment(f"/release-book {HEAD}", "2026-12-01T12:00:00Z")], timeline))


class Controller(unittest.TestCase):
    def setUp(self):
        self.fake = FakeGitHub().__enter__()
        self.addCleanup(self.fake.__exit__, None, None, None)
        env = mock.patch.dict(os.environ, self.fake.env())
        env.start()
        self.addCleanup(env.stop)
        for name in ("GITHUB_OUTPUT", "GITHUB_STEP_SUMMARY", "GITHUB_ACTIONS"):
            os.environ.pop(name, None)
        self.s = self.fake.state
        self.base = self.s.commit(BASE_FILES)
        self.s.refs["heads/main"] = {"type": "commit", "sha": self.base}
        self.s.tag("v1.0.0", self.base)
        self.s.tag("v2.0.0", self.base)
        self.api = br.GitHub()

    def open_pr(self, files=None, *, author=OWNER, base=None, approve=True, ci=True, **pull):
        base = base or self.base
        self.head = self.s.commit(files or update_files(), [base])
        self.s.pull(PR, self.head, base, author=author, **pull)
        if approve and author == OWNER:
            self.s.comment(PR, f"/release-book {self.head}")
        elif approve:
            self.s.review(PR, "APPROVED", self.head)
        if ci:
            self.s.ci_run(self.head)
        return self.head

    def run_op(self, func, *args, **kwargs):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = func(*args, **kwargs)
        values = dict(line.split("=", 1) for line in out.getvalue().splitlines() if "=" in line and " " not in line.split("=", 1)[0])
        return result, values, out.getvalue()

    def inspect(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            _, values, _ = self.run_op(br.inspect, self.api, {"inputs": {"pr": str(PR)}})
        return values, err.getvalue()

    def assertGate(self, pattern, func, *args, **kwargs):
        with self.assertRaisesRegex(policy.PolicyError, pattern), contextlib.redirect_stdout(io.StringIO()):
            func(*args, **kwargs)

    # ------------------------------------------------------------ candidate

    def test_eligible_owner_pr(self):
        head = self.open_pr()
        values, _ = self.inspect()
        self.assertEqual(values, {"eligible": "true", "pr": str(PR), "head": head, "base": self.base, "tag": "v2.1.0"})

    def test_eligible_contributor_pr(self):
        self.open_pr(author="contributor")
        self.assertEqual(self.inspect()[0]["eligible"], "true")

    def test_review_on_an_old_head_is_not_approval(self):
        old = self.open_pr(author="contributor")
        self.s.pulls[PR]["head"]["sha"] = self.s.commit(update_files(**{"VALIDATION.md": "summary 3\n"}), [old])
        self.s.ci_run(self.s.pulls[PR]["head"]["sha"])
        values, err = self.inspect()
        self.assertEqual(values["eligible"], "false")
        self.assertIn("no current owner approval", err)

    def test_comment_from_another_user_is_ignored(self):
        self.open_pr(approve=False)
        self.s.comment(PR, f"/release-book {self.head}", user="someone")
        self.assertIn("no current owner approval", self.inspect()[1])

    def test_pr_conditions(self):
        cases = [({"draft": True}, "non-draft"), ({"same_repo": False}, "from this repository"),
                 ({"mergeable": None}, "not mergeable")]
        for pull, message in cases:
            with self.subTest(pull=pull):
                self.open_pr(**pull)
                self.assertIn(message, self.inspect()[1])

    def test_head_behind_main_is_refused(self):
        main2 = self.s.commit({**BASE_FILES, "figures/new.svg": "<svg/>"}, [self.base])
        self.s.refs["heads/main"] = {"type": "commit", "sha": main2}
        self.head = self.s.commit(update_files(), [self.base])
        self.s.pull(PR, self.head, main2)
        self.s.comment(PR, f"/release-book {self.head}")
        self.s.ci_run(self.head)
        self.assertIn("behind main", self.inspect()[1])

    def test_preflight_must_pass_on_the_exact_head(self):
        self.open_pr(ci=False)
        self.assertIn("Book CI has not passed", self.inspect()[1])
        self.s.ci_run(self.head, job_conclusion="failure")
        self.assertIn("'Book release preflight' has not passed", self.inspect()[1])
        self.s.ci_run(self.head, job="Some other job")
        self.assertIn("'Book release preflight' has not passed", self.inspect()[1])
        self.s.ci_run(self.head, branch="other-branch")
        self.assertIn("'Book release preflight' has not passed", self.inspect()[1])

    def test_scope_is_content_only(self):
        cases = [(update_files(**{"tools/build.py": "changed\n"}), "mixed: tools/build.py"),
                 (update_files(**{"tools/book.json": book("2.1.0", agent_ready={"feed": False})}), "mixed: tools/book.json"),
                 ({**BASE_FILES, "tools/build.py": "changed\n"}, "tooling"),
                 ({**BASE_FILES, "manuscript/01-the-agent-ready-web.md": "Updated.\n"}, "must bump the version")]
        for files, message in cases:
            with self.subTest(message=message):
                self.open_pr(files)
                self.assertIn(message, self.inspect()[1])

    def test_ambiguous_workflow_run_signal(self):
        self.open_pr()
        self.s.pull(8, self.head, self.base)
        self.s.comment(8, f"/release-book {self.head}")
        event = {"workflow_run": {"head_branch": "update/chapter-1",
                                  "head_repository": {"full_name": "webmaxru/agent-ready-web"}}}
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertGate("ambiguous", br.inspect, self.api, event)

    def test_comment_events_need_the_owner_command(self):
        self.open_pr()
        event = {"issue": {"number": PR, "pull_request": {}}, "comment": {"user": {"login": "someone"},
                                                                           "body": f"/release-book {self.head}"}}
        self.assertEqual(br.event_numbers(self.api, event), [])
        event["comment"]["user"]["login"] = OWNER
        self.assertEqual(br.event_numbers(self.api, event), [PR])
        event["issue"].pop("pull_request")
        self.assertEqual(br.event_numbers(self.api, event), [])

    # ------------------------------------------------------------ merge

    def merge(self):
        _, values, _ = self.run_op(br.merge, self.api, PR, self.head, self.base)
        return values

    def test_merge_squashes_the_exact_head_and_dispatches_the_release(self):
        self.open_pr()
        values = self.merge()
        merge_sha = self.s.resolve("main")
        self.assertEqual(values, {"merge_sha": merge_sha, "tag": "v2.1.0"})
        self.assertEqual(self.s.commits[merge_sha]["parents"], [self.base])
        self.assertEqual(self.s.dispatches, [("release.yml", {"ref": "main", "inputs": {
            "pr": str(PR), "head_sha": self.head, "base_sha": self.base, "merge_sha": merge_sha, "tag": "v2.1.0"}})])

    def test_merge_refuses_a_changed_head_or_base(self):
        self.open_pr()
        self.assertGate("head changed", br.merge, self.api, PR, "c" * 40, self.base)
        self.assertGate("base changed", br.merge, self.api, PR, self.head, "c" * 40)
        self.s.refs["heads/main"] = {"type": "commit", "sha": self.s.commit(BASE_FILES, [self.base])}
        self.assertGate("main moved", br.merge, self.api, PR, self.head, self.base)
        self.assertFalse(self.s.pulls[PR]["merged"])
        self.assertEqual(self.s.dispatches, [])

    def test_merge_api_is_sha_conditional(self):
        self.open_pr()
        with self.assertRaisesRegex(br.APIError, "HTTP 409"):
            self.api.request("PUT", f"pulls/{PR}/merge", {"sha": "c" * 40, "merge_method": "squash"})

    def test_merge_is_idempotent_after_a_merge(self):
        self.open_pr()
        first = self.merge()
        self.assertEqual(self.merge(), first)
        self.assertEqual(len(self.s.dispatches), 2)

    # ------------------------------------------------------------ release plan

    def plan(self, **kwargs):
        return self.run_op(br.release_plan, self.api, **kwargs)[1]

    def merged(self, files=None):
        self.open_pr(files)
        return self.merge()["merge_sha"]

    def test_release_plan_checks_provenance(self):
        merge_sha = self.merged()
        values = self.plan(number=PR, head=self.head, base=self.base, merge_sha=merge_sha, tag="v2.1.0")
        self.assertEqual(values["recovery"], "false")
        self.assertEqual(values["previous"], "v2.0.0")
        self.assertEqual(values["prerelease"], "false")
        self.assertEqual(self.s.gh_calls, [])

    def test_release_plan_rejects_forgeries(self):
        merge_sha = self.merged()
        other = self.s.commit(update_files(), [self.base])
        self.assertGate("not this pull request's merge", self.plan, number=PR, merge_sha=other)
        self.assertGate("does not match", self.plan, number=PR, merge_sha=merge_sha, tag="v2.2.0")
        self.assertGate("head changed", self.plan, number=PR, head="c" * 40)
        self.s.tag("v2.1.0", other)
        self.assertGate("not the merge of exactly one approved pull request", self.plan, tag="v2.1.0")
        self.assertGate("points at another commit", self.plan, tag="v2.1.0", merge_sha=merge_sha)
        self.assertGate("already points at another commit", self.plan, number=PR)

    def test_release_plan_rejects_a_squash_with_another_tree(self):
        merge_sha = self.merged()
        self.s.commits[merge_sha]["tree"] = "f" * 40
        self.assertGate("not a squash", self.plan, number=PR)

    def test_release_plan_needs_the_previous_release_as_ancestor(self):
        self.merged()
        self.s.tag("v2.0.0", self.s.commit({"x": "unrelated"}))
        self.assertGate("not an ancestor", self.plan, number=PR)

    def test_release_plan_from_a_tag(self):
        merge_sha = self.merged()
        self.s.tag("v2.1.0", merge_sha)
        self.assertEqual(self.plan(tag="v2.1.0")["pr"], str(PR))
        self.assertGate("does not exist", self.plan, tag="v9.9.9")

    # ------------------------------------------------------------ publish

    def assets(self, tag, *, corrupt=None):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: [p.unlink() for p in folder.iterdir()] and folder.rmdir())
        lines = []
        for name in policy.expected_assets(tag)[:-1]:
            magic = b"%PDF-" if name.endswith(".pdf") else b"PK\x03\x04"
            data = (b"junk" if name == corrupt else magic) + name.encode()
            (folder / name).write_bytes(data)
            lines.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
        (folder / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        notes = folder / "notes.md"
        notes.write_text("- Updated.\n", encoding="utf-8")
        return str(folder), str(notes)

    def publish(self, tag, merge_sha, **kwargs):
        folder, notes = self.assets(tag, **kwargs)
        return self.run_op(br.publish, self.api, tag, merge_sha, folder, notes)[2]

    def release(self, tag):
        return next(r for r in self.s.releases if r["tag_name"] == tag)

    def test_publish_tags_drafts_uploads_and_publishes(self):
        merge_sha = self.merged()
        out = self.publish("v2.1.0", merge_sha)
        ref = self.s.refs["tags/v2.1.0"]
        self.assertEqual(ref["type"], "tag")
        self.assertEqual(self.s.tag_objects[ref["sha"]]["sha"], merge_sha)
        self.assertEqual([c[:2] for c in self.s.gh_calls], [["release", "create"], ["release", "upload"], ["release", "edit"]])
        self.assertIn("--draft", self.s.gh_calls[0])
        self.assertIn("--verify-tag", self.s.gh_calls[0])
        release = self.release("v2.1.0")
        self.assertFalse(release["draft"])
        self.assertTrue(release["latest"])
        self.assertEqual(policy.missing_assets("v2.1.0", release["assets"]), [])
        self.assertIn("(Latest)", out)

    def test_published_complete_release_is_a_no_op(self):
        merge_sha = self.merged()
        self.publish("v2.1.0", merge_sha)
        calls = len(self.s.gh_calls)
        self.assertIn("left unchanged", self.publish("v2.1.0", merge_sha))
        self.assertEqual(len(self.s.gh_calls), calls)
        self.assertEqual(self.plan(number=PR)["recovery"], "true")

    def test_published_incomplete_release_fails_without_writes(self):
        merge_sha = self.merged()
        self.publish("v2.1.0", merge_sha)
        self.release("v2.1.0")["assets"].pop(0)
        calls = len(self.s.gh_calls)
        self.assertGate("incomplete", self.plan, number=PR)
        self.assertGate("incomplete", self.publish, "v2.1.0", merge_sha)
        self.assertEqual(len(self.s.gh_calls), calls)

    def test_publish_never_moves_a_tag(self):
        merge_sha = self.merged()
        self.s.tag("v2.1.0", self.base)
        self.assertGate("never moved", self.publish, "v2.1.0", merge_sha)
        self.assertEqual(self.s.gh_calls, [])

    def test_publish_checks_the_files(self):
        merge_sha = self.merged()
        name = policy.expected_assets("v2.1.0")[2]
        self.assertGate("not a valid .epub", self.publish, "v2.1.0", merge_sha, corrupt=name)
        folder, notes = self.assets("v2.1.0")
        Path(folder, "SHA256SUMS.txt").write_text("0" * 64 + "  " + name + "\n", encoding="utf-8")
        self.assertGate("does not match", br.publish, self.api, "v2.1.0", merge_sha, folder, notes)
        self.assertNotIn("tags/v2.1.0", self.s.refs)

    def test_latest_only_for_the_highest_stable(self):
        self.s.releases.append({"id": 1, "tag_name": "v3.0.0", "draft": False, "prerelease": False,
                                "assets": [], "latest": True})
        self.s.tag("v3.0.0", self.base)
        merge_sha = self.merged(update_files("2.0.1"))
        self.publish("v2.0.1", merge_sha)
        self.assertIn("--latest=false", self.s.gh_calls[-1])
        self.assertTrue(self.release("v3.0.0")["latest"])

    def test_prerelease(self):
        merge_sha = self.merged(update_files("2.1.0-rc.1"))
        self.assertEqual(self.plan(number=PR)["prerelease"], "true")
        self.publish("v2.1.0-rc.1", merge_sha)
        self.assertIn("--prerelease", self.s.gh_calls[0])
        self.assertIn("--latest=false", self.s.gh_calls[-1])
        self.assertTrue(self.release("v2.1.0-rc.1")["prerelease"])

    # ------------------------------------------------------------ deploy

    def deploy(self, tag="v2.1.0", **kwargs):
        return self.run_op(br.deploy, self.api, tag, interval=0, **kwargs)

    def test_deploy_reports_a_missing_secret_as_not_deployed(self):
        code, _, out = self.deploy()
        self.assertEqual(code, 0)
        self.assertIn("## Web edition NOT deployed", out)
        self.assertIn("AZURE_STATIC_WEB_APPS_API_TOKEN", out)
        self.assertIn("./infra/deploy.sh", out)
        self.assertNotIn("is live", out)
        self.assertEqual(self.s.dispatches, [("deploy-swa.yml", {"ref": "main", "inputs": {"ref": "v2.1.0"}})])

    def test_deploy_outcomes(self):
        for outcome, code, text in [("deployed", 0, "## Web edition deployed"), ("failed", 1, "NOT deployed"),
                                    ("hang", 1, "deploy not confirmed")]:
            with self.subTest(outcome=outcome):
                self.s.deploy_outcome = outcome
                result, _, out = self.deploy(timeout=1)
                self.assertEqual(result, code)
                self.assertIn(text, out)

    def test_prerelease_is_not_deployed(self):
        code, _, out = self.deploy("v2.1.0-rc.1")
        self.assertEqual(code, 0)
        self.assertIn("not deployed", out)
        self.assertEqual(self.s.dispatches, [])

    # ------------------------------------------------------------ CLI end to end

    def cli(self, *args):
        env = {**os.environ}
        return subprocess.run([sys.executable, str(Path(br.__file__)), *args], env=env, capture_output=True,
                              text=True, encoding="utf-8", timeout=120)

    def test_cli_end_to_end(self):
        self.open_pr()
        tmp = Path(tempfile.mkdtemp())
        event = tmp / "event.json"
        event.write_text(json.dumps({"inputs": {"pr": str(PR)}}), encoding="utf-8")
        inspected = self.cli("inspect", "--event", str(event))
        self.assertIn("eligible=true", inspected.stdout, inspected.stderr)
        refused = self.cli("merge", "--pr", str(PR), "--head", "c" * 40, "--base", self.base)
        self.assertEqual(refused.returncode, 1)
        self.assertIn("head changed", refused.stderr)
        merged = self.cli("merge", "--pr", str(PR), "--head", self.head, "--base", self.base)
        self.assertEqual(merged.returncode, 0, merged.stderr)
        inputs = self.s.dispatches[-1][1]["inputs"]
        plan = self.cli("release-plan", "--pr", inputs["pr"], "--head", inputs["head_sha"], "--base",
                        inputs["base_sha"], "--merge-sha", inputs["merge_sha"], "--tag", inputs["tag"])
        self.assertIn("recovery=false", plan.stdout, plan.stderr)
        folder, notes = self.assets("v2.1.0")
        published = self.cli("publish", "--tag", "v2.1.0", "--merge-sha", inputs["merge_sha"], "--assets", folder,
                             "--notes", notes)
        self.assertEqual(published.returncode, 0, published.stderr)
        self.assertFalse(self.release("v2.1.0")["draft"])
        again = self.cli("release-plan", "--tag", "v2.1.0")
        self.assertIn("recovery=true", again.stdout, again.stderr)
        deployed = self.cli("deploy", "--tag", "v2.1.0", "--interval", "0", "--timeout", "5")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        self.assertIn("NOT deployed", deployed.stdout)
        event.unlink()
        tmp.rmdir()


if __name__ == "__main__":
    unittest.main()
