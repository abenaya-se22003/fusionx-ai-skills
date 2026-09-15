# Lending Module — FusionX Reference
*Source: Confluence → FusionX Space → Loan Origination and Loan Management (page/20513044)*
*Last synced: June 2026*

## Official Module Name
`Loan Origination and Loan Management`
Navigation root: `FusionX Home → Lending Module`

## Sub-Module Hierarchy

### Loan Origination
- `Lending Module | Loan Origination | Dashboard`
  - New Lead Creation
  - Loan Appraisal
  - OD Appraisal
  - Loan Top-up
  - Direct Loan Request
  - Leads in Progress (Tab)
  - Appraisal Submitted (Tab)
  - Approved / Rejected (Tabs)
  - Own Approval Pending (Tab)
  - Pending Exceptions (Tab)
  - Other Approval Pending (Tab)
  - Lead Transfer
  - Origination Without Lead (OD)
  - Process OD
  - Process Current Account
  - Relief Officer Assignment & Confirmation
  - Loan Reschedule (via appraisal)

### Customer Group Mapping
- `Lending Module | Customer Group Mapping`

### Loan Account Management
- `Lending Module | Loan Account Management | Account Activation`
  - Initiate, Collect Charges, Print Offer Letter, Agreement, Disbursement, Activation
  - Purchase Order Creation
- `Lending Module | Loan Account Management | Account Maintenance`
  - Pre Termination
  - Loan Account Cancellation
  - Loan Restructure and Account Partial Pay Off
  - Loan Account Statement Generate
  - Account Write Off
  - Blocking / Unblocking Disbursement
  - Loan Correction
  - Pledging Release for Ongoing Loan
  - Freeze / Unfreeze Loan Account
  - Account Status Manual Flagging
  - Loan Rescheduling / Loan Reschedule Activation
  - Account Inquiry
  - Appraisal Inquiry
  - Final Settlement
  - Facility Amendments
  - Account Amendments Approval
  - Portfolio Assign
  - Tax Rate Change
  - Subsequent Loan Disbursement
  - Due Date Change
  - Penal Interest Rate Change
  - Change Payee
  - Legal Transfer
  - Add Account Comments
  - Account Partial Pay Off - Asset Release
  - Receipt Reversal
  - IIS & Bad Debt Bucket Provision Process
  - Loan Pretermination Expiry Process
  - Penal Interest Calculation & Posting
  - Contract Status Update
  - Rental Recovery Process – CASA
  - Blacklisting

### Transaction Management
- `Lending Module | Transaction Management`
  - Contract Transfer
  - Waive Off Transaction Balance
  - Debit Charges
  - Excess Payment Refund
  - Non Counter Deposit
  - Receipt Reallocation
  - Confirmation Disbursement
  - Credit Note Posting
  - Revise Interest Rates
  - Charges Refund
  - Purchase Order Regeneration / Cancellation
  - Reminder Letter Printing
- `Lending Module | Transaction Management - Under Taking Management`
  - Create / Approve / Clear Under Taking
- `Lending Module | Bad Debt Provisions`
  - Bad Debt Provision Initiation
  - IIS Bad Debt Provision GL Posting

### Settings (Master Definitions)
Navigation: `Lending Module | Master Definition | [Category] | [Screen]`

**Lending Module Controls:** Business Module Setting, Module Level Feature & Benefit Item Setting, Authorization Setting, Penal Interest Template Setting & Authorization

**Loan Module Common Definitions:** Check List Item/Template Setting, Document Checklist Definition, Due Date Template Setting, Account Status Manual Flagging Setting, Common List Definition, Loan Provider Interest Rate Type, Loan Documents Setting, Document Event Setting, System Generated Document Type Mapping, Reminder Parameter Setting, Center Attendance View Settings, Repayment Frequency/Template/Type/Amount Type Settings

**Product Definitions:** Eligibility Template Definitions, Residency Eligibility, Dynamic Steppers Mapping Template

**Tax Configuration:** Tax Code Mapping, Tax Code Definition (Lending), Tax Profile Rule Definition, Tax Applicable Event Definition

**Credit Appraisal Definitions:** Business/Sub Type, Expense Type, Business/Salary/Other/Cultivation Income Types, Statement Type/Item Level/Template, Salary Expense Type, Business Risk Type/Rating Authority, Exception Type/Approval Group, Household Expense Category, Cultivation Income Type

