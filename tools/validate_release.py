"""Release checks for a checkout of this book (stdlib only). See RELEASING.md.

  change  --root DIR --base-ref REF    a pull request's changes against its base
  release --root DIR --tag vX.Y.Z --sha SHA [--allow-existing-tag]
                                       a commit that is about to be released as tag
  notes   --root DIR --tag vX.Y.Z --repo OWNER/NAME
                                       print the release notes from CHANGELOG.md

The approval controller and the release workflow run this file from main (trusted) against
the exact commit under review, so a pull request can't weaken its own checks.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_policy as policy  # noqa: E402
from release_policy import PolicyError  # noqa: E402

ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def git(root, *args):
    try:
        out = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                             text=True, encoding="utf-8")
    except FileNotFoundError as error:
        raise PolicyError("git is required") from error
    except subprocess.CalledProcessError as error:
        raise PolicyError(f"git {' '.join(args)}: {error.stderr.strip()}") from error
    return out.stdout


def commit_of(root, ref):
    return git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").strip()


def show(root, rev, path):
    """A file at a revision, or None if it doesn't exist there."""
    listed = git(root, "ls-tree", "--name-only", rev, "--", path).strip()
    return git(root, "show", f"{rev}:{path}") if listed else None


def tags(root):
    return git(root, "tag", "--list", "v*").split()


def book(text, where):
    try:
        data = json.loads(text or "")
    except ValueError as error:
        raise PolicyError(f"{where}: tools/book.json is not valid JSON ({error})") from error
    if not isinstance(data, dict):
        raise PolicyError(f"{where}: tools/book.json must be a JSON object")
    return data


def changes(root, base, head="HEAD"):
    """[(path, new_mode)] changed between base and head, renames split into delete + add."""
    out = git(root, "diff", "--raw", "--no-renames", "--no-abbrev", "-z", base, head)
    fields = out.split("\0")
    result = []
    i = 0
    while i < len(fields) - 1:
        meta, path = fields[i], fields[i + 1]
        i += 2
        if not meta.startswith(":"):
            raise PolicyError(f"unexpected git diff output: {meta!r}")
        result.append((path, meta[1:].split()[1]))
    return result


def table_header_index(text):
    for line in (text or "").splitlines():
        if line.lstrip().startswith("|") and "Retrieved" in line:
            cells = [c.strip() for c in CELL_SPLIT.split(line.strip())]
            return cells.index("Retrieved") if "Retrieved" in cells else None
    return None


def row_date(line, index):
    """The Retrieved date of a validation-table row, or None for a non-row line."""
    stripped = line.strip()
    if not stripped.startswith("|") or re.fullmatch(r"[|\s:-]+", stripped):
        return None
    cells = [c.strip() for c in CELL_SPLIT.split(stripped)]
    if index is not None and index < len(cells):
        m = ISO.search(cells[index])
        if m:
            return m.group(1)
    found = ISO.findall(stripped)
    return found[-1] if found else None


def added_lines(root, base, head, path):
    out = git(root, "diff", "-U0", "--no-renames", base, head, "--", path)
    return [line[1:] for line in out.splitlines() if line.startswith("+") and not line.startswith("+++")]


def check_evidence(root, base, head, changed):
    """Changed chapters need a validation row re-checked in this change and an editorial note."""
    paths = {p for p, _ in changed}
    errors = []
    window_start = git(root, "show", "-s", "--format=%cs", base).strip()
    latest_allowed = (datetime.datetime.now(datetime.timezone.utc).date()
                      + datetime.timedelta(days=1)).isoformat()
    for path, mode in sorted(changed):
        stem = policy.evidence_stem(path)
        if not stem or mode == "000000":
            continue
        table = f"validation/{stem}.md"
        text = show(root, head, table)
        if text is None:
            continue
        log = f"editorial/{stem}-editorial-log.md"
        if log not in paths:
            errors.append(f"{path} changed but {log} did not; note what changed and why")
        if table not in paths:
            errors.append(f"{path} changed but {table} did not; add or re-date the rows you checked")
            continue
        index = table_header_index(text)
        dates = [d for d in (row_date(line, index) for line in added_lines(root, base, head, table)) if d]
        if not any(window_start <= d <= latest_allowed for d in dates):
            errors.append(f"{table}: no added or updated row with a Retrieved date between "
                          f"{window_start} and today; record the sources you re-checked")
        if any(d > latest_allowed for d in dates):
            errors.append(f"{table}: a Retrieved date is in the future")
    if any(p.startswith("validation/") for p in paths) and "VALIDATION.md" not in paths:
        errors.append("validation/ changed but VALIDATION.md did not; update the summary and dates")
    return errors


