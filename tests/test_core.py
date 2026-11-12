import json
from io import BytesIO
from zipfile import ZipFile
import pytest
from figmabridge import convert, pack, validate
from figmabridge.webapp import create_app


@pytest.fixture
def figma():
    return {"name": "Demo", "document": {"children": [
        {"id": "0:1", "type": "CANVAS", "children": [
            {"id": "1:1", "name": "Home", "type": "FRAME",
             "absoluteBoundingBox": {"x": 10, "y": 10, "width": 900, "height": 600},
             "children": [{"id": "1:2", "name": "Hello", "type": "TEXT", "characters": "Welcome",
                           "absoluteBoundingBox": {"x": 20, "y": 30, "width": 100, "height": 20}}]},
            {"id": "2:1", "name": "Orders", "type": "FRAME", "children": [
                {"id": "2:2", "name": "Save Button", "type": "INSTANCE", "children": []}]}
        ]}
    ]}}


def test_import_screens(figma):
    manifest, app, warnings = convert(figma)
    assert manifest["format_version"] == "1.0.0"
    assert app["screen_order"] == ["home", "orders"]
    assert app["screens"][0]["nodes"][0]["props"]["text"] == "Welcome"
    assert app["screens"][0]["nodes"][0]["layout"]["x"] == 10
    assert warnings


def test_archive_roundtrip(figma):
    m, a, _ = convert(figma)
    payload = pack(m, a)
    assert validate(payload) == {"screens": 2, "nodes": 2}
    with ZipFile(BytesIO(payload)) as archive:
        assert set(archive.namelist()) == {"manifest.json", "application.json"}
        assert json.loads(archive.read("application.json"))["start_screen"] == "home"


def test_no_frames():
    with pytest.raises(ValueError, match="No Figma frames"):
        convert({"document": {"children": []}})


def test_bad_zip():
    with pytest.raises(ValueError):
        validate(b"not a zip")


def test_http_import(figma):
    app = create_app()
    client = app.test_client()
    assert client.get("/health").json["status"] == "ok"
    response = client.post("/import", data={
        "file": (BytesIO(json.dumps(figma).encode()), "file.json")
    }, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].endswith("application.scraft")
    assert validate(response.data)["screens"] == 2


def test_no_unsafe_actions(figma):
    m, a, _ = convert(figma)
    a["screens"][0]["nodes"][0]["action"] = {"type": "http_request", "url": "https://bad"}
    with pytest.raises(ValueError, match="Unsafe action"):
        pack(m, a)
