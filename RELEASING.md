# Releasing

Each release of *Agent-Ready Websites in Action* is a Git tag `vX.Y.Z` on the squash-merge commit of an owner-approved content pull request. The **Release book** workflow builds the book from that commit, tags it and publishes a GitHub Release with four files, plus their checksums:

- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z.pdf`: the PDF, 7 × 9.25 in (reading, Leanpub).
- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z-print-7.5x9.25.pdf`: the paperback interior, 7.5 × 9.25 in (KDP). Same text block and page count as the PDF.
- `Agent-Ready-Websites-in-Action-Maxim-Salnikov-vX.Y.Z.epub`: EPUB 3, checked with EPUBCheck.
- `Agent-Ready-Websites-in-Action-HTML-vX.Y.Z.zip`: the web edition, readable offline (open `index.html`).
- `SHA256SUMS.txt`.

The release notes are the version's section of [`CHANGELOG.md`](CHANGELOG.md). After a stable release is published, the workflow asks `deploy-swa` to put that tag on the web edition at https://agent-ready-web.salnikov.no (see [`DEPLOY.md`](DEPLOY.md)). Everything runs on the built-in `GITHUB_TOKEN`; no secrets are needed for the release itself.

```text
/update-book check ─► /update-book prepare ─► content PR ─► Book release preflight (green)
        ─► owner approval of the exact head ─► Release approved book: squash-merge
        ─► Release book: build, annotated tag, draft, upload, publish ─► deploy-swa: web edition
```

