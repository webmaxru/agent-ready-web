# Releasing

Each release of *Agent-Ready Websites in Action* is a Git tag `vX.Y.Z` on a commit that is already on `main`: releases come only from merged code. The Release workflow builds the book from that tag and publishes a GitHub Release with four files, plus their checksums:

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

## Cut a release (the usual way: merge a release pull request)

1. Create a branch named `release/vX.Y.Z` (or add the label `release` to the pull request).
2. On it, set `"version"` in [`tools/book.json`](tools/book.json) to the new version, and `"checked_as_of"` to the month the book was last checked against its sources (the title and copyright pages print it).
3. In `CHANGELOG.md`, change the version's heading from `## [X.Y.Z] - unreleased` to `## [X.Y.Z] - YYYY-MM-DD` (the release date). The release fails if the date is missing.
4. Open the pull request. Book CI lints, builds every edition, runs EPUBCheck and the agent-readiness audit, and attaches the PDFs to the run so you can read them.
5. Merge it. **Actions → Release** then reads the version from `tools/book.json`, tags the merge commit `vX.Y.Z`, checks the tag against `tools/book.json`, takes the notes from `CHANGELOG.md`, runs the lint, builds the editions, runs EPUBCheck, publishes the release and starts the web deploy. The release is marked **Latest** only when its tag is the highest stable version. A pull request closed without merging releases nothing, and if the tag already exists the workflow stops and says so.
6. Upload the new PDF and EPUB to Leanpub, and the print PDF to KDP (see [README.md](README.md#publishing)).

Locally, before step 4 (optional; CI does the same):

```sh
python3 tools/lint_manuscript.py
python3 tools/build.py all
```

## Tag by hand

You can still push a tag yourself after the merge:

```sh
git switch main && git pull
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

The workflow checks that the tagged commit is on `main` and refuses the tag otherwise, so an unmerged branch can't be released.

## Rebuild or publish a release by hand

**Actions → Release → Run workflow**, with `tag` set to an existing tag (for example `v1.0.0`). The workflow builds from that tag and replaces the release's files, keeping the release itself. Use it when a build fix must reach an existing release.

The release notes always come from `CHANGELOG.md` on the default branch, so a corrected changelog entry can be republished the same way.

## Roll back the web edition

**Actions → deploy-swa → Run workflow**, with `ref` set to an earlier tag. The PDF and EPUB of every version stay on their GitHub Releases.

## Fix a bad release

Don't move a tag that people may have downloaded. Fix the problem on `main`, add a patch entry to CHANGELOG.md, and release `vX.Y.(Z+1)`. To withdraw a release completely, delete it on GitHub (Releases → … → Delete), then delete the tag (`git push origin :refs/tags/vX.Y.Z`).

## What the build reads

The editions are built only from `manuscript/` (the text, `Book.txt` and the images in `manuscript/resources/images/`), `tools/book.json` (title, version, copyright lines, links, agent-ready settings), `CHANGELOG.md` (the web edition's Release history page and `releases.xml` feed) and `theme/` (all styling). `figures/` holds the sources of the figures; render them into `manuscript/resources/images/` before a release.
