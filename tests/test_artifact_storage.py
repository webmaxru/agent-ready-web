"""Artifact retention, race safety and failure recovery without live writes."""
import copy
import hashlib
import io
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import artifact_storage as storage
import book_release as release
import release_policy as policy

REPO = "webmaxru/agent-ready-web"
REF = "refs/heads/preview/book"
SHA = "a" * 40


def run(i, **values):
    return dict(id=i, repository={"full_name": REPO}, head_repository={"full_name": REPO},
                path=".github/workflows/ci.yml", event="workflow_dispatch", head_branch="preview/book",
                head_sha=SHA, run_attempt=1, status="completed", conclusion="success", **values)


def artifact(i, producer, ref=REF, **values):
    data = dict(id=i, name=storage.preview_name(REPO, ref, producer["id"], producer["run_attempt"]),
                expired=False, created_at=f"2026-11-{producer['id']:02}T00:00:00Z",
                workflow_run={k: producer[k] for k in ("id", "head_sha", "head_branch")})
    data.update(values)
    return data


class API:
    repo = REPO

    def __init__(self):
        self.runs = {i: run(i) for i in (1, 2, 3)}
        self.artifacts = [artifact(i + 10, self.runs[i]) for i in (1, 2, 3)]
        self.jobs = [{"name": "build", "steps": [
            {"name": "Upload requested book preview", "conclusion": "success"}]}]
        self.deleted = []
        self.calls = []
        self.hook = None

    def request(self, method, path, data=None, **kwargs):
        self.calls.append((method, path))
        if self.hook:
            self.hook(method, path)
        url = urlsplit(path)
        pieces = url.path.split("/")
        if method == "DELETE":
            i = int(pieces[-1])
            self.deleted.append(i)
            self.artifacts = [a for a in self.artifacts if a["id"] != i]
            return None
        if pieces[:2] == ["actions", "artifacts"] and len(pieces) == 3:
            return copy.deepcopy(next(a for a in self.artifacts if a["id"] == int(pieces[2])))
        if pieces[:2] == ["actions", "runs"]:
            producer = self.runs[int(pieces[2])]
            if len(pieces) == 3:
                return copy.deepcopy(producer)
            if pieces[-1] == "jobs":
                items, key = self.jobs, "jobs"
            else:
                items = [a for a in self.artifacts if a["workflow_run"]["id"] == producer["id"]]
                key = "artifacts"
        else:
            items, key = self.artifacts, "artifacts"
        page = int(parse_qs(url.query)["page"][0])
        return {key: copy.deepcopy(items[(page - 1) * 100:page * 100])}