The sections below explain each step. [Scenarios](#scenarios-what-to-do-when) walks through the situations you will actually meet, with commands.

## Book release flow contract v1

Every book repository follows the same release flow. A repository conforms when `tests/test_flow_contract.py` passes and each rule below is covered by a test in that repository's own suite.

1. **Workflow surface (same names everywhere).**
   `ci.yml` named "Book CI" with the aggregate job "Book release preflight"; `book-approval-signal.yml` named "Book approval signal"; `approved-book.yml` named "Release approved book"; `release.yml` named "Release book"; one deploy workflow, `deploy-swa.yml` or `deploy-pages.yml`.
2. **Controller.**
   Triggers: `workflow_run` of "Book approval signal" and "Book CI", `issue_comment`, schedule `17,47 * * * *`, and `workflow_dispatch` with the input `pr`. Jobs run only from `main`. Workflow `permissions: {}` with least privilege per job. Concurrency group `approved-book`, no cancel. Validators always run from `main`, never from the pull request.
3. **Eligibility.**
   The pull request is open, not a draft, from the same repository, targets `main`, is mergeable, and its head contains the current `main`. Its files are content-only under the book's allowlist. "Book release preflight" is green on the exact head, and the version, CHANGELOG and evidence checks pass.
4. **Authorization.**
   Someone else's pull request: an owner Approve review on the current head. The owner's own pull request: an owner comment `/release-book <40-character head SHA>`. A later push, a CHANGES_REQUESTED review, a dismissed review or an edited or deleted comment revokes it. A non-owner never authorizes.
5. **Merge.**
   A squash merge conditioned on the approved head SHA. The controller then dispatches `release.yml`, because merges made with `GITHUB_TOKEN` trigger no workflows.
6. **Release.**
   `release.yml` is dispatch-only, with the inputs `pr`, `head_sha`, `base_sha`, `merge_sha` and `tag`, and the concurrency group `book-publish`. Steps: plan, build from the merge commit, annotated tag, draft release, upload assets, publish, deploy the released tag, smoke test. Never clobber assets and never move a tag. A complete release is a no-op. A partial release or a provenance mismatch fails with no writes. Latest goes only to the highest stable version, and prereleases are never Latest. A fix is a new version.
7. **Deploy.**
   Production serves only released editions. A push to `main` deploys only when the content equals the latest published release (the `published-source` job). The release deploys its own tag. A manual dispatch takes a released ref or sha, which is the rollback path.
8. **No other publisher.**
   A tag push, a label or a branch name never publishes. A manual merge to `main` bypasses the controller; the fix is a catch-up pull request with a higher version.
9. **Pins.**
   Runner `ubuntu-24.04`. `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`, `actions/download-artifact@v8` (a full commit SHA with a trailing `# v7.x.y` version comment is acceptable).

### Per-book settings

| Setting | Agent-Ready Websites in Action |
| --- | --- |
| Format/build | Markdown ordered by `manuscript/Book.txt`; `python tools/build.py all` builds HTML zip, EPUB 3, reading PDF (7 × 9.25 in) and print PDF (7.5 × 9.25 in). Lint, EPUBCheck, site/CSP checks and Lighthouse agentic-browsing audit stay required. |
| Version file, scheme and tags | `tools/book.json`: SemVer `X.Y.Z`, tag `vX.Y.Z`; review copies `X.Y.Z-rc.N` / `vX.Y.Z-rc.N`. Release metadata keys: `version`, `edition`, `checked_as_of`, `year`. |
| Content allowlist | `tools/release_policy.py`: `manuscript/`, `editorial/`, `validation/`, `figures/`, `VALIDATION.md`; `CHANGELOG.md` and the metadata keys may accompany content. Tooling-only and mixed PRs never auto-merge. |
| Evidence rules | Changed chapters/appendices with a validation table need a changed editorial log and fresh added/updated `Retrieved` rows. Validation changes also require `VALIDATION.md`; content symlinks/submodules are rejected. The date window starts at the base commit and permits tomorrow UTC for time-zone tolerance. |
| Deploy target and domain | Azure Static Web Apps Free, `deploy-swa.yml`, https://agent-ready-web.salnikov.no (live). Token absence skips cleanly. Only published **stable** editions deploy; prereleases never reach production, including by manual dispatch. |
| Published-source comparison | Main's trusted Python policy compares every content-allowlisted path, `CHANGELOG.md` and release-metadata keys to the highest published stable release. Tooling/theme/build-configuration differences alone may deploy; any content or evidence difference skips. No duplicated YAML content-path list. Released refs resolve to immutable SHAs before checkout; legacy `v1.0.0` and `v2.0.0` remain rollback targets. |
| Catch-up PR rules | A higher version than the unreleased main version and the latest stable release, dated CHANGELOG notes covering the entire unreleased change, and a genuine allowlisted content/evidence update. Version/CHANGELOG alone are tooling-only and fail. Existing evidence rules still apply; no special catch-up bypass. |
| Upstream-update scouting | `/update-book check` calls `tools/check_upstream.py` for cited-source changes; `/update-book prepare` updates affected chapters and their evidence. Preparation stops at a local commit unless the owner requests a PR. |

The contract suite is unchanged across the four books. `tests/test_book_release.py` covers approval, merge, provenance, no-write recovery and production-source decisions with a loopback GitHub API and a strict `gh` shim; its CLI rehearsal also uses a temporary Git repository. `tests/test_validate_release.py` covers version/evidence rules, and `tests/test_workflows.py` checks trusted-main execution and workflow references. Run everything with `python -m unittest discover -s tests -v`.

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
   - A new push needs a new approval. Editing or deleting an authorization comment revokes it; post a fresh comment rather than editing one.
   - A later "changes requested" review, or a dismissed review, blocks the release until he approves again. A `/release-book` comment then counts only if it comes after that barrier.
5. **Release approved book** (`.github/workflows/approved-book.yml`) does the rest. It starts on the review, on the comment, when Book CI finishes, on a 30-minute scan that catches missed events, or by hand with the pull request number. It:
   - checks that the pull request is from this repository, targets `main`, is not a draft, is mergeable, is not behind `main` and is content-only, and that Book release preflight passed on that exact head;
   - runs `main`'s validator and lint against the head (a pull request cannot change the rules it is checked by);
   - squash-merges only if the head is still the approved SHA;
   - dispatches **Release book** with the pull request, head, base and merge SHAs and the tag. A merge made with the built-in token starts no other workflows, so the dispatch is explicit.
6. **Release book** (`.github/workflows/release.yml`) publishes the version:
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

The tests are in `tests/` (stdlib `unittest`, loopback only, no live GitHub writes): `python3 -m unittest discover -s tests`.

## Recovery

- **Before the merge** (approval not picked up, a transient failure): **Actions → Release approved book → Run workflow** with the pull request number.
- **After the merge, before any tag/release exists** (for example, a build failed): **Actions → Release book → Run workflow** on `main` with the pull request number. The same provenance checks run.
- **Existing tag/release:** a complete publication is a successful no-op, including no deploy. A tag-only state, missing tag, draft, missing asset, or forged provenance fails without writes. Leave the partial version unchanged and release a new version. Retry only the deploy with `deploy-swa.yml` when publication succeeded.
- **Published files are never replaced and tags are never moved.** A fix to a published version, even a build-only fix, is a new patch version through a new pull request.

## Changes from the earlier flow

- Merging a `release/` branch, the `release` label and pushing a tag no longer publish anything. Every release goes through the owner's approval.
- **Run workflow** on Release book never replaces assets, even in a draft. It publishes a fresh approved release or confirms an already complete one.
- The tag is created by the workflow, after the build, as an annotated tag. You no longer tag by hand.
- `v1.0.0` and `v2.0.0` were published by the earlier flow. They stay as they are, and they are not rebuilt.

The repository is public. **A manual merge bypasses the approval controller**, regardless of repository visibility or rulesets. Release book refuses a human merge, and `published-source` prevents unreleased content from reaching production. Use a catch-up PR with a higher version through the normal flow.

## Roll back the web edition

**Actions → deploy-swa → Run workflow**, with `ref` set to an earlier tag. The PDF and EPUB of every version stay on their GitHub Releases.

## Fix a bad release

Don't move or reuse a tag that people may have downloaded. Fix the problem through a new content PR, add a patch entry to CHANGELOG.md, and release `vX.Y.(Z+1)`. Existing tags and published assets stay unchanged.

## What the build reads

The editions are built only from `manuscript/` (the text, `Book.txt` and the images in `manuscript/resources/images/`), `tools/book.json` (title, version, copyright lines, links, agent-ready settings), `CHANGELOG.md` (the web edition's Release history page and `releases.xml` feed) and `theme/` (all styling). `figures/` holds the sources of the figures; render them into `manuscript/resources/images/` before a release.

## Scenarios: what to do when

Commands use the [GitHub CLI](https://cli.github.com/) (`gh`) from a clone of this repository and work in bash and PowerShell, except `python3`, which is `python` on Windows. `N` is the pull request number and `vX.Y.Z` a tag.

### What triggers what

| Event | What happens | Release? |
| --- | --- | --- |
| PR opened or pushed | **Book CI** runs the lint, the four editions, EPUBCheck, `check_site`, Lighthouse and the release checks. Its **Book release preflight** job is the gate. | No |
| Owner **Approve** review, or an owner `/release-book <SHA>` comment | **Release approved book** re-checks everything and squash-merges the approved head. | Yes, through **Release book** |
| Book CI or approval-signal run finishes, or the half-hourly scan | The controller looks for an approved PR it missed. It never approves anything itself. | Only if a valid approval exists |
| **Release approved book → Run workflow** with `pr` | Same re-check for one PR. | Only if a valid approval exists |
| Push a tag, add a label, press **Merge** | Nothing in the release flow. | **No** |
| Push to `main` | **deploy-swa / published-source** compares content to the highest published stable edition. Only matching content deploys; tooling differences are allowed. Unreleased changes skip cleanly. | **No** |
| **Release book → Run workflow** on `main` | Checks the merged PR's provenance; a new release builds before tagging. A complete release is a no-op; a partial release fails without writes. | Only for an eligible, previously unpublished merge |
| New stable release published, or release's explicit deploy dispatch | **deploy-swa** builds that released tag, not a newer main commit. | Already published |
| **deploy-swa → Run workflow** on `main`, with `ref` | Accepts only a published stable tag or its full SHA; this is the rollback path. | No |

The web edition and downloads share the release boundary. Only the controller's approved squash-merge can produce a new publication; an ordinary main push cannot put unreleased book content online.

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

**Result:** the PR is squash-merged, `vX.Y.Z` is an annotated tag on the merge commit, the release has the PDF, print PDF, EPUB, HTML zip and `SHA256SUMS.txt`, it is Latest if it is the highest stable version, and `deploy-swa` puts the tag on https://agent-ready-web.salnikov.no. The run summary of **Release book** says **Web edition deployed** after the smoke test succeeds.

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

An approval counts only for the head it was given on. A push after approval, a **Request changes** review, a dismissed review, or editing/deleting the authorization comment voids it. Nothing merges until you approve again (a new **Approve** review, or a fresh `/release-book <SHA>` comment after any review barrier). An old SHA or edited comment is ignored.

### 5. The branch is behind `main`

The head must include current `main`, and GitHub must report the PR as mergeable. Update the branch and approve again:

```sh
gh pr update-branch N
```

If GitHub reports a conflict, resolve it on the branch first.

### 6. Approved, but the PR is still open

Look at the latest **Release approved book** run for the cause: failing preflight, a head that moved, a branch behind `main`, a conflict, or a run that never started. Fix that, or just run the controller for this PR:

```sh
gh workflow run approved-book.yml -f pr=N --ref main
```

If the run died within a second with no steps, see [Runs that fail without starting](#11-runs-that-fail-without-starting).

### 7. Tooling, docs and workflow changes

A PR that touches only files outside the content allowlist (`tools/` other than the release keys of `book.json`, `theme/`, `.github/`, `infra/`, `README.md`, `RELEASING.md`, tests) is **tooling-only**. It must not change `version`, `edition`, `checked_as_of` or `year` in `tools/book.json`, and it must not add a CHANGELOG version section: `validate_release.py` fails it with `a tooling-only change must not change release metadata`. It never releases, and the controller never merges it. Merge it yourself when CI is green. Its main push may rebuild using the new tooling only if the trusted content comparison matches the latest published stable release. If main already carries unreleased book changes, deployment skips.

### 8. Mixed content and tooling

A PR that changes both content and tooling passes CI, but the controller never merges it (`controller never merges mixed changes automatically. Split the pull request.`). Split it into two PRs: tooling first (merged by you), then the content PR.

### 9. Review copy (prerelease)

Use a prerelease version such as `2.1.0-rc.1` for a copy to share before the real edition. The PR still goes through scenario 1 and still merges into `main`. The release is marked pre-release, is never Latest, and **Release book** reports that it was not deployed. The main-push gate also keeps that prerelease content off production; manual dispatch refuses prereleases. To graduate it, open a new content/evidence PR that sets `2.1.0` and adds a dated CHANGELOG section.

### 10. A manual merge by mistake

Pressing **Merge** on a content PR, or merging from the command line, bypasses the controller. The effects:

- The web edition stays at its published version: **published-source** skips the unreleased content.
- **No tag, no release, no downloads.**
- **Release book** refuses it, because the merge was not made by the controller's built-in token.
- The version the PR carried is now on `main` unreleased. A content PR must change `version`, so that version number can no longer be used (`content changed without a new version (still 2.1.0)`).

Fix it with a catch-up PR. For example, if `main` carries `2.1.0` but the latest tag is `v2.0.0`:

1. Branch from `main`, set `version` in `tools/book.json` to `2.1.1` and add a dated `## [2.1.1] - YYYY-MM-DD` section to `CHANGELOG.md`. Move the unreleased `2.1.0` notes under it so the release notes describe the whole edition.
2. **Include a genuine content/evidence update**: a correction you want anyway, or a re-check recorded in the allowlisted editorial/validation files (and `VALIDATION.md` when validation changes). Version and CHANGELOG alone are tooling-only and fail. Evidence files are content under this repository's policy; never fabricate evidence merely to pass the gate.
3. Check it: `python3 tools/validate_release.py change --root . --base-ref origin/main` prints `release check passed: content change for v2.1.1`.
4. Open the PR and authorize it as in scenario 1.

### 11. Runs that fail without starting

Inspect the run's annotations and event/ref before retrying:

```sh
gh run view RUN_ID
gh run view RUN_ID --log-failed
```

Controller and publisher jobs deliberately skip dispatches from any branch other than `main`. Select `main` for recovery. For a transient CI failure, `gh run rerun RUN_ID --failed` repeats failed jobs; for an eligible PR missed by the controller, use scenario 6. Do not change repository settings or bypass a failed gate.

### 12. The release failed after the merge

The controller merged the PR but the build failed **before any tag or draft was created**. Run **Release book** for it:

```sh
gh workflow run release.yml -f pr=N --ref main
```

To confirm an existing approved publication, use `gh workflow run release.yml -f tag=vX.Y.Z --ref main`. A complete release is a no-op, with no deploy. A tag-only state, a draft (even with all assets), a missing tag, incomplete assets or a provenance mismatch fails without writes. Leave it unchanged and create a higher version through the normal content PR flow. Use scenario 13 when publication succeeded and only deployment needs retrying. The legacy `v1.0.0`/`v2.0.0` releases predate this provenance contract: do not run publisher recovery on them; rollback remains supported.

### 13. Only the deploy failed

The release is published and complete, but its web edition was not deployed: **deploy-swa** failed, or the run summary says **Web edition NOT deployed** or *not confirmed*. Do not re-run **Release book**. Check that the Azure token exists, then deploy the tag:

```sh
gh secret list | grep AZURE_STATIC_WEB_APPS_API_TOKEN
gh workflow run deploy-swa.yml -f ref=vX.Y.Z --ref main
```

In PowerShell, use `gh secret list | Select-String AZURE_STATIC_WEB_APPS_API_TOKEN`. If the secret is missing, see [DEPLOY.md](DEPLOY.md). If the site is up but the domain does not answer, see [CUSTOM-DOMAIN.md](CUSTOM-DOMAIN.md).

### 14. Roll back the web edition

Downloads stay as they are; only the site changes:

```sh
gh workflow run deploy-swa.yml -f ref=v1.0.0 --ref main
```

Only published stable tags (including `v1.0.0` and `v2.0.0`) or their full commit SHAs are accepted; branches, unpublished tags and drafts fail. A later eligible push to main or a new stable release may roll forward again, so correct the underlying problem through a new content PR.

### 15. A published release is wrong

Do not edit the release, replace its assets or move its tag. Fix the problem, add a patch version through scenario 1 and release it. Roll back production with scenario 14 while that fix is prepared.

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
| `<workflow> failed` | Open the run. Use scenario 11 (startup/CI), 12 (release) or 13 (deploy); never retry partial publication as if it were a fresh release. |
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