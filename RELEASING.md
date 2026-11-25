# Releasing

Each release of *Agent-Ready Websites in Action* is a Git tag `vX.Y.Z` on the squash-merge commit of an owner-approved content pull request. The Release workflow builds the book from that commit, tags it and publishes a GitHub Release with four files, plus their checksums:

- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z.pdf`: the PDF, 7 × 9.25 in (reading, Leanpub).
- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z-print-7.5x9.25.pdf`: the paperback interior, 7.5 × 9.25 in (KDP). Same text block and page count as the PDF.
- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z.epub`: EPUB 3, checked with EPUBCheck.
- `Agent-Ready-Websites-in-Action-HTML-vX.Y.Z.zip`: the web edition, readable offline (open `index.html`).
- `SHA256SUMS.txt`.

The release notes are the version's section of [`CHANGELOG.md`](CHANGELOG.md). After a stable release is published, the workflow asks `deploy-swa` to put that tag on the web edition at https://agent-ready-web.salnikov.no (see [`DEPLOY.md`](DEPLOY.md)). Everything runs on the built-in `GITHUB_TOKEN`; no secrets are needed for the release itself.

## Version numbers

Versions follow Semantic Versioning, read for a book:

- **Major** (`2.0.0`): the book is revised as a whole, chapters are added, removed or reordered, or a standard it teaches changes in a way that breaks earlier listings.
- **Minor** (`1.1.0`): new material inside the current structure. A new section or appendix, a new figure or listing, a status update (for example a standard that moves from draft to recommendation, or a new Lighthouse version that changes the scoring).
- **Patch** (`1.0.1`): corrections. Typos, broken links, wrong numbers, layout fixes, theme and build fixes that change no text.
- **Pre-release** (`1.1.0-rc.1`): a review copy. Published as a GitHub pre-release, never marked Latest, and not deployed to the web edition.

Version 2.0.0 is the release of *Agent-Ready Websites in Action*.

## How a version is released

A version is released only from an **owner-approved, content-only pull request**. Nothing else publishes: not a push, a tag, a label, nor a branch name.

1. **Update.** Run `/update-book` (`.github/prompts/update-book.prompt.md`). In `check` mode it is read-only and reports which cited sources changed upstream (`python3 tools/check_upstream.py`) and which chapters that affects. In `prepare` mode it:
   - edits only those chapters;
   - re-dates their rows in `validation/` and `VALIDATION.md` and adds an entry to each changed chapter's editorial log;
   - sets `version`, `edition` and `checked_as_of` in `tools/book.json` and adds a dated `## [X.Y.Z] - YYYY-MM-DD` section to `CHANGELOG.md`;
   - runs the lint and the full build;
   - stops at a local commit.
   
   `.github/prompts/release-content.prompt.md` covers the metadata and the pull request.
2. **Open a pull request** to `main` from a branch of this repository. A content pull request changes only `manuscript/`, `editorial/`, `validation/`, `figures/`, `VALIDATION.md`, `CHANGELOG.md` and the release-metadata keys of `tools/book.json` (`version`, `edition`, `checked_as_of`, `year`).
3. **Book CI** runs on the pull request. Its aggregate check **Book release preflight** must be green. It covers the lint, the four editions, EPUBCheck, `check_site`, the Lighthouse agentic-browsing audit and the release checks below.
4. **The owner approves.**
   - A pull request by someone else needs an **Approve** review from `webmaxru` on its current head commit.
   - On his own pull request (GitHub forbids approving your own), he comments exactly `/release-book <the full 40-character head SHA>`.
   - A new push needs a new approval.
   - A later "changes requested" review, or a dismissed review, blocks the release until he approves again. A `/release-book` comment then counts only if it comes after that barrier.
5. **Release approved book** (`.github/workflows/approved-book.yml`) does the rest. It starts on the review, on the comment, when Book CI finishes, on a 30-minute scan that catches missed events, or by hand with the pull request number. It:
   - checks that the pull request is from this repository, targets `main`, is not a draft, is mergeable, is not behind `main` and is content-only, and that Book release preflight passed on that exact head;
   - runs `main`'s validator and lint against the head (a pull request cannot change the rules it is checked by);
   - squash-merges only if the head is still the approved SHA;
   - dispatches **Release** with the pull request, head, base and merge SHAs and the tag. A merge made with the built-in token starts no other workflows, so the dispatch is explicit.
