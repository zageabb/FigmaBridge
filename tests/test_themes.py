"""Theme and reusable-component metadata regression tests."""
from figmabridge import convert, pack, validate


def test_derived_palette_and_component_catalogue():
    figma = {
        "name": "Themed",
        "components": {"1:50": {"name": "Primary button", "description": "Reusable control"}},
        "document": {"children": [{"type": "CANVAS", "id": "0:1", "children": [{
            "type": "FRAME", "id": "1:1", "name": "Home", "children": [{
                "type": "TEXT", "id": "1:2", "characters": "Hello",
                "fills": [{"type": "SOLID", "color": {"r": 1, "g": 0, "b": 0}}],
            }],
        }]}]},
    }
    manifest, app, warnings = convert(figma)
    assert app["themes"]["light"]["tokens"]["figma.colour.ff0000"] == "#FF0000"
    assert app["screens"][0]["nodes"][0]["style"]["color_token"] == "figma.colour.ff0000"
    assert app["components"][0]["metadata_only"] is True
    assert app["components"][0]["source"]["key"] == "1:50"
    assert any("metadata only" in warning for warning in warnings)
    assert validate(pack(manifest, app))["screens"] == 1


def test_colour_tokens_are_reused():
    figma = {"document": {"children": [{"type": "CANVAS", "children": [{
        "type": "FRAME", "id": "1:1", "name": "Home", "children": [
            {"type": "TEXT", "id": str(i), "characters": "Text",
             "fills": [{"type": "SOLID", "color": {"r": 0, "g": 0.5, "b": 1}}]}
            for i in range(2, 5)]
    }]}]}}
    _, app, _ = convert(figma)
    tokens = app["themes"]["light"]["tokens"]
    assert len(tokens) == 1
    values = {n["style"]["color_token"] for n in app["screens"][0]["nodes"]}
    assert len(values) == 1


def test_no_fabricated_dark_theme():
    figma = {"document": {"children": [{"type": "CANVAS", "children": [
        {"type": "FRAME", "name": "Home", "children": []}
    ]}]}}
    _, app, _ = convert(figma)
    assert "dark" not in app["themes"]
