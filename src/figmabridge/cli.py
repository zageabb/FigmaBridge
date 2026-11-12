"""Command line conversion and validation."""
import argparse
import json
from pathlib import Path
from .core import convert, pack, validate, MAX_BYTES


def main():
    parser = argparse.ArgumentParser(description="Import Figma JSON to .scraft")
    sub = parser.add_subparsers(dest="command", required=True)
    imp = sub.add_parser("import-json")
    imp.add_argument("input", type=Path)
    imp.add_argument("-o", "--output", type=Path, required=True)
    imp.add_argument("--name")
    check = sub.add_parser("validate")
    check.add_argument("input", type=Path)
    args = parser.parse_args()
    if args.input.stat().st_size > MAX_BYTES:
        parser.error("Input exceeds 25 MiB")
    if args.command == "validate":
        print(json.dumps(validate(args.input.read_bytes()), indent=2))
        return
    figma = json.loads(args.input.read_text(encoding="utf-8"))
    manifest, application, warnings = convert(figma, args.name)
    args.output.write_bytes(pack(manifest, application))
    print(json.dumps({"output": str(args.output), "screens": len(application["screens"]),
                      "warnings": warnings}, indent=2))


if __name__ == "__main__":
    main()
