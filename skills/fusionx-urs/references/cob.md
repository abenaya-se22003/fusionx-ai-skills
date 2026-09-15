# Customer Onboarding Module (COB / KYC) — FusionX Reference
*Source: Confluence → FusionX Space → Customer Onboarding Module (page/20513023)*
*Last synced: June 2026*

## Official Module Name
`Customer Onboarding Module` — abbreviated **COB**
Navigation root: `FusionX Home → Customer Onboarding`
Jira label: `CustomerOnBoardingModule`

## Sub-Module Hierarchy

### Customer Onboarding (Creation)
- `Customer Onboarding | Customer Management | Onboard Individual Customers`
  - General Information, Individual Customer Details, Sensitive Information, Personal Demographical Information, Living Condition Details, Contact Details, Bank Account Details, Employment Details, Relationship Details, Other Details, Tax Profile, Power of Attorney, Document Checklist
  - Upload: Customer Image, Address Proof, Identification Documents, Other Documents
- `Customer Onboarding | Customer Management | Onboard Non-Individual Customers`
  - Corporate Profile, Contact Details, Bank Account Details, Other Details, Tax Profile, Power of Attorney, Document Checklist

### Customer Inquiry (View)
- `Customer Onboarding | Customer Inquiry | View Customer List`
- `Customer Onboarding | Customer Inquiry | Create New Customer`
- View accessible from CASA, Loan Origination, Term Deposit, Cash & Teller for unified customer profile

### Customer Update
- `Customer Onboarding | Customer Management | Update Customers`
  - Modify existing records; full audit trail maintained

### Pending Approvals — Customer (Maker-Checker)
- `Customer Onboarding | Pending Approvals | Approve Pending Customer`
  - Approval for customer creation (`cob:approvalsCreate:view`)
  - Approval for customer updates (`cob:approvalsUpdate:view`)

### Pending Approvals — PEP
- `Customer Onboarding | PEP Approvals | Approve Pending PEP Customer`
  - PEP approval for customers (`cob:pepApprovalsCreate:view`, `cob:pepApprovalsUpdate:view`)
- `Customer Onboarding | PEP Approvals | Approve Pending PEP Other Parties`
  - PEP approval for Relations, Key Persons, Power of Attorney parties (`cob:pepOther:Capproval:view`, `cob:pepOther:Uapproval:view`)

### Remove Assignee
- Remove assigned user from an authorization request

### Reports
- **Jasper Reports:** Customer Audit Log Report, Customer Details Report
- **BI Reports:**
  - Customer 360: Customer Overview, Assets – Savings & Current Accounts, Assets – FD Account Details, Liabilities – Lending Account Details
  - Customer Details Report (Individual / Non-Individual)

## RBAC Roles
| Role | Permission | Scope |
|---|---|---|
| cob-approvalsCreate-view | cob:approvalsCreate:view | Pending approval — customer creations |
| cob-approvalsUpdate-view | cob:approvalsUpdate:view | Pending approval — customer updates |
| cob-onboardingCreate-view | cob:onboardingCreate:view | COB onboarding, customer inquiry — creations |
| cob-onboardingUpdate-view | cob:onboardingUpdate:view | COB onboarding, customer inquiry — updates |
| cob-pepApprovalsCreate-view | cob:pepApprovalsCreate:view | PEP approval — customer creations |
| cob-pepApprovalsUpdate-view | cob:pepApprovalsUpdate:view | PEP approval — customer updates |
| cob-pepOtherCreateAppr-view | cob:pepOther:Capproval:view | PEP approval — other parties creations |
| cob-pepOtherUpdateAppr-view | cob:pepOther:Uapproval:view | PEP approval — other parties updates |

## Key Jira Label
- COB epics: label = `CustomerOnBoardingModule`
- Epic JQL: `project in (PF,FX) and type in (Epic) and labels = CustomerOnBoardingModule ORDER BY created DESC`

## E2E Impact Notes (COB-specific)
- **Upstream of all modules** — Customer record must exist in COB before account can be opened in CASA, Loan Origination, or TD
- **KYC/AML compliance** — PEP flagging and approval workflow are mandatory regulatory controls; changes here affect compliance reporting
- **CASA downstream** — Account opening in CASA uses COB customer data; signature upload in COB feeds CASA signature verification
- **Lending downstream** — Loan Origination New Lead Creation links to COB customer record
- **TD downstream** — Term Deposit account opening requires valid COB customer
- **Audit trail** — All customer creation/update events must be logged; Customer Audit Log Report is the primary audit output
- **Data integrity** — Validation rules on COB fields propagate to all downstream modules using the customer record
