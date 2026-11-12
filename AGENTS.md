# FigmaBridge agent instructions

Read the canonical `.scraft` specification in zageabb/Application-Standard before making changes:
https://github.com/zageabb/Application-Standard/blob/main/standards/SCRAFT_FILE_FORMAT_v1.md

Design what matters, let AI propose what's missing, and approve what changes.

Do not copy the canonical standard into FigmaBridge. Never invent an interaction or hide an unmapped property. Keep extracted, inferred and proposed semantics distinguishable. Never store Figma tokens in commits or .scraft ZIPs.

Update DEVELOPMENT.md and tests for each implementation change. Preserve reverse-proxy compatibility under /apps/figmabridge/.

## Temporary GitHub Actions billing exception (2026-11-12)

GitHub Actions is blocked by account billing. **Do not wait on, require, or report green Actions status** until the user lifts this exception. Continue development and independent testing. Run pytest, CLI round-trips, format validation and smoke tests locally or through an available non-Actions runner. Record exact test commands, environment and outcomes in DEVELOPMENT.md. GitHub PRs may merge with this documented CI exception when available independent checks pass; never describe CI as passed or skip security-critical tests merely because Actions is unavailable.
