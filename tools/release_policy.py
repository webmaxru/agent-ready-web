"""Release policy shared by the release validator and the approval controller (stdlib only).

One place defines which paths are book content, which tools/book.json keys are release
metadata, how versions and tags compare, which files a release must carry, and how the
release notes are cut from CHANGELOG.md. See RELEASING.md.
"""
from __future__ import annotations

import json
import re
from pathlib import PurePosixPath

OWNER = "webmaxru"

# Reader-facing content and the evidence that backs it.
CONTENT_PREFIXES = ("manuscript/", "editorial/", "validation/", "figures/")
CONTENT_FILES = {"VALIDATION.md"}
# Release files: allowed beside content, never content on their own.
CHANGELOG = "CHANGELOG.md"
BOOK_JSON = "tools/book.json"
RELEASE_FILES = {CHANGELOG, BOOK_JSON}
# The only tools/book.json keys a content PR may change. Every other key is build configuration.
METADATA_KEYS = frozenset({"version", "edition", "checked_as_of", "year"})

FILE_STEM = "Agent-Ready-Websites-in-Action-Maxim-Salnikov"
HTML_ZIP_STEM = "Agent-Ready-Websites-in-Action-HTML"

_NUM = r"(?:0|[1-9][0-9]*)"
_PRE_ID = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
VERSION_RE = re.compile(rf"({_NUM})\.({_NUM})\.({_NUM})(?:-({_PRE_ID}(?:\.{_PRE_ID})*))?\Z")
TAG_RE = re.compile(rf"v({_NUM})\.({_NUM})\.({_NUM})(?:-({_PRE_ID}(?:\.{_PRE_ID})*))?\Z")
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


class PolicyError(ValueError):
    pass


# ---------------------------------------------------------------- versions and tags

def parse_version(value):
    if not isinstance(value, str) or not VERSION_RE.fullmatch(value):
        raise PolicyError(f"{value!r} is not a semantic version X.Y.Z[-pre]")
    return value


def version_key(value):
    """Semantic Versioning 2.0.0 precedence as a sortable tuple."""
    m = VERSION_RE.fullmatch(value)
    if not m:
        raise PolicyError(f"{value!r} is not a semantic version X.Y.Z[-pre]")
    core = tuple(int(x) for x in m.group(1, 2, 3))
    pre = m.group(4)
    if pre is None:
        return core + (1, ())
    ids = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core + (0, ids)


def is_prerelease(version):
    return "-" in parse_version(version)


def tag_version(tag):
    if not isinstance(tag, str) or not TAG_RE.fullmatch(tag):
        raise PolicyError(f"{tag!r} is not a vX.Y.Z[-pre] tag")
    return tag[1:]


def release_tags(names):
    return [n for n in names if isinstance(n, str) and TAG_RE.fullmatch(n)]


def latest_stable(names):
    stable = [n for n in release_tags(names) if not is_prerelease(n[1:])]
    return max(stable, key=lambda n: version_key(n[1:]), default=None)


def previous_release(names, version):
    """The highest stable tag below version: the release this one must descend from."""
    key = version_key(version)
    earlier = [n for n in release_tags(names)
               if not is_prerelease(n[1:]) and version_key(n[1:]) < key]
    return max(earlier, key=lambda n: version_key(n[1:]), default=None)


def is_newest_stable(version, published):
    """Whether a release of version may take the Latest label from the published tags."""
    if is_prerelease(version):
        return False
    key = version_key(version)
    return all(version_key(n[1:]) <= key for n in release_tags(published)
               if not is_prerelease(n[1:]))


# ---------------------------------------------------------------- CHANGELOG

_HEADING = re.compile(r"^## \[([^\]]+)\][ \t]*(?:[-–—][ \t]*(.*?))?[ \t]*$", re.M)


def changelog_versions(text):
    return [m.group(1) for m in _HEADING.finditer(text)]


