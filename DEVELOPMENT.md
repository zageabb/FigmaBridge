# FigmaBridge development register

Updated: 2026-11-12. Separate development from ScreenCraft.
**Canonical SCRAFT spec:** [Application-Standard](https://github.com/zageabb/Application-Standard/blob/main/standards/SCRAFT_FILE_FORMAT_v1.md) version 1.0.0, observed source blob `edd51749b6ea9cc82963d494cc79c13cde9fe052`.
Read the latest upstream source before every mapping change. Do not duplicate the normative specification.

## Phase status
1. Foundation — **code in PR #1, independent tests pending; Actions billing blocked**: Flask app, CLI, ZIP writer, structural validator, pytest, CI.
2. Design extraction — **partial, expanded**: top-level Figma frames, basic nodes, solid fills, text, geometry, inferred controls, Figma component metadata, Auto Layout spacing/alignment, supported click-navigation and review warnings. Actual asset packaging and editor acceptance pending.
3. Advanced conversion — **partial**: safe click navigation and Auto Layout settings implemented; reusable component definitions, assets, themes, responsive views and visual diff reports still planned.
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

## 2026-11-12 development continuation
- Importer now stores Figma component identity/properties, Auto Layout direction, padding, alignment and clipping.
- ON_CLICK NODE prototype reactions map to a `navigate` action only when the source is a button and the destination is a known screen. Unsupported actions are flagged rather than executed.
- Added `POST /api/inspect` report with screen inventory and warnings, plus **Inspect first** UI action. No Figma JSON retained.
- Added tests in `tests/test_conversion.py` covering navigation, unmapped destinations, layout and inspect endpoint.
- **Verification:** source committed in PR #1; pytest has not been executed independently in this environment. GitHub Actions unavailable due to billing. Consequently the feature branch is not marked tested, and merge remains pending independent evidence.

## 2026-11-12 Phase 3 continuation (PR #2 candidate)
- Implemented source-derived Figma solid-fill colour tokens in `themes.light.tokens`; editable nodes reference matching tokens.
- Preserved Figma reusable-component catalogue entries with `metadata_only: true` instead of fabricating definitions; source IDs and descriptions retained.
- Added regression tests for token reuse, catalogue metadata and no artificial dark-theme creation.
- The converter still cannot package graphic assets or reconstruct full reusable component definitions; actual visual parity is unverified.
- Verification status: code and tests committed, **pytest not executed**; Actions billing exception remains. New work must be treated as unverified until an independent test runner can execute it.

## 2026-11-12 Phase 3 asset packaging (PR #3 candidate)
- PR #2 merged into main under the user-approved GitHub Actions billing exception (merge `6e1372c`).
- Added opt-in offline image packaging with CLI `--assets-dir`. Local image filenames correspond to Figma node IDs (e.g. `12:34` -> `12_34.png`). Asset references stay inside the .scraft ZIP and are stored in `application.assets`.
- Validator now checks ZIP entry allowlisting, duplicate entries, expansion limits, image signatures, media types and optional SHA-256 checksums; undeclared and missing assets are rejected.
- Added `tests/test_assets.py` covering packaged assets, missing exports, signature mismatches, undeclared entries and ZIP traversal.
- **Not yet implemented:** automatic Figma asset download/export, full decoded image safety checks, full SCRAFT-1 conformance and visual parity checks.
- **Verification:** code committed but pytest cannot run from this connector environment; GitHub Actions unavailable due to billing. PR is unverified and should receive independent tests before production deployment. No claim that acceptance is met.

## 2026-11-12 Phase 3 responsive continuation (PR #4 candidate)
- PR #3 merged into main via squash commit `84c1344`; GitHub Actions exemption remains active.
- Added `responsive.py` to preserve Figma layout sizing and constraints, annotate viewport class and identify possible mobile/desktop/tablet frame groups without automatically merging screens or inventing breakpoints.
- Added `tests/test_responsive.py` for integration regression (committed, not executed on the full checkout).
- **Independent test evidence:** isolated local mirror of the new `annotate_responsive` module tested with `python -m pytest -q test_responsive_isolated.py`, CPython local environment, **2 passed in 0.07s**. This verifies two targeted behaviours of the copied module only; it does not verify the whole repository or its import pipeline.
- Full repository pytest, CLI archive round-trip, image validation, ScreenCraft import and deployment smoke tests remain pending. These must not be marked passed on the basis of the isolated check.
