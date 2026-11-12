"""FigmaBridge CLI: offline JSON, optional Figma REST API and validation."""
import argparse
import json
import os
from pathlib import Path
from .core import convert, pack, validate, MAX_BYTES
from .figma_api import fetch_figma_file


def main():
    parser = argparse.ArgumentParser(description="Import Figma designs to .scraft")
    sub = parser.add_subparsers(dest="command", required=True)
    offline = sub.add_parser("import-json")
    offline.add_argument("input", type=Path)
    online = sub.add_parser("import-figma")
    online.add_argument("file_key", help="Figma file key from design URL")
    for cmd in (offline, online):
        cmd.add_argument("-o", "--output", type=Path, required=True)
        cmd.add_argument("--name")
    check = sub.add_parser("validate")
    check.add_argument("input", type=Path)
    args = parser.parse_args()
    if args.command == "validate":
        if args.input.stat().st_size > MAX_BYTES:
            parser.error("Input exceeds 25 MiB")
        print(json.dumps(validate(args.input.read_bytes()), indent=2))
        return
    if args.command == "import-json":
        if args.input.stat().st_size > MAX_BYTES:
            parser.error("Input exceeds 25 MiB")
        figma = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        figma = fetch_figma_file(args.file_key, os.environ.get("FIGMA_TOKEN"))
    manifest, application, warnings = convert(figma, args.name)
    args.output.write_bytes(pack(manifest, application))
    print(json.dumps({"output": str(args.output), "screens": len(application["screens"]),
                      "warnings": warnings}, indent=2))


if __name__ == "__main__":
    main()
