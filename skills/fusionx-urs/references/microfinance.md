# MicroFinance Module — FusionX Reference
*Source: Confluence → FusionX Space → MicroFinance Module (page/256901121)*
*Last synced: June 2026*

## Official Module Name
`MicroFinance Module`
Navigation root: `FusionX Home → MicroFinance` (also accessible via Lending Module settings)
Jira label: `RewardModule` (per Confluence epic table; verify current label with BA team)

## Overview
The MicroFinance Module enables FusionX to handle group-based and individual micro-lending operations. It builds on the Lending Module's core infrastructure, adding center-based group management, center attendance, credit scoring, and microenterprise-specific workflows.

## Sub-Module Hierarchy

### Origination (via Lending Module)
Shares Lending Module origination flows:
- `Lending Module | Loan Origination | Dashboard` — New Lead, Loan Appraisal, Direct Loan Request, Lead Transfer
- ME-specific: Direct loan origination for microenterprise clients

### Loan Account Management (via Lending Module)
- `Lending Module | Loan Account Management | Account Activation`
- `Lending Module | Loan Account Management | Account Maintenance`
  - All standard Lending maintenance screens apply to MF accounts

### Transaction Management (via Lending Module)
- `Lending Module | Transaction Management` — all transaction screens apply

### MicroFinance-Specific Settings
`Lending Module | Master Definition | Micro Finance Definitions | [Screen]`
- Business Centers Setting — define locations/centers for group business activities
- Business Group Settings — organize customers/businesses into microfinance groups
- Credit Score Template Mapping Settings — map credit scoring templates to MF customers
- Credit Score Template Mapping Approval Settings — approval workflow for template mapping
- Credit Score Definition Setting — define credit score criteria and scoring models
- Credit Score Level Define Setting — define score ranges (low/medium/high risk)
- Character Assessment Event Setting — define events for character/creditworthiness assessment

### Center Attendance (via Lending Common Definitions)
`Lending Module | Master Definition | Loan Module Common Definitions | Center Attendance View Settings`

### Reports (MicroFinance-specific)
Navigation: `Lending Module | Reports & Enquiries`
- ME Executions Report — loan/contract executions specific to microenterprise segment
- Monthly Average TR for each ME — average monthly transaction rate per microenterprise
- Staff Incentive Report — staff performance incentives linked to ME portfolio
- Lending Collection BI Report — collection activity for MF accounts
- Branch Wise Loan Portfolio Report — MF portfolio by branch
- Product Wise PAR & Collateral Wise PAR Report — portfolio at risk for MF products

## RBAC Roles
| Role | Permission |
|---|---|
| Standard roles | View, Create, Update |
| Supervisor | Approve, Modify |
| Admin | Full Access |

## Key Jira Label
- MicroFinance epics: label = `RewardModule` (confirm with BA — page references this for MF epics)
- Epic JQL: `type = Epic AND labels = RewardModule`

## E2E Impact Notes (MicroFinance-specific)
- **Built on Lending Module** — all MF loans use Lending Module infrastructure; E2E impacts are a superset of Lending Module impacts
- **Credit Score** — Credit Score Definition and Level settings feed into loan origination eligibility checks for MF clients
- **Center/Group Management** — Business Centers and Business Group settings affect how accounts are grouped for collection and reporting
- **Repayment Schedule Engine** — MF loans often use weekly/fortnightly repayment; Repayment Frequency and Type settings are critical
- **DPD/Arrears** — center-level DPD tracking and group lending dynamics; Portfolio At Risk (PAR) is key metric
- **EOD/Batch** — penal interest, DPD calculation, and collection batch jobs run for MF accounts
- **Reporting** — ME Executions, Monthly Average TR, Lending Collection BI are MF-specific KPI reports