class Previews(unittest.TestCase):
    def setUp(self):
        self.api = API()
        quiet = mock.patch.object(release, "summary")
        quiet.start()
        self.addCleanup(quiet.stop)

    def test_namespace_binds_repo_full_ref_run_and_attempt(self):
        name = storage.preview_name(REPO, REF, 2, 1)
        for args in (("other/book", REF, 2, 1), (REPO, REF.replace("heads", "tags"), 2, 1),
                     (REPO, "refs/heads/preview-book", 2, 1), (REPO, REF, 2, 2)):
            self.assertNotEqual(name, storage.preview_name(*args))
        with self.assertRaises(release.GateError):
            storage.preview_name(REPO, "main", 2, 1)

    def test_deletes_older_only_preserves_replacement_newer_diagnostics_and_staging(self):
        for i, name in enumerate(("audit-1-1", "editions-v2.0.0", "release-notes-v2.0.0",
                                  "book-old", "book-preview-v2-other"), 100):
            self.api.artifacts.append(artifact(i, self.api.runs[1], name=name))
        self.api.artifacts.append(artifact(200, self.api.runs[1], ref="refs/tags/preview/book"))
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [11])

    def test_reverse_completion_never_deletes_newer_upload(self):
        self.api.artifacts[0]["created_at"] = "2026-12-01T00:00:00Z"
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])
        storage.cleanup_preview(self.api, 3)
        self.assertEqual(self.api.deleted, [12])
        # A queued older cleanup must not remove the latest replacement.
        with self.assertRaises(release.GateError):
            storage.cleanup_preview(self.api, 2)
        self.assertNotIn(13, self.api.deleted)

    def test_active_producer_and_rerun_are_preserved(self):
        for values in ({"status": "in_progress"}, {"run_attempt": 2, "status": "in_progress"},
                       {"conclusion": "failure"}):
            with self.subTest(values=values):
                self.api = API()
                self.api.runs[1].update(values)
                storage.cleanup_preview(self.api, 2)
                self.assertEqual(self.api.deleted, [])

    def test_completed_same_run_removes_only_superseded_attempts(self):
        previous = artifact(201, self.api.runs[2], created_at="2026-11-02T12:00:00Z")
        self.api.runs[2]["run_attempt"] = 2
        replacement = artifact(202, self.api.runs[2], created_at="2026-11-02T13:00:00Z")
        newer = artifact(203, dict(self.api.runs[2], run_attempt=3),
                         created_at="2026-11-02T14:00:00Z")
        unrelated = artifact(204, self.api.runs[2], name="audit-2-1")
        self.api.artifacts = [previous, replacement, newer, unrelated]
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [201])
        self.assertEqual([a["id"] for a in self.api.artifacts], [202, 203, 204])

    def test_completed_older_run_removes_all_superseded_attempts(self):
        previous = artifact(101, self.api.runs[1])
        self.api.runs[1]["run_attempt"] = 2
        latest = artifact(102, self.api.runs[1])
        self.api.artifacts = [previous, latest, self.api.artifacts[1], self.api.artifacts[2]]
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [101, 102])
        self.assertEqual([a["id"] for a in self.api.artifacts], [12, 13])

    def test_active_rerun_preserves_every_previous_attempt(self):
        previous = artifact(101, self.api.runs[1])
        latest = artifact(102, dict(self.api.runs[1], run_attempt=2))
        self.api.runs[1].update(run_attempt=3, status="in_progress", conclusion=None)
        self.api.artifacts = [previous, latest, self.api.artifacts[1]]
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])

    def test_same_run_rerun_started_before_delete_preserves_previous_attempt(self):
        previous = artifact(201, self.api.runs[2], created_at="2026-11-02T12:00:00Z")
        self.api.runs[2]["run_attempt"] = 2
        replacement = artifact(202, self.api.runs[2], created_at="2026-11-02T13:00:00Z")
        self.api.artifacts = [previous, replacement]

        def hook(method, path):
            if path == "actions/artifacts/202":
                self.api.runs[2].update(run_attempt=3, status="in_progress", conclusion=None)
        self.api.hook = hook
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])

    def test_producer_is_rechecked_immediately_before_delete(self):
        reads = 0

        def hook(method, path):
            nonlocal reads
            if path == "actions/runs/1":
                reads += 1
                if reads == 2:
                    self.api.runs[1]["status"] = "in_progress"
        self.api.hook = hook
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])

    def test_failed_or_unconfirmed_replacement_keeps_previous(self):
        for change in ("failed-run", "failed-upload", "missing-id", "expired", "wrong-sha", "missing-artifact"):
            with self.subTest(change=change):
                self.api = API()
                if change == "failed-run":
                    self.api.runs[2]["conclusion"] = "failure"
                elif change == "failed-upload":
                    self.api.jobs[0]["steps"][0]["conclusion"] = "failure"
                elif change == "missing-id":
                    self.api.artifacts[1]["id"] = None
                elif change == "expired":
                    self.api.artifacts[1]["expired"] = True
                elif change == "wrong-sha":
                    self.api.artifacts[1]["workflow_run"]["head_sha"] = "b" * 40
                else:
                    self.api.artifacts.pop(1)
                with self.assertRaises(release.GateError):
                    storage.cleanup_preview(self.api, 2)
                self.assertEqual(self.api.deleted, [])

    def test_ordinary_dispatch_without_preview_does_not_delete(self):
        self.api.artifacts.pop(1)
        self.api.jobs[0]["steps"] = []
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])

    def test_replacement_expiry_during_cleanup_fails_closed(self):
        def hook(method, path):
            if path == "actions/artifacts/12":
                self.api.artifacts[1]["expired"] = True
        self.api.hook = hook
        with self.assertRaises(release.GateError):
            storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])

    def test_wrong_workflow_repository_or_event_cannot_authorize_deletion(self):
        for change in ({"path": ".github/workflows/other.yml"}, {"event": "pull_request"},
                       {"repository": {"full_name": "other/repo"}},
                       {"head_repository": {"full_name": "other/fork"}}):
            with self.subTest(change=change):
                self.api = API()
                self.api.runs[2].update(change)
                with self.assertRaises(release.GateError):
                    storage.cleanup_preview(self.api, 2)
                self.assertEqual(self.api.deleted, [])

    def test_candidate_from_other_workflow_or_with_wrong_metadata_is_never_deleted(self):
        self.api.runs[1]["path"] = ".github/workflows/other.yml"
        with self.assertRaises(release.GateError):
            storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])
        self.api = API()
        self.api.artifacts[0]["workflow_run"]["head_sha"] = "b" * 40
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])

    def test_ambiguous_replacement_is_rejected(self):
        self.api.artifacts.append(artifact(99, self.api.runs[2]))
        with self.assertRaises(release.GateError):
            storage.cleanup_preview(self.api, 2)
        self.assertEqual(self.api.deleted, [])

    def test_pagination_snapshot_before_deleting(self):
        self.api.artifacts = [artifact(i + 100, self.api.runs[1]) for i in range(101)]
        self.api.artifacts.append(artifact(12, self.api.runs[2]))
        storage.cleanup_preview(self.api, 2)
        self.assertEqual(len(self.api.deleted), 101)
        self.assertNotIn(12, self.api.deleted)
        self.assertIn(("GET", "actions/artifacts?per_page=100&page=2"), self.api.calls)

    def test_delete_error_is_not_swallowed(self):
        def hook(method, path):
            if method == "DELETE":
                raise release.APIError("HTTP 403")
        self.api.hook = hook
        with self.assertRaisesRegex(release.APIError, "403"):
            storage.cleanup_preview(self.api, 2)

    def test_loopback_api_uses_real_pagination_and_delete_transport(self):
        api = self.api

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def handle_request(self):
                result = api.request(self.command, self.path.split(f"/repos/{REPO}/", 1)[1])
                self.send_response(204 if result is None else 200)
                self.end_headers()
                if result is not None:
                    self.wfile.write(json.dumps(result).encode())

            do_GET = handle_request
            do_DELETE = handle_request

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with mock.patch.dict(os.environ, GITHUB_REPOSITORY=REPO, GH_TOKEN="test",
                                 GITHUB_API_URL=f"http://127.0.0.1:{server.server_port}"):
                storage.cleanup_preview(release.GitHub(), 2)
        finally:
            server.shutdown()
            thread.join()
            server.server_close()
        self.assertEqual(api.deleted, [11])


