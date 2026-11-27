# Deploying the web edition to Azure Static Web Apps

The free web edition of the book (`python3 tools/build.py site` → `dist/site/`) is live at https://agent-ready-web.salnikov.no on an **Azure Static Web App on the Free plan**. It's uploaded with the app's deployment token, so it doesn't depend on GitHub Pages or Azure's GitHub app. This repository is public.

## Prerequisites

- An Azure subscription where you can create a resource group (Contributor or Owner).
- **Azure CLI**, a current release (the latest when this was written: 2.91.0; `az upgrade` updates it), logged in with `az login`. The script installs Bicep through `az bicep install` if it's missing.
- **Python 3.11+** for the build (`tools/requirements.txt` is installed into `.venv/` by the script).
- **Node.js 20+** (18 is the minimum) for the upload: the script runs the Static Web Apps CLI `2.1.0` through `npx`, and on its first upload the CLI downloads Microsoft's deployment client (about 70 MB, kept in `~/.swa`).
- Optional: **GitHub CLI** (`gh auth login`) with admin rights on `webmaxru/agent-ready-web`, so the script can store the deployment token as a repository secret. Without it, the script prints the two manual steps.
- Windows: use `infra/deploy.ps1` (Windows PowerShell 5.1 or PowerShell 7). macOS/Linux/WSL: `infra/deploy.sh`.

## The one command

```bash
./infra/deploy.sh
```

```powershell
pwsh ./infra/deploy.ps1          # or: powershell -ExecutionPolicy Bypass -File .\infra\deploy.ps1
```

It shows the subscription and asks before changing anything (`--yes` / `-Yes` skips the question). Then: tools and login check → resource group `rg-agent-ready-web` → `infra/main.bicep` (Static Web App `swa-agent-ready-web`, Free, West Europe) → site build → pre-upload check (`infra/check_site.py`: Free-plan limits, and that the Content-Security-Policy allows exactly what the pages load) → upload to production → GitHub secret → `curl` checks that `/` answers 200 and a missing page answers 404 → prints the URL.

Safe to re-run. Useful options (`--help` lists all):

| bash | PowerShell | What |
| --- | --- | --- |
| `--custom-domain agent-ready-web.salnikov.no` | `-CustomDomain ...` | Bind the domain after checking its CNAME. See [CUSTOM-DOMAIN.md](CUSTOM-DOMAIN.md). |
| `--upload-only` | `-UploadOnly` | App exists: build and upload only. |
| `--no-build` | `-NoBuild` | Upload `dist/site` as it is. |
| `--infra-only` | `-InfraOnly` | Azure resources + GitHub secret, no build or upload. |
| `--build-only` | `-BuildOnly` | Build locally, touch nothing in Azure. |
| `--skip-github` | `-SkipGitHub` | Don't set the GitHub secret. |
| `--budget-email you@example.com` | `-BudgetEmail ...` | Add a monthly budget alert (default 1 per month in your billing currency). |
| `--subscription <id>`, `--location`, `--resource-group`, `--swa-name`, `--repo` | same names | Override the defaults. |

Static Web Apps accepts only `westeurope`, `eastus2`, `centralus`, `westus2` and `eastasia` as the resource's region (West Europe is the closest to Norway). The content itself is served from a global edge.

## What it creates and what it costs

| Resource | Notes |
| --- | --- |
| Resource group `rg-agent-ready-web` | Holds everything below; teardown deletes it. |
| Static Web App `swa-agent-ready-web`, **Free** plan | No repository link, preview environments off. |
| Custom domain binding (optional) | Free managed TLS certificate. |
| Budget `budget-agent-ready-web` (optional) | Email at 80 % actual and 100 % forecast. Alerts only. |
| GitHub secret `AZURE_STATIC_WEB_APPS_API_TOKEN` | On `webmaxru/agent-ready-web`. |

