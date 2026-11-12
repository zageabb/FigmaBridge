# FigmaBridge development register

Updated: 2026-11-12. Separate development from ScreenCraft.
**Canonical SCRAFT spec:** [Application-Standard](https://github.com/zageabb/Application-Standard/blob/main/standards/SCRAFT_FILE_FORMAT_v1.md) version 1.0.0, observed source blob `edd51749b6ea9cc82963d494cc79c13cde9fe052`.
Read the latest upstream source before every mapping change. Do not duplicate the normative specification.

## Phase status
1. Foundation — **code in PR #1, independent tests pending; Actions billing blocked**: Flask app, CLI, ZIP writer, structural validator, pytest, CI.
2. Design extraction — **partial**: top-level Figma frames, basic nodes, solid fills, text, geometry, inferred controls and warnings. Actual asset packaging and editor acceptance pending.
3. Advanced conversion — **planned**: component instances/variants, assets, themes, layout constraints, responsive views, supported prototype links, import diff reports.
4. Figma connectivity — **partial**: opt-in REST file API retrieval via `FIGMA_TOKEN`, strict file key/host, size cap and timeouts; caching, API retry/rate-limit handling and editor plugin still planned.
5. ScreenCraft/GitHub integration — **planned**: compatibility tests, GitHub branch/PR sync, safe reconciliation and human approval for changes.

## Phase acceptance
- P1: green unit tests, malformed archives rejected, valid baseline SCRAFT file.
- P2: genuine multi-screen Figma JSON produces editable ScreenCraft nodes; unconverted elements visible.
- P3: two themes, packaged image, table, navigation, mobile layout, reusable components and stable IDs survive round trip.
- P4: authorised API import and offline fallback; no secret leakage or unexpected external requests.
- P5: ScreenCraft imports and reopens generated .scraft, with changes proposed through reviewable PRs.

## Decisions
- Python package is reusable; Flask is only a standalone frontend, CLI remains offline capable.
- The .scraft contract is authored in Application-Standard; importer must not change the shared format unilaterally.
- `figma_node_id` and inferred control warnings preserve source provenance.
- Never invent working business actions; no arbitrary code or production data in .scraft.
- Temporary exception (2026-11-12): GitHub Actions is blocked by billing. Do not wait on GitHub Actions; independent local pytest, CLI, archive validation and Flask smoke tests become the immediate gates. Merge with recorded independent test evidence where permitted, without claiming CI is green. Restore CI checks when billing is fixed. Tests, documentation and manual updates remain required with code changes.
- Prefix hosting under `/apps/figmabridge/` is an acceptance requirement, not yet validated.
- Design principle: Design what matters, let AI propose what's missing, and approve what changes.

## Open risks
- Validator is baseline structural validation, not yet full SCRAFT-1 conformance (assets, refs, JSON nesting caps and complete schema checks pending).
- Current extraction uses placeholder graphics; actual editable preview and visual parity unverified.
- Figma API token management, rate limiting, retry/backoff, optional plugin and server hardening pending.
- ScreenCraft API and shared integration contract will be tested once available.

## CI infrastructure exception — 2026-11-12
- User confirmed GitHub Actions is blocked by billing and authorised ignoring Actions for now.
- Continue Phases 1–5 and independent tests; avoid repeated Actions status checks while blocked.
- For each test run record the command, environment, pass/fail counts, outstanding failures, and merge decision here.
- Exception removes the CI gate, **not** functional/security acceptance criteria. No tests have been claimed as passing under this exception yet.
