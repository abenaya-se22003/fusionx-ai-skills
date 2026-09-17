---
name: api-field-mapper
description: Map FusionX Master Data and API Requirements fields from a Word document to real API endpoints, request/response fields, or live dropdown lookups, then produce a formatted Excel mapping. Use for Swagger/OpenAPI field mapping, captured FusionX network payloads, master-data lookup endpoints, or refreshing module API specifications; not for general functional testing or user-manual creation.
---

# FusionX API Field Mapper

Maps field names from a "Master Data and API Requirements" Word document to
their real API operations and parameters for one CBS module, and produces a
formatted Excel workbook — via two complementary routes: (A) Swagger/OpenAPI
specs (steps 0–7 below), and (B) live inspection of the actual FusionX app
in a headed browser with real network-traffic capture (step 8). Built for
the lending module first; designed to extend to CASA, TD, and future modules
without changes to the scripts — only `config/modules.json` needs new
entries.

Scripts live in `scripts/` (this skill's own directory — always invoke them
with the absolute path resolved from where this SKILL.md lives, not a
relative path, since the working directory will be the user's project
folder). Config lives in `config/modules.json` next to this file.

## Output folder convention (always use this — don't ask, don't flatten)

Resolve scope before creating the module and feature/flow folder described
below.

## Intake: resolve meaningful ambiguity before capture

When asked to capture APIs for a feature or flow, establish only the details
that are missing and materially affect what will be captured:

- the FusionX module and feature/flow, including its intended start and end;
- whether the deliverable covers CREATE/SAVE traffic, dropdown/master-data
  lookups, or both;
- the FusionX dashboard URL and tenant, plus Swagger/OpenAPI URLs only if
  Swagger support is requested or needed;
- the source requirements document when the output must map its fields.

Ask a concise clarifying question before interacting with the app when those
details remain ambiguous. For example, "Capture the APIs for Loan Request"
does not establish whether the user needs the submit POST, each dropdown GET,
or both. Do not silently choose a narrower scope. Once scope is clear, use
the live-capture examples in `references/live-capture-examples.md` to
recognize and retain the required request/response evidence; their values are
illustrative only and must never be copied into a deliverable.

If the intended API evidence or output shape is still unclear after those
questions, ask the user to provide a sanitized example of the expected
request/response capture, workbook, or prior finding. Ask for the example only
to resolve the ambiguity (for instance, whether a response cell should contain
raw JSON or a selected field); redact credentials, tokens, personal data, and
environment-specific secrets. Do not proceed by inventing a format when the
example would materially change the deliverable.

## Output folder convention

Every task's outputs — working files and the final `.xlsx` alike — live
under a per-task folder nested inside a per-module folder in the user's
project directory:
```
<project_dir>/
  <ModuleDisplayName>/                          e.g. Lending/  (matches config/modules.json's display_name)
    <NN>_<Short_Task_Name>_<yyyy-mm-dd>/         e.g. 01_Swagger_Field_Mapping_2026-09-08/
      <all intermediate + final files for that one task>
    <NN>_<Short_Task_Name>_<yyyy-mm-dd>/         e.g. 02_New_Lead_Creation_And_Appraisal_2026-09-09/
      ...
```
- Create `<project_dir>/<ModuleDisplayName>/` before writing anything when it
  does not already exist. A module's first feature/flow therefore starts at
  `01_<Feature_or_Flow>_<date>`; never place a new module's findings loose at
  the project root.
- Treat each numbered task folder as the feature/flow's findings folder: it
  contains its raw captures, mapping JSON, notes, and delivered workbook.
  This mirrors the established `Lending/<NN>_<Feature_or_Flow>_<date>/`
  structure. Do not invent an extra `findings/` subdirectory unless the user
  explicitly asks for one.
- `<NN>` is a zero-padded sequence number (`01`, `02`, ...) reflecting the
  order tasks were run for that module — check existing folders under
  `<project_dir>/<Module>/` first and continue the sequence; don't restart
  at 01 for a module that already has task folders.
- `<Short_Task_Name>` is a brief, filesystem-safe description of what the
  task was (e.g. `Swagger_Field_Mapping`, `New_Lead_Creation_And_Appraisal`,
  `Master_Data_Lookup_Endpoints`) — not the generic step name.
