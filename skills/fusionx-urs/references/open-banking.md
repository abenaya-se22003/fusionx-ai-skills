# Open Banking — FusionX Reference
*Sources:*
*- PCA Product Data Model v3.1.2: https://openbanking.atlassian.net/wiki/spaces/DZ/pages/1077805528/*
*- SME Loan API Specification v2.3.1: https://openbanking.atlassian.net/wiki/spaces/DZ/pages/1009878557/*
*Last synced: June 2026*

## Official Module Name
`Open Banking`
Navigation root: `FusionX Home → Open Banking`
Relates to: API Gateway, Consent Management, AISP, PISP, Product Data APIs, TPP Registration (DCR)

---

## ACRONYMS & GLOSSARY (always include relevant ones in URS Section 1.3)

| Acronym / Term | Definition |
|---|---|
| OBIE | Open Banking Implementation Entity |
| OB | Open Banking |
| API | Application Programming Interface |
| AISP | Account Information Service Provider |
| PISP | Payment Initiation Service Provider |
| TPP | Third Party Provider |
| PCA | Personal Current Account |
| BCA | Business Current Account |
| CCA | Consumer Credit Act |
| SME | Small and Medium-sized Enterprise |
| CMA9 | The nine largest UK banks mandated by the Competition and Markets Authority |
| CMA | Competition and Markets Authority |
| FCA | Financial Conduct Authority |
| MMC | Monthly Maximum Charge — CMA-defined cap on unarranged overdraft charges for PCA products |
| AER | Annual Equivalent Rate — representative rate for credit interest |
| EAR | Effective Annual Rate — representative rate for overdrafts |
| APR | Annual Percentage Rate — used for loan product comparison |
| RepAPR | Representative APR — rate offered to at least 51% of accepted applicants |
| MIG | Message Implementation Guide — worked examples for API message fields |
| UML | Unified Modelling Language — used for API class diagrams |
| JSON | JavaScript Object Notation — data format used in Open Banking API responses |
| REST | Representational State Transfer — API architecture style |
| DCR | Dynamic Client Registration — OAuth-based mechanism for TPP registration |
| FAPI | Financial-grade API — security profile for Open Banking |
| TierBandMethod | `Whole` (entire balance at one rate) or `Tiered` (each tier at its own rate) |
| DepositInterestAppliedCoverage | Whether credit interest applies to `Whole` balance or is `Tiered` |
| FixedVariableInterestRateType | Whether the rate is `Fixed` or `Variable` |
| MarketingState | Product lifecycle state: `Promotional`, `Regular`, or `BackBook` |
| PredecessorID | Links sequenced marketing states to order rate changes over a product's life |
| StateTenureLength / StateTenurePeriod | Duration a marketing state applies (e.g., 9 Months) |
| FirstMarketedDate / LastMarketedDate | Active date range for a marketing state |
| OverdraftType | `Committed` (bank cannot demand immediate repayment) or `OnDemand` |
| FeeCapOccurrence | Caps fees based on number of occurrences rather than a fixed amount |
| OverdraftControlIndicator | Flag for fees/caps tied to overdraft control features |
| CappingPeriod | Period over which fee caps apply (e.g., `Month`) |
| FeeMinMaxType | Whether the cap is a `Maximum` or `Minimum` |
| RepaymentType | e.g., `CapitalAndInterest`, `FixedCapitalFullyAmortising` |
| RepaymentFrequency | How often repayments are made (e.g., `Monthly`) |
| RepaymentHoliday | Optional deferred repayment period at loan start |
| EarlyRepayment | Repayment before scheduled end date, potentially with charges |
| PrepaymentFee | Fee charged for early/partial repayment |
| ArrangedOverdraft | Overdraft agreed in advance with the bank |
| UnarrangedOverdraft | Overdraft not pre-approved by the bank |
| BorrowingItem | Per-transaction fee for paid/unpaid items under insufficient funds |
| BufferAmount | Small interest-free overdraft buffer before fees apply |
| x-fapi-auth-date | HTTP header: customer's last authentication date |
| x-fapi-interaction-id | HTTP header: unique interaction/correlation ID per API call |
| x-fapi-customer-ip-address | HTTP header: end-user's IP address |