**Credit Appraisal Approval:** Approval Level/Category/Group & DA Limit Definition

**Product Interest Template:** Interest Template Setting & Authorization

**Product Common Definitions:** Loan Applicable Range, Pay Mode, Sales/Service Access Channels, Product Common List, Calculation/Application Frequency, Due Date Setting

**Product Feature Definitions:** Feature Benefit Template/Item/Eligibility/Item Type/Eligibility Type/Group Type Settings & Authorization

**Product Eligibility Definitions:** Other/Officer/Age/Branch Eligibility Settings

**Product And Sub Product Definitions:** Core Product Template & Authorization, Sub Product Setting & Authorization, Product Group Details, Segment Details, Brand, Main Product, Disbursement Conditions

**Transaction Definitions:** Waive Off Approval Groups, Loan Account Status, Transaction Code/Sub Code/Event/Allocation Template/Core Method, Credit Note Type, Waive Off Type/Event, Payment Voucher Type, Deposit Code

**Product Fee & Charges Template Definitions:** Fee Charge Template & Authorization, Fee Rate Type, Fee Type/Charge Group Definition, Penal Interest Type

**Bad Debt Provisioning:** Bad Debt Provisions Method/Bucket Definition, Bad Debt & Interest in Suspense Template & Authorization

**Micro Finance Definitions:** Business Centers, Business Group, Credit Score Template Mapping & Approval, Credit Score Definition/Level, Character Assessment Event

**System Operation:** Process Scheduler Setting

### Reports
Navigation: `Lending Module | Reports & Enquiries`

- **General:** Pre Terminated Account, Written Off Contracts, Loan Account Details, Customer Contract Details, Available Collateral, Borrower Confirmation Record, Repayment Schedule, Appraisal Report, Restructure and Partial Pay Off Report, Governance Tracking Report
- **Marketing:** Expiry Detail/Summary, Lead Summary/Details, Credit Appraisal Status, Product Wise Collateral Count, Executions by Branch, Execution, Large Borrowers, ME Executions
- **Financial:** List of Pre Paid Rentals, Listing of Excess Payments, Average TR on Execution Branch Wise, Overdue Contract List with Excess, Activation Pending Contracts, Earned Income, Overdue Interest Detail List, Vehicle Tracking Service Payout
- **Transaction:** Account Balance Detail, Loan Charges Payable, PD Cheque Listing, Contract Payment Details
- **Tax:** Tax Report
- **Recovery:** Arrears Report
- **BI:** Branch Wise Disbursement, Branch Wise Loan Portfolio, Collateral Received, Credit Life Premium Payout, Daily Collection Non-Counter, Debt Recovery, Excess Refund, Listing of Undertaking, List of Recovery Terminated Contracts, Insurance, Loan Status, Maturity Analysis of Assets, Portfolio Detail, Product Wise PAR & Collateral Wise PAR, Rescheduled Contract, Staff Incentive, Vehicle Tracker, Write-off, Portfolio At Risk As At Date, OD Utilization & Expiry, Monthly Average TR for ME, BI Commission, ICQF, Branch Wise Product Portfolio, Lending Portfolio and PAR BI, Lending Collection BI, General Ledger Trial Balance

## Key Jira Labels
- Lending Module epics: label = `LendingModule`
- Epic JQL: `project in (PF,FX,FXL) and type in (Epic,stories) and labels = LendingModule ORDER BY created DESC`
- Jira link format: `https://lolcgroupdev.atlassian.net/browse/PF-XXXXX`

## E2E Impact Notes (Lending-specific)
- **Repayment Schedule Engine** — always assess when touching product/sub-product settings, repayment type/frequency/amount type, or rescheduling features
- **GL / Loan Accounting** — impacted by disbursement, write-off, waive-off, penal interest posting, bad debt provisioning
- **DPD / Arrears** — impacted by due date change, penal interest, rescheduling, pre-termination, write-off
- **EOD/Batch** — impacted by process scheduler, penal interest calculation, bad debt provision initiation, rental recovery
- **CASA touchpoint** — Rental Recovery Process runs via CASA accounts; non-counter deposits affect CASA
