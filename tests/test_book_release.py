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
from test_validate_release import Repo, git  # noqa: E402

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
    return {"user": {"login": user}, "body": body, "created_at": at, "updated_at": at}


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
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {OLD}", at)]))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {HEAD[:12]}", at)]))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {HEAD} please", at)]))
        self.assertFalse(br.approval(pr, [], [comment(f"/release-book {HEAD}", at, "someone")]))
        self.assertFalse(br.approval(pr, [], []))

    def test_surrounding_whitespace_neither_signals_nor_authorizes_release(self):
        command = f"/release-book {HEAD}"
        for body in (" " + command, command + " ", command + "\n", command + "\r\n"):
            with self.subTest(body=body):
                signal = comment(body, "2026-12-01T10:00:00Z")
                self.assertEqual(br.event_numbers(None, {"issue": {"number": PR, "pull_request": {}},
                                                         "comment": signal}), [])
                self.assertFalse(br.approval(pr_dict(HEAD), [], [signal]))

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

    def test_edited_comment_and_deleted_comment_are_not_authorization(self):
        approved = comment(f"/release-book {HEAD}", "2026-12-01T10:00:00Z")
        approved["updated_at"] = "2026-12-01T10:01:00Z"
        self.assertFalse(br.approval(pr_dict(HEAD), [], [approved]))
        self.assertFalse(br.approval(pr_dict(HEAD), [], []))

    def test_late_dismissal_of_an_older_review_revokes_a_newer_approval(self):
        reviews = [review(1, "DISMISSED", OLD, "2026-12-01T09:00:00Z"),
                   review(2, "APPROVED", HEAD, "2026-12-01T10:00:00Z")]
        timeline = [{"event": "review_dismissed", "created_at": "2026-12-01T11:00:00Z",
                     "dismissed_review": {"review_id": 1}}]
        self.assertFalse(br.approval(pr_dict(HEAD, "contributor"), reviews, [], timeline))


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

    def test_another_reviewers_barrier_blocks_until_fresh_owner_authorization(self):
        for author in (OWNER, "contributor"):
            with self.subTest(author=author):
                self.open_pr(author=author, approve=False)
                self.s.reviews[PR], self.s.comments[PR], self.s.timeline[PR] = [], [], []

                def authorize(at):
                    if author == OWNER:
                        self.s.comment(PR, f"/release-book {self.head}", at=at)
                    else:
                        self.s.review(PR, "APPROVED", self.head, at=at)

                authorize("2026-12-01T10:00:00Z")
                if author == OWNER:
                    self.s.review(PR, "CHANGES_REQUESTED", self.head, user="outsider", at="2026-12-01T11:00:00Z")
                else:
                    old = self.s.review(PR, "DISMISSED", self.head, user="outsider", at="2026-12-01T09:00:00Z")
                    self.s.timeline[PR].append({"event": "review_dismissed", "created_at": "2026-12-01T11:00:00Z",
                                                "dismissed_review": {"review_id": old["id"]}})
                self.assertIn("no current owner approval", self.inspect()[1])
                self.assertGate("no current owner approval", br.merge, self.api, PR, self.head, self.base)
                self.assertEqual(self.s.writes, [])
                authorize("2026-12-01T12:00:00Z")
                self.assertEqual(self.inspect()[0]["eligible"], "true")

    def test_pr_conditions(self):
        cases = [({"draft": True}, "non-draft"), ({"same_repo": False}, "from this repository"),
                 ({"mergeable": None}, "not mergeable"), ({"mergeable": False}, "not mergeable")]
        for pull, message in cases:
            with self.subTest(pull=pull):
                self.open_pr(**pull)
                self.assertIn(message, self.inspect()[1])

    def test_closed_pr_and_wrong_base_are_refused_without_writes(self):
        self.open_pr()
        for key, value in (("state", "closed"), ("base", {**self.s.pulls[PR]["base"], "ref": "develop"})):
            with self.subTest(key=key):
                original = self.s.pulls[PR][key]
                self.s.pulls[PR][key] = value
                self.assertIn("only open", self.inspect()[1])
                self.s.pulls[PR][key] = original
        self.assertEqual(self.s.writes, [])

    def test_head_behind_main_is_refused(self):
        main2 = self.s.commit({**BASE_FILES, "figures/new.svg": "<svg/>"}, [self.base])
        self.s.refs["heads/main"] = {"type": "commit", "sha": main2}
        self.head = self.s.commit(update_files(), [self.base])
        self.s.pull(PR, self.head, main2)
        self.s.comment(PR, f"/release-book {self.head}")
        self.s.ci_run(self.head)
        self.assertIn("behind main", self.inspect()[1])
        self.assertGate("behind main", br.merge, self.api, PR, self.head, main2)
        self.assertEqual(self.s.writes, [])

    def test_stale_pull_base_cannot_hide_current_main(self):
        self.open_pr()
        self.s.refs["heads/main"] = {"type": "commit", "sha": self.s.commit(BASE_FILES, [self.base])}
        self.assertIn("behind main", self.inspect()[1])
        self.assertEqual(self.s.writes, [])

    def test_owner_comment_is_revoked_by_a_new_head_edit_or_deletion(self):
        self.open_pr()
        approved = self.s.comments[PR][0]
        approved["updated_at"] = "2099-01-01T00:00:00Z"
        self.assertIn("no current owner approval", self.inspect()[1])
        approved["updated_at"] = approved["created_at"]
        self.s.pulls[PR]["head"]["sha"] = self.s.commit(update_files(), [self.head])
        self.assertIn("no current owner approval", self.inspect()[1])
        self.s.comments[PR].clear()
        self.assertIn("no current owner approval", self.inspect()[1])
        self.assertEqual(self.s.writes, [])

    def test_preflight_must_pass_on_the_exact_head(self):
        self.open_pr(ci=False)
        self.s.ci_run(self.base)
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
        self.assertEqual(self.s.merge_requests[0]["sha"], self.head)
        self.assertEqual(self.s.merge_requests[0]["merge_method"], "squash")
        self.assertEqual(self.s.dispatches, [("release.yml", {"ref": "main", "inputs": {
            "pr": str(PR), "head_sha": self.head, "base_sha": self.base, "merge_sha": merge_sha, "tag": "v2.1.0"}})])

    def test_merge_refuses_a_changed_head_or_base(self):
        self.open_pr()
        self.assertGate("head changed", br.merge, self.api, PR, "c" * 40, self.base)
        self.assertGate("base changed", br.merge, self.api, PR, self.head, "c" * 40)
        self.s.refs["heads/main"] = {"type": "commit", "sha": self.s.commit(BASE_FILES, [self.base])}
        self.assertGate("behind main", br.merge, self.api, PR, self.head, self.base)
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
        self.publish("v2.1.0", merge_sha)
        self.assertEqual(self.plan(tag="v2.1.0")["pr"], str(PR))
        self.assertGate("does not exist", self.plan, tag="v9.9.9")

    def test_manual_merge_is_not_release_provenance(self):
        merge_sha = self.merged()
        self.s.pulls[PR]["merged_by"] = {"login": OWNER}
        writes = list(self.s.writes)
        self.assertGate("manual merge", self.plan, number=PR)
        self.assertGate("manual merge", self.publish, "v2.1.0", merge_sha)
        self.assertEqual(self.s.writes, writes)

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
        self.assertNotIn("--clobber", self.s.gh_calls[1])
        release = self.release("v2.1.0")
        self.assertFalse(release["draft"])
        self.assertTrue(release["latest"])
        self.assertEqual(policy.missing_assets("v2.1.0", release["assets"]), [])
        self.assertIn("(Latest)", out)
        self.assertIn("published=true", out)

    def test_published_complete_release_is_a_no_op(self):
        merge_sha = self.merged()
        self.publish("v2.1.0", merge_sha)
        writes = list(self.s.writes)
        result = self.publish("v2.1.0", merge_sha)
        self.assertIn("left unchanged", result)
        self.assertIn("published=false", result)
        self.assertEqual(self.plan(number=PR)["recovery"], "true")
        self.assertEqual(self.s.writes, writes)

    def test_published_incomplete_release_fails_without_writes(self):
        merge_sha = self.merged()
        self.publish("v2.1.0", merge_sha)
        self.release("v2.1.0")["assets"].pop(0)
        writes = list(self.s.writes)
        self.assertGate("incomplete", self.plan, number=PR)
        self.assertGate("incomplete", self.publish, "v2.1.0", merge_sha)
        self.assertEqual(self.s.writes, writes)

    def test_partial_release_states_fail_without_any_write(self):
        merge_sha = self.merged()
        self.publish("v2.1.0", merge_sha)
        release = self.release("v2.1.0")
        tagged = self.s.refs["tags/v2.1.0"]
        for state in ("draft", "tag-only", "missing-tag"):
            with self.subTest(state=state):
                release["draft"] = state == "draft"
                self.s.releases = [] if state == "tag-only" else [release]
                if state == "missing-tag":
                    del self.s.refs["tags/v2.1.0"]
                else:
                    self.s.refs["tags/v2.1.0"] = tagged
                writes = list(self.s.writes)
                self.assertGate("partial release", self.plan, number=PR)
                self.assertGate("partial release", self.publish, "v2.1.0", merge_sha)
                self.assertEqual(self.s.writes, writes)

    def test_publish_rechecks_provenance_before_creating_a_tag(self):
        merge_sha = self.merged()
        self.s.commits[merge_sha]["tree"] = "f" * 40
        writes = list(self.s.writes)
        self.assertGate("not a squash", self.publish, "v2.1.0", merge_sha)
        self.assertEqual(self.s.writes, writes)

    def test_publish_never_moves_a_tag(self):
        merge_sha = self.merged()
        self.s.tag("v2.1.0", self.base)
        self.assertGate("points at another commit", self.publish, "v2.1.0", merge_sha)
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

    def add_release(self, tag, **flags):
        self.s.releases.append({"tag_name": tag, "draft": False, "prerelease": False, **flags})

    def test_deploy_only_highest_published_stable(self):
        for tag in ("v2.1.0", "v2.10.0"):
            self.add_release(tag)
        self.s.tag("v7.0.0", self.base)
        self.add_release("v8.0.0", draft=True)
        self.add_release("v9.0.0", prerelease=True)
        self.add_release("v10.0.0-rc.1")
        self.s.deploy_outcome = "deployed"
        code, _, out = self.deploy("v2.1.0")
        self.assertEqual(code, 0)
        self.assertIn("v2.10.0", out)
        self.assertEqual(self.s.dispatches, [])
        self.assertEqual(self.deploy("v2.10.0")[0], 0)
        self.assertEqual(self.s.dispatches, [(br.DEPLOY_WORKFLOW, {"ref": "main", "inputs": {
            "ref": "v2.10.0", "latest_only": "true"}})])

    def test_unpublished_candidate_is_not_dispatched(self):
        self.s.tag("v2.1.0", self.base)
        result = self.cli("deploy", "--tag", "v2.1.0", "--timeout", "1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a published stable release", result.stderr)
        self.assertEqual(self.s.dispatches, [])

    def test_deploy_reports_a_missing_secret_as_not_deployed(self):
        self.add_release("v2.1.0")
        code, _, out = self.deploy()
        self.assertEqual(code, 1)
        self.assertIn("## Web edition NOT deployed", out)
        self.assertIn("AZURE_STATIC_WEB_APPS_API_TOKEN", out)
        self.assertIn("./infra/deploy.sh", out)
        self.assertNotIn("is live", out)
        self.assertEqual(self.s.dispatches, [("deploy-swa.yml", {"ref": "main", "inputs": {
            "ref": "v2.1.0", "latest_only": "true"}})])

    def test_deploy_outcomes(self):
        self.add_release("v2.1.0")
        for outcome, code, text in [("deployed", 0, "## Web edition deployed"), ("failed", 1, "NOT deployed"),
                                    ("smoke-skipped", 1, "not confirmed"), ("upload-skipped", 1, "not confirmed"),
                                    ("hang", 1, "deploy not confirmed")]:
            with self.subTest(outcome=outcome):
                self.s.deploy_outcome = outcome
                result, _, out = self.deploy(timeout=1)
                self.assertEqual(result, code)
                self.assertIn(text, out)

    def test_deploy_ignores_nearby_runs(self):
        self.add_release("v2.1.0")
        dispatch = self.s.deploy_dispatched

        def interleaved():
            self.s.deploy_outcome = "failed"
            ours = dispatch()
            self.s.deploy_outcome = "smoke-skipped"
            dispatch()
            return ours

        with mock.patch.object(self.s, "deploy_dispatched", side_effect=interleaved):
            result = self.cli("deploy", "--tag", "v2.1.0", "--timeout", "2", "--interval", "0")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(self.s.runs[0]["html_url"], result.stdout)
        self.assertNotIn(self.s.runs[1]["html_url"], result.stdout)
        self.assertNotIn("is live", result.stdout)
        self.assertEqual(len(self.s.dispatches), 1)

    def timed_deploy(self, received):
        """Run the deploy CLI against the loopback API; `received` maps "run"/"jobs" GETs to arrival times."""
        clock, paths, request = [0.0], [], br.GitHub.request

        def respond(api, method, path, *args, **kwargs):
            result = request(api, method, path, *args, **kwargs)
            paths.append(path)
            kind = ("jobs" if path.endswith("/jobs?per_page=100")
                    else "run" if path.startswith("actions/runs/") and path.count("/") == 2 else None)
            if method == "GET" and kind in received:
                clock[0] = max(clock[0], received[kind])
            return result

        def sleep(seconds):
            clock[0] += seconds

        out = io.StringIO()
        with mock.patch.object(br.GitHub, "request", autospec=True, side_effect=respond), \
                mock.patch.object(br.time, "monotonic", lambda: clock[0]), \
                mock.patch.object(br.time, "sleep", sleep), contextlib.redirect_stdout(out):
            code = br.main(["deploy", "--tag", "v2.1.0", "--timeout", "100", "--interval", "15"])
        return code, out.getvalue(), paths

    def test_deploy_evidence_must_arrive_before_the_deadline(self):
        self.add_release("v2.1.0")
        self.s.deploy_outcome = "deployed"
        for name, received, code in [("on time", {"run": 10, "jobs": 20}, 0),
                                     ("run at deadline", {"run": 100}, 1), ("run late", {"run": 120}, 1),
                                     ("jobs at deadline", {"jobs": 100}, 1), ("jobs late", {"jobs": 120}, 1)]:
            with self.subTest(name):
                dispatches = len(self.s.dispatches)
                result, out, paths = self.timed_deploy(received)
                self.assertEqual(result, code, out)
                self.assertEqual(len(self.s.dispatches), dispatches + 1)
                self.assertFalse([p for p in paths if p.startswith(f"actions/workflows/{br.DEPLOY_WORKFLOW}/runs")])
                if code:
                    self.assertIn("did not finish in time", out)
                    self.assertNotIn("is live", out)
                    if "jobs" not in received:
                        self.assertFalse(any(p.endswith("/jobs?per_page=100") for p in paths))
                else:
                    self.assertIn("v2.1.0 is live", out)

    def test_missing_dispatch_identity_is_not_retried_or_inferred(self):
        self.add_release("v2.1.0")
        self.s.deploy_outcome = "deployed"
        request = self.api.request

        def lost_response(method, *args, **kwargs):
            result = request(method, *args, **kwargs)
            return {} if method == "POST" else result

        with mock.patch.object(self.api, "request", side_effect=lost_response):
            code, _, out = self.deploy(timeout=1)
        self.assertEqual(code, 1)
        self.assertIn("not confirmed", out)
        self.assertEqual(len(self.s.dispatches), 1)

    def test_missing_workflow_fails_delivery(self):
        self.add_release("v2.1.0")
        with mock.patch.object(br, "DEPLOY_WORKFLOW", "missing.yml"):
            code, _, out = self.deploy(timeout=1)
        self.assertEqual(code, 1)
        self.assertIn("missing.yml", out)
        self.assertEqual(self.s.dispatches, [])

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
        repo = Repo()
        self.addCleanup(repo.close)
        self.base = repo.base
        repo.chapter()
        repo.release()
        self.head = repo.commit()
        for sha in (self.base, self.head):
            files = {name: git(repo.root, "show", f"{sha}:{name}") for name in
                     git(repo.root, "ls-tree", "-r", "--name-only", sha).splitlines()}
            self.s.commits[sha] = {"files": files, "tree": git(repo.root, "rev-parse", f"{sha}^{{tree}}"),
                                  "parents": [] if sha == self.base else [self.base]}
        self.s.refs["heads/main"] = {"type": "commit", "sha": self.base}
        self.s.tag("v1.0.0", self.base)
        self.s.tag("v2.0.0", self.base)
        self.s.pull(PR, self.head, self.base)
        self.s.comment(PR, f"/release-book {self.head}")
        self.s.ci_run(self.head)
        checked = subprocess.run([sys.executable, str(Path(br.validator.__file__)), "change", "--root",
                                  str(repo.root), "--base-ref", self.base, "--head", self.head],
                                 capture_output=True, text=True, timeout=120)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        tmp = Path(repo.tmp.name)
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
        self.assertEqual(self.s.dispatches[-1][0], "release.yml")
        self.assertEqual(set(inputs), {"pr", "head_sha", "base_sha", "merge_sha", "tag"})
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
        self.s.deploy_outcome = "deployed"
        deployed = self.cli("deploy", "--tag", "v2.1.0", "--interval", "0", "--timeout", "5")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        self.assertIn("v2.1.0 is live", deployed.stdout)
        self.assertIn(self.s.runs[-1]["html_url"], deployed.stdout)
        workflow, payload = self.s.dispatches[-1]
        self.assertEqual((workflow, payload), ("deploy-swa.yml", {"ref": "main", "inputs": {
            "ref": "v2.1.0", "latest_only": "true"}}))
        event.write_text(json.dumps(payload), encoding="utf-8")
        with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "workflow_dispatch"}):
            source = self.cli("published-source", "--event", str(event))
        self.assertEqual(source.returncode, 0, source.stderr)
        self.assertIn(f"sha={inputs['merge_sha']}", source.stdout)


