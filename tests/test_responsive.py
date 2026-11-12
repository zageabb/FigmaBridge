"""Responsive layout conversion tests: keep frame variants non-destructive."""
from figmabridge import convert, pack, validate


def test_mobile_desktop_frames_remain_separate():
    figma = {"name": "Demo", "document": {"children": [
        {"type": "CANVAS", "children": [
            {"type": "FRAME", "name": "Orders / Desktop", "id": "1:1",
             "absoluteBoundingBox": {"width": 1440, "height": 900},
             "children": [{"type": "TEXT", "name": "Label", "id": "1:2", "characters": "Orders",
                           "layoutSizingHorizontal": "FILL",
                           "constraints": {"horizontal": "STRETCH", "vertical": "TOP"}}]},
            {"type": "FRAME", "name": "Orders / Mobile", "id": "2:1",
             "absoluteBoundingBox": {"width": 390, "height": 844}, "children": []}
        ]}
    ]}}
    manifest, application, warnings = convert(figma)
    assert application["screen_order"] == ["orders-desktop", "orders-mobile"]
    assert application["screens"][0]["source"]["figma_viewport_class"] == "desktop"
    assert application["screens"][1]["source"]["figma_viewport_class"] == "mobile"
    node = application["screens"][0]["nodes"][0]
    assert node["layout"]["width"] == "fill"
    assert node["props"]["figma_constraints"]["horizontal"] == "STRETCH"
    assert any("Possible responsive variants" in item for item in warnings)
    assert validate(pack(manifest, application))["screens"] == 2


def test_vertical_only_sizing_is_safe():
    figma = {"document": {"children": [{"type": "CANVAS", "children": [
        {"type": "FRAME", "name": "Only", "children": [
            {"type": "TEXT", "id": "7:8", "characters": "Hello",
             "layoutSizingVertical": "FILL"}
        ]}
    ]}]}}
    _, app, _ = convert(figma)
    assert app["screens"][0]["nodes"][0]["layout"]["height"] == "fill"
