# Releasing

Each release of *Agent-Ready Websites in Action* is a Git tag `vX.Y.Z` on the squash-merge commit of an owner-approved content pull request. The Release workflow builds the book from that commit, tags it and publishes a GitHub Release with four files, plus their checksums:

- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z.pdf`: the PDF, 7 × 9.25 in (reading, Leanpub).
- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z-print-7.5x9.25.pdf`: the paperback interior, 7.5 × 9.25 in (KDP). Same text block and page count as the PDF.
- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z.epub`: EPUB 3, checked with EPUBCheck.
- `Agent-Ready-Websites-in-Action-HTML-vX.Y.Z.zip`: the web edition, readable offline (open `index.html`).
- `SHA256SUMS.txt`.

The release notes are the version's section of [`CHANGELOG.md`](CHANGELOG.md). After a stable release is published, the workflow asks `deploy-swa` to put that tag on the web edition at https://agent-ready-web.salnikov.no (see [`DEPLOY.md`](DEPLOY.md)). Everything runs on the built-in `GITHUB_TOKEN`; no secrets are needed for the release itself.

```text
/update-book check ─► /update-book prepare ─► content PR ─► Book release preflight (green)
        ─► owner approval of the exact head ─► Release approved book: squash-merge
        ─► Release: build, annotated tag, draft, upload, publish ─► deploy-swa: web edition
