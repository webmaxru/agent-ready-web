"""An in-memory GitHub REST API (only what tools/book_release.py uses) and a gh shim.

The controller talks to it over real HTTP (GITHUB_API_URL), and `gh release ...` calls go
through a shim script (BOOK_RELEASE_GH) that forwards its arguments to the same server, so a
test can run inspect -> merge -> release-plan -> publish -> deploy end to end.
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
import sys
import tempfile
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = "webmaxru/agent-ready-web"
OWNER = "webmaxru"


def sha(*parts):
    return hashlib.sha1("\0".join(map(str, parts)).encode()).hexdigest()


def now(offset=0):
    t = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=offset)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


class State:
    def __init__(self):
        self.commits = {}      # sha -> {"parents": [...], "tree": str, "files": {path: text}}
        self.refs = {}         # "heads/main", "tags/v1.0.0" -> {"type": "commit"|"tag", "sha": ...}
        self.tag_objects = {}  # sha -> {"type": "commit", "sha": ...}
        self.pulls = {}        # number -> pr dict (plus private "_files")
        self.reviews = {}
        self.comments = {}
        self.timeline = {}
        self.releases = []
        self.runs = []
        self.jobs = {}
        self.dispatches = []   # (workflow, payload)
        self.gh_calls = []
        self.writes = []
        self.merge_requests = []
        self.deploy_outcome = "skipped"
        self.next_id = 1000
        self.lock = threading.Lock()

    def new_id(self):
        self.next_id += 1
        return self.next_id

    # ------------------------------------------------------------ git model
    def commit(self, files, parents=()):
        tree = sha("tree", json.dumps(files, sort_keys=True))
        commit_sha = sha("commit", tree, *parents, len(self.commits))
        self.commits[commit_sha] = {"parents": list(parents), "tree": tree, "files": dict(files)}
        return commit_sha

    def resolve(self, ref):
        if ref in self.commits:
            return ref
        for name in (f"heads/{ref}", f"tags/{ref}"):
            if name in self.refs:
                obj = self.refs[name]
                while obj["type"] == "tag":
                    obj = self.tag_objects[obj["sha"]]
                return obj["sha"]
        raise KeyError(ref)

    def ancestors(self, commit_sha):
        seen, queue = [], [commit_sha]
        while queue:
            c = queue.pop(0)
            if c in seen:
                continue
            seen.append(c)
            queue.extend(self.commits[c]["parents"])
        return seen

    def merge_base(self, a, b):
        mine = set(self.ancestors(a))
        return next(c for c in self.ancestors(b) if c in mine)

    def tag(self, name, commit_sha, annotated=True):
        if annotated:
            obj = sha("tagobj", name, commit_sha)
            self.tag_objects[obj] = {"type": "commit", "sha": commit_sha}
            self.refs[f"tags/{name}"] = {"type": "tag", "sha": obj}
        else:
            self.refs[f"tags/{name}"] = {"type": "commit", "sha": commit_sha}

    # ------------------------------------------------------------ PRs
    def pull(self, number, head, base_sha, *, author=OWNER, branch="update/chapter-1", draft=False,
             mergeable=True, same_repo=True):
        files = self.commits[head]["files"]
        base_files = self.commits[base_sha]["files"]
        changed = sorted(p for p in set(files) | set(base_files) if files.get(p) != base_files.get(p))
        self.pulls[number] = {
            "number": number, "title": f"Book update {number}", "state": "open", "draft": draft,
            "merged": False, "mergeable": mergeable, "merge_commit_sha": None, "merged_at": None,
            "user": {"login": author}, "changed_files": len(changed),
            "head": {"sha": head, "ref": branch,
                     "repo": {"full_name": REPO if same_repo else "someone/fork"}},
            "base": {"sha": base_sha, "ref": "main", "repo": {"full_name": REPO}},
            "_files": [{"filename": p} for p in changed],
        }
        self.reviews.setdefault(number, [])
        self.comments.setdefault(number, [])
        self.timeline.setdefault(number, [])
        return self.pulls[number]

    def review(self, number, state, commit_id, *, user=OWNER, at=None):
        review = {"id": self.new_id(), "user": {"login": user}, "state": state,
                  "commit_id": commit_id, "submitted_at": at or now()}
        self.reviews[number].append(review)
        return review

    def comment(self, number, body, *, user=OWNER, at=None):
        at = at or now()
        self.comments[number].append({"id": self.new_id(), "user": {"login": user}, "body": body,
                                      "created_at": at, "updated_at": at})

    def ci_run(self, head, branch="update/chapter-1", *, conclusion="success", job_conclusion="success",
               job="Book release preflight"):
        run_id = self.new_id()
        self.runs.append({"id": run_id, "workflow": "ci.yml", "event": "pull_request", "head_sha": head,
                          "head_branch": branch, "head_repository": {"full_name": REPO},
                          "status": "completed", "conclusion": conclusion, "created_at": now(),
                          "html_url": f"https://example.test/runs/{run_id}"})
        self.jobs[run_id] = [{"name": "Release checks", "conclusion": "success", "steps": []},
                             {"name": "build", "conclusion": "success", "steps": []},
                             {"name": job, "conclusion": job_conclusion, "steps": []}]

    # ------------------------------------------------------------ gh shim
    def gh(self, args):
        self.gh_calls.append(args)
        if args[0] != "release":
            raise ValueError(args)
        verb, tag, rest = args[1], args[2], args[3:]
        release = next((r for r in self.releases if r["tag_name"] == tag), None)
        if verb == "create":
            if release:
                raise ValueError("release exists")
            if f"tags/{tag}" not in self.refs:
                raise ValueError("--verify-tag: tag missing")
            self.releases.append({"id": self.new_id(), "tag_name": tag, "draft": "--draft" in rest,
                                  "prerelease": "--prerelease" in rest, "assets": [], "latest": False})
        elif verb == "upload":
            if "--clobber" in rest:
                raise ValueError("asset replacement is forbidden")
            if not release:
                raise ValueError("no release")
            if not release["draft"]:
                raise ValueError("uploading to a published release")
            for item in rest:
                if item.startswith("--"):
                    continue
                name = os.path.basename(item)
                if any(a["name"] == name for a in release["assets"]):
                    raise ValueError("asset already exists")
                release["assets"].append({"name": name, "state": "uploaded", "size": os.path.getsize(item)})
        elif verb == "edit":
            if "--draft=false" in rest:
                release["draft"] = False
            if "--latest=true" in rest:
                for r in self.releases:
                    r["latest"] = False
                release["latest"] = True
        else:
            raise ValueError(args)

    # ------------------------------------------------------------ deploy-swa
    def deploy_dispatched(self):
        run_id = self.new_id()
        outcome = self.deploy_outcome
        run = {"id": run_id, "workflow": "deploy-swa.yml", "event": "workflow_dispatch", "head_sha": "",
               "head_branch": "main", "created_at": now(),
               "status": "in_progress" if outcome == "hang" else "completed",
               "conclusion": None if outcome == "hang" else ("failure" if outcome == "failed" else "success"),
               "html_url": f"https://example.test/runs/{run_id}"}
        self.runs.append(run)
        skip = "success" if outcome == "skipped" else "skipped"
        upload = ("success" if outcome in {"deployed", "smoke-skipped"}
                  else "failure" if outcome == "failed" else "skipped")
        smoke = "success" if outcome in {"deployed", "upload-skipped"} else "skipped"
        self.jobs[run_id] = [{"name": "deploy", "conclusion": run["conclusion"], "steps": [
            {"name": "Skip until the Static Web App exists", "conclusion": skip},
            {"name": "Deploy to Azure Static Web Apps (production)", "conclusion": upload},
            {"name": "Smoke test", "conclusion": smoke}]}]
        return run


class Handler(BaseHTTPRequestHandler):
    state: State = None

    def log_message(self, *args):
        pass

    def _send(self, code, data=None):
        raw = b"" if data is None else json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(length) or b"null")

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def _route(self, method):
        with self.state.lock:
            if method != "GET":
                self.state.writes.append((method, self.path))
            try:
                code, data = self.route(method)
            except (KeyError, StopIteration):
                code, data = 404, {"message": "Not Found"}
        self._send(code, data)

    def route(self, method):
        s = self.state
        url = urllib.parse.urlsplit(self.path)
        query = dict(urllib.parse.parse_qsl(url.query))
        page, per_page = int(query.get("page", 1)), int(query.get("per_page", 30))

        def paged(items):
            return 200, items[(page - 1) * per_page: page * per_page]

        if url.path == "/_gh":
            try:
                s.gh(self._body())
            except ValueError as error:
                return 422, {"message": str(error)}
            return 200, {}
        prefix = f"/repos/{REPO}/"
        if not url.path.startswith(prefix):
            return 404, {}
        path = urllib.parse.unquote(url.path[len(prefix):])
        parts = path.split("/")

        if method == "GET" and parts == ["pulls"]:
            prs = [p for p in s.pulls.values() if p["state"] == query.get("state", "open")]
            if "head" in query:
                branch = query["head"].split(":", 1)[1]
                prs = [p for p in prs if p["head"]["ref"] == branch]
            return paged([{k: v for k, v in p.items() if not k.startswith("_")} for p in prs])
        if parts[0] == "pulls":
            pr = s.pulls[int(parts[1])]
            if len(parts) == 2 and method == "GET":
                return 200, {k: v for k, v in pr.items() if not k.startswith("_")}
            if parts[2] == "files":
                return paged(pr["_files"])
            if parts[2] == "reviews":
                return paged(s.reviews[pr["number"]])
            if parts[2] == "merge" and method == "PUT":
                body = self._body()
                s.merge_requests.append(body)
                if body.get("merge_method") != "squash":
                    return 422, {"message": "Only squash merges are allowed"}
                if pr["state"] != "open" or body.get("sha") != pr["head"]["sha"]:
                    return 409, {"message": "Head branch was modified"}
                main = s.resolve("main")
                merge = s.commit(s.commits[pr["head"]["sha"]]["files"], [main])
                s.commits[merge]["tree"] = s.commits[pr["head"]["sha"]]["tree"]
                s.refs["heads/main"] = {"type": "commit", "sha": merge}
                pr.update(state="closed", merged=True, merge_commit_sha=merge, merged_at=now(), mergeable=None,
                          merged_by={"login": "github-actions[bot]"})
                return 200, {"merged": True, "sha": merge}
        if parts[0] == "issues" and parts[2] == "comments":
            return paged(s.comments[int(parts[1])])
        if parts[0] == "issues" and parts[2] == "timeline":
            return paged(s.timeline[int(parts[1])])
        if parts[0] == "compare":
            a, b = parts[1].split("...")
            return 200, {"merge_base_commit": {"sha": s.merge_base(s.resolve(a), s.resolve(b))}}
        if parts[0] == "contents":
            files = s.commits[s.resolve(query["ref"])]["files"]
            name = "/".join(parts[1:])
            if name not in files:
                return 404, {}
            return 200, {"encoding": "base64", "content": base64.b64encode(files[name].encode()).decode()}
        if parts[0] == "commits" and parts[2] == "pulls":
            return paged([{k: v for k, v in p.items() if not k.startswith("_")}
                          for p in s.pulls.values() if p["merge_commit_sha"] == parts[1]])
        if parts[:2] == ["git", "commits"]:
            c = s.commits[parts[2]]
            return 200, {"sha": parts[2], "tree": {"sha": c["tree"]},
                         "parents": [{"sha": p} for p in c["parents"]]}
        if parts[:2] == ["git", "ref"]:
            name = "/".join(parts[2:])
            return 200, {"ref": f"refs/{name}", "object": dict(s.refs[name])}
        if parts[:2] == ["git", "tags"] and method == "GET":
            return 200, {"object": dict(s.tag_objects[parts[2]])}
        if parts[:2] == ["git", "tags"] and method == "POST":
            body = self._body()
            obj = sha("tagobj", body["tag"], body["object"])
            s.tag_objects[obj] = {"type": "commit", "sha": body["object"]}
            return 201, {"sha": obj}
        if parts[:2] == ["git", "refs"] and method == "POST":
            body = self._body()
            name = body["ref"][len("refs/"):]
            if name in s.refs:
                return 422, {"message": "Reference already exists"}
            s.refs[name] = {"type": "tag" if body["sha"] in s.tag_objects else "commit", "sha": body["sha"]}
            return 201, {}
        if parts == ["tags"]:
            return paged([{"name": n[len("tags/"):]} for n in s.refs if n.startswith("tags/")])
        if parts == ["releases"]:
            return paged([{k: v for k, v in r.items() if k != "assets"} for r in s.releases])
        if parts[0] == "releases" and parts[2] == "assets":
            release = next(r for r in s.releases if r["id"] == int(parts[1]))
            return paged(release["assets"])
        if parts[:2] == ["actions", "workflows"]:
            workflow = parts[2]
            if len(parts) == 3:
                known = ("ci.yml", "release.yml", "deploy-swa.yml")
                return (200, {"path": workflow}) if workflow in known else (404, {})
            if parts[3] == "dispatches":
                body = self._body()
                s.dispatches.append((workflow, body))
                if workflow == "deploy-swa.yml":
                    run = s.deploy_dispatched()
                    if self.headers.get("X-GitHub-Api-Version") == "2026-03-10":
                        return 200, {"workflow_run_id": run["id"], "html_url": run["html_url"],
                                     "run_url": f"http://{self.headers['Host']}{prefix}actions/runs/{run['id']}"}
                return 204, None
            if parts[3] == "runs":
                runs = [r for r in s.runs if r["workflow"] == workflow
                        and (not query.get("head_sha") or r["head_sha"] == query["head_sha"])
                        and (not query.get("event") or r["event"] == query["event"])]
                return 200, {"workflow_runs": runs[::-1]}
        if parts[:2] == ["actions", "runs"]:
            if len(parts) == 3:
                return 200, next(r for r in s.runs if r["id"] == int(parts[2]))
            if parts[3] == "jobs":
                return 200, {"jobs": s.jobs[int(parts[2])]}
        return 404, {"message": f"unhandled {method} {path}"}


SHIM = r'''
import json, os, sys, urllib.error, urllib.request
data = json.dumps([os.path.abspath(a) if os.path.isfile(a) else a for a in sys.argv[1:]]).encode()
request = urllib.request.Request(os.environ["FAKE_GH_URL"] + "/_gh", data, method="POST",
                                 headers={"Content-Type": "application/json"})
try:
    urllib.request.urlopen(request, timeout=30).read()
except urllib.error.HTTPError as error:
    sys.stderr.write("gh shim: " + error.read().decode() + "\n")
    sys.exit(1)
'''


class FakeGitHub:
    """Start a server; .env() gives the environment the controller needs."""

    def __enter__(self):
        self.state = State()
        handler = type("BoundHandler", (Handler,), {"state": self.state})
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name)
        (tmp / "gh_shim.py").write_text(SHIM, encoding="utf-8")
        if os.name == "nt":
            self.gh = tmp / "gh.cmd"
            self.gh.write_text(f'@"{sys.executable}" "{tmp / "gh_shim.py"}" %*\n', encoding="utf-8")
        else:
            self.gh = tmp / "gh"
            self.gh.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{tmp / "gh_shim.py"}" "$@"\n',
                               encoding="utf-8")
            self.gh.chmod(0o755)
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def env(self, **extra):
        env = {"GITHUB_REPOSITORY": REPO, "GH_TOKEN": "test-token", "GITHUB_API_URL": self.url,
               "BOOK_RELEASE_GH": str(self.gh), "FAKE_GH_URL": self.url}
        env.update(extra)
        return env