**Cost: 0.** The Free plan has no charge, and overage bandwidth is listed as unavailable on Free, so there is nothing that can be billed. Free plan limits ([quotas](https://learn.microsoft.com/en-us/azure/static-web-apps/quotas), [plans](https://learn.microsoft.com/en-us/azure/static-web-apps/plans), read 2026-11-02):

- 100 GB bandwidth per month per subscription, overage "unavailable" on Free
- 250 MB storage per environment (500 MB across all environments), 15,000 files, 30 MB request size
- 2 custom domains per app, free auto-renewing SSL certificates
- 10 Free apps per subscription, 3 preview environments per app
- No SLA

The current site is about 14 MB and 90 files, well inside these limits; `infra/check_site.py` fails the upload before a limit is hit.

## Secrets

Exactly one: **`AZURE_STATIC_WEB_APPS_API_TOKEN`**, the Static Web App's deployment token, as a GitHub Actions repository secret.

- The script reads it with `az staticwebapp secrets list` into memory and pipes it to `gh secret set`. It's never printed, never on a command line, never in a file.
- By hand: `az staticwebapp secrets list -n swa-agent-ready-web -g rg-agent-ready-web --query properties.apiKey -o tsv | pbcopy` (Windows: `| Set-Clipboard`), or Portal → the Static Web App → Overview → **Manage deployment token** → copy. Then GitHub → repo Settings → Secrets and variables → Actions → **New repository secret**, name `AZURE_STATIC_WEB_APPS_API_TOKEN`.
- If it ever leaks: Portal → Manage deployment token → **Reset token**, then re-run `./infra/deploy.sh --infra-only` to store the new one.

No other secrets, variables or Azure credentials are used. The workflow uses only this token.

## How GitHub deploys after the first run

`.github/workflows/deploy-swa.yml` builds the site and uploads it with `Azure/static-web-apps-deploy@v1` (pinned to a commit) on:

- a push to `main`, **only** when `published-source` confirms content, evidence, CHANGELOG and release metadata match the highest published stable release; tooling/theme differences alone are allowed;
- a dispatch from **Release book** after publishing the highest stable edition. It passes the new tag as `ref`, sets `latest_only` so the queued run rechecks that tag, and waits for the exact run returned by the API. There is no separate `release: published` trigger;
- **Run workflow** on `main`, with a required `ref` that is a published stable tag or its full commit SHA.

The gate and content allowlist run from trusted `main` code, not the requested ref; checkout uses the immutable SHA the gate returns. Branch names, unpublished tags, drafts and prereleases are refused for manual dispatch. A manually merged content PR therefore cannot put unreleased text online.

Without the secret (for example in a fork or fresh setup), the standalone workflow uploads nothing and stays green. Its summary says **Web edition NOT deployed**. The **Release book** caller fails delivery: a green workflow without a successful Azure upload and smoke test is not proof of deployment. A missing run ID or timeout also leaves delivery unconfirmed; inspect Actions before retrying. The current production token and domain are configured; [CUSTOM-DOMAIN.md](CUSTOM-DOMAIN.md) documents setup and recovery. Runs never overlap (concurrency group `swa-production`). The smoke-test summary shows the URL, `/`, missing-page and agent-file status codes.

## Rolling back

Actions → **deploy-swa** → **Run workflow** on `main` → `ref` = the published stable release tag to go back to (for example `v1.0.0`) → Run. It resolves the tag to its commit, builds it and uploads it to production. Roll forward the same way with a newer published tag. A main push rolls forward only if its book content passes the published-source gate.

Locally: `git checkout v1.0.0 && ./infra/deploy.sh --upload-only` (Windows: `git checkout v1.0.0; pwsh ./infra/deploy.ps1 -UploadOnly`).

## Tear down

```bash
./infra/teardown.sh                          # lists the group's contents, asks you to type its name
./infra/teardown.sh --remove-github-secret   # also removes the GitHub secret
```

```powershell
pwsh ./infra/teardown.ps1 [-RemoveGitHubSecret]
```

It deletes the resource group `rg-agent-ready-web` with the Static Web App, its domain binding and the budget. Your DNS record isn't touched: delete the `agent-ready-web` CNAME in Cloudflare yourself.

## Files

| File | What |
| --- | --- |
| `infra/deploy.sh`, `infra/deploy.ps1` | The one command (bash / PowerShell twins). |
| `infra/teardown.sh`, `infra/teardown.ps1` | Delete everything. |
| `infra/main.bicep` | Static Web App (Free) + optional custom domain + optional budget module. |
| `infra/budget.bicep` | Monthly budget with email alerts. |
| `infra/main.bicepparam` | Parameters for a direct `az deployment group create` without the script. |
| `infra/check_site.py` | Pre-upload check (limits, CSP vs. pages); `--update-csp` refreshes the inline-script hashes. |
| `staticwebapp.config.json` | Headers (CSP, HSTS, nosniff, referrer and permissions policy), caching, the 404 page, MIME types. Copied into `dist/site/` by the build. |
| `.github/workflows/deploy-swa.yml` | Published-source gate, build, upload and smoke check on main pushes and explicit dispatches. |
| `.github/workflows/infra.yml` | No-login validation of the infra files: Bicep build + lint, PowerShell parse (5.1 and 7), PSScriptAnalyzer, ShellCheck. |
| `CUSTOM-DOMAIN.md` | agent-ready-web.salnikov.no step by step. |
