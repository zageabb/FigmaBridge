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
6. Bidirectional editable Figma export — **planned**: .scraft-to-Figma plugin write bridge, ID-safe updates and reviewable round-trip reconciliation without MCP.

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

## Phase 6 — Bidirectional editable Figma export (planned, 2026-11-12)

**Goal:** Write editable ScreenCraft/.scraft designs back into native Figma design files without relying on MCP, while retaining the existing read/import pathway. This is a *future independent phase*; do not interrupt Phases 1–5.

**Architecture:** Keep Python/Flask/CLI as the conversion, inspection and synchronisation service. The Figma REST API supports reading file designs but must **not** be assumed to support creating or editing Figma document nodes. Implement writes through a small Figma Plugin API companion (JavaScript/TypeScript) running in Figma with the user's permission. Export a validated, versioned intermediate design payload from FigmaBridge and let the plugin create/update Figma nodes. Support local file handoff first; optionally offer a secure explicitly authorised bridge later. The plugin must be invoked within Figma; do not claim a REST request can launch it unattended.

**Scope and requirements:**
- Export .scraft screens as editable Figma frames and child objects: text, shapes, buttons, inputs, cards, containers, grid/table-like structures, images, component representations, basic theme tokens, layout constraints and Auto Layout where representable.
- Retain stable .scraft IDs and Figma node IDs via namespaced plugin metadata / mapping manifests; distinguish native Figma editable properties from ScreenCraft-only interaction semantics. Preserve non-Figma metadata for round-trip where practical, and report lossy conversions.
- Provide both **Create new design** and **Update existing mapped design** modes. A new design may be created within a document the user opens; do not assume API permission to create/manage Figma files remotely. Avoid accidentally duplicating frames or replacing unmapped native objects.
- Reimport the resulting Figma document through the current authorised REST/plugin JSON read path and compare changes before applying them to .scraft. Present add/change/delete conflicts and manual Figma edits for explicit review and approval; never silently overwrite.
- Figma component styles, typography, constraints and token/variable mapping need capability checks against the current Plugin API, account permissions and plan entitlements. Mark unsupported items with useful warnings instead of silently flattening them.
- Protect credentials and design data: no token in .scraft/plugin manifests/logs; validate input sizes and asset types, restrict remote calls, require user consent before modifying files, and never execute arbitrary scripts from a design.
- Keep an offline export package/CLI pathway and avoid a mandatory Figma/MCP connection for ordinary ScreenCraft editing.

**Acceptance criteria:**
1. Convert a multi-screen .scraft file into an export payload and use the plugin to create editable, recognisable Figma layers (not a flattened screenshot).
2. Re-run export on a mapped Figma document without unintended duplicates; detect changed/deleted targets and require approval for destructive updates.
3. Demonstrate round-trip Figma → .scraft → Figma → .scraft with stable IDs, supported layout/property fidelity and explicit mismatch report.
4. Test nested objects, reusable components, images, tables/grids, desktop/mobile frames, text and colour tokens; document unsupported design/interaction properties.
5. Run independent Python and plugin tests plus actual Figma desktop/browser manual verification. Record evidence and unresolved API limitations; GitHub Actions remains subject to the existing billing exception.

**Status:** PLANNED — design requirement only. No Figma write implementation or live testing is claimed.