---

## SPEC 1 — PCA Product Data Model v3.1.2

### Purpose
Defines the data model for Personal Current Account (PCA) product information exposed via the Open Banking Products API. Used when writing URS for PCA product data exposure, overdraft fee modelling, credit interest tier structures, and MMC implementation.

### Product Sections & What to Include

| Product Section | Fields to Include in FusionX URS |
|---|---|
| **Product (PCA)** | `Name`, `ProductType` ("PCA"), `MonthlyMaximumCharge` (mandatory for front-book), Open Data Product ID |
| **CoreProduct** | Merged into Product section — no separate section needed |
| **PCAMarketingState** | Not required — only current state information needed |
| **CreditInterest** | TierBandSet fields (excl. eligibility), all TierBand fields. Only current state required |
| **Overdraft** | All TierBandSet fields (incl. OverdraftFeesAndCharges), all TierBand fields. Only current state required |
| **Eligibility** | Not required — eligibility at time of PCA sale is unreliable |
| **FeaturesAndBenefits** | Not required for back-book; use Open Data API for front-book features |
| **OtherFeesAndCharges** | Periodic Fee (service charge) |

### Credit Interest Model (key rules)
- `AER` is the only mandatory representative rate for product comparison
- `Gross` rate also supported (Net rate discontinued from April 2016, may still appear in back-book)
- Both `CalculationFrequency` and `ApplicationFrequency` must be captured
- `DepositInterestAppliedCoverage`: `Whole` = single rate on entire balance; `Tiered` = rate applied per tier
- `Destination`: `PayAway` (credited to another account) or `SelfCredit` (credited to same account)

### Overdraft Model (key rules)
- `OverdraftType`: `Committed` (bank cannot demand immediate repayment) or `OnDemand`
- `OverdraftFeeCharges` defined at TierBandSet level for non-tiered fees; at TierBand level for tiered fees
- MMC covers all unarranged overdraft charges including debit interest

### Key Field Names for Data Dictionary (PCA)
```
Credit Interest:
  AER, BankInterestRateType (Gross/Net), CalculationFrequency, ApplicationFrequency
  TierValueMinimum, TierValueMaximum, TierBandMethod (Whole/Tiered)
  DepositInterestAppliedCoverage, Destination (PayAway/SelfCredit)

Overdraft:
  OverdraftType (Committed/OnDemand), ArrangedOverdraftLimit
  OverdraftFeesAndCharges: FeeType, FeeAmount, FeeRate, FeeCategory
  FeeCapAmount, FeeCapOccurrence, CappingPeriod, FeeMinMaxType
  OverdraftControlIndicator, BufferAmount
  MonthlyMaximumCharge (MMC)

Product:
  ProductName, ProductType ("PCA"), ProductId, MarketingState
  MonthlyMaximumCharge

API Response Envelope:
  Data, Links.Self, Meta.TotalPages

FAPI Security Headers:
  x-fapi-auth-date, x-fapi-customer-ip-address, x-fapi-interaction-id
```

### API Endpoint Pattern
```
GET /accounts/{AccountId}/product
Response: { "Data": { "Product": [...] }, "Links": { "Self": "..." }, "Meta": { "TotalPages": 1 } }
```

---

## SPEC 2 — SME Loan API Specification v2.3.1

### Purpose
Defines the data model for SME Unsecured Loan product information exposed via the Open Banking Open Data API. Used when writing URS for SME loan product data exposure, loan interest tiers, repayment structures, eligibility rules, and marketing state sequencing.