class Staging(unittest.TestCase):
    def setUp(self):
        self.api = API()
        self.api.runs[2].update(path=".github/workflows/release.yml", head_branch="main",
                                status="in_progress")
        self.api.artifacts = [artifact(21, self.api.runs[2], name="editions-v2.1.0"),
                              artifact(22, self.api.runs[2], name="release-notes-v2.1.0"),
                              artifact(23, self.api.runs[2], name="audit-2")]
        self.api.jobs = [{"name": name, "conclusion": "success"} for name in (
            "Build the editions (exact merge commit, before tagging)", "Tag and publish the GitHub Release",
            "Deploy the web edition")]
        self.plan = mock.patch.object(release, "release_plan", return_value={"recovery": "true"}).start()
        self.download = mock.patch.object(release, "gh", side_effect=self.download_files).start()
        mock.patch.object(release, "summary").start()
        self.addCleanup(mock.patch.stopall)

    def download_files(self, *args):
        folder = Path(args[args.index("--dir") + 1])
        names = policy.expected_assets("v2.1.0")
        sums = []
        for name in names[:-1]:
            content = b"%PDF-test" if name.endswith(".pdf") else b"PK\x03\x04test"
            (folder / name).write_bytes(content)
            sums.append(f"{hashlib.sha256(content).hexdigest()}  {name}\n")
        (folder / "SHA256SUMS.txt").write_text("".join(sums), encoding="utf-8")

    def cleanup(self):
        storage.cleanup_release(self.api, 2, "v2.1.0", SHA, "21", "22")

    def test_published_integrity_verified_and_all_consumers_finished(self):
        self.cleanup()
        self.assertEqual(self.api.deleted, [21, 22])
        self.plan.assert_called_once_with(self.api, tag="v2.1.0", merge_sha=SHA)
        self.assertEqual(self.api.artifacts[0]["name"], "audit-2")

    def test_failed_or_active_publisher_or_deployment_retains_recovery(self):
        for name in ("Tag and publish the GitHub Release", "Deploy the web edition"):
            for conclusion in ("failure", None, "cancelled"):
                with self.subTest(name=name, conclusion=conclusion):
                    job = next(j for j in self.api.jobs if j["name"] == name)
                    job["conclusion"] = conclusion
                    with self.assertRaises(release.GateError):
                        self.cleanup()
                    self.assertEqual(self.api.deleted, [])
                    job["conclusion"] = "success"
        self.download.assert_not_called()

    def test_partial_or_unconfirmed_publication_retains_staging(self):
        for side_effect, result in ((release.GateError("draft or incomplete"), None),
                                    (None, {"recovery": "false"})):
            self.plan.side_effect = side_effect
            self.plan.return_value = result
            with self.assertRaises(release.GateError):
                self.cleanup()
            self.assertEqual(self.api.deleted, [])

    def test_download_failure_and_invalid_checksums_retain_staging(self):
        self.download.side_effect = release.APIError("download failed")
        with self.assertRaises(release.APIError):
            self.cleanup()
        self.assertEqual(self.api.deleted, [])

        def corrupt(*args):
            self.download_files(*args)
            folder = Path(args[args.index("--dir") + 1])
            (folder / "SHA256SUMS.txt").write_text("invalid\n")
        self.download.side_effect = corrupt
        with self.assertRaises(ValueError):
            self.cleanup()
        self.assertEqual(self.api.deleted, [])

    def test_staging_ids_are_exact_and_required(self):
        for editions, notes in (("0", "22"), ("21", "21"), ("23", "22")):
            with self.subTest(editions=editions, notes=notes):
                with self.assertRaises(release.GateError):
                    storage.cleanup_release(self.api, 2, "v2.1.0", SHA, editions, notes)
                self.assertEqual(self.api.deleted, [])

    def test_missing_downstream_job_and_rerun_during_verification_retain_staging(self):
        jobs = self.api.jobs[:]
        self.api.jobs.pop()
        with self.assertRaises(release.GateError):
            self.cleanup()
        self.assertEqual(self.api.deleted, [])
        self.api.jobs = jobs

        def download(*args):
            self.download_files(*args)
            self.api.runs[2]["run_attempt"] += 1
        self.download.side_effect = download
        with self.assertRaises(release.GateError):
            self.cleanup()
        self.assertEqual(self.api.deleted, [])


