# FigmaBridge agent instructions

Read the canonical `.scraft` specification in zageabb/Application-Standard before making changes:
https://github.com/zageabb/Application-Standard/blob/main/standards/SCRAFT_FILE_FORMAT_v1.md

Design what matters, let AI propose what's missing, and approve what changes.

Do not copy the canonical standard into FigmaBridge. Never invent an interaction or hide an unmapped property. Keep extracted, inferred and proposed semantics distinguishable. Never store Figma tokens in commits or .scraft ZIPs.

Update DEVELOPMENT.md and tests for each implementation change. Require green CI before merge unless a blocker is explicitly recorded; do not claim untested deployment success. Preserve reverse proxy compatibility under /apps/figmabridge/.
