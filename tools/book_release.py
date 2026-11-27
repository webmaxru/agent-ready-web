"""Approval controller and publisher for book releases (stdlib only). Run only from main.

  inspect       which open pull request (if any) is approved and ready to merge
  merge         SHA-conditional squash merge of that exact head, then dispatch release.yml
  release-plan  check the provenance of a merge (or an existing tag) before anything is written
  publish       annotated tag at the merge, draft release, upload every edition, publish
  deploy        dispatch deploy-swa.yml for the tag and report whether the web edition went live
  published-source  read-only production gate: only published stable book content may deploy

A manual merge bypasses this controller (see the catch-up scenario in RELEASING.md).
"""
from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_policy as policy  # noqa: E402
import validate_release as validator  # noqa: E402
from release_policy import OWNER, PolicyError  # noqa: E402

CHECK_WORKFLOW = "ci.yml"
CHECK_JOB = "Book release preflight"
RELEASE_WORKFLOW = "release.yml"
DEPLOY_WORKFLOW = "deploy-swa.yml"
DEPLOY_STEP = "Deploy to Azure Static Web Apps (production)"
SMOKE_STEP = "Smoke test"
SKIP_STEP = "Skip until the Static Web App exists"


class GateError(PolicyError):
    pass


class APIError(RuntimeError):
    pass