```

The sections below explain each step. [Scenarios](#scenarios-what-to-do-when) walks through the situations you will actually meet, with commands.

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
   - **deploy:** dispatches `deploy-swa` with `ref` set to the tag, and reports in the run summary whether the web edition went live. A pre-release is not deployed. If the deploy fails, or the Azure deployment token is missing, the summary says **Web edition NOT deployed** (see [scenario 13](#13-only-the-deploy-failed)).
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

## Scenarios: what to do when

Commands use the [GitHub CLI](https://cli.github.com/) (`gh`) from a clone of this repository and work in bash and PowerShell, except `python3`, which is `python` on Windows. `N` is the pull request number and `vX.Y.Z` a tag.

### What triggers what

| Event | What happens | Release? |
| --- | --- | --- |
| PR opened or pushed | **Book CI** runs the lint, the four editions, EPUBCheck, `check_site`, Lighthouse and the release checks. Its **Book release preflight** job is the gate. | No |
| Owner **Approve** review, or an owner `/release-book <SHA>` comment | **Release approved book** re-checks everything and squash-merges the approved head. | Yes, through **Release** |
| Book CI or approval-signal run finishes, or the half-hourly scan | The controller looks for an approved PR it missed. It never approves anything itself. | Only if a valid approval exists |
| **Release approved book → Run workflow** with `pr` | Same re-check for one PR. | Only if a valid approval exists |
| Push a tag, add a label, press **Merge** | Nothing in the release flow. | **No** |
| Push to `main` touching `manuscript/`, `theme/`, `tools/`, `staticwebapp.config.json`, `infra/check_site.py` or `CHANGELOG.md` | **deploy-swa** deploys the web edition. | **No** |

The last two rows matter: the web edition and the downloads are separate. Only the controller's squash-merge produces a tag and downloads.

### 1. Routine update (your own PR)

1. `/update-book check` for the impact report, then `/update-book prepare` for a tested commit on a branch.
2. Check locally what CI will check:

   ```sh
   python3 tools/validate_release.py change --root . --base-ref origin/main   # prints the tag, e.g. "content change for v2.1.0"
   python3 tools/lint_manuscript.py
   python3 -m unittest discover -s tests
   ```

3. Push and open the PR against `main`:

   ```sh
   git push -u origin content/my-update
   gh pr create --base main --title "Update for <what changed>" --body "See CHANGELOG."
   ```

4. Wait for **Book release preflight** to pass (`gh pr checks N --watch`). Read the CHANGELOG section and check that the validation rows and editorial log say what you re-checked.
5. Authorize **the exact head**. You wrote the PR, so GitHub will not let you approve it. Comment instead:

   ```sh
   gh pr comment N --body "/release-book $(gh pr view N --json headRefOid --jq .headRefOid)"
   ```

6. Watch it go through, normally within a few minutes:

   ```sh
   gh run list --workflow approved-book.yml -L 3
   gh run list --workflow release.yml -L 3
   gh release view vX.Y.Z
   ```

**Result:** the PR is squash-merged, `vX.Y.Z` is an annotated tag on the merge commit, the release has the PDF, print PDF, EPUB, HTML zip and `SHA256SUMS.txt`, it is Latest if it is the highest stable version, and `deploy-swa` puts the tag on https://agent-ready-web.salnikov.no. The run summary of **Release** says **Web edition deployed**.

### 2. Someone else's PR on a branch in this repository

A collaborator with write access opens a content PR.

1. Read the diff. The PR must be non-draft, target `main`, change only content files and pass **Book release preflight**. A contributor usually does not know about the version bump, the CHANGELOG section, the editorial log and the validation rows, so preflight fails until they exist. Add them to the contributor's branch yourself:

   ```sh
   gh pr checkout N
   # edit tools/book.json (version, edition, checked_as_of), CHANGELOG.md, editorial/, validation/ and VALIDATION.md
   git add -A && git commit -m "Prepare vX.Y.Z" && git push
   ```

2. When preflight is green, submit an **Approve** review on the current head and stop there:

   ```sh
   gh pr review N --approve
   ```

**Do not press Merge.** A manual merge publishes nothing (scenario 10). The pushes in step 1 change the head, so approve after them, not before.

### 3. A pull request from a fork

The controller only merges PRs whose head branch is in this repository, so a fork PR is refused. Re-create it on a branch here and keep the contributor's commits:

```sh
gh pr checkout N
git switch -c content/from-pr-N
git push -u origin content/from-pr-N
gh pr create --base main --head content/from-pr-N --title "<title>" --body "Supersedes #N"
```

You now own the new PR, so continue with scenario 1: add the bump, CHANGELOG and evidence, then comment `/release-book <SHA>`. Close the original PR with a thank-you.

### 4. A new push after approval, requested changes or a dismissed review

An approval counts only for the head it was given on. A push after approval, a **Request changes** review or a dismissed review voids it. Nothing merges until you approve again (a new **Approve** review, or a new `/release-book <SHA>` with the new head SHA). An old SHA in an old comment is ignored.

### 5. The branch is behind `main`

The head must include current `main`, and GitHub must report the PR as mergeable. Update the branch and approve again:

```sh
gh pr update-branch N
```

If GitHub reports a conflict, resolve it on the branch first.

### 6. Approved, but the PR is still open

Look at the latest **Release approved book** run for the cause: failing preflight, a head that moved, a branch behind `main`, a conflict, or a run that never started. Fix that, or just run the controller for this PR:

```sh
gh workflow run approved-book.yml -f pr=N
```

If the run died within a second with no steps, see [Runs that fail without starting](#11-runs-that-fail-without-starting).

### 7. Tooling, docs and workflow changes

A PR that touches only files outside the content allowlist (`tools/` other than the release keys of `book.json`, `theme/`, `.github/`, `infra/`, `README.md`, `RELEASING.md`, tests) is **tooling-only**. It must not change `version`, `edition`, `checked_as_of` or `year` in `tools/book.json`, and it must not add a CHANGELOG version section: `validate_release.py` fails it with `a tooling-only change must not change release metadata`. It never releases, and the controller never merges it. Merge it yourself when CI is green. A change under `tools/` or `theme/` still redeploys the web edition on merge, because **deploy-swa** watches those paths.

### 8. Mixed content and tooling

A PR that changes both content and tooling passes CI, but the controller never merges it (`controller never merges mixed changes automatically. Split the pull request.`). Split it into two PRs: tooling first (merged by you), then the content PR.

### 9. Review copy (prerelease)

Use a prerelease version such as `2.1.0-rc.1` for a copy to share before the real edition. The PR still goes through scenario 1 and still merges into `main`. The release is marked pre-release, is never Latest, and the Release run summary says the web edition was not deployed for a pre-release. Because the text is on `main`, the next push-triggered **deploy-swa** builds it, so a prerelease does not keep text off the web edition. To graduate it, open a new PR that sets `2.1.0`, adds that CHANGELOG section and carries the evidence.

### 10. A manual merge by mistake

Pressing **Merge** on a content PR, or merging from the command line, bypasses the controller. The repository is private on the free plan, so it has no branch protection and GitHub allows it. The effects:

- The web edition deploys the new content (**deploy-swa** runs on the push).
- **No tag, no release, no downloads.** The site is ahead of the PDF and EPUB.
- **Release** refuses it, because it is not an approved PR's merge.
- The version the PR carried is now on `main` unreleased. A content PR must change `version`, so that version number can no longer be used (`content changed without a new version (still 2.1.0)`).

Fix it with a catch-up PR. For example, if `main` carries `2.1.0` but the latest tag is `v2.0.0`:

1. Branch from `main`, set `version` in `tools/book.json` to `2.1.1` and add a dated `## [2.1.1] - YYYY-MM-DD` section to `CHANGELOG.md`. Move the unreleased `2.1.0` notes under it so the release notes describe the whole edition.
2. **Include at least one real content change**: a correction you want anyway, or a re-checked chapter with its editorial log and a re-dated validation row. A PR with only the version, the CHANGELOG and the evidence files counts as tooling-only and fails with `a tooling-only change must not change release metadata`.
3. Check it: `python3 tools/validate_release.py change --root . --base-ref origin/main` prints `release check passed: content change for v2.1.1`.
4. Open the PR and authorize it as in scenario 1.