### Top-Level Structure
```
Brand
  └── SMELoan (one or more per brand)
        ├── Name
        ├── Identification (unique internal product ID, Max40Text)
        ├── Segment (e.g., Basic, Regular, Premium, OtherSegment)
        ├── MarketingState[] (Promotional / Regular / BackBook)
        │     ├── Identification
        │     ├── PredecessorID (sequences states; not change history)
        │     ├── MarketingState (Promotional / Regular / BackBook)
        │     ├── FirstMarketedDate / LastMarketedDate
        │     ├── StateTenureLength / StateTenurePeriod
        │     ├── CoreProduct
        │     ├── LoanInterest
        │     ├── Repayment
        │     ├── Eligibility
        │     ├── FeaturesAndBenefits
        │     └── OtherFeesAndCharges
```

### MarketingState Sequencing (critical concept)
- `PredecessorID` sequences the states a customer moves through during product lifecycle (NOT change history)
- `FirstMarketedDate` / `LastMarketedDate` — period when this state was advertised
- Example: Promotional (9 months, 3% rate) → Promotional (12 months, 5% rate) → Regular (14.9% variable)
- When a marketing state is updated, PredecessorID in downstream states must also be updated
- CMA9 banks only need to provide current and known future states — no historical audit required

### Core Product Section
| Field | Description |
|---|---|
| `ProductURL` | Link to bank's product page |
| `TcsAndCsURL` | Terms & conditions URL |
| `SalesAccessChannels` | Channels via which SME loan can be sold (Branch, Online, etc.) |
| `ServicingAccessChannels` | Channels via which loan can be serviced |
| `MonthlyCharge` | Monthly servicing charge (if applicable) |

### Loan Interest Section
| Field | Description |
|---|---|
| `LoanInterestTierBandSet` | Set of interest tiers for the loan |
| `LoanProviderInterestRateType` | Type of rate (e.g., base rate linked, fixed) |
| `LoanProviderBaseRate` | Rate tied to provider base rate (variable) |
| `RepAPR` | Representative APR (rate for ≥51% of accepted applicants) |
| `FixedVariableInterestRateType` | `Fixed` or `Variable` |
| `TierValueMinimum` / `TierValueMaximum` | Loan amount range for this tier |
| `TierValueMinTerm` / `TierValueMaxTerm` | Loan term range for this tier |
| `BankInterestRate` | The actual interest rate value |
| `BankInterestRateType` | `Gross` / `Net` |
| `ApplicationFrequency` | How often interest is applied |
| `CalculationFrequency` | How often interest is calculated |

### Repayment Section
| Field | Description |
|---|---|
| `RepaymentType` | `CapitalAndInterest`, `FixedCapitalFullyAmortising`, etc. |
| `RepaymentFrequency` | `Monthly`, `Weekly`, `Quarterly`, etc. |
| `AmountType` | How repayment amount is defined |
| `MaxHolidayLength` / `MaxHolidayPeriod` | Maximum repayment holiday allowed |
| `RepaymentHoliday` | Whether deferred repayment period exists |
| `EarlyRepayment` | Conditions for early repayment |
| `PrepaymentFee` | Fee for early or partial repayment |

### Eligibility Section
| Field | Description |
|---|---|
| `MinimumAge` | Minimum age of applicant |
| `ResidencyType` | Residency requirement (e.g., UK Resident) |
| `LegalStructure` | Legal form of SME (e.g., SoleTrader, Partnership, LimitedCompany) |
| `ScoringType` | Credit scoring methodology |
| `TradingType` | Type of trading activity |
| `MinimumTradingPeriod` | Minimum trading history required |
| `IndustrySector` | Industry sector restrictions (if any) |
| `OtherEligibility` | Any other eligibility criteria |

### Features & Benefits Section
- Benefits can be individual or grouped (BenefitGroup)
- Each benefit can have its own eligibility criteria (as notes)
- Key benefit types: insurance, cashback, discount, reward

