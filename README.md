# FigmaBridge

Standalone Flask and Python CLI converting Figma design JSON into ScreenCraft `.scraft` ZIP documents.

**Canonical schema:** [Application-Standard SCRAFT-1](https://github.com/zageabb/Application-Standard/blob/main/standards/SCRAFT_FILE_FORMAT_v1.md). This repository deliberately links to rather than duplicates the shared standard.

## Install and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
flask --app figmabridge.webapp run --debug --port 5080
```

Open http://127.0.0.1:5080/ and upload Figma REST JSON.

## CLI

```bash
figmabridge import-json exported-figma.json -o application.scraft
figmabridge import-json exported-figma.json --assets-dir ./exported-images -o with-images.scraft
figmabridge validate application.scraft
export FIGMA_TOKEN="your-figma-personal-access-token"
figmabridge import-figma YOUR_FIGMA_FILE_KEY -o application.scraft
pytest -q
```

Treat `FIGMA_TOKEN` as a secret; do not commit it, put it into `.scraft` or pass it on the command line.

## Current limitations

- Only top-level frames within Figma pages become screens.
- Text, structure, bounds, solid fills and inferred controls are converted.
- Vector/image exports, live component instances/variants, responsive reconciliation, dark themes and prototype actions are not yet supported.
- No claims of visual parity or ScreenCraft import compatibility until integration acceptance tests pass.
- The optional API loader uses the Figma REST endpoint and cannot bypass Figma account permissions and rate limits.
- The development web server is for local use only. Secure production deployment and prefixed routing need verification.

See [DEVELOPMENT.md](DEVELOPMENT.md) for implementation phases, acceptance gates and blockers.

## Local Figma raster exports

Export individual raster image/vector nodes from Figma as PNG, JPG, WebP or GIF. Rename each export to its **Figma node ID**, replacing special characters with underscores (e.g. `12:34` → `12_34.png`), and place it in the folder given to `--assets-dir`. Image nodes whose files are found become packaged assets, referenced by nodes with `props.asset_path`. SHA-256 and MIME signatures are checked when the .scraft is read back. Missing exports remain reported as placeholders.

This does not yet download assets automatically from Figma or establish pixel-perfect parity. Asset count/size is limited, and .scraft archives are data-only.
