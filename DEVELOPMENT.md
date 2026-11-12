# FigmaBridge development register

Updated: 2026-11-12. Standalone importer runs alongside ScreenCraft development.
Authoritative .scraft standard: [Application-Standard SCRAFT-1](https://github.com/zageabb/Application-Standard/blob/main/standards/SCRAFT_FILE_FORMAT_v1.md).
Do not fork/copy the schema into this repository; record the format version and source commit when validating.

## Status
- Phase 1 Foundation: IMPLEMENTED IN FEATURE BRANCH, PENDING TEST/CI REVIEW. Flask app, CLI, basic SCRAFT-1 writer/validator, pytest.
- Phase 2 Basic extraction: PARTIAL. Figma REST JSON frames/text/containers/geometry; inferred controls flagged; graphical assets remain placeholders.
- Phase 3 Advanced design conversion: PLANNED. Real assets, components, themes, interactions, responsive reconciliation, visual diffs.
- Phase 4 Figma connectivity: PLANNED. API, caching, OAuth/token safety and optional Figma plugin.
- Phase 5 ScreenCraft integration: PLANNED. Package/REST contract, GitHub PR sync and round-trip tests.

## Acceptance gates
1. Unit tests and CI green; malformed archives and unsupported actions rejected.
2. Figma multi-screen JSON imports as editable .scraft and warnings are visible.
3. Two themes, bundled image, mock table, navigation, responsive views and preserved IDs round-trip in ScreenCraft.
4. Authenticated Figma imports meet rate limits and never persist credentials.
5. ScreenCraft end-to-end import and GitHub review workflow proven.

## Decisions
- Flask with reusable Python converter package; CLI for offline operation.
- Free Figma JSON first; live API optional and no dependency for offline tests.
- Maintain source node IDs under node props for traceability.
- AI inference must remain reviewable; unsupported Figma controls do not acquire fabricated behaviour.
- No production SQL or executable actions inside .scraft.
- Keep tests and docs current; do not merge until CI is verified green.
- Reverse-proxy route /apps/figmabridge/ must be verified separately before deployment claims.

## Outstanding issues
- Specification is draft SCRAFT-1; track upstream changes and version compatibility.
- Actual editable ScreenCraft round-trip and visual parity cannot yet be verified.
- Asset extraction, design-token mapping and responsive auto-layout remain unimplemented.
- Upload-side processing limit, production auth, CSRF, rate limiting and deployment hardening before public hosting.