### Other Fees & Charges Section
Common fees to capture in URS Data Dictionary:
| Fee Type | Description |
|---|---|
| Arrangement Fee | Loan setup/origination fee |
| Legal Cost Fee | Legal documentation costs |
| Late Payment Fee | Penalty for missed/late repayment |
| BorrowingItem (Return Fee) | Fee for returned/unpaid items |
| Early Repayment Charge | Penalty for paying off loan early |
| Overpayment Fee | Fee if overpayment limit exceeded |

### Key Field Names for Data Dictionary (SME Loan)
```
Product Identification:
  ProductName, Identification (Max40Text), Segment, ProductType

Marketing State:
  MarketingState (Promotional/Regular/BackBook), PredecessorID
  FirstMarketedDate, LastMarketedDate, StateTenureLength, StateTenurePeriod

Core Product:
  ProductURL, TcsAndCsURL, SalesAccessChannels, ServicingAccessChannels, MonthlyCharge

Loan Interest:
  RepAPR, LoanProviderInterestRateType, LoanProviderBaseRate
  FixedVariableInterestRateType (Fixed/Variable)
  TierValueMinimum, TierValueMaximum, TierValueMinTerm, TierValueMaxTerm
  BankInterestRate, BankInterestRateType (Gross/Net)
  ApplicationFrequency, CalculationFrequency

Repayment:
  RepaymentType, RepaymentFrequency, AmountType
  MaxHolidayLength, MaxHolidayPeriod, PrepaymentFee

Eligibility:
  MinimumAge, ResidencyType, LegalStructure, ScoringType
  TradingType, MinimumTradingPeriod, IndustrySector

API:
  GET /unsecured-sme-loans HTTP/1.1
  Content-Type: application/prs.openbanking.opendata.v2.1+json
  Response: { "data": [{ "Brand": [{ "BrandName": "...", "SMELoan": [...] }] }] }

FAPI Security Headers:
  x-fapi-auth-date, x-fapi-customer-ip-address, x-fapi-interaction-id
```

---

## WHEN TO USE EACH SPEC

| URS Scope | Use |
|---|---|
| PCA product data via Open Banking API | PCA Product Data Model v3.1.2 |
| Overdraft fee/charge modelling (arranged/unarranged/per-item/caps) | PCA Product Data Model v3.1.2 |
| Credit interest tier structures (AER, Gross, tiered vs whole) | PCA Product Data Model v3.1.2 |
| Monthly Maximum Charge (MMC) implementation | PCA Product Data Model v3.1.2 |
| Account product comparison API endpoints | PCA Product Data Model v3.1.2 |
| SME unsecured loan product data via Open Banking | SME Loan API Specification v2.3.1 |
| Loan interest tiers, RepAPR, fixed vs variable rates | SME Loan API Specification v2.3.1 |
| Repayment structures, early repayment, payment holidays | SME Loan API Specification v2.3.1 |
| Loan eligibility rules (age, residency, legal structure, trading) | SME Loan API Specification v2.3.1 |
| Marketing state sequencing for promotional/regular rate transitions | SME Loan API Specification v2.3.1 |
| Arrangement and other loan fees/charges | SME Loan API Specification v2.3.1 |

---

## E2E Impact Notes (Open Banking-specific)
- **API Gateway** — all Open Banking endpoints are exposed via API Gateway; TPP authentication via FAPI/DCR
- **Consent Management** — AISP access requires customer consent; consent lifecycle (create/revoke/expire) must be covered in URS
- **CASA upstream** — PCA product data is sourced from CASA module product definitions
- **Lending upstream** — SME Loan product data is sourced from Lending module sub-product settings
- **Common Settings** — GL mappings, tax codes, and document types may be impacted if Open Banking triggers new transaction types
- **Security** — All API calls must include FAPI headers (`x-fapi-auth-date`, `x-fapi-interaction-id`, `x-fapi-customer-ip-address`)
- **Audit & Compliance** — All TPP API calls must be logged; consent audit trail is mandatory
- **EOD/Batch** — Product data updates (bulk rate changes, marketing state transitions) must be reflected in API responses from next processing cycle
