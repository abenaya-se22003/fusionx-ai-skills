# Live API Capture Examples

These sanitized examples show the evidence shape expected from a real
FusionX feature/flow capture. They are not endpoint specifications and must
not be copied into a deliverable. Capture the actual method, path, fields,
and raw response from the user's authorized system session.

## CREATE/SAVE: correlated request and response

A wizard confirmation can emit more than one request. Save each raw body and
record the shared UI trigger in `workflow_capture_notes.md`.

```text
UI trigger: Customer Details > Save and confirm
POST https://<host>/lending-origination/customer/{tenant}
201 Created

Request body:
{
  "leadId": 987654,
  "firstName": "Test",
  "lastName": "Customer",
  "residentTypeId": 1001,
  "contact": [{"contactTypeId": 2001, "contactNo": "<test-number>"}],
  "status": "ACTIVE"
}

Response body:
{
  "messages": "CREATED.",
  "value": {"customerId": 456789, "leadId": 987654}
}
```

The workbook maps the input control to the request field actually present in
the captured POST (for example, `residentTypeId`) and records the real
response fields (for example, `value.customerId`).

## Dropdown lookup: live raw response in the workbook

Opening a dropdown may produce a GET. Save its complete raw response in
`lookup_responses/`, then load that same file into the `Response Field` cell
for every field using this lookup.

```text
UI trigger: Customer Details > Resident Type dropdown opened
GET https://<host>/comn-common/residency-type/{tenant}/status/ACTIVE
200 OK

Response body:
[
  {"id": 1001, "code": "RESI", "name": "RESIDENT", "status": "ACTIVE"},
  {"id": 1002, "code": "NRES", "name": "NON-RESIDENT", "status": "ACTIVE"}
]
```

This is evidence of a High live-verified lookup only when the GET and its raw
body were captured during the UI action. A visible endpoint without a captured
body is Medium at most.

## Dependent lookup: preserve dependency and generalize values

Record the observed request immediately, but replace record-specific values
with placeholders in the workbook API path and explain each dependency.

```text
Observed GET:
https://<host>/lending-product/sub-product/{tenant}/main-product-id/3001/status/ACTIVE/validate?branchId=4001&customerTypeId=5001&date=1990-01-01

Workbook API Path:
https://<host>/lending-product/sub-product/{tenant}/main-product-id/{productId}/status/ACTIVE/validate?branchId={branchId}&customerTypeId={customerTypeId}&date={dateOfBirth}

Notes:
Dependent on selected product, branch, customer type, and date of birth;
the response is an eligibility-filtered list, not a generic product list.
```

## Static and blocked controls

If opening a control creates no network request, record `Matched Service` as
`(client-side static)`, `HTTP Method` as `N/A`, and the observed static values
in Notes. If the flow cannot continue because of approval, role, product, or
test-data configuration, record the impacted fields as `Blocked` with the
specific observed dependency. Do not manufacture an endpoint or response.
