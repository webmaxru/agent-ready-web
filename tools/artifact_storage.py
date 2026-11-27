"""Conservative Actions artifact cleanup. Execute cleanup only from trusted main."""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile

import book_release as release


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def preview_name(repo, ref, run_id, attempt):
    if not ref.startswith(("refs/heads/", "refs/tags/")):
        raise release.GateError("preview requires a full branch or tag ref")
    return f"book-preview-v1-{digest(repo)}-{digest(ref)}-{int(run_id)}-{int(attempt)}"


def collection(api, path, key):
    items = []
    for page in range(1, 101):
        data = api.request("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
        batch = data[key]
        if not isinstance(batch, list):
            raise release.GateError(f"invalid {key} response")
        items.extend(batch)
        if len(batch) < 100:
            return items
    raise release.GateError(f"pagination limit exceeded: {path}")


def producer(api, run_id, workflow, event):
    run = api.request("GET", f"actions/runs/{run_id}")
    if (run["id"] != run_id or run["repository"]["full_name"] != api.repo
            or run["head_repository"]["full_name"] != api.repo
            or run["path"] != f".github/workflows/{workflow}" or run["event"] != event):
        raise release.GateError("artifact producer identity mismatch")
    return run


def completed(run):
    return run["status"] == "completed" and run["conclusion"] == "success"


def preview_identity(api, run, artifact):
    for prefix in ("refs/heads/", "refs/tags/"):
        ref = prefix + run["head_branch"]
        if artifact["name"] == preview_name(api.repo, ref, run["id"], run["run_attempt"]):
            return ref
    return None


def artifact_matches(artifact, run):
    metadata = artifact.get("workflow_run") or {}
    return (metadata.get("id") == run["id"] and metadata.get("head_sha") == run["head_sha"]
            and metadata.get("head_branch") == run["head_branch"]
            and not artifact.get("expired", True) and type(artifact.get("id")) is int
            and artifact["id"] > 0)


def cleanup_preview(api, run_id):
    run = producer(api, run_id, "ci.yml", "workflow_dispatch")
    if not completed(run):
        raise release.GateError("replacement producer did not complete successfully; retaining previews")
    artifacts = collection(api, f"actions/runs/{run_id}/artifacts", "artifacts")
    jobs = collection(api, f"actions/runs/{run_id}/attempts/{run['run_attempt']}/jobs", "jobs")
    uploaded = any(step.get("name") == "Upload requested book preview" and step.get("conclusion") == "success"
                   for job in jobs for step in job.get("steps", []))
    matches = [(a, preview_identity(api, run, a)) for a in artifacts if artifact_matches(a, run)]
    matches = [(a, ref) for a, ref in matches if ref]
    if not matches:
        if uploaded:
            raise release.GateError("successful preview upload has no replacement identity")
        release.summary("No successful preview replacement; nothing deleted.")
        return
    if len(matches) != 1:
        raise release.GateError("ambiguous preview replacement identity")
    replacement, ref = matches[0]
    if not uploaded:
        raise release.GateError("replacement upload success is not confirmed")
    # Snapshot before deleting, so pagination cannot skip items after a deletion.
    candidates = collection(api, "actions/artifacts", "artifacts")
    namespace = f"book-preview-v1-{digest(api.repo)}-{digest(ref)}-"
    for artifact in candidates:
        if artifact["id"] == replacement["id"]:
            continue
        match = re.fullmatch(re.escape(namespace) + r"([1-9]\d*)-([1-9]\d*)", artifact["name"])
        if not match:
            continue
        old_id, attempt = map(int, match.groups())
        old = producer(api, old_id, "ci.yml", "workflow_dispatch")
        if (old_id == run_id or old_id >= run_id or not completed(old)
                or old["run_attempt"] != attempt or preview_identity(api, old, artifact) != ref
                or not artifact_matches(artifact, old)
                or artifact["created_at"] >= replacement["created_at"]):
            continue
        current = api.request("GET", f"actions/artifacts/{replacement['id']}")
        if current != replacement:
            raise release.GateError("replacement changed or expired; retaining older previews")
        # A re-run may have started while listing artifacts.
        fresh = producer(api, old_id, "ci.yml", "workflow_dispatch")
        if fresh != old or not completed(fresh):
            continue
        api.request("DELETE", f"actions/artifacts/{artifact['id']}")
        release.summary(f"Deleted superseded preview artifact {artifact['id']}.")


def cleanup_release(api, run_id, tag, sha, editions, notes):
    run = producer(api, run_id, "release.yml", "workflow_dispatch")
    if run["head_branch"] != "main":
        raise release.GateError("release cleanup requires a main producer")
    jobs = collection(api, f"actions/runs/{run_id}/attempts/{run['run_attempt']}/jobs", "jobs")
    required = {"Build the editions (exact merge commit, before tagging)",
                "Tag and publish the GitHub Release", "Deploy the web edition"}
    good = {job["name"] for job in jobs if job["conclusion"] == "success"}
    if not required <= good:
        raise release.GateError("publication or downstream consumer is incomplete")
    plan = release.release_plan(api, tag=tag, merge_sha=sha)
    if plan["recovery"] != "true":
        raise release.GateError("publication is not confirmed")
    # Reuse the publisher's format and SHA256 validator on actual published bytes.
    with tempfile.TemporaryDirectory() as folder:
        release.gh("release", "download", tag, "--repo", api.repo, "--dir", folder)
        release.check_files(tag, folder)
    artifacts = collection(api, f"actions/runs/{run_id}/artifacts", "artifacts")
    expected = {int(editions): f"editions-{tag}", int(notes): f"release-notes-{tag}"}
    if len(expected) != 2 or any(i <= 0 for i in expected):
        raise release.GateError("missing staging upload identity")
    selected = [a for a in artifacts if a["id"] in expected]
    if len(selected) != 2 or any(a["name"] != expected[a["id"]] or not artifact_matches(a, run)
                                 for a in selected):
        raise release.GateError("staging artifact identity mismatch")
    fresh = producer(api, run_id, "release.yml", "workflow_dispatch")
    if fresh["run_attempt"] != run["run_attempt"]:
        raise release.GateError("release was retried during cleanup")
    for artifact in selected:
        api.request("DELETE", f"actions/artifacts/{artifact['id']}")
        release.summary(f"Deleted published release staging artifact {artifact['id']}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("preview-name", "preview", "release"))
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--tag")
    parser.add_argument("--sha")
    parser.add_argument("--editions")
    parser.add_argument("--notes")
    args = parser.parse_args()
    try:
        if args.operation == "preview-name":
            release.output({"name": preview_name(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_REF"],
                                                 os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"])})
        elif args.operation == "preview":
            cleanup_preview(release.GitHub(), args.run_id)
        else:
            cleanup_release(release.GitHub(), args.run_id, args.tag, args.sha, args.editions, args.notes)
    except (release.GateError, release.APIError, OSError, ValueError, KeyError,
            TypeError, subprocess.CalledProcessError) as error:
        print(f"::error::Artifact cleanup failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
