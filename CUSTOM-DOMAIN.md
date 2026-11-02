# Custom domain: agent-ready-web.salnikov.no

How to serve the web edition at **https://agent-ready-web.salnikov.no** from the Azure Static Web App that `./infra/deploy.sh` creates. You do two things: add one DNS record, then tell Azure about the domain. The certificate is free and automatic.

The site is already built for this address: every page's `<link rel="canonical">`, `sitemap.xml` and `robots.txt` use `https://agent-ready-web.salnikov.no` (`site_url` in `tools/book.json`). Until the domain is bound, those links point at a name that doesn't resolve yet, so bind it soon after the first deploy.

## What DNS looks like today

Read-only lookups on 2026-11-02 at 21:17 UTC through Cloudflare's public resolver 1.1.1.1 (DNS over HTTPS, `https://cloudflare-dns.com/dns-query`; `dig NS salnikov.no`, `dig agent-ready-web.salnikov.no`, `dig CAA salnikov.no` give the same answers):

| Lookup | Answer | What it means |
| --- | --- | --- |
| `NS salnikov.no` | `gina.ns.cloudflare.com`, `stan.ns.cloudflare.com` | The zone is hosted on **Cloudflare DNS**. The record goes in the Cloudflare dashboard. |
| `agent-ready-web.salnikov.no` | `NXDOMAIN` | The name doesn't exist yet. Nothing to remove, nothing to conflict with. |
| `CAA salnikov.no` | none | Any certificate authority may issue certificates, so Azure's managed certificate isn't blocked. |
| `A salnikov.no`, `CNAME www.salnikov.no` | GitHub Pages addresses, `webmaxru.github.io` | Your apex and `www` sites. Not touched by any of this. |
| `CNAME webmcp.salnikov.no` | `brave-sea-02f4e5103.5.azurestaticapps.net` | The WebMCP book's web edition, set up exactly the way this page describes. The new record sits next to it. |

## Steps

### 1. Deploy and note the default hostname

```bash
./infra/deploy.sh
```

The last line prints `https://<something>.azurestaticapps.net`. That host name (without `https://`) is the CNAME target. Later you can read it with:

```bash
az staticwebapp show -n swa-agent-ready-web -g rg-agent-ready-web --query defaultHostname -o tsv
```

### 2. Add the CNAME in Cloudflare

Cloudflare dashboard > salnikov.no > DNS > Records > **Add record**:

| Field | Value |
| --- | --- |
| Type | `CNAME` |
| Name | `agent-ready-web` |
| Target | the default hostname from step 1, e.g. `nice-sea-0123abc.6.azurestaticapps.net` |
| Proxy status | **DNS only** (grey cloud). Not proxied. |
| TTL | Auto (Cloudflare sets 300 seconds for Auto on DNS-only records), or 1 hour once it works |

Check that the public DNS sees it (it should print the azurestaticapps.net name):

```bash
dig +short CNAME agent-ready-web.salnikov.no @1.1.1.1
```

Why DNS only: Azure validates the domain by looking up this CNAME and later renews the certificate by reaching the site directly. A proxied (orange-cloud) record hides the CNAME behind Cloudflare's own addresses, and validation or renewal then fails. Static Web Apps already serves the content from its own global edge, so the proxy adds nothing here.

### 3. Add the domain to the Static Web App

Pick one. All three do the same thing.

**a. The deploy script** (checks the CNAME first, binds, waits for the certificate, then requests the page):

```bash
./infra/deploy.sh --upload-only --no-build --custom-domain agent-ready-web.salnikov.no
# Windows: pwsh ./infra/deploy.ps1 -UploadOnly -NoBuild -CustomDomain agent-ready-web.salnikov.no
```

**b. Azure CLI:**

```bash
az staticwebapp hostname set -n swa-agent-ready-web -g rg-agent-ready-web --hostname agent-ready-web.salnikov.no
```

CNAME validation is the default for this command (`--validation-method cname-delegation`). It waits for validation; add `--no-wait` to return at once.

**c. Azure portal:** your Static Web App > Settings > **Custom domains** > **+ Add** > **Custom domain on other DNS** > enter `agent-ready-web.salnikov.no` > Next > Hostname record type **CNAME** > **Add**.

(Infra-as-code alternative: set `param customDomain = 'agent-ready-web.salnikov.no'` in `infra/main.bicepparam` and run `az deployment group create -g rg-agent-ready-web -f infra/main.bicep -p infra/main.bicepparam`. The deployment fails if the CNAME doesn't resolve yet, which is why the script uses the CLI route.)

### 4. Validation and the certificate

- A subdomain such as `agent-ready-web.salnikov.no` is validated through its **CNAME** record. The **TXT** method (`dns-txt-token`, a `_dnsauth` record) is for apex domains, or for moving a domain that is already serving traffic elsewhere without downtime. Neither applies here.
- Azure checks that the CNAME is "available in the global DNS system". Microsoft's page says propagation depends on the TTL and "may take several days". For a brand-new record with a 300-second TTL it is normally much faster; the script waits 10 minutes and then leaves Azure to finish in the background.
- Follow the status (`Validating` / `Adding` / `Ready` / `Failed`):

  ```bash
  az staticwebapp hostname list -n swa-agent-ready-web -g rg-agent-ready-web -o table
  az staticwebapp hostname show -n swa-agent-ready-web -g rg-agent-ready-web --hostname agent-ready-web.salnikov.no --query "{status:status, error:errorMessage}"
  ```

- **TLS is automatic and free.** Static Web Apps creates and renews a managed certificate for the custom domain. Renewal needs the domain to keep resolving to the app over the public internet, which is one more reason to keep the record DNS only.
- The Free plan allows **2 custom domains per app**, so this one fits.

### 5. Make it the default domain (recommended)

Portal > your Static Web App > **Custom domains** > select `agent-ready-web.salnikov.no` > **Set default**. From then on, requests to the `azurestaticapps.net` address redirect to `https://agent-ready-web.salnikov.no`, so search engines and readers see one address. Only one domain can be the default. (The `az staticwebapp hostname` commands have no option for this; Microsoft's page describes the portal.)

### 6. Check it

```bash
dig +short CNAME agent-ready-web.salnikov.no @1.1.1.1      # -> <name>.azurestaticapps.net
curl -I https://agent-ready-web.salnikov.no/               # -> HTTP/2 200, with strict-transport-security and content-security-policy headers
curl -sI https://agent-ready-web.salnikov.no/nope | head -1 # -> HTTP/2 404 (the book's own 404 page)
curl -sI https://agent-ready-web.salnikov.no/ | grep -i '^link:'               # -> the Link header: index.md, llms.txt, ard.json ...
curl -s -o /dev/null -w '%{http_code}\n' https://agent-ready-web.salnikov.no/.well-known/ard.json  # -> 200
echo | openssl s_client -connect agent-ready-web.salnikov.no:443 -servername agent-ready-web.salnikov.no 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

## Apex vs subdomain

`agent-ready-web.salnikov.no` is a subdomain, so a plain CNAME is all it takes. An apex domain (`salnikov.no` itself) can't have a CNAME in standard DNS; it needs an ALIAS/ANAME record or CNAME flattening (Cloudflare does flattening at the apex), TXT validation instead of CNAME validation, or Azure DNS. You don't need any of that here, and your apex keeps pointing at GitHub Pages.

## Troubleshooting

- **Validation fails or hangs, and the record is orange-cloud.** Switch it to DNS only, then delete the domain in Azure (`az staticwebapp hostname delete -n swa-agent-ready-web -g rg-agent-ready-web --hostname agent-ready-web.salnikov.no --yes`) and add it again. The script detects this case: the name answers with A records but no CNAME.
- **"CNAME record is invalid" / a conflict.** A CNAME can't share its name with other records. Make sure there is no A, AAAA or TXT record named `agent-ready-web` in the zone.
- **Typo in the target.** The target must be exactly the app's default hostname, including the region number (`.6.` in the example). Compare it with `az staticwebapp show ... --query defaultHostname`.
- **Certificate never issued after validation.** Check CAA. salnikov.no has no CAA records today, which allows every CA. If you add CAA records later, they must also allow the CA that Azure uses for managed certificates. Microsoft's Q&A answers name DigiCert (`0 issue "digicert.com"`); the Static Web Apps docs pages listed under Sources don't name the issuer, so check the issuer of the certificate on the live site (the `openssl` line above) before you write a CAA record.
- **"Domain is already in use."** A domain can be bound to only one Static Web App per Azure "slice". If you ever move it to a new app, remove it from the old one first.
- **Still stuck.** `az staticwebapp hostname show ... --query errorMessage` gives Azure's reason; the portal's Custom domains page shows the same status.

## After it works

- Set it as the default domain (step 5).
- Nothing to change in the book: `site_url` in `tools/book.json` is already `https://agent-ready-web.salnikov.no`, and the canonical links, sitemap and robots.txt are generated from it. If you ever pick another address, change `site_url` there and redeploy.
- Optionally raise the CNAME's TTL to 1 hour.
- If you remove the site later (`./infra/teardown.sh`), delete the CNAME too, so the name doesn't point at a hostname that no longer exists.

## Sources

Microsoft Learn, read 2026-11-02:

- Custom domains in Azure Static Web Apps (apex vs subdomain, TXT for zero-downtime moves, the slice rule): https://learn.microsoft.com/en-us/azure/static-web-apps/custom-domain
- Set up a custom domain with an external DNS provider (CNAME record, portal steps, "may take several days"): https://learn.microsoft.com/en-us/azure/static-web-apps/custom-domain-external
- Set up an apex domain with an external provider: https://learn.microsoft.com/en-us/azure/static-web-apps/apex-domain-external
- Manage the default domain (Set default): https://learn.microsoft.com/en-us/azure/static-web-apps/custom-domain-default
- `az staticwebapp hostname` (set/show/list/delete, `--validation-method {cname-delegation, dns-txt-token}`): https://learn.microsoft.com/en-us/cli/azure/staticwebapp/hostname
- Hosting plans (2 custom domains on Free, free auto-renewing certificates): https://learn.microsoft.com/en-us/azure/static-web-apps/plans
- `Microsoft.Web/staticSites/customDomains` template reference (`validationMethod`): https://learn.microsoft.com/en-us/azure/templates/microsoft.web/staticsites/customdomains

Other sources:

- Cloudflare, Time to Live (Auto = 300 seconds on DNS-only records): https://developers.cloudflare.com/dns/manage-dns-records/reference/ttl/
- Microsoft Q&A on CAA and DigiCert (community answers, not product docs): https://learn.microsoft.com/en-us/answers/questions/1095144/cannot-verify-custom-domain-for-azure-static-web-a
- Microsoft Q&A on Cloudflare proxying breaking validation and renewal: https://learn.microsoft.com/en-us/answers/questions/5517292/azure-static-web-app-certificate-renewal-failing-t