class GitHub:
    def __init__(self):
        self.repo = os.environ["GITHUB_REPOSITORY"]
        self.token = os.environ["GH_TOKEN"]
        self.api = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")

    def request(self, method, path, data=None, *, missing=False, api_version="2022-11-28"):
        body = json.dumps(data).encode() if data is not None else None
        request = urllib.request.Request(
            f"{self.api}/repos/{self.repo}/{path}", body, method=method,
            headers={"Authorization": f"Bearer {self.token}",
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json",
                     "X-GitHub-Api-Version": api_version},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            if missing and error.code == 404:
                return None
            raise APIError(f"GitHub {method} {path}: HTTP {error.code}") from error

    def pages(self, path):
        result = []
        for page in range(1, 101):
            batch = self.request("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise GateError(f"expected a list from {path}")
            result.extend(batch)
            if len(batch) < 100:
                return result
        raise GateError(f"pagination limit exceeded for {path}")


def gh(*args):
    subprocess.run([os.environ.get("BOOK_RELEASE_GH", "gh"), *args], check=True)


def full_sha(value):
    if not isinstance(value, str) or not policy.SHA_RE.fullmatch(value):
        raise GateError("expected a full lowercase 40-character commit SHA")
    return value


def output(values):
    for key, value in values.items():
        print(f"{key}={value}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            for key, value in values.items():
                handle.write(f"{key}={value}\n")


def summary(text):
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(text.rstrip() + "\n")


def file_at(api, path, ref):
    data = api.request("GET", f"contents/{path}?ref={ref}", missing=True)
    if data is None:
        return None
    if data.get("encoding") != "base64":
        raise GateError(f"cannot read {path} at {ref[:12]}")
    return base64.b64decode(data["content"]).decode("utf-8")


def version_at(api, ref):
    text = file_at(api, policy.BOOK_JSON, ref)
    try:
        return policy.parse_version(json.loads(text or "{}").get("version"))
    except ValueError as error:
        raise GateError(f"tools/book.json at {ref[:12]}: {error}") from error


def peel(api, ref):
    obj = ref["object"]
    for _ in range(10):
        if obj["type"] != "tag":
            break
        obj = api.request("GET", f"git/tags/{obj['sha']}")["object"]
    if obj["type"] != "commit":
        raise GateError("tag does not point at a commit")
    return full_sha(obj["sha"])


def is_ancestor(api, ancestor, commit):
    """True when ancestor is reachable from commit (unrelated histories give HTTP 404)."""
    data = api.request("GET", f"compare/{ancestor}...{commit}", missing=True)
    return bool(data) and data["merge_base_commit"]["sha"] == ancestor


def find_release(api, tag):
    """The release for tag, drafts included (GET releases/tags/... hides drafts)."""
    matches = [r for r in api.pages("releases") if r.get("tag_name") == tag]
    if len(matches) > 1:
        raise GateError(f"more than one release uses {tag}; resolve it by hand")
    return matches[0] if matches else None


def published_stable_tags(api):
    return [r["tag_name"] for r in api.pages("releases") if not r["draft"] and not r["prerelease"]
            and policy.TAG_RE.fullmatch(r["tag_name"]) and not policy.is_prerelease(r["tag_name"][1:])]


# ---------------------------------------------------------------- approval

def approval(pr, reviews, comments, timeline=()):
    """Whether the owner authorized this exact head. Only the owner ever authorizes.

    Someone else's PR: the owner's latest formal review is APPROVED on the head SHA.
    The owner's own PR (GitHub forbids self-approval): an unedited owner comment whose
    whole body is exactly "/release-book <head sha>".
    Barriers: a CHANGES_REQUESTED or DISMISSED review by any reviewer, and any
    review_dismissed timeline event at its own time. The authorization must come strictly
    after the latest barrier. COMMENTED reviews neither authorize nor revoke.
    """
    head = full_sha(pr["head"]["sha"])
    formal = sorted(
        (r for r in reviews if (r.get("user") or {}).get("login") == OWNER
         and r.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}),
        key=lambda r: (r.get("submitted_at") or "", r["id"]),
    )
    latest = formal[-1] if formal else None
    barrier = max((r.get("submitted_at") or "" for r in reviews
                   if r.get("state") in {"CHANGES_REQUESTED", "DISMISSED"}), default="")
    for event in timeline:
        if event.get("event") == "review_dismissed":
            barrier = max(barrier, event.get("created_at") or "")
    author = (pr.get("user") or {}).get("login")
    if author != OWNER:
        return bool(latest and latest["state"] == "APPROVED" and latest.get("commit_id") == head
                    and (latest.get("submitted_at") or "") > barrier)
    command = f"/release-book {head}"
    return any(
        (c.get("user") or {}).get("login") == OWNER and c.get("body") == command
        and c.get("updated_at") == c.get("created_at")
        and (c.get("created_at") or "") > barrier
        for c in comments
    )


# ---------------------------------------------------------------- candidate PR

def scope(api, number, pr, base, head):
    files = api.pages(f"pulls/{number}/files")
    if len(files) != pr["changed_files"]:
        raise GateError("the changed-file list is incomplete")
    paths = []
    for item in files:
        paths.append(item["filename"])
        if item.get("previous_filename"):
            paths.append(item["previous_filename"])
    keys = []
    if policy.BOOK_JSON in paths:
        keys = policy.changed_keys(file_at(api, policy.BOOK_JSON, base) or "{}",
                                   file_at(api, policy.BOOK_JSON, head) or "{}")
    result = policy.classify(paths, keys)
    if result["kind"] != "content":
        detail = ", ".join(result["tooling"][:5]) or "no content files"
        raise GateError(f"not a content-only update ({result['kind']}: {detail}); merge it by hand "
                        "after review, or split it")
    if not {policy.BOOK_JSON, policy.CHANGELOG} <= set(paths) or "version" not in keys:
        raise GateError("a content update must bump the version in tools/book.json and add its "
                        "CHANGELOG.md section")
    return result


def checks_passed(api, pr, head):
    runs = api.request("GET", f"actions/workflows/{CHECK_WORKFLOW}/runs?head_sha={head}"
                              "&event=pull_request&per_page=100")["workflow_runs"]
    matches = [r for r in runs if r["head_sha"] == head and r["head_branch"] == pr["head"]["ref"]
               and (r.get("head_repository") or {}).get("full_name") == api.repo]
    latest = max(matches, key=lambda r: r["id"], default=None)
    if not latest or latest["status"] != "completed" or latest["conclusion"] != "success":
        raise GateError(f"Book CI has not passed on {head[:12]}")
    jobs = api.request("GET", f"actions/runs/{latest['id']}/jobs?per_page=100")["jobs"]
    if not any(j["name"] == CHECK_JOB and j.get("conclusion") == "success" for j in jobs):
        raise GateError(f"'{CHECK_JOB}' has not passed on {head[:12]}")


def candidate(api, number, *, expected_head=None, expected_base=None, checks=False):
    pr = api.request("GET", f"pulls/{number}")
    head_repo = pr["head"].get("repo") or {}
    if (pr["base"]["ref"] != "main" or pr["base"]["repo"]["full_name"] != api.repo
            or head_repo.get("full_name") != api.repo or pr.get("draft")
            or (pr["state"] != "open" and not pr.get("merged"))):
        raise GateError("only open, non-draft pull requests from this repository into main qualify")
    head = full_sha(pr["head"]["sha"])
    if expected_head and head != full_sha(expected_head):
        raise GateError("the pull request head changed after preflight")
    base = full_sha(pr["base"]["sha"])
    if pr.get("merged"):
        if (pr.get("merged_by") or {}).get("login") != "github-actions[bot]":
            raise GateError("a manual merge bypasses the controller; open a catch-up content PR")
        commit = api.request("GET", f"git/commits/{full_sha(pr['merge_commit_sha'])}")
        base = full_sha(commit["parents"][0]["sha"])
    elif pr.get("mergeable") is not True:
        raise GateError("GitHub reports the pull request as not mergeable (or not computed yet)")
    if expected_base and base != full_sha(expected_base):
        raise GateError("the pull request base changed after preflight")
    scope(api, number, pr, base, head)
    if not approval(pr, api.pages(f"pulls/{number}/reviews"), api.pages(f"issues/{number}/comments"),
                    api.pages(f"issues/{number}/timeline")):
        raise GateError("no current owner approval of this exact head")
    if not pr.get("merged"):
        main = full_sha(api.request("GET", "git/ref/heads/main")["object"]["sha"])
        if not is_ancestor(api, main, head):
            raise GateError("the head is behind main; update the branch and approve again")
        if base != main:
            raise GateError("main moved during preflight; update the branch and approve again")
    if checks:
        checks_passed(api, pr, head)
    tag = "v" + version_at(api, head)
    fresh = api.request("GET", f"pulls/{number}")
    if fresh["head"]["sha"] != head or fresh["base"]["sha"] != pr["base"]["sha"]:
        raise GateError("the pull request changed during authorization")
    return pr, head, base, tag


# ---------------------------------------------------------------- inspect and merge

RELEASE_COMMAND = re.compile(r"/release-book [0-9a-f]{40}")


def event_numbers(api, event):
    if "issue" in event and "pull_request" in event["issue"]:
        comment = event.get("comment") or {}
        if ((comment.get("user") or {}).get("login") == OWNER
                and RELEASE_COMMAND.fullmatch(comment.get("body") or "")):
            return [event["issue"]["number"]]
        return []
    if (event.get("inputs") or {}).get("pr"):
        return [int(event["inputs"]["pr"])]
    if event.get("schedule"):
        # A fixed cap bounds API use; older PRs can be re-checked by dispatch with a PR number.
        return [p["number"] for p in api.request(
            "GET", "pulls?state=open&base=main&sort=updated&direction=desc&per_page=30")]
    run = event.get("workflow_run") or {}
    if (run.get("head_repository") or {}).get("full_name") != api.repo:
        return []
    branch = run.get("head_branch")
    if not isinstance(branch, str) or not branch or branch == "main":
        return []
    head = urllib.parse.quote(f"{api.repo.split('/')[0]}:{branch}", safe="")
    return [p["number"] for p in api.pages(f"pulls?state=open&base=main&head={head}")]


def inspect(api, event):
    eligible = []
    for number in event_numbers(api, event):
        try:
            pr, head, base, tag = candidate(api, number, checks=True)
            if pr.get("merged"):
                continue
        except (GateError, PolicyError) as error:
            print(f"PR #{number} not eligible: {error}", file=sys.stderr)
            continue
        eligible.append({"pr": str(number), "head": head, "base": base, "tag": tag})
    if len(eligible) > 1 and not event.get("schedule"):
        raise GateError("ambiguous signal; dispatch with one explicit PR number")
    if eligible:
        # Rotate through a backlog rather than retrying one failing PR forever.
        index = int(datetime.datetime.now(datetime.timezone.utc).timestamp() // 1800) % len(eligible)
        output({"eligible": "true", **eligible[index]})
    else:
        output({"eligible": "false"})


def merge(api, number, head, base):
    pr, _, _, tag = candidate(api, number, expected_head=head, expected_base=base, checks=True)
    if pr.get("merged"):
        merge_sha = full_sha(pr["merge_commit_sha"])
    else:
        main = api.request("GET", "git/ref/heads/main")["object"]["sha"]
        if main != base:
            raise GateError("main moved during preflight; update the branch and approve again")
        result = api.request("PUT", f"pulls/{number}/merge", {
            "sha": head, "merge_method": "squash", "commit_title": f"{pr['title']} (#{number})"})
        if not result or not result.get("merged"):
            raise GateError("GitHub refused the SHA-conditional merge")
        merge_sha = full_sha(result["sha"])
    # A merge made with GITHUB_TOKEN starts no push workflows, so the release is dispatched.
    api.request("POST", f"actions/workflows/{RELEASE_WORKFLOW}/dispatches", {
        "ref": "main", "inputs": {"pr": str(number), "head_sha": head, "base_sha": base,
                                  "merge_sha": merge_sha, "tag": tag}})
    output({"merge_sha": merge_sha, "tag": tag})


# ---------------------------------------------------------------- release plan

def release_plan(api, *, number=None, head=None, base=None, merge_sha=None, tag=None):
    """Read-only provenance check. Writes nothing; fails on any mismatch."""
    if tag:
        policy.tag_version(tag)
    if not number:
        if not tag and not merge_sha:
            raise GateError("give the approved PR (pr, merge_sha) or an existing release tag")
        ref = api.request("GET", f"git/ref/tags/{tag}", missing=True) if tag else None
        if not ref and not merge_sha:
            raise GateError(f"{tag} does not exist; recover with the PR number instead")
        if ref:
            tagged = peel(api, ref)
            if merge_sha and full_sha(merge_sha) != tagged:
                raise GateError(f"{tag} points at another commit")
            merge_sha = tagged
        merge_sha = full_sha(merge_sha)
        matches = [p for p in api.pages(f"commits/{merge_sha}/pulls")
                   if p.get("merged_at") and p.get("merge_commit_sha") == merge_sha]
        if len(matches) != 1:
            raise GateError(f"{tag} is not the merge of exactly one approved pull request")
        number = matches[0]["number"]
    pr, actual_head, actual_base, head_tag = candidate(
        api, int(number), expected_head=head, expected_base=base, checks=True)
    if not pr.get("merged"):
        raise GateError(f"PR #{number} is not merged")
    merge_sha = full_sha(merge_sha or pr["merge_commit_sha"])
    if pr["merge_commit_sha"] != merge_sha:
        raise GateError("the release commit is not this pull request's merge")
    commit = api.request("GET", f"git/commits/{merge_sha}")
    source = api.request("GET", f"git/commits/{actual_head}")
    if (len(commit["parents"]) != 1 or commit["parents"][0]["sha"] != actual_base
            or source["tree"]["sha"] != commit["tree"]["sha"]):
        raise GateError("the merge is not a squash of the approved head onto the preflight base")
    if not is_ancestor(api, merge_sha, "main"):
        raise GateError("the release commit is not on main")
    version = version_at(api, merge_sha)
    expected = f"v{version}"
    if expected != head_tag or (tag and tag != expected):
        raise GateError(f"the tag does not match tools/book.json at the merge ({expected})")
    tag = expected
    names = [t["name"] for t in api.pages("tags")]
    previous = policy.previous_release(names, version)
    if previous:
        prev_sha = peel(api, api.request("GET", f"git/ref/tags/{previous}"))
        if not is_ancestor(api, prev_sha, merge_sha):
            raise GateError(f"the previous release {previous} is not an ancestor of the merge")
    elif policy.latest_stable(names):
        raise GateError(f"{tag} is lower than every existing release")
    ref = api.request("GET", f"git/ref/tags/{tag}", missing=True)
    if ref and peel(api, ref) != merge_sha:
        raise GateError(f"{tag} already points at another commit; tags are never moved")
    release = find_release(api, tag)
    recovery = "false"
    if ref or release:
        if not ref or not release or release["draft"]:
            raise GateError(f"{tag} is a partial release (tag-only, missing tag or draft); "
                            "left unchanged: release a new version")
        missing = policy.missing_assets(tag, api.pages(f"releases/{release['id']}/assets"))
        if missing:
            raise GateError(f"{tag} is published but incomplete (missing {', '.join(missing)}); "
                            "published files are never overwritten: release a new patch version")
        recovery = "true"
        summary(f"{tag} is already published with every edition; nothing to do.")
    values = {"merge_sha": merge_sha, "head": actual_head, "base": actual_base, "pr": str(number),
              "tag": tag, "version": version, "prerelease": str(policy.is_prerelease(version)).lower(),
              "previous": previous or "", "recovery": recovery}
    output(values)
    return values


# ---------------------------------------------------------------- publish

MAGIC = {".pdf": b"%PDF-", ".epub": b"PK\x03\x04", ".zip": b"PK\x03\x04"}


def check_files(tag, folder):
    folder = Path(folder)
    names = policy.expected_assets(tag)
    for name in names:
        path = folder / name
        if not path.is_file() or path.stat().st_size == 0:
            raise GateError(f"missing or empty release file {name}")
        magic = MAGIC.get(path.suffix)
        if magic and path.read_bytes()[:len(magic)] != magic:
            raise GateError(f"{name} is not a valid {path.suffix} file")
    sums = {}
    for line in (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            sums[name.lstrip("*")] = digest
    for name in names[:-1]:
        if sums.get(name) != hashlib.sha256((folder / name).read_bytes()).hexdigest():
            raise GateError(f"SHA256SUMS.txt does not match {name}")
    return [str(folder / n) for n in names]


def publish(api, tag, sha, folder, notes):
    version = policy.tag_version(tag)
    full_sha(sha)
    plan = release_plan(api, tag=tag, merge_sha=sha)
    if plan["recovery"] == "true":
        summary(f"{tag} was already published with every edition; left unchanged.")
        output({"published": "false"})
        return
    files = check_files(tag, folder)
    if not os.path.isfile(notes) or not os.path.getsize(notes):
        raise GateError("missing release notes")
    latest = policy.is_newest_stable(version, published_stable_tags(api))
    pre = ["--prerelease"] if policy.is_prerelease(version) else []
    obj = api.request("POST", "git/tags", {"tag": tag, "message": tag, "object": sha, "type": "commit"})
    api.request("POST", "git/refs", {"ref": f"refs/tags/{tag}", "sha": obj["sha"]})
    print(f"Created the annotated tag {tag} at {sha}.")
    gh("release", "create", tag, "--verify-tag", "--draft", "--latest=false",
       "--title", tag, "--notes-file", notes, *pre)
    gh("release", "upload", tag, *files)
    release = find_release(api, tag)
    if not release or not release["draft"]:
        raise GateError(f"the draft release for {tag} disappeared or was published by someone else")
    missing = policy.missing_assets(tag, api.pages(f"releases/{release['id']}/assets"))
    if missing:
        raise GateError(f"upload incomplete ({', '.join(missing)}); the release stays a draft")
    gh("release", "edit", tag, "--draft=false", f"--latest={'true' if latest else 'false'}", *pre)
    summary(f"Published {tag} at `{sha[:12]}` with {len(files)} files"
            f"{' (Latest)' if latest else ''}{' as a pre-release' if pre else ''}.")
    output({"published": "true"})


# ---------------------------------------------------------------- deploy

def published_source(api, event, root):
    """Resolve production to an immutable SHA; compare content with main's trusted policy."""
    kind = event.get("event_name")
    tags = published_stable_tags(api)
    if kind == "push":
        if event.get("ref") != "refs/heads/main":
            raise GateError("production push must target main")
        tag = policy.latest_stable(tags)
        if not tag:
            summary("No published stable edition; production deploy skipped.")
            output({"eligible": "false"})
            return
        target = full_sha(event.get("after"))
    elif kind == "workflow_dispatch":
        inputs = event.get("inputs") or {}
        ref = inputs.get("ref")
        if isinstance(ref, str) and policy.TAG_RE.fullmatch(ref):
            tag = ref
        elif isinstance(ref, str) and policy.SHA_RE.fullmatch(ref):
            matches = [t for t in tags if peel(api, api.request("GET", f"git/ref/tags/{t}")) == ref]
            tag = policy.latest_stable(matches)
        else:
            raise GateError("give a published stable release tag or full SHA, never a branch")
        if tag not in tags:
            raise GateError(f"{ref} is not a published stable release")
        if inputs.get("latest_only") in ("true", True) and tag != policy.latest_stable(tags):
            summary(f"{tag} was superseded before deployment; production left unchanged.")
            output({"eligible": "false"})
            return
        target = None
    else:
        raise GateError("unsupported production deploy event")
    released = peel(api, api.request("GET", f"git/ref/tags/{tag}"))
    if target:
        changed = validator.changes(root, released, target)
        content = [path for path, _ in changed if policy.is_content(path) or path == policy.CHANGELOG]
        if policy.BOOK_JSON in {path for path, _ in changed}:
            keys = policy.changed_keys(validator.show(root, released, policy.BOOK_JSON),
                                       validator.show(root, target, policy.BOOK_JSON))
            if set(keys) & policy.METADATA_KEYS:
                content.append(policy.BOOK_JSON)
        if content:
            summary(f"Unreleased book content differs from {tag}; production deploy skipped.")
            output({"eligible": "false"})
            return
    output({"eligible": "true", "sha": target or released, "tag": tag})


def deploy(api, tag, *, timeout=1500, interval=15):
    version = policy.tag_version(tag)
    if policy.is_prerelease(version):
        summary(f"## Web edition not deployed\n\n{tag} is a pre-release; the web edition keeps the latest stable release.")
        return 0
    tags = published_stable_tags(api)
    if tag not in tags:
        raise GateError(f"{tag} is not a published stable release; nothing dispatched")
    latest = policy.latest_stable(tags)
    if tag != latest:
        summary(f"## Web edition not deployed\n\n{tag} is older than {latest}; production left unchanged.")
        return 0
    if not api.request("GET", f"actions/workflows/{DEPLOY_WORKFLOW}", missing=True):
        summary(f"## Web edition NOT deployed\n\nThere is no {DEPLOY_WORKFLOW} workflow.")
        print(f"::warning title=Web edition not deployed::no {DEPLOY_WORKFLOW} workflow")
        return 1
    receipt = api.request("POST", f"actions/workflows/{DEPLOY_WORKFLOW}/dispatches",
                          {"ref": "main", "inputs": {"ref": tag, "latest_only": "true"}},
                          api_version="2026-03-10")
    run_id = receipt.get("workflow_run_id") if isinstance(receipt, dict) else None
    if type(run_id) is not int or run_id <= 0:
        summary(f"## Web edition: deploy not confirmed\n\nNo run ID returned for {tag}; "
                "inspect Actions before retrying. No second dispatch was sent.")
        return 1
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        run = api.request("GET", f"actions/runs/{run_id}", missing=True)
        if run and run["id"] != run_id:
            raise GateError(f"deploy not confirmed: expected run {run_id}, got {run['id']}")
        if run and run["status"] == "completed":
            break
        time.sleep(interval)
    else:
        summary(f"## Web edition: deploy not confirmed\n\nRun {run_id} did not finish in time. "
                "Inspect it before retrying.")
        return 1
    if run["conclusion"] != "success":
        summary(f"## Web edition NOT deployed\n\nThe deploy of {tag} failed: {run['html_url']}")
        print(f"::error title=Web edition not deployed::the deploy run failed: {run['html_url']}")
        return 1
    jobs = api.request("GET", f"actions/runs/{run_id}/jobs?per_page=100")["jobs"]
    passed = [{s["name"] for s in job.get("steps", []) if s.get("conclusion") == "success"}
              for job in jobs if job.get("conclusion") == "success"]
    if any({DEPLOY_STEP, SMOKE_STEP} <= steps for steps in passed):
        summary(f"## Web edition deployed\n\n{tag} is live. Run: {run['html_url']}")
        return 0
    if any(SKIP_STEP in steps for steps in passed):
        summary(f"## Web edition NOT deployed\n\nThe GitHub Release {tag} is published, but the web "
                "edition was **not** deployed: the repository secret `AZURE_STATIC_WEB_APPS_API_TOKEN` "
                "is missing. The owner must run `./infra/deploy.sh` (see DEPLOY.md), then "
                f"**Actions → deploy-swa → Run workflow** with ref `{tag}`. Run: {run['html_url']}")
        print("::warning title=Web edition NOT deployed::AZURE_STATIC_WEB_APPS_API_TOKEN is missing; "
              "run ./infra/deploy.sh (see DEPLOY.md)")
        return 1
    summary(f"## Web edition: deploy not confirmed\n\nUpload and smoke test did not both succeed "
            f"for {tag}: {run['html_url']}")
    return 1


# ---------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("operation", choices=["inspect", "merge", "release-plan", "publish", "deploy",
                                              "published-source"])
    parser.add_argument("--event")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--head")
    parser.add_argument("--base")
    parser.add_argument("--merge-sha")
    parser.add_argument("--tag")
    parser.add_argument("--assets")
    parser.add_argument("--notes")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--timeout", type=int, default=1500)
    parser.add_argument("--interval", type=int, default=15)
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        api = GitHub()
        if args.operation in {"inspect", "published-source"}:
            with open(args.event or os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as handle:
                event = json.load(handle)
            if args.operation == "inspect":
                inspect(api, event)
            else:
                event["event_name"] = os.environ["GITHUB_EVENT_NAME"]
                published_source(api, event, args.root)
        elif args.operation == "merge":
            merge(api, args.pr, full_sha(args.head), full_sha(args.base))
        elif args.operation == "release-plan":
            release_plan(api, number=args.pr, head=args.head or None, base=args.base or None,
                         merge_sha=args.merge_sha or None, tag=args.tag or None)
        elif args.operation == "publish":
            publish(api, args.tag, args.merge_sha, args.assets, args.notes)
        else:
            return deploy(api, args.tag, timeout=args.timeout, interval=args.interval)
    except (APIError, PolicyError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"::error::book release: {error}" if os.environ.get("GITHUB_ACTIONS") == "true"
              else f"book release: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
