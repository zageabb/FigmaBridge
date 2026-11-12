"""Package approved local raster exports, without downloading arbitrary URLs.

Filename convention: Figma node 12:34 -> 12_34.png or 12_34.webp.
Only image nodes may receive assets. A node not exported remains a placeholder.
"""
from hashlib import sha256
from pathlib import Path
import re

MAX_ASSET_BYTES = 10 * 1024 * 1024
MAGIC = {
    ".png": (b"\x89PNG\r\n\x1a\n", "image/png"),
    ".jpg": (b"\xff\xd8\xff", "image/jpeg"),
    ".jpeg": (b"\xff\xd8\xff", "image/jpeg"),
    ".webp": (b"RIFF", "image/webp"),
    ".gif": (b"GIF8", "image/gif"),
}


def media_info(name, data):
    suffix = Path(name).suffix.lower()
    if suffix not in MAGIC:
        raise ValueError("Unsupported image type")
    signature, mime = MAGIC[suffix]
    if not data.startswith(signature):
        raise ValueError("Image signature does not match its extension")
    if suffix == ".webp" and data[8:12] != b"WEBP":
        raise ValueError("Invalid WebP signature")
    if not data or len(data) > MAX_ASSET_BYTES:
        raise ValueError("Image exceeds 10 MiB limit")
    return mime


def attach_local_assets(application, directory):
    """Return (asset_bytes_by_archive_path, warnings), modifying app in place."""
    root = Path(directory)
    if not root.is_dir():
        raise ValueError("Asset directory does not exist")
    payloads, warnings = {}, []
    for screen in application.get("screens", []):
        for node in screen.get("nodes", []):
            if node.get("type") != "image":
                continue
            fid = node.get("props", {}).get("figma_node_id", "")
            if not fid:
                continue
            base = re.sub(r"[^A-Za-z0-9_-]", "_", fid)
            matches = [root / (base + ext) for ext in MAGIC]
            matches = [p for p in matches if p.is_file() and not p.is_symlink()]
            if not matches:
                warnings.append(f"{fid}: image export not supplied")
                continue
            file = matches[0]
            data = file.read_bytes()
            mime = media_info(file.name, data)
            checksum = sha256(data).hexdigest()
            path = f"assets/{checksum[:24]}{file.suffix.lower()}"
            payloads[path] = data
            node.setdefault("props", {})["asset_path"] = path
            if not any(entry["path"] == path for entry in application["assets"]):
                application["assets"].append({
                    "id": checksum[:24], "path": path,
                    "media_type": mime, "sha256": checksum,
                })
    return payloads, warnings
