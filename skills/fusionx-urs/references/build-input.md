# Build input

Pass UTF-8 JSON to `scripts/build_urs.py`. The top-level metadata is `title`, `client`, `module`,
`version`, `drafted_by`, `release_date`, and `jira`. Lists used by the builder are shown in the
bundled example. Empty optional sections render as `[To be completed]` and must be resolved before
delivery.

`test_data` is required whenever `test_scenarios` is populated. Each row has six values:
dataset ID, data type (`Synthetic` or `Internal system data`), supporting scenario IDs,
field/value pairs, setup/preconditions, and expected outcome. For internal data, put source and
retrieval date in setup/preconditions; mask sensitive values.
