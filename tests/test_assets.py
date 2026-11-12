"""Raster packaging and hostile archive regression tests."""
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import json

import pytest
from figmabridge import convert, pack, validate
from figmabridge.assets import attach_local_assets, media_info

# Minimal valid PNG signature + IHDR/IEND fixture. Signature validation is
# deliberately separate from full image decoding (future Pillow validation).
PNG = bytes.fromhex(
    "89504e470d0a1a0a"
    "0000000d49484452000000010000000108060000001f15c489"
    "0000000b49444154789c636000020000050001a5f64540"
    "0000000049454e44ae426082"
)


def fixture():
    return {"name": "Images", "document": {"children": [
        {"type": "CANVAS", "children": [
            {"type": "FRAME", "name": "Home", "id": "1:1", "children": [
                {"type": "VECTOR", "id": "12:34", "name": "Logo"}
            ]}
        ]}
    ]}}


def test_packaged_asset_roundtrip(tmp_path):
    (tmp_path / "12_34.png").write_bytes(PNG)
    manifest, app, _ = convert(fixture())
    images, warnings = attach_local_assets(app, tmp_path)
    assert not warnings
    assert len(app["assets"]) == 1
    assert app["screens"][0]["nodes"][0]["props"]["asset_path"].startswith("assets/")
    blob = pack(manifest, app, images)
    assert validate(blob)["screens"] == 1
    with ZipFile(BytesIO(blob)) as archive:
        assert app["assets"][0]["path"] in archive.namelist()


def test_missing_asset_is_warning(tmp_path):
    _, app, _ = convert(fixture())
    images, warnings = attach_local_assets(app, tmp_path)
    assert not images
    assert any("12:34" in entry for entry in warnings)


def test_image_signature_rejected():
    with pytest.raises(ValueError, match="signature"):
        media_info("bad.png", b"not a png")


def test_missing_declaration_rejected():
    manifest, app, _ = convert(fixture())
    with pytest.raises(ValueError, match="Undeclared"):
        pack(manifest, app, {"assets/orphan.png": PNG})


def test_zip_traversal_rejected():
    manifest, app, _ = convert(fixture())
    out = BytesIO()
    with ZipFile(out, "w", ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("application.json", json.dumps(app))
        archive.writestr("../bad.png", PNG)
    with pytest.raises(ValueError, match="unsafe"):
        validate(out.getvalue())
