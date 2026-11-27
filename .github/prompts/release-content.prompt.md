---
description: Prepare a new version of Agent-Ready Websites in Action as a local commit or, when asked, open its content pull request for the owner's approval, which then merges and releases it automatically.
---

# Release a book version

A book version (`tools/book.json` `version`, tag `vX.Y.Z`) versions **reader-facing content** only. Tooling, workflow and theme-only changes never get a version and are never released as one. Use `/update-book` first when chapters still need research and edits.

## Inputs and boundary

- **Mode:** `prepare` by default. `open-pr` only when the user asks for it.
- **Version:** `X.Y.Z` per `RELEASING.md`. It must be higher than the latest stable tag. A review copy is `X.Y.Z-rc.N`, published as a GitHub pre-release.
- **Date:** `YYYY-MM-DD`, normally today.

`prepare` means local files and a local commit only. Nothing in this prompt merges, tags, publishes or dispatches a workflow. The owner's approval of the pull request is the explicit authorization for the automatic merge and release.

## Prepare

1. **Establish the version story.** Read the latest published release, the local tags, `tools/book.json`, the top of `CHANGELOG.md` and the actual diff against `main`. Fetch missing tags without force.
2. **Check the evidence.** Every changed chapter needs:
   - its editorial-log entry;
   - its validation rows, with real retrieval dates;
   - an updated `VALIDATION.md`.
   
   Missing evidence means the version is not ready, even if the build is green. Never invent a check.
3. **Set the metadata together.**
   - In `tools/book.json`, set `version`, `edition` if it changes, and `checked_as_of` (the month the sources were checked, as the copyright page prints it). Set `year` only if it changes. Change no other key.
   - Add a top section to `CHANGELOG.md`, in the existing style:
     ```markdown
     ## [X.Y.Z] - YYYY-MM-DD

     ### Changed

     - Reader-facing change, with the affected chapters.
     ```
     Keep every earlier section.
4. **Run the same checks as the PR check.** Stop on a nonzero exit code:
   ```sh
   python3 tools/lint_manuscript.py
   python3 tools/validate_release.py change --root . --base-ref origin/main
   python3 tools/validate_release.py notes --root . --tag vX.Y.Z --repo webmaxru/agent-ready-web
   python3 tools/build.py all
   ```
   The following are errors, not warnings:
   - a content change without a higher version;
   - a missing or duplicate dated CHANGELOG section;
   - a tag that already exists;
   - missing evidence;
   - a version bump on a tooling-only change.
   
   Open the PDF and check the version and date on the copyright page.
5. **Commit locally.** Stage only this update's files, including new ones. Use the co-author trailer. Report the version, the evidence and the commit. In `prepare` mode, stop here.

## Open the pull request and get it released (`open-pr`)

1. Push a branch to this repository (not a fork) and open a pull request to `main`. Keep it content-only:
   - `manuscript/`, `editorial/`, `validation/`, `figures/`, `VALIDATION.md` and `CHANGELOG.md`;
   - the release-metadata keys of `tools/book.json`.
   
   Any other file makes it a mixed pull request. CI still checks a mixed pull request, but it is never merged or released automatically, so split it.
2. **Book CI** runs the **Book release preflight** check: lint, all four editions, EPUBCheck, `check_site`, the Lighthouse agentic-browsing audit and the release validation.
3. The owner, `webmaxru`, approves the pull request.
   - A pull request by anyone else needs his **Approve** review on the current head.
   - GitHub does not let an author approve his own pull request, so on his own pull request he comments exactly:
     ```text
     /release-book <full 40-character head SHA>
     ```
   - A new push or editing/deleting the authorization comment invalidates the approval.
   - A "changes requested" review by any reviewer, or any review dismissal, blocks the release until he authorizes again after it. Only he authorizes; plain comment reviews neither authorize nor revoke.
4. **Release approved book** takes over:
   - It re-checks the approval, the scope, the head and the CI result.
   - It runs `main`'s validator and lint against the head.
   - It squash-merges only if the head is still that SHA, then dispatches **Release book**.
   
   **Release book** then:
   - checks that the merge is that pull request's squash on `main`;
   - builds every edition from the merge commit;
   - only then creates the annotated tag `vX.Y.Z`;
   - uploads the files to a draft release and publishes it;
   - dispatches **deploy-swa** only for a new highest published stable tag. Delivery requires that exact run to finish successfully with both the upload and smoke test green, with that evidence received before the wait deadline.
5. Confirm the result:
   ```sh
   gh release view vX.Y.Z --repo webmaxru/agent-ready-web --json tagName,isDraft,isPrerelease,assets,url
   gh api repos/webmaxru/agent-ready-web/releases/latest --jq .tag_name
   ```
   Then check the deploy job's run summary. The web edition is live; missing-token or failed-deploy runs still report **not deployed**, never a false success.
6. Upload the PDF, EPUB and print PDF to Leanpub and KDP (`README.md#publishing`).

## Reruns and fixes

- **Before the merge:** re-run **Release approved book** with the pull request number. A scheduled scan also retries recent approvals.
- **After the merge:** re-run **Release book** on `main` with the pull request number, or with the existing tag. It is idempotent:
  - A published release with every file is a successful no-op.
  - Tag-only states, drafts, missing tags and missing files fail with no writes. Use a new version, never repair assets in place.
  - So does a merge or tag that doesn't match an approved pull request.
- **Never clobber or move a tag.** A wrong file or text in a published version is fixed by a new patch version (`vX.Y.(Z+1)`) through a new pull request.
- Never weaken a check, change secrets or settings, or merge by hand to push a release through. A manual merge bypasses the controller; the production gate keeps its unreleased content offline.
