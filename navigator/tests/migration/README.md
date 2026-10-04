# Python → TypeScript migration contracts

The initial suite was built and passed against Python **before** implementation
of the TypeScript backend. Further boundary and network cases were added during
migration and passed against both implementations. `cases.py` supplies the same
inputs to both; `oracle.py` is a test-only JSON adapter, not a runtime bridge.

The existing Python backend is retained as the reference for local research and
comparison. Production TypeScript must not import it, spawn Python, or call the
old HTTP service.

| Area | Checks |
|---|---|
| Source documents and packets | All saved source texts, cleaning, Unicode, headings, selection, packet content and hashes |
| Model answers | JSON fences, nested objects, trailing commas, truncation, receipts, incorrect packet IDs |
| Rules and citations | Required fields, official schema, numbers/dates, exact/ellipsis/fuzzy quotes, chapter merging, conflicts |
| Coverage | Both sides of date and unit boundaries, unknown facts, occupancy dates, rolling years, owner exceptions, conditional windows, replacement units, conflicting address counts |
| Priority and review | Direction, dependency chains, cycles, missing sources, state/city review flags, export |
| Changes | Supplied dates, five actual cases, synthetic types, missing rules, valid/invalid date replacements |
| API extraction | Completion/resume, repair, one pass, preview, malformed and unfinished responses, whole response archives |
| Model tools | Cards, self-checks, final validation, error handling, repeated correction |
| HTTP client | Actual local requests, request payload and credentials, no redirects/retries, malformed responses |
| Address resolution | Actual local Census requests, saved cache, full 500-address offline replay, missing cache failures |
| Web server | All six routes, response fields, input errors, static asset bytes, traversal rejection, request-only facts |
| Real acceptance | All 500 addresses on three dates, every rule trace and explanation, every extracted source and packet |

Only measured query duration, random attempt names and timestamps are excluded
where they are inherently variable. Decisions, array order, explanations, errors,
source text, omission reasons and all stable fields must match.

Raw run logs and the fixed local source/data copy live in `tests/.migration/`,
which is ignored by Git. Tests and this scope document are versionable.

Existing test assumptions were corrected before migration:

- Preserve an existing evaluation directory byte-for-byte instead of requiring
  it not to exist.
- A complete Los Angeles cutoff example includes the replacement-unit condition
  now required by the project's updated labels.
- The Massachusetts negative case uses the date specified in T5 and distinguishes
  a state rule prohibiting local caps from a rule imposing a cap, using the
  explicit `preempts_local` relation in the record.