- Everything the task produces goes inside that one task folder: fetched
  swagger JSON, extracted-fields JSON, the compiled rows JSON, captured
  request/response bodies, `lookup_responses/`, any throwaway assembly
  script, and the final `.xlsx`. Nothing task-specific stays loose at the
  project root.
- A source document genuinely shared across multiple tasks for the same
  module (e.g. the Word doc with the module's Master Data & API
  Requirements) lives at the module-folder root, one level up from the task
  folders, not duplicated into each one.
- Tool-managed state like `.playwright-cli/` stays at the project root —
  don't try to relocate it; the CLI writes there itself relative to the
  working directory and splitting it per task isn't supported or worth the
  effort. Concurrent tasks are kept apart by *naming* their `playwright-cli`
  sessions differently (see 8.1), not by giving each task its own
  `.playwright-cli/` workspace. (The full-coverage driving instructions used
  to be a separate project-root file the user had to keep supplying — they're
  now bundled at `<skill_dir>/references/browser-gotchas.md`, see 8.2,
  so there's nothing project-specific to place for that anymore.)
- If the project directory already has task output sitting loose at the
  root from before this convention existed, offer to reorganize it into
  this structure (inferring module + task groupings from filenames/content)
  rather than leaving old and new conventions mixed.

Steps 6 and 8.4 below both write into a task folder using this convention —
treat "the project working directory" anywhere below as shorthand for the
correct `<project_dir>/<Module>/<NN>_<Task>_<date>/` path, not the bare
project root.

## 0. One-time dependency check

This skill needs Python 3 with `python-docx`, `openpyxl`, and `requests`. If
they are not installed, run:
```
pip install python-docx openpyxl requests
```

For live FusionX inspection, also install the Playwright CLI:
```
npm install -g @playwright/cli
```
Confirm it is available with `playwright-cli list`; it is a shell CLI, not an
MCP tool. If live capture is requested but the CLI cannot capture correlated
requests and responses, report that limitation before proceeding and do not
represent UI-only observations as captured API evidence.
Before any browser interaction, read and follow
`references/browser-session.md`; it is this repository's mandatory session
contract and takes precedence over this skill's browser-specific guidance.
Also read `references/browser-gotchas.md` before driving complex FusionX
controls. Do not capture credentials, tokens, or unnecessary personal data.

## 1. Identify the module and confirm swagger sources

Ask (or infer from context) which module this task is for: `lending`, `casa`,
`td`, etc. Before fetching, establish the source URLs for this task:

- For Swagger/OpenAPI mapping, use URLs supplied in the current request or
  sources already configured for that same module. If neither exists, ask the
  user for Swagger UI or direct OpenAPI JSON URLs. Never guess a host, borrow
  URLs from another module, or treat downloaded JSON from a prior task as the
  current source.
- For live inspection, use a FusionX dashboard URL and tenant supplied in the
  current request or configured for that same module. If neither exists, ask
  the user for them. The user performs login and MFA; do not request, record,
  or handle credentials.

Then:
```
python <skill_dir>/scripts/fetch_swagger.py --list-modules
```
- If the module exists with sources registered, proceed to step 2.
- If the module doesn't exist yet, or has no sources, or the user is giving
  you a **new set of swagger URLs for a module** (as they did for `lending`):
  edit `<skill_dir>/config/modules.json` directly (it's a plain JSON file —
  use the Edit/Write tool) to add/update the module's `swagger_sources` list.
  URLs can be either `.../swagger-ui.html` pages or direct `.../v2/api-docs`
  / `.../v3/api-docs` URLs — the fetch script derives the JSON endpoint
  either way. Then continue.
- Never silently reuse another module's swagger sources for a different
  module — ask if it's ambiguous which module a task belongs to.

## 2. Fetch fresh swagger JSONs (always do this — never reuse stale files)

The user explicitly wants **the latest JSON every time a task is triggered**.
Run this even if JSON files already exist on disk from a previous run:
```
python <skill_dir>/scripts/fetch_swagger.py --module <module> --outdir "<project_dir>/<Module>/<NN>_<Task>_<date>/swagger_json"
```
This saves one `<service>.json` per swagger source (overwriting any previous
copy — that's intentional, it IS the latest) plus a `_fetch_report.json`
audit file, into that task folder's `swagger_json/` (see "Output folder
convention" above) — not inside the skill directory.
If a source fails to fetch, the script still saves the others — report which
ones failed to the user rather than aborting silently.

## 3. Extract fields from the Word document

Find the "Master Data and API Requirements" (or similarly named) `.docx` —
check the module folder root first (`<project_dir>/<Module>/`, since it's
shared across tasks per the "Output folder convention" above), then the
project root if it's not there yet, e.g. on a module's very first task. Then:
```
python <skill_dir>/scripts/extract_docx.py "<path-to-docx>" --out "<project_dir>/<Module>/<NN>_<Task>_<date>/fields_extracted.json"
```
If the doc was found loose at the project root (first task for this
module), move it into `<project_dir>/<Module>/` once you've created that
folder, rather than leaving it outside the module structure.
This walks the document in true reading order and splits every table into
logical sections, auto-detecting the "field listing" table(s) — the ones with
a `Field Name` column (`is_field_table: true`). It also preserves every other
table (scope, integration approach/classification, API activity hints,
failure handling, etc.) with its nearest preceding heading as context — read
these too, they carry real hints for matching (e.g. an "Activity"/"Usage"
table naming actual API operations, or a "Recommended Mechanism" table
telling you which data areas are real-time API vs batch/file).

The script's stdout summarizes what it found (table count, field-row count,
headers). If `is_field_table` doesn't land on the table you expect for a new
module's doc, open the JSON and use whichever section actually has the field
list — the doc template may vary slightly module to module.

## 4. Build understanding of the swagger surface

Don't try to read the raw JSON files — they're 200KB–1.3MB each. Use the
inspection toolkit instead (pointing at the task folder's `swagger_json/`
from step 2):
```
python <skill_dir>/scripts/swagger_tools.py index --dir "<task_folder>/swagger_json"
python <skill_dir>/scripts/swagger_tools.py search --dir "<task_folder>/swagger_json" --q "<keyword>"
python <skill_dir>/scripts/swagger_tools.py show --file "<task_folder>/swagger_json/<service>.json" --path "<path>" --method <verb>
python <skill_dir>/scripts/swagger_tools.py props --file "<task_folder>/swagger_json/<service>.json" --name <SchemaName>
```
- `index` (optionally `--tag`/`--q` filtered) gives you the operation
  landscape per service — skim this once per module to learn which service
  owns which domain (e.g. for lending: `lending-origination` owns the mobile
  journey/customer/lead/loan-request/guarantor/collateral flow;
  `lending-product` owns product configuration; `lending-account` owns
  account/OD/facility data; `lending-transaction` owns postings/transactions).
- `search --q <term>` is your main matching tool — it searches operation
  paths/tags/summaries AND schema property names in one pass, across every
  file in the module.
- `show` gives you one operation's fully-resolved parameters + request body +
  response schema, with `$ref` chains already dereferenced into a readable
  tree (`(required)` tags, `enum`/`format`/`description` shown inline).
- `props` gives you a schema's resolved property tree directly by name —
  useful once `search` has told you the DTO name to drill into.

## 5. Match fields, screen-by-screen (not one-by-one)

Work through the field table grouped by its screen/module column (e.g.
"Mobile Screen"), not row by row from scratch — fields on the same screen
almost always land on the same operation/schema:

1. For each screen group, identify the likely business activity (cross-check
   against any "Activity"/"Usage" hint table from step 3).
2. `search` for 1-2 keywords from the screen/activity name, and `show`/`props`
   the strongest candidate operation or DTO.
3. Map each field in that screen against the resolved property list using
   name similarity — normalize both sides (strip spaces/case, expand common
   abbreviations) before comparing:
   - "Resident Type" ≈ `residentTypeId`/`residentType`
   - "Title" ≈ `title`/`titleId`, "Gender" ≈ `gender`/`genderId`
   - "Mobile Number"/"Phone" ≈ `contactNo`/`mobileNo`/`phoneNumber`
   - "ID Number" ≈ `identificationNo`, "ID Type" ≈ `identificationType(Id)`
   - Prefer an exact/near property-name match; fall back to description or
     enum-value match; fall back to "no match" rather than forcing a weak one.
4. Every field from step 3 must end up in the output — including ones with no
   match. Use `confidence: "Not Found"` and a `notes` explanation (e.g. "no
   corresponding property in any lending swagger schema — likely a
   local/derived UI field, confirm with FusionX team") rather than omitting
   the row.
5. Assign `confidence`: `High` (clear name/semantic match on the operation
   you're confident owns this screen), `Medium` (matched a property but on a
   schema/operation whose ownership is a bit ambiguous, or name match is
   partial), `Low` (weak/guessed match, flag for human review), `Not Found`.

## 6. Compile the mapping JSON and build the Excel

Write a JSON file matching the schema documented at the top of
`scripts/build_excel.py` (module, source_docx, generated_at, swagger_sources
metadata, and a `rows` list — one dict per field, every field from step 3
represented) into the task folder. Then:
```
python <skill_dir>/scripts/build_excel.py --data "<task_folder>/mapping_rows.json" --out "<task_folder>/<Module>_API_Field_Mapping_<yyyy-mm-dd>.xlsx"
```
This produces a two-sheet workbook: `Field-API Mapping` (bold header, frozen
top row, autofilter table, wrapped notes, rows color-coded by confidence:
green=High, yellow=Medium, orange=Low, red=Not Found) and `Summary` (source
metadata, swagger sources used with fetch timestamps, counts by confidence
and by matched service).

Save outputs inside that task's folder (see "Output folder convention"
above), e.g. `<project_dir>/Lending/01_Swagger_Field_Mapping_<date>/`:
```
swagger_json/*.json                        (fetched swagger, refreshed each run — no extra <module> nesting needed, the module folder already provides that)
fields_extracted.json                      (from step 3)
mapping_rows.json                          (Claude-authored intermediate from step 6)
<Module>_API_Field_Mapping_<date>.xlsx     (final deliverable)
```

## 7. Wrap up

Report to the user: how many fields were mapped, the confidence breakdown,
and call out every "Not Found"/"Low" row explicitly (these need human/vendor
follow-up — the source doc itself may note, as it did for lending, that the
API inventory isn't fully confirmed yet). Send the `.xlsx` file to the user.

## 8. Live FusionX inspection workflow (network capture, NOT swagger)

Use this instead of (or in addition to) steps 2–6 when the user asks you to
walk the actual live FusionX app and capture *real* request/response
traffic — either to verify/correct swagger-derived guesses, to document a
CREATE/SAVE flow end-to-end (e.g. "New Lead Creation and Appraisal"), or to
document the GET lookup endpoints that feed dropdowns (master-data lookups).
This produces ground truth the swagger workflow cannot: real IDs, real enum
values, corrected field names (swagger sometimes lies — e.g. a field's real
name only shows up in the actual POST body), and confirmation that a field
is genuinely absent from the live app rather than just missing from the spec.

When the user asks to capture the APIs for a named feature, screen, or flow,
this live workflow is the default. Create that feature/flow's task folder
using the output convention above, drive the authorized path in the live app,
and produce findings from correlated network traffic. Use Swagger only when
the user also requests it or when it helps locate a candidate; never use
Swagger alone as proof of the API, request fields, or lookup response for a
live-capture request.

### 8.0 One-time tool setup

This workflow uses the Playwright CLI installed in step 0. Then, once per
project working directory:
```
playwright-cli install
```
This detects the local Chrome install and initializes a `.playwright-cli/`
workspace in the current directory (where snapshots/console logs land).

### 8.1 Open a headed session (always start here, every task)

Check `<skill_dir>/config/modules.json` for the module's `live_app` entry
(`tenant`, `dashboard_url`). If it is empty for the module in question, ask
the user for the FusionX dashboard URL and tenant. Store them in the entry
only if the user authorizes retaining those environment-specific values;
otherwise use them for the current task only.

Per `references/browser-session.md` Section 0, this task's session is named
`fx-api-<task-folder-slug>-<tag>` (`<task-folder-slug>` from the `<NN>_<Short_
Task_Name>` you just established under "Output folder convention"; `<tag>` a
random/timestamp suffix generated once). Run `playwright-cli list` and check
for that exact name — a differently-named session in that list belongs to a
different task or a different skill's workflow, possibly running right now;
never adopt it just because it looks authenticated. If found, reuse it. If
not, open it:
```
playwright-cli -s=<name> open --headed --browser chrome "<live_app.dashboard_url>"
```
- `--headed` is mandatory — the user must be able to see and interact with
  the window (e.g. to complete login/MFA). Never use a headless session for
  interactive authentication.
- If login is required, bring the visible window to the foreground, have the
  user complete it, and wait for confirmation before authenticated actions.
- Use the shared contract for session reuse, lifecycle ownership, and
  recovery. In particular, do not use `playwright-cli attach`, and don't
  re-run `open` against a name that's already open — it silently replaces
  the running browser under the same name instead of reusing it.

### 8.2 Drive the app and capture traffic

Follow `<skill_dir>/references/browser-gotchas.md`
(bundled with the skill — no need to ask the user for it) for how
thoroughly to click through screens, fill forms, and handle Ant Design's
virtualized dropdowns. Key
commands for this skill's purposes (`<name>` is this task's session name from
8.1 — every call below carries it; a bare `playwright-cli <command>` targets
the anonymous `default` session, not this task's):
```
playwright-cli -s=<name> snapshot                         # current page a11y tree, with element refs
playwright-cli -s=<name> click <ref>                      # interact using refs from the last snapshot
playwright-cli -s=<name> fill <ref> <text>
playwright-cli -s=<name> requests                         # numbered list of network calls since last navigation
playwright-cli -s=<name> request-body <n>                 # a specific request's outgoing JSON body
playwright-cli -s=<name> response-body <n>                # a specific request's raw response JSON
```
When saving screenshots, snapshots, or captured response files, use absolute
paths inside the current task folder. Keep raw responses separate from the
workbook and do not save authentication material or unnecessary personal data.
Two different things to capture depending on what the user asked for — if
it's ambiguous which one, ask; don't guess:

- **CREATE/SAVE flows** (e.g. "New Lead Creation and Appraisal"): fill the
  form, submit, then find the resulting POST in `requests` and pull its
  `request-body` (the real field names) and `response-body` (what comes
  back, e.g. new-record IDs). Feed these into `build_excel.py`'s schema
  (`request_field` = real POST field, `response_field` = what the create
  response returns).
- **Lookup/dropdown GET endpoints** (e.g. "give me the API path, method,
  request parameter, and response for each dropdown" — the default reading
  of any request for "the API info behind the dropdowns/master data",
  phrased exactly like that or not): open the dropdown, find the resulting
  GET in `requests`, and pull its `response-body` — this is the real
  master-data list (id/code/name/status/...). Feed these into
  `build_lookup_excel.py`'s schema — see 8.3 below for the exact columns.

A field can legitimately map to **different real endpoints depending on
which screen/stage of the journey you're on** — e.g. in this project,
"Repayment Pattern" was a hardcoded client-side list (no API call) at the
Loan Request screen, but a real dependent GET lookup at the later Appraisal
Loan Calculation screen. Don't assume one capture applies everywhere a field
name appears — capture each occurrence separately and note the divergence.

Pull `response-body` **immediately** after the action that triggers it —
don't wait and come back for it later; a request's body can become
unavailable after enough subsequent navigation/reloads happen. If it comes
back empty even right after, don't dig around it (see 8.5) — just re-trigger
the same UI action once more to generate a fresh request and try again.

#### Retain live-capture evidence and workflow context

For every material CREATE, SAVE, or lookup capture, save the raw bodies in
the task folder using stable, descriptive names such as
`capture_create_customer_reqbody.json` and
`capture_create_customer_respbody.json`. Strip auth headers, tokens, and
unnecessary personal data. Keep a `workflow_capture_notes.md` alongside the
captures that records the triggering UI action, method/path/status, related
requests, IDs returned, dependencies, and any correction to an earlier
Swagger-based hypothesis.

Do not assume a wizard step maps to one API call. A single confirmation can
create a header and a full entity in separate requests; map each field to the
request that actually carries it, and state their shared trigger in `notes`.
Likewise, a visible control ID can differ from the submitted field name (for
example, a name-bound combobox can submit an ID). Treat the captured request
body as authoritative, retain the UI control identifier as supporting context
in `notes`, and mark unresolved differences as Medium or Low rather than
silently choosing one.

If a later workflow stage is approval-, role-, product-, or data-gated,
document the observed dependency and affected fields as `Blocked`; do not
bypass the workflow or use another identity without the user's authorization.

Not every dropdown is backed by a network call. Open it and check
`requests` for a new entry — if nothing fired, it's a hardcoded client-side
list (common for small fixed sets like day-of-week, YES/NO toggles, or a
2–3-option enum). Record these too, with `matched_service` /
`request_parameter` describing the field and `confidence: "Static"` — don't
leave them out just because there's no API to point to; "confirmed no API
call, hardcoded client-side" is itself a useful, reportable finding.

Dependent lookups (a GET whose URL or query string embeds another field's
selected id, e.g. Sub Product depending on Product id, or District
depending on Country id) should have their `api_path` written with
`{placeholderName}` in place of the literal value that was captured for one
particular test record — the literal id is specific to that record, not a
general fact about the endpoint. Note the dependency relationship in
`notes` (e.g. "Sub Product also takes branch/customerType/DOB/residentType
as query params — this is an eligibility-validated list, not a plain
status/ACTIVE list").

**Do not** work around a stuck/empty `response-body` result by navigating a
tab directly to the raw API URL, or by running a manual `fetch()` inside the
page using a token pulled from `sessionStorage`/`localStorage`. Both were
tried in this project on 2026-09-09 and broke FusionX's silent OIDC token
renewal (`AuthNex silent renewal error: login_required`), leaving the app
stuck on the "personalization in progress" splash until a fresh headed
session was reopened (see 8.5).

### 8.3 Lookup-mapping column schema (use these exact columns/values)

When the deliverable is master-data lookup endpoints (not a CREATE/SAVE
flow), the user wants this exact column layout — confirmed against their
own example sheet, don't ask for the format again:

**Live response evidence is mandatory.** For every `High` lookup row, the
`Response Field` cell must be populated from the raw JSON body returned by
the system API when the corresponding control was opened. Do not substitute a
Swagger schema, an inferred field list, a hand-written sample, or a prose
summary. Save that body first under `lookup_responses/`, load it into the
mapping JSON, and let `build_lookup_excel.py` render it into the workbook.
If the raw body cannot be captured, lower the confidence and say why; do not
claim the endpoint is live-verified merely because its path was observed.

| Column | Content |
|---|---|
| Screen ID / Mobile Screen / Section / Field Name / UI Control | from the Word doc, same as the swagger workflow |
| Matched Service | the owning microservice path segment (e.g. `comn-common`, `comn-person`, `lending-origination`, `lending-product`, `col-collateral`), or `(client-side static)` if no API call |
| API Path | the **full URL** actually observed in `requests` (e.g. `https://<host>/comn-common/residency-type/{tenant}/status/ACTIVE`), with dependent segments as `{placeholders}` per 8.2 |
| HTTP Method | almost always `GET` for lookups; `N/A` for static/no-call fields |
| Request Parameter | the form field the selected value is written into (e.g. `residentTypeId`, `address[].paddAddressGeoNextLevelId`) |
| Response Field | the **raw JSON response body**, captured live — not summarized, not paraphrased. `build_lookup_excel.py` pretty-prints and handles truncation automatically; pass it the raw captured text as-is |
| Match Confidence | `High` (endpoint + real response captured), `Medium` (endpoint confirmed live but response not separately captured, or captured with an unresolved ambiguity), `Low` (endpoint identified but returned empty/204, or only partially confirmed), `Static` (confirmed no network call — hardcoded client-side list), `Not Found` (confirmed absent from the live app), `Blocked` (screen/data never loaded due to environment/config gaps on the test tenant, not something skipped) |
| Notes | dependency relationships, corrections vs. any earlier swagger-based guess, why something is Blocked/Not Found, anything the value doesn't obviously communicate |

Assemble rows with a small throwaway Python script inside the task folder
(not the skill directory) rather than hand-authoring one giant JSON by hand
in the Write tool — it's far less error-prone once you're past ~20 rows.
Pattern that worked well:
```python
import json, os
RESP_DIR = r"<project_dir>/<Module>/<NN>_<Task>_<date>/lookup_responses"
def load(fname):
    if not fname: return None
    with open(os.path.join(RESP_DIR, fname), encoding="utf-8") as f:
        text = f.read()
    try: return json.loads(text)
    except (ValueError, TypeError): return text

rows = []
def add(screen_id, mobile_screen, section, field_name, ui_control, service,
        path, method, req_param, resp_file, confidence, notes):
    rows.append({...})  # see build_lookup_excel.py's docstring for the exact dict shape

add("MOB-01", "Lead Generation", "Lead Details", "Resident Type", "Dropdown",
    "comn-common", "https://<host>/comn-common/residency-type/{tenant}/status/ACTIVE",
    "GET", "residentTypeId", "resp_residency.json", "High", "...")
# ... one add() call per field ...

json.dump({"module": "...", "generated_at": "...", "rows": rows},
          open("lookup_mapping_rows.json", "w", encoding="utf-8"), indent=2)
```
Save each captured raw response body to its own file under a
`lookup_responses/` folder inside the task folder as you go (step 8.2),
then `load()` it by filename when assembling — this is also what makes the
untruncated-response fallback in 8.4 possible.

Name a response file after the endpoint or capture event (for example,
`resp_country.json`, `resp_subproduct.json`, or `resp_124.json`) and reuse
that same file for every field backed by the same GET. Do not duplicate a
large raw response per field on disk just because it appears in multiple
workbook rows. Preserve observed service-path and payload spelling exactly,
including genuine backend typos; explain the anomaly in `notes` rather than
silently normalizing it. For each dependent lookup, retain the captured
response plus the generalized placeholder path and list every parent/context
parameter in `notes`.

### 8.4 Compile and build the sheet

Once the rows JSON exists (8.3), build with whichever script matches what
was captured, writing both the data JSON and the output `.xlsx` into the
task folder (see "Output folder convention" above):
```
python <skill_dir>/scripts/build_excel.py --data "<task_folder>/mapping_rows.json" --out "<task_folder>/<Name>_API_Field_Mapping_<date>.xlsx"
python <skill_dir>/scripts/build_lookup_excel.py --data "<task_folder>/lookup_rows.json" --out "<task_folder>/<Name>_Lookup_Endpoints_<date>.xlsx"
```
`build_lookup_excel.py` pretty-prints JSON response bodies into the
`Response Field` column and truncates anything over ~30,000 characters
(Excel's per-cell limit) with a pointer to a companion raw-JSON file — the
`lookup_responses/` files from 8.3 already serve as that companion, no extra
step needed.

Every row must land in the output, same rule as step 5.4 — including fields
confirmed absent from the live app (`confidence: "Not Found"`) and fields
whose screen/data never loaded due to environment/config gaps on the test
tenant rather than anything skipped (`confidence: "Blocked"`, with a note
explaining why, e.g. "no rules configured for this lead/product in this UAT
tenant, screen renders empty").

For a live CREATE/SAVE mapping, retain the completed task-folder evidence
alongside the workbook:
```
capture_<action>_reqbody.json
capture_<action>_respbody.json        # when a response was captured
workflow_capture_notes.md
live_capture_mapping_rows.json
<Name>_API_Mapping_<date>.xlsx
```
The notes and mapping JSON are the auditable source for the workbook; do not
discard them after rendering the Excel file.

### 8.5 Recovering from a stuck/broken session

If the app gets stuck on "Please wait, Your personalization is in progress."
and won't resolve after a `reload`, or the console shows
`AuthNex silent renewal error: login_required`, follow the Recovery section
of `references/browser-session.md`: inspect existing sessions and tabs first,
then surface a genuinely unusable session before replacing it. Do not use raw
API navigation or injected token-based fetches as a workaround; they can
break the app's silent OIDC renewal.

## Extending to a new module (CASA, TD, ...)

1. Get the module's swagger URLs from the user (swagger-ui.html or api-docs
   links are both fine). If the task also involves live inspection (step 8),
   get the module's live-app dashboard URL and tenant too.
2. Add/update the entry in `config/modules.json`:
   ```json
   "casa": {
     "display_name": "CASA",
     "swagger_sources": ["http://...", ...],
     "live_app": { "tenant": "...", "dashboard_url": "https://.../web/.../dashboard" }
   }
   ```
3. Locate that module's Master Data/API Requirements Word doc.
4. Run steps 2–7 above with `--module casa`. The doc's table layout may not
   be byte-identical to the lending doc — `extract_docx.py`'s header-boundary
   detection is heuristic (see `HEADER_HINTS` in that script) and generally
   copes with the same corporate template, but sanity-check
   `fields_extracted.json`'s `field_table_indices` against the doc before
   trusting it blindly on a new module's document.