class PublishedSource(unittest.TestCase):
    run_op = Controller.run_op
    assertGate = Controller.assertGate

    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.close)
        self.fake = FakeGitHub().__enter__()
        self.addCleanup(self.fake.__exit__, None, None, None)
        env = mock.patch.dict(os.environ, self.fake.env())
        env.start()
        self.addCleanup(env.stop)
        for name in ("GITHUB_OUTPUT", "GITHUB_STEP_SUMMARY", "GITHUB_ACTIONS"):
            os.environ.pop(name, None)
        self.s = self.fake.state
        self.api = br.GitHub()
        self.published("v2.0.0", self.repo.base)

    def published(self, tag, sha, **kwargs):
        self.s.tag(tag, sha)
        self.s.releases.append({"id": len(self.s.releases) + 1, "tag_name": tag, "draft": False,
                                "prerelease": False, **kwargs})

    def gate(self, event):
        result = self.run_op(br.published_source, self.api, event, self.repo.root)[1]
        self.assertEqual(self.s.writes, [])
        return result

    def push(self):
        return self.gate({"event_name": "push", "ref": "refs/heads/main", "after": self.repo.commit()})

    def test_main_push_compares_all_trusted_content_paths_including_metadata(self):
        for path in (*policy.CONTENT_FILES, *(p + "extra.md" for p in policy.CONTENT_PREFIXES),
                     policy.CHANGELOG, policy.BOOK_JSON):
            with self.subTest(path=path):
                if path == policy.BOOK_JSON:
                    self.repo.book(version="2.1.0")
                else:
                    self.repo.write({path: "unreleased\n"})
                self.assertEqual(self.push(), {"eligible": "false"})
                git(self.repo.root, "restore", "--source", self.repo.base, "--staged", "--worktree", ".")

    def test_tooling_only_push_preserves_published_content(self):
        self.repo.write({"tools/build.py": "print('new build')\n", "theme/site.css": "body {}"})
        self.repo.book(agent_ready={"feed": False})
        result = self.push()
        self.assertEqual(result, {"eligible": "true", "sha": git(self.repo.root, "rev-parse", "HEAD"),
                                  "tag": "v2.0.0"})

    def test_gate_uses_policy_extensions_not_a_duplicate_path_list(self):
        self.repo.write({"new-content/extra.md": "unreleased\n"})
        with mock.patch.object(policy, "CONTENT_PREFIXES", (*policy.CONTENT_PREFIXES, "new-content/")):
            self.assertEqual(self.push(), {"eligible": "false"})

    def test_deleted_or_renamed_content_is_not_published(self):
        self.repo.write({"manuscript/01-the-agent-ready-web.md": None, "tools/renamed.md": "old text\n"})
        self.assertEqual(self.push(), {"eligible": "false"})

    def test_highest_published_stable_is_used_not_drafts_or_prereleases(self):
        self.repo.chapter()
        self.repo.release("2.1.0")
        newer = self.repo.commit()
        self.published("v2.1.0", newer)
        self.published("v9.0.0", self.repo.base, draft=True)
        self.published("v10.0.0-rc.1", self.repo.base, prerelease=True)
        self.assertEqual(self.push()["tag"], "v2.1.0")
        self.repo.write({"VALIDATION.md": "not released\n"})
        self.assertEqual(self.push(), {"eligible": "false"})

    def test_no_release_skips_main_push(self):
        self.s.releases.clear()
        self.assertEqual(self.push(), {"eligible": "false"})

    def test_manual_rollback_uses_its_own_published_tag_or_sha(self):
        self.repo.chapter()
        self.repo.release("2.1.0")
        self.published("v2.1.0", self.repo.commit())
        self.assertEqual(self.gate({"event_name": "workflow_dispatch", "inputs": {
            "ref": "v2.0.0", "latest_only": "true"}}), {"eligible": "false"})
        for event in ({"event_name": "workflow_dispatch", "inputs": {"ref": "v2.0.0"}},
                      {"event_name": "workflow_dispatch", "inputs": {"ref": self.repo.base}}):
            with self.subTest(event=event):
                self.assertEqual(self.gate(event), {"eligible": "true", "sha": self.repo.base, "tag": "v2.0.0"})

    def test_unreleased_tags_shas_branches_drafts_and_prereleases_are_refused(self):
        self.repo.chapter()
        sha = self.repo.commit()
        self.s.tag("v2.1.0", sha)
        self.published("v3.0.0", sha, draft=True)
        self.published("v4.0.0-rc.1", sha, prerelease=True)
        for ref in ("v2.1.0", sha, "main", "", "--help", "v3.0.0", "v4.0.0-rc.1"):
            with self.subTest(ref=ref):
                self.assertGate("published stable", self.gate,
                                {"event_name": "workflow_dispatch", "inputs": {"ref": ref}})
        self.assertEqual(self.s.writes, [])

    def test_release_event_and_other_push_branches_fail(self):
        self.assertGate("unsupported", self.gate, {"event_name": "release", "release": {"tag_name": "v2.0.0"}})
        self.assertGate("main", self.gate, {"event_name": "push", "ref": "refs/heads/other"})

    def test_push_cli_runs_the_gate_on_a_real_git_checkout(self):
        self.repo.write({"tools/build.py": "print('tooling update')\n"})
        sha = self.repo.commit()
        event = self.repo.root / "event.json"
        event.write_text(json.dumps({"ref": "refs/heads/main", "after": sha}), encoding="utf-8")
        env = {**os.environ, "GITHUB_EVENT_NAME": "push"}
        result = subprocess.run([sys.executable, str(Path(br.__file__)), "published-source", "--event",
                                 str(event), "--root", str(self.repo.root)], env=env, capture_output=True,
                                text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"sha={sha}", result.stdout)
        self.assertEqual(self.s.writes, [])


if __name__ == "__main__":
    unittest.main()