def changelog_section(text, version):
    """(date, body) of the version's section; date is '' when the heading has none."""
    headings = list(_HEADING.finditer(text))
    for i, m in enumerate(headings):
        if m.group(1) == version:
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            return (m.group(2) or "").strip(), text[m.end():end]
    raise PolicyError(f"CHANGELOG.md has no '## [{version}]' section")


def dated_section(text, version):
    date, body = changelog_section(text, version)
    if not DATE_RE.fullmatch(date):
        raise PolicyError(f"CHANGELOG.md: '## [{version}]' has no release date YYYY-MM-DD "
                          f"(found {date!r})")
    if not body.strip():
        raise PolicyError(f"CHANGELOG.md: '## [{version}]' is empty")
    return date, body


def release_notes(text, version, repo, tag):
    """The version's CHANGELOG section with relative links pointed at the tagged files."""
    _, body = dated_section(text, version)
    body = re.sub(r"(?m)^\[[^\]]+\]: \S+\s*$", "", body)
    base = f"https://github.com/{repo}/blob/{tag}/"
    body = re.sub(r"\]\((?!https?:|#|mailto:)([^)]+)\)", lambda m: "](" + base + m.group(1) + ")", body)
    return body.strip() + "\n"


# ---------------------------------------------------------------- release files

def expected_assets(tag):
    tag_version(tag)
    return [
        f"{FILE_STEM}-{tag}.pdf",
        f"{FILE_STEM}-{tag}-print-7.5x9.25.pdf",
        f"{FILE_STEM}-{tag}.epub",
        f"{HTML_ZIP_STEM}-{tag}.zip",
        "SHA256SUMS.txt",
    ]


def missing_assets(tag, assets):
    """Expected files not present as uploaded, non-empty release assets."""
    ok = {a.get("name") for a in assets
          if a.get("state") == "uploaded" and type(a.get("size")) is int and a["size"] > 0}
    return [n for n in expected_assets(tag) if n not in ok]


# ---------------------------------------------------------------- change classification

def changed_keys(old, new):
    """Top-level keys whose values differ between two tools/book.json texts (or dicts)."""
    if isinstance(old, str):
        old = json.loads(old) if old.strip() else {}
    if isinstance(new, str):
        new = json.loads(new) if new.strip() else {}
    if not isinstance(old, dict) or not isinstance(new, dict):
        raise PolicyError("tools/book.json must be a JSON object")
    return sorted(k for k in set(old) | set(new) if old.get(k, object()) != new.get(k, object()))


def safe_path(path):
    if not isinstance(path, str) or not path or "\\" in path or path.startswith("/"):
        return False
    parts = PurePosixPath(path).parts
    return ".." not in parts and "." not in parts and str(PurePosixPath(path)) == path


def is_content(path):
    return safe_path(path) and (path in CONTENT_FILES or path.startswith(CONTENT_PREFIXES))


def classify(paths, book_json_keys=()):
    """Sort changed paths into content, release and tooling.

    paths: every changed path (for renames, both the old and new names).
    book_json_keys: the tools/book.json keys that changed, when it changed.
    tools/book.json counts as a release file only if every changed key is release metadata.
    Returns {"kind": "content"|"tooling"|"mixed"|"none", "content": [...], "release": [...],
    "tooling": [...]}.
    """
    content, release, tooling = [], [], []
    for path in sorted(set(paths)):
        if is_content(path):
            content.append(path)
        elif path == CHANGELOG:
            release.append(path)
        elif path == BOOK_JSON and set(book_json_keys) <= METADATA_KEYS:
            release.append(path)
        else:
            tooling.append(path)
    if content and tooling:
        kind = "mixed"
    elif content:
        kind = "content"
    elif tooling or release:
        kind = "tooling"
    else:
        kind = "none"
    return {"kind": kind, "content": content, "release": release, "tooling": tooling}


def evidence_stem(path):
    """The chapter stem whose validation table backs a manuscript file, or None."""
    m = re.fullmatch(r"manuscript/([0-9]{2}-[a-z0-9-]+|appendix-[a-z]-[a-z0-9-]+)\.md", path)
    return m.group(1) if m else None