### 11. Runs that fail without starting

If **Release approved book** or **Book CI** runs end in about a second with no steps and the annotation *"The job was not started because recent account payments have failed or your spending limit needs to be increased"*, GitHub Actions is blocked by billing, not by this repository. Fix **Settings → Billing and plans**, then run `gh workflow run approved-book.yml -f pr=N` for each affected PR.

### 12. The release failed after the merge

The PR is merged but there is no (or an incomplete) release. Run **Release** for it:

```sh
gh workflow run release.yml -f pr=N
```

Or, for a release that already exists but is incomplete, give only its tag: `gh workflow run release.yml -f tag=vX.Y.Z`. Release checks the merge again. If the release is already complete, it is a no-op that goes straight to the deploy. If files are missing or the merge or tag does not trace back to an approved PR, it fails without writing anything. Then look at the tag and the draft release on GitHub and decide what is safe. Never move a tag or overwrite published downloads; the answer to a bad published file is a new patch version.

### 13. Only the deploy failed

The release is published and complete, but the web edition is not live: **deploy-swa** failed, or the run summary says **Web edition NOT deployed** or *not confirmed*. Do not re-run **Release**. Check that the Azure token exists, then deploy the tag:

```sh
gh secret list | grep AZURE_STATIC_WEB_APPS_API_TOKEN
gh workflow run deploy-swa.yml -f ref=vX.Y.Z
```

In PowerShell, use `gh secret list | Select-String AZURE_STATIC_WEB_APPS_API_TOKEN`. If the secret is missing, see [DEPLOY.md](DEPLOY.md). If the site is up but the domain does not answer, see [CUSTOM-DOMAIN.md](CUSTOM-DOMAIN.md).

### 14. Roll back the web edition

Downloads stay as they are; only the site changes:

```sh
gh workflow run deploy-swa.yml -f ref=v1.0.0
```

Any tag that contains `tools/build.py` can be built, which includes `v1.0.0`. The next push to `main` that touches a deploy path will redeploy `main`, so fix `main` too if the rollback is meant to last.

### 15. A published release is wrong

Do not edit the release or move its tag. Fix `main`, add a patch version through scenario 1 and release it. To withdraw a release completely, delete the GitHub release, then delete the tag with `git push origin :refs/tags/vX.Y.Z`. The version number stays used on `main`, so the next release must still be higher.

### 16. Choosing the version

Follow [Version numbers](#version-numbers). When unsure, ask what a reader of the last stable tag would notice: broken earlier listings or a restructured book is major, new material is minor, corrections are patch. The version must be higher than the latest stable tag and different from the version on `main`. Preflight tells you if it is not.

### 17. Leanpub, KDP and Kindle

The workflow publishes GitHub downloads and the web edition only. Upload the PDF and EPUB to Leanpub, the print PDF to KDP and the EPUB to Kindle by hand from the release page; see [Publishing](README.md#publishing).

### 18. Control center alerts

If you use the book control center, each alert has a fix on this page:

| Alert | Cause and fix |
| --- | --- |
| `PR #N is ready for your approval` | Preflight is green. Approve the head (scenario 2) or comment `/release-book <SHA>` (scenario 1). |
| `PR #N release preflight is failing` | Open the failed **Book CI** run. Fix the PR, or re-run failed jobs if the failure was transient. |
| `PR #N was approved but is still open` | Scenario 6. |
| `PR #N changed after your approval` | Scenario 4. Approve the new head. |
| `<workflow> failed` | Open the run. Re-run failed jobs, or use scenario 11 (billing), 12 (release) or 13 (deploy). |
| `<run> has been queued for N days` | An orphaned run. `gh run cancel <run-id>`. |
| `N content file(s) changed since vX.Y.Z without a release` | Scenario 10: content reached `main` without the controller. |
| `Site is not responding` | Scenario 13, then [DEPLOY.md](DEPLOY.md) and [CUSTOM-DOMAIN.md](CUSTOM-DOMAIN.md). |

### Before you open any PR

```sh
python3 -m unittest discover -s tests
python3 tools/lint_manuscript.py
python3 tools/validate_release.py change --root . --base-ref origin/main   # content PR: prints the tag; tooling-only: a note that no release is needed
python3 tools/build.py all                                                 # all editions, as CI builds them
```