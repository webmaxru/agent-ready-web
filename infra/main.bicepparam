// Parameters for a direct deployment without the script:
//   az deployment group create -g rg-agent-ready-web -f infra/main.bicep -p infra/main.bicepparam
// infra/deploy.sh and deploy.ps1 pass their own values and do not read this file.
using 'main.bicep'

param swaName = 'swa-agent-ready-web'
param location = 'westeurope'

// Set to 'agent-ready-web.salnikov.no' only after the CNAME record resolves (CUSTOM-DOMAIN.md).
param customDomain = ''

// Set an email to create the optional budget alert.
param budgetContactEmail = ''
param budgetAmount = 1