def validate_change(root, base_ref, head="HEAD"):
    base = commit_of(root, base_ref)
    head = commit_of(root, head)
    changed = changes(root, base, head)
    paths = [p for p, _ in changed]
    old_text = show(root, base, policy.BOOK_JSON)
    new_text = show(root, head, policy.BOOK_JSON)
    old, new = book(old_text, base_ref), book(new_text, "HEAD")
    keys = policy.changed_keys(old, new) if policy.BOOK_JSON in paths else []
    result = policy.classify(paths, keys)
    kind = result["kind"]
    errors = []
    for path, mode in changed:
        if policy.is_content(path) and mode in ("120000", "160000"):
            errors.append(f"{path}: symlinks and submodules are not allowed in content")
    old_log = show(root, base, policy.CHANGELOG) or ""
    new_log = show(root, head, policy.CHANGELOG) or ""
    new_headings = [v for v in policy.changelog_versions(new_log) if v not in policy.changelog_versions(old_log)
                    and v.lower() != "unreleased"]
    metadata_changed = sorted(set(keys) & policy.METADATA_KEYS)

    if kind in ("tooling", "none"):
        if metadata_changed:
            errors.append("a tooling-only change must not change release metadata in tools/book.json "
                          f"({', '.join(metadata_changed)}); release metadata changes ride with content")
        for v in new_headings:
            errors.append(f"a tooling-only change must not add the CHANGELOG version section [{v}]")
        summary = f"tooling-only change ({len(paths)} files); no release"
    else:
        version = policy.parse_version(new.get("version"))
        tag = f"v{version}"
        names = tags(root)
        latest = policy.latest_stable(names)
        if latest and policy.version_key(version) <= policy.version_key(latest[1:]):
            errors.append(f"content changed: tools/book.json version {version} must be higher than "
                          f"the latest release {latest} (see RELEASING.md for which part to bump)")
        if old.get("version") == version:
            errors.append(f"content changed without a new version (still {version})")
        if tag in names:
            errors.append(f"tag {tag} already exists; pick the next version")
        try:
            policy.dated_section(new_log, version)
        except PolicyError as error:
            errors.append(str(error))
        for key in ("edition", "checked_as_of"):
            if not str(new.get(key) or "").strip():
                errors.append(f"tools/book.json {key} is empty")
        errors += check_evidence(root, base, head, changed)
        summary = f"content change for {tag}: {len(result['content'])} content files"
        if kind == "mixed":
            summary += (f"; ALSO tooling ({', '.join(result['tooling'])}): valid, but the approval "
                        "controller never merges mixed changes automatically. Split the pull request.")
    if errors:
        raise PolicyError("\n".join(errors))
    return kind, summary


def validate_release(root, tag, sha, allow_existing_tag=False):
    version = policy.tag_version(tag)
    if not policy.SHA_RE.fullmatch(sha or ""):
        raise PolicyError("--sha must be a full 40-character commit SHA")
    if commit_of(root, "HEAD") != sha:
        raise PolicyError(f"check out {sha} before validating its release")
    if git(root, "status", "--porcelain", "--untracked-files=no").strip():
        raise PolicyError("the checkout has local changes")
    data = book(show(root, sha, policy.BOOK_JSON), sha)
    if data.get("version") != version:
        raise PolicyError(f"tools/book.json version is {data.get('version')!r}, the tag is {tag}")
    policy.dated_section(show(root, sha, policy.CHANGELOG) or "", version)
    names = tags(root)
    if tag in names:
        if not allow_existing_tag:
            raise PolicyError(f"tag {tag} already exists; a fix is a new patch version")
        if commit_of(root, f"refs/tags/{tag}") != sha:
            raise PolicyError(f"tag {tag} points at another commit; tags are never moved")
    previous = policy.previous_release(names, version)
    if previous:
        prev = commit_of(root, f"refs/tags/{previous}")
        if subprocess.run(["git", "merge-base", "--is-ancestor", prev, sha], cwd=root).returncode != 0:
            raise PolicyError(f"the previous release {previous} is not an ancestor of {sha}")
    elif policy.latest_stable(names):
        raise PolicyError(f"{tag} is lower than every existing release")
    return f"{tag} at {sha[:12]} (previous release: {previous or 'none'})"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("change")
    c.add_argument("--root", type=Path, default=Path("."))
    c.add_argument("--base-ref", required=True)
    c.add_argument("--head", default="HEAD")
    r = sub.add_parser("release")
    r.add_argument("--root", type=Path, default=Path("."))
    r.add_argument("--tag", required=True)
    r.add_argument("--sha", required=True)
    r.add_argument("--allow-existing-tag", action="store_true")
    n = sub.add_parser("notes")
    n.add_argument("--root", type=Path, default=Path("."))
    n.add_argument("--tag", required=True)
    n.add_argument("--repo", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "change":
            kind, summary = validate_change(args.root, args.base_ref, args.head)
            print(f"release check passed: {summary}")
        elif args.cmd == "release":
            print(f"release check passed: {validate_release(args.root, args.tag, args.sha, args.allow_existing_tag)}")
        else:
            text = (args.root / policy.CHANGELOG).read_text(encoding="utf-8")
            notes = policy.release_notes(text, policy.tag_version(args.tag), args.repo, args.tag)
            sys.stdout.buffer.write(notes.encode("utf-8"))
    except (PolicyError, OSError) as error:
        for line in str(error).splitlines():
            print(f"::error::{line}" if _in_actions() else f"error: {line}", file=sys.stderr)
        return 1
    return 0


def _in_actions():
    import os
    return os.environ.get("GITHUB_ACTIONS") == "true"


if __name__ == "__main__":
    raise SystemExit(main())
