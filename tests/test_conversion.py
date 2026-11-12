"""Regression coverage for Figma semantics and inspection reporting."""
import json
from io import BytesIO
from zipfile import ZipFile

from figmabridge import convert, pack, validate
from figmabridge.webapp import create_app


def sample():
    return {
        "name": "Navigation demo",
        "document": {"children": [{"type": "CANVAS", "id": "0:1", "children": [
            {"id": "1:1", "type": "FRAME", "name": "Home",
             "absoluteBoundingBox": {"x": 5, "y": 9, "width": 800, "height": 500},
             "children": [
                 {"id": "1:2", "type": "FRAME", "name": "Open Button",
                  "layoutMode": "HORIZONTAL", "itemSpacing": 8, "paddingLeft": 12,
                  "componentId": "component-123",
                  "componentProperties": {"State": {"value": "Default"}},
                  "reactions": [{"trigger": {"type": "ON_CLICK"},
                                 "action": {"type": "NODE", "destinationId": "2:1"}}],
                  "children": [{"id": "1:3", "type": "TEXT", "characters": "Open"}]}]},
            {"id": "2:1", "type": "FRAME", "name": "Details", "children": []},
        ]}]},
    }


def test_reactions_map_only_safe_button_navigation():
    manifest, app, warnings = convert(sample())
    button = app["screens"][0]["nodes"][0]
    assert button["type"] == "button"
    assert button["action"] == {"type": "navigate", "target_screen": "details"}
    assert button["layout"]["mode"] == "flex"
    assert button["layout"]["padding"]["left"] == 12
    assert button["props"]["figma_component_id"] == "component-123"
    assert button["props"]["figma_component_properties"]["State"]["value"] == "Default"
    assert validate(pack(manifest, app))["screens"] == 2


def test_unknown_target_warns_instead_of_adding_action():
    doc = sample()
    reaction = doc["document"]["children"][0]["children"][0]["children"][0]["reactions"][0]
    reaction["action"]["destinationId"] = "does-not-exist"
    _, app, warnings = convert(doc)
    assert "action" not in app["screens"][0]["nodes"][0]
    assert any("navigation not mapped" in warning for warning in warnings)


def test_inspection_api_shows_warnings():
    app = create_app()
    response = app.test_client().post(
        "/api/inspect",
        data={"file": (BytesIO(json.dumps(sample()).encode()), "figma.json")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.json["screens"][0]["name"] == "Home"
    assert response.json["format_version"] == "1.0.0"


def test_inspection_api_rejects_bad_input():
    response = create_app().test_client().post(
        "/api/inspect",
        data={"file": (BytesIO(b"broken"), "broken.json")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.json["error"]
