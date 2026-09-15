# Cash & Teller Module — FusionX Reference
*Source: Confluence → FusionX Space → Cash & Teller Module (page/20709449)*
*Last synced: June 2026*

## Official Module Name
`Cash & Teller Module`
Navigation root: `FusionX Home → Cash & Teller`
Jira label: `CashModule`

## Sub-Module Hierarchy

### Main Teller Administration
- `Cash & Teller | Main Teller | Open Vault`
- `Cash & Teller | Main Teller | Close Vault`
- `Cash & Teller | Main Teller | Open Till`
- `Cash & Teller | Main Teller | Close Till`
- `Cash & Teller | Main Teller | Agree the Vault Balance`
- `Cash & Teller | Main Teller | Cash Transfer to Teller`
- `Cash & Teller | Main Teller | Excess Cash`
- `Cash & Teller | Main Teller | Treasury Cash Receive`
- `Cash & Teller | Main Teller | Branch Cash Allocation`
- `Cash & Teller | Main Teller | Central Cash Confirmation`
- `Cash & Teller | Main Teller | Cash Courier`
- `Cash & Teller | Main Teller | Branch Main Teller Float In`
- `Cash & Teller | Main Teller | Requesting Funds From Central Cash`
- `Cash & Teller | Main Teller | Bank Deposit & Bank Deposit Reversal`
- `Cash & Teller | Main Teller | Inter Branch Cash Transfer Request & Acceptance`
- `Cash & Teller | Main Teller | Forceful Till Transfer`
- `Cash & Teller | Main Teller | Funds Withdrawal From Banks`
- `Cash & Teller | Main Teller | Inter Teller Transfer & Authorize Teller to Teller Transfer`
- `Cash & Teller | Main Teller | CASA Fund Transfer (Teller Transaction) & Authorize Fund Transfer`
- `Cash & Teller | Main Teller | Transfer Cash/Cheque Till to Vault & Accept Teller Cash/Cheque Transfer`
- `Cash & Teller | Main Teller | Balancing Transaction At Day End`

### Branch Teller Operations
- `Cash & Teller | Teller Management | CASA Cash Deposit`
- `Cash & Teller | Teller Management | CASA Cash Withdrawal`
- `Cash & Teller | Teller Management | CASA Cheque Deposit`
- `Cash & Teller | Teller Management | CASA Cheque Withdrawal`
- `Cash & Teller | Teller Management | TD Cash Deposit`
- `Cash & Teller | Teller Management | TD Cash Withdrawal`
- `Cash & Teller | Teller Management | General Cash Direct Payments`
- `Cash & Teller | Teller Management | CASA Cheque Withdrawal (Teller Transaction) & Checker & Final Action`
- `Cash & Teller | Teller Management | CASA Cash Deposit & Withdrawal & Teller Limit Controller Approval`
- `Cash & Teller | Teller Management | Transaction Reversal & Transaction Reversal Confirmation`

### Till Management
- Till opening, balancing, and closing procedures
- Inter-till cash transfers
- Vault-to-till cash transfers
- User-level till allocation with teller limits

### Vault Management
- Centralized vault balance tracking
- Branch-to-branch vault transfers

### Authorization & Override
- Role-based transaction authorization
- Teller limits enforcement
- Dual verification for high-value transactions
- Manual override by supervisors (approval matrix)

### Reports
- Teller Balancing Sheet
- Daily Teller Transaction Report
- Branch Wise Cash Summary Report

## Key Features
- **Multi-currency support** — transactions in multiple currencies with automated conversion
- **Maker-Checker workflow** — mandatory for high-value or flagged transactions
- **Denomination Templates** — pre-configured templates for common transaction types
- **Real-time vault/till balance updates** after each transaction

## Integration Points
- **CASA** — cash deposits and withdrawals post directly to CASA accounts
- **Lending** — loan repayment receipts processed via teller
- **Term Deposit** — TD cash deposit and withdrawal
- **GL** — all teller transactions generate GL postings in real time

## Key Jira Label
- Cash & Teller epics: label = `CashModule`
- Epic JQL: `project in (PF,FX) and type in (Epic) and labels = CashModule ORDER BY created DESC`

## E2E Impact Notes (Cash & Teller-specific)
- **GL / Finance Postings** — every cash transaction posts to GL in real time; impacts Cash Finance Account Mapping in Common Settings
- **CASA downstream** — teller cash transactions credit/debit CASA accounts; must validate account status before processing
- **TD downstream** — TD cash deposit/withdrawal flows through teller; maturity payouts may be via teller
- **Lending downstream** — loan repayments received via teller are posted to loan accounts
- **EOD / Balancing** — Day-end balancing is a critical teller close procedure; impacts vault and till reconciliation
- **Vault/Till limits** — teller limit controller approval required when transaction exceeds configured limits
- **Multi-currency** — exchange rate from Common Settings (Currency Exchange Rate Setting) is used for conversions
- **Audit trail** — all teller transactions must be logged; Transaction Reversal requires confirmation workflow