class Failures(unittest.TestCase):
    def test_collection_limit_and_invalid_response_fail_explicitly(self):
        api = mock.Mock()
        api.request.return_value = {"artifacts": [None] * 100}
        with self.assertRaisesRegex(release.GateError, "pagination limit"):
            storage.collection(api, "actions/artifacts", "artifacts")
        api.request.return_value = {"artifacts": {}}
        with self.assertRaisesRegex(release.GateError, "invalid"):
            storage.collection(api, "actions/artifacts", "artifacts")

    def test_cli_returns_failure_and_annotation_for_api_error(self):
        with mock.patch.object(sys, "argv", ["artifact_storage.py", "preview", "--run-id", "2"]), \
                mock.patch.object(release, "GitHub"), \
                mock.patch.object(storage, "cleanup_preview", side_effect=release.APIError("HTTP 403")), \
                mock.patch.object(sys, "stderr", new_callable=io.StringIO) as stderr:
            self.assertEqual(storage.main(), 1)
            self.assertIn("::error::Artifact cleanup failed: HTTP 403", stderr.getvalue())


class Workflows(unittest.TestCase):
    def test_upload_and_cleanup_contract(self):
        root = Path(__file__).resolve().parent.parent
        ci = (root / ".github/workflows/ci.yml").read_text()
        self.assertIn("upload_preview:\n", ci)
        self.assertIn("type: boolean\n        default: false", ci)
        preview = ci[ci.index("      - name: Upload requested book preview"):ci.index("\n  book-release-preflight:")]
        self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.upload_preview", preview)
        self.assertIn("retention-days: 1", preview)
        self.assertNotIn("lh-*.json", preview)
        self.assertEqual(ci.count("actions/upload-artifact@"), 2)
        self.assertNotIn("actions: write", ci)
        cleanup = (root / ".github/workflows/preview-cleanup.yml").read_text()
        self.assertIn("ref: main", cleanup)
        self.assertIn("cancel-in-progress: false", cleanup)
        self.assertNotIn("pull_request_target", cleanup)
        self.assertNotIn("secrets.", cleanup)
        release_workflow = (root / ".github/workflows/release.yml").read_text()
        staging = release_workflow[release_workflow.index("\n  cleanup:"):]
        self.assertIn("needs: [plan, build, publish, deploy]", staging)
        self.assertIn("needs.publish.outputs.published == 'true'", staging)
        self.assertIn("needs.deploy.result == 'success'", staging)
        self.assertEqual(release_workflow.count("retention-days: 7"), 2)
        build = release_workflow[release_workflow.index("\n  build:"):release_workflow.index("\n  publish:")]
        self.assertIn("editions: ${{ steps.editions.outputs.artifact-id }}", build)
        self.assertIn("notes: ${{ steps.notes.outputs.artifact-id }}", build)
        self.assertNotIn("artifact_storage", (root / ".github/workflows/deploy-swa.yml").read_text())


if __name__ == "__main__":
    unittest.main()