6. **Release** (`.github/workflows/release.yml`) publishes the version:
   - **plan:** checks that the merge commit is that pull request's squash on `main`, that its tree is the approved head, that the tag matches `tools/book.json`, and that the previous release is an ancestor;
   - **build:** builds the four editions and `SHA256SUMS.txt` from the exact merge commit, with the lint, `check_site` and EPUBCheck. This happens *before* any tag exists, so a failed build leaves nothing behind;
   - **publish:** creates the annotated tag `vX.Y.Z` at the merge commit, uploads the files to a draft release, checks them and publishes it. The notes are the version's `CHANGELOG.md` section. The release is marked **Latest** only if it is the highest stable version; `X.Y.Z-rc.N` is published as a pre-release;
   - **deploy:** dispatches `deploy-swa` with `ref` set to the tag, and reports in the run summary whether the web edition went live. A pre-release is not deployed. While the Azure deployment token is missing, the summary says **Web edition NOT deployed** (see [`DEPLOY.md`](DEPLOY.md)).
7. Upload the new PDF and EPUB to Leanpub, and the print PDF to KDP (see [README.md](README.md#publishing)).

Locally, before step 2 (CI runs the same checks):

```sh
python3 tools/lint_manuscript.py
python3 tools/validate_release.py change --root . --base-ref origin/main
python3 tools/build.py all
```

### Release checks

`tools/validate_release.py change` runs in Book CI (and against the approved head, from `main`). It enforces:

- **A content change needs a new version.** Any change under `manuscript/`, `editorial/`, `validation/` or `figures/`, or to `VALIDATION.md`, needs all of the following:
  - a `tools/book.json` `version` higher than the latest stable tag;
  - a tag for it that doesn't exist yet;
  - a matching dated section `## [X.Y.Z] - YYYY-MM-DD` in `CHANGELOG.md`.
- **A tooling-only change has no version.** It must not change the release-metadata keys or add a CHANGELOG version section. A pull request that mixes tooling and content passes CI, but it is never merged or released automatically: split it.
- **Evidence.** Every changed chapter or appendix that has a `validation/<stem>.md` table needs:
  - its `editorial/<stem>-editorial-log.md` changed;
  - its validation table changed, with at least one added or updated row whose `Retrieved` date is no older than the base commit and not in the future.
  
  Any change under `validation/` also needs `VALIDATION.md`.
- **No symlinks or submodules** in content.

The tests are in `tests/` (stdlib `unittest`, no network): `python3 -m unittest discover -s tests`.

## Recovery

- **Before the merge** (approval not picked up, a transient failure): **Actions → Release approved book → Run workflow** with the pull request number.
- **After the merge** (the build or the upload failed): **Actions → Release → Run workflow** with the pull request number, or with only the tag of an existing release. The same provenance checks run. A published release that has every file is a successful no-op and goes straight to the deploy. A release with missing files, or a merge or tag that doesn't trace back to an approved pull request, fails without writing anything.
- **Published files are never replaced and tags are never moved.** A fix to a published version, even a build-only fix, is a new patch version through a new pull request.

## Changes from the earlier flow

- Merging a `release/` branch, the `release` label and pushing a tag no longer publish anything. Every release goes through the owner's approval.
- **Run workflow** on Release no longer rebuilds an existing release and replaces its files (`--clobber`). It only completes or confirms an approved release.
- The tag is created by the workflow, after the build, as an annotated tag. You no longer tag by hand.
- `v1.0.0` and `v2.0.0` were published by the earlier flow. They stay as they are, and they are not rebuilt.

The repository is private on the free plan, so it has no branch protection: **a manual merge bypasses the approval controller.** A version merged by hand is not released automatically. Release refuses it, because it is not an approved pull request's merge. Release it with a new patch version through the normal flow.

## Roll back the web edition

**Actions → deploy-swa → Run workflow**, with `ref` set to an earlier tag. The PDF and EPUB of every version stay on their GitHub Releases.

## Fix a bad release

Don't move a tag that people may have downloaded. Fix the problem on `main`, add a patch entry to CHANGELOG.md, and release `vX.Y.(Z+1)`. To withdraw a release completely, delete it on GitHub (Releases → … → Delete), then delete the tag (`git push origin :refs/tags/vX.Y.Z`).

## What the build reads

The editions are built only from `manuscript/` (the text, `Book.txt` and the images in `manuscript/resources/images/`), `tools/book.json` (title, version, copyright lines, links, agent-ready settings), `CHANGELOG.md` (the web edition's Release history page and `releases.xml` feed) and `theme/` (all styling). `figures/` holds the sources of the figures; render them into `manuscript/resources/images/` before a release.
