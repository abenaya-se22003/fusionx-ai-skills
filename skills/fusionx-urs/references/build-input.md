# Build input

Pass UTF-8 JSON to `scripts/build_urs.py`. The top-level metadata is `title`, `client`, `module`,
`version`, `drafted_by`, `release_date`, and `jira`. Lists used by the builder are shown in the
bundled example. Empty optional sections render as `[To be completed]` and must be resolved before
delivery.
