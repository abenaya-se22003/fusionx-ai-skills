# Term Deposit Module — FusionX Reference
*Source: Confluence → FusionX Space → Term Deposit Module (page/20742146)*
*Last synced: June 2026*

## Official Module Name
`Term Deposit Module` — abbreviated **TD**
Navigation root: `FusionX Home → Term Deposit`
Jira labels: `TDModule`, `TD_Modul`, `FDModule`

## Sub-Module Hierarchy

### Dashboard
- `Term Deposit | Dashboard`
  - Real-time overview: TD portfolio, maturity schedules, performance metrics, key financial indicators

### Account Management — Opening
- `Term Deposit | Account Management | Opening Account`
  - Initiate new term investment account; capture customer details; compliance verification; link to TD product

### Account Activation
- `Term Deposit | Activate Account | Account Activation and Return`
  - Activate account (commence investment) and calculate return (profit over tenure)
- `Term Deposit | Activate Account | Special Rate Approval and Reject`
  - Approve or reject non-standard interest/profit rate requests
- `Term Deposit | Activate Account | Cancel Account`
  - Pre-activation cancellation; early withdrawal with penalty settlement

### Manage Account
- `Term Deposit | Manage Account | Update Account`
  - Modify: customer information, maturity instructions, nominee details; subject to verification
- `Term Deposit | Manage Account | Account Inquiry`
  - View: balance, tenure, maturity date, returns, transaction history
- `Term Deposit | Manage Account | Clone Account`
  - Replicate an existing TD account structure for a new account
- `Term Deposit | Manage Account | Deactivate Account`
  - Temporarily suspend account without closing

### Account Confirmation Lists
- `Term Deposit | Account Confirmation List | Pre Activation Cancellation List`
- `Term Deposit | Account Confirmation List | Deactivation Confirmation List`
- `Term Deposit | Account Confirmation List | Reactivation Confirmation List`
- `Term Deposit | Account Confirmation List | Pre-Mature Confirmation List`
- `Term Deposit | Account Confirmation List | Mature Confirmation List`
- `Term Deposit | Account Confirmation List | Account Update Confirmation List`
- `Term Deposit | Account Confirmation List | Security Status Change Confirmation List`
- `Term Deposit | Account Confirmation List | Security Document Reprint Approval`
- `Term Deposit | Account Confirmation List | Ownership Transfer Confirmation List`
- `Term Deposit | Account Confirmation List | Interest Adjustment Confirmation List`

### Transaction Management
- `Term Deposit | Manage Transaction | Transactions`
  - **Pre-Mature** — early closure before maturity date; penalties applied per product terms
  - **Mature** — maturity processing; principal + returns disbursed
  - **Renewal Process** — extend TD for new tenure (auto or manual); updated rate applied
  - **Interest Adjustment** — correct/modify interest due to error, rate change, or policy update
- `Term Deposit | Manage Transaction | External Interest Payment`
  - Transfer interest directly to external beneficiary/account
- `Term Deposit | Manage Transaction | External Interest Pay Confirmation`
  - Confirm external interest payment transfer

### Security Document
- `Term Deposit | Security Document | Print`
- `Term Deposit | Security Document | Re-Print`

### Maintenance
- `Term Deposit | Maintenance | Ownership Transfer` — change registered owner; update records
- `Term Deposit | Maintenance | Security Management` — safeguard assets; access controls and documentation
- `Term Deposit | Maintenance | Bulk Credit Interest Rate Update` — mass rate change across multiple TD accounts
- `Term Deposit | Maintenance | Bulk Rate Update Confirmation` — verify bulk rate changes applied

### Settings
- `Term Deposit | Settings | Tax Profile Rule Definition`

### Alert Management
- `Term Deposit | Alert Management`
  - Maturity reminders, rate change notifications, compliance alerts

### Reports
Navigation: `Term Deposit | Reports`
- Deposit Register – Detail Summary Report
- Renewal Details Report
- Interest Detail Report
- Term Deposit Payment Report
- Advice Certificate Details Report
- Periodic Transaction Report
- Account Status Report
- Pre-Mature Details Report
- Closure Details Report
- Applied Interest Detail Report
- Balance Confirmation Report
- Term Deposit Movement Report

## Key Jira Labels
- TD epics: labels `TDModule`, `TD_Modul`, `FDModule`
- Epic JQL: `project in (PF,FX,FUSIONX_TD) and type in (Epic,Story) and labels in (TD_Modul,TDModule,FDModule) and labels not in (Stabilization,StabilizationDetail) ORDER BY created DESC`

## E2E Impact Notes (TD-specific)
- **GL / Finance Postings** — maturity, pre-mature closure, interest application, and renewal all generate GL entries; uses TD Finance Account Mapping from Common Settings
- **COB upstream** — TD account opening requires valid customer record in COB
- **CASA touchpoint** — interest payouts and maturity proceeds are typically credited to customer's CASA account; external interest payments go to linked account
- **Cash & Teller** — TD cash deposits and withdrawals processed via teller
- **EOD/Batch** — interest accrual, maturity processing, and renewal triggers are EOD batch jobs; Schedule Log in Common Settings tracks these
- **Tax** — Tax Profile Rule Definition controls withholding tax on TD interest; TD GL Category Mapping governs GL postings
- **Bulk rate update** — impacts accrued interest calculations for all affected accounts from next calculation run
- **Compliance** — Balance Confirmation Report and Advice Certificate are key customer-facing compliance documents
