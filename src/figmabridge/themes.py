"""Conservative translation of Figma paint styles into editable SCRAFT themes.

The canonical .scraft contract lives in Application-Standard. Imported source
metadata is preserved as ordinary data and never executed.
"""
import re


def _hex(paint):
    if not isinstance(paint, dict) or paint.get("type") != "SOLID" or not paint.get("visible", True):
        return None
    color = paint.get("color") or {}
    if not all(isinstance(color.get(k), (float, int)) for k in ("r", "g", "b")):
        return None
    return "#" + "".join(f"{max(0, min(255, round(color[k] * 255))):02X}"
                       for k in ("r", "g", "b"))


def apply_theme(figma, app):
    """Assign stable colour tokens to nodes; return informational warnings.

    Tokens are source-derived. No dark theme is fabricated from a light theme.
    """
    palette = {}
    used = set()
    source_tokens = {}

    def register(name, hex_value):
        if not hex_value:
            return None
        if hex_value in source_tokens:
            return source_tokens[hex_value]
        base = "figma." + re.sub(r"[^a-z0-9]+", ".", str(name).lower()).strip(".")
        base = base[:90] or "figma.colour"
        token = base
        counter = 2
        while token in used:
            token = f"{base}.{counter}"
            counter += 1
        used.add(token)
        palette[token] = hex_value
        source_tokens[hex_value] = token
        return token

    for style_id, definition in (figma.get("styles") or {}).items():
        if not isinstance(definition, dict):
            continue
        # REST styles metadata contains descriptions, but not necessarily
        # resolved paint definitions. Never pretend a colour was retrieved.
        value = definition.get("color")
        if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            register(definition.get("name") or style_id, value.upper())

    def visit(node):
        if not isinstance(node, dict):
            return
        for screen in app.get("screens", []):
            pass

    # The Figma API provides the full node tree. Index original node IDs so
    # colour token assignment remains deterministic across imports.
    indexed = {}
    def index(node):
        if not isinstance(node, dict):
            return
        if node.get("id"):
            indexed[node["id"]] = node
        for child in node.get("children") or []:
            index(child)
    index(figma.get("document") or figma)

    for screen in app.get("screens", []):
        for node in screen.get("nodes", []):
            source_id = node.get("props", {}).get("figma_node_id")
            source = indexed.get(source_id, {})
            for item in source.get("fills") or []:
                color = _hex(item)
                if color:
                    token = register(f"colour.{color[1:]}", color)
                    if token:
                        style = node.setdefault("style", {})
                        key = "color_token" if node["type"] == "text" else "background_color_token"
                        style[key] = token
                    break
    app.setdefault("themes", {})["light"] = {"tokens": palette}
    return [] if palette else ["No resolved solid colours found; theme remains empty"]
