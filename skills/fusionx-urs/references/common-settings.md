# Common Settings Module — FusionX Reference
*Source: Confluence → FusionX Space → Common Settings Module (page/20709491)*
*Last synced: June 2026*

## Official Module Name
`Common Settings Module`
Navigation root: `FusionX Home → Common Settings`
Jira label: `CommonModule`

## Purpose
Centralizes system-wide configuration parameters — used by ALL other modules. When a URS impacts system-wide configuration (GL mapping, tax codes, holiday calendar, currencies, geography, alerts, user access), reference this module.

## Sub-Module Hierarchy

### Settings → Common Settings
`Common Settings | Settings | Common Settings | [Screen]`
- Address Mapping Definition, Default Value Definition, Currency Exchange Rate, Currency Type Definition
- Document Type Definition, Period Type Definition, Officer Type, Legal Structure, Residency Type
- ID Code Sequence, Channel, Channel Level, Organization Level, Organization
- Bank & Financial Institutes, Common List, Notification Types
- Alert Event, Alert Limit, Alert Template, Alert Mask
- Service Providers, Geography Level, Geography Hierarchy Master
- Designation, Languages, Sales Hierarchy, Sales Hierarchy Level, Department Level, Branch
- Document Category, Document Sub Category, Document Details, Document Header
- Chub Details, Drawer Details, Entity Type Mapping, File Category, File Sub Category
- Product Category, Letter Type, Exception Type, Exception Sub Type, Sub Channel Level
- Set of Books, Analytics Report URL Config, Comn Geo Attribute, Next Number Validation

### Settings → Customer Settings
`Common Settings | Settings | Customer Settings | [Screen]`
- Identification Type, Contact Type, Occupation, Individual Person Type, Key Person Type
- Person Common List, Product Category – Facility, FATCA Category, Turn Over
- Sector, Sub Sector, Document Checklist, Customer Segmentation, Document Header

### Settings → Tax Configuration
`Common Settings | Settings | Tax Configuration | [Screen]`
- Tax Code Definition, Tax Formula, Tax Formula Details

### Settings → Calendar
`Common Settings | Settings | Calendar | Holiday Management`

### Settings → Finance GL Settings
`Common Settings | Settings | Finance GL Settings | [Screen]`
- Finance Account Category, GL Type, Finance Account, Finance Sub Account, Finance Account Mapping
- TD Finance Account Mapping, Lending Transaction Account Mapping, Lending Finance Account Mapping
- Oracle Code Mapping, TD GL Category Mapping, CASA GL Category Mapping
- Cash Finance Account Mapping, GL Multi-Currency Setup

### Settings → Risk Calculation
`Common Settings | Settings | Risk Calculation | [Screen]`
- Credit Risk Grading, Credit Risk Assessment Main/Sub Criteria
- Credit Risk Parameter Template, Credit Risk Template
- Master Value Pair, Risk Parameter Field Setup

### Settings → Third Party Reporting
`Common Settings | Settings | Third Party Reporting | Reporting Agency Definition`

### Schedules
`Common Settings | Schedules | Schedule Log`
- Create, view, update schedule log for TD, CASA, and Lending EOD processes

### User Access Management
`Common Settings | User Access Management | Module Feature`
`Common Settings | User Access Management | User Access Granting`

### CRIB
`Common Settings | CRIB | CRIB Process`
`Common Settings | CRIB | Data Mapping`

### Finance GL (Operations)
`Common Settings | Finance GL | [Screen]`
- GL Transaction Details, Manual GL Process, Unlock GL Schedulers, Sync, GL Inquiry
- Manual Journal Entry, Manual Journal Entry Confirmation

### Balance Confirmation Letter
`Common Settings | Balance Confirmation Letter`

### Blacklist Management
`Common Settings | Blacklist Management | Person Blacklist`
`Common Settings | Blacklist Management | Person Whitelist`
`Common Settings | Blacklist Management | Map Rules to Transaction Event`

### Document Management
`Common Settings | Document Management | Customer Document`

### Reports
`Common Settings | Reports | General Reports`
- Tax Summary Report, Tax Detail Report, Tax Certificate, Common Reports, Person Blacklist Detail Report

### Cash Balancing
`Common Settings | Cash Balancing | Cash Balancing Details`

## Key Jira Label
- Common Module epics: label = `CommonModule`
- Epic JQL: `project in (PF,FX) and type in (Epic) and labels = CommonModule ORDER BY created DESC`

## E2E Impact Notes (Common Settings-specific)
- **All modules depend on Common Settings** — any change to GL mapping, tax codes, currency rates, holidays, or document types affects all modules simultaneously
- **GL Mappings** — Finance Account Mapping, TD/CASA/Lending/Cash GL Mappings are the authoritative source for all financial posting rules
- **Holiday Calendar** — impacts EOD scheduling, due date calculation, and maturity date logic across Lending, TD, and CASA
- **Currency Exchange Rate** — used by Cash & Teller for multi-currency transactions and by TD for foreign currency deposits
- **Tax Code Definition** — parent tax configuration consumed by Lending Tax Code Definition and TD Tax Profile Rule; changes here cascade to all modules
- **Blacklist Management** — Person Blacklist feeds into Lending loan origination blacklist check and COB customer onboarding validation
- **Document Types** — Document Type Definition and Document Category/Sub Category are shared across COB, CASA, Lending, and TD for document checklist management
- **Schedule Log** — single source of truth for all EOD batch job monitoring across TD, CASA, and Lending
- **User Access Management** — Module Feature and User Access Granting govern RBAC across all FusionX modules
- **Alert/Notification system** — Alert Event, Alert Template, Alert Mask settings control system-generated alerts for all modules
