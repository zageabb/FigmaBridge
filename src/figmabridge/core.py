"""Conservative Figma JSON -> SCRAFT-1 conversion, with explicit warnings.

Canonical specification:
https://github.com/zageabb/Application-Standard/blob/main/standards/SCRAFT_FILE_FORMAT_v1.md
"""
from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import json
import re
import uuid

MAX_BYTES = 25 * 1024 * 1024
MAX_SCREENS = 100
MAX_NODES = 500
COMPONENTS = {"text", "button", "input", "select", "checkbox", "table",
              "image", "container", "tabs", "modal"}
ACTIONS = {"navigate", "back", "show_modal", "close_modal", "toggle_visibility",
           "set_mock_field", "add_mock_row", "delete_mock_row", "message"}


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")[:80] or "unnamed"


def unique(name, used):
    base = name
    number = 2
    while name in used:
        name = f"{base}-{number}"
        number += 1
    used.add(name)
    return name


def _color(paints):
    for paint in paints or []:
        if paint.get("type") == "SOLID" and paint.get("visible", True):
            color = paint.get("color", {})
            if all(c in color for c in ("r", "g", "b")):
                return "#" + "".join(f"{max(0, min(255, round(color[c] * 255))):02X}" for c in ("r", "g", "b"))
    return None


def _layout(node, parent):
    bounds = node.get("absoluteBoundingBox") or {}
    origin = (parent or {}).get("absoluteBoundingBox") or {}
    result = {}
    for key in ("x", "y", "width", "height"):
        if key in bounds:
            result[key] = round(bounds[key] - origin.get(key, 0), 2) if key in ("x", "y") else round(bounds[key], 2)
    if node.get("layoutMode") in ("HORIZONTAL", "VERTICAL"):
        result["mode"] = "flex"
        result["direction"] = "row" if node["layoutMode"] == "HORIZONTAL" else "column"
        result["gap"] = node.get("itemSpacing", 0)
        padding = {axis: node.get("padding" + suffix, 0)
                   for axis, suffix in (("top", "Top"), ("right", "Right"),
                                        ("bottom", "Bottom"), ("left", "Left"))}
        result["padding"] = padding
        if node.get("primaryAxisAlignItems"):
            result["justify"] = node["primaryAxisAlignItems"].lower()
        if node.get("counterAxisAlignItems"):
            result["align"] = node["counterAxisAlignItems"].lower()
    if node.get("clipsContent"):
        result["overflow_x"] = "hidden"
        result["overflow_y"] = "hidden"
    return result


def _kind(node):
    typ = node.get("type")
    if typ == "TEXT":
        return "text", False
    if typ in ("FRAME", "GROUP", "COMPONENT", "INSTANCE", "SECTION"):
        name = node.get("name", "").lower()
        for marker, kind in (("button", "button"), ("modal", "modal"),
                             ("checkbox", "checkbox"), ("dropdown", "select"),
                             ("input", "input"), ("text field", "input")):
            if marker in name:
                return kind, True
        return "container", False
    return "image", False


def convert(figma, name=None):
    """Return (manifest, application, warnings); never invent interactions."""
    if not isinstance(figma, dict):
        raise ValueError("Figma input must be a JSON object")
    root = figma.get("document", figma)
    if not isinstance(root, dict):
        raise ValueError("Missing Figma document")
    screens, warnings, used_screens = [], [], set()
    pending_navigation = []
    frame_ids = {}

    for page in root.get("children", []):
        for frame in page.get("children", []):
            if frame.get("type") not in ("FRAME", "COMPONENT", "INSTANCE"):
                continue
            if len(screens) >= MAX_SCREENS:
                raise ValueError("Too many screens")
            screen_id = unique(slug(frame.get("name", "screen")), used_screens)
            if frame.get("id"):
                frame_ids[frame["id"]] = screen_id
            used_nodes, nodes = set(), []

            def visit(node, parent, parent_id=None):
                if len(nodes) >= MAX_NODES:
                    raise ValueError("Too many nodes in screen")
                kind, inferred = _kind(node)
                node_id = unique("figma-" + slug(node.get("id", "unknown")), used_nodes)
                props = {"figma_name": node.get("name", ""), "figma_node_id": node.get("id", "")}
                if kind == "text":
                    props["text"] = node.get("characters", "")
                elif kind in ("button", "input", "select", "checkbox"):
                    props["label"] = node.get("name", kind)
                if inferred:
                    warnings.append(f"{node.get('id')}: inferred {kind} from layer name; review")
                if kind == "image":
                    warnings.append(f"{node.get('id')}: graphics require asset export; image placeholder")
                if node.get("componentId"):
                    props["figma_component_id"] = node["componentId"]
                if node.get("componentProperties"):
                    props["figma_component_properties"] = node["componentProperties"]
                style = {}
                color = _color(node.get("fills"))
                if color:
                    style["color" if kind == "text" else "background_color"] = color
                for k, v in (node.get("style") or {}).items():
                    if k in ("fontFamily", "fontSize", "fontWeight"):
                        style[{"fontFamily": "font_family", "fontSize": "font_size", "fontWeight": "font_weight"}[k]] = v
                output = {"id": node_id, "type": kind, "parent_id": parent_id,
                          "props": props, "layout": _layout(node, parent), "style": style}
                nodes.append(output)
                # Figma REST exposes prototype links as reactions; some exports
                # use interactions with an actions array. Handle both, safely.
                reactions = list(node.get("reactions") or []) + list(node.get("interactions") or [])
                for reaction in reactions:
                    trigger = reaction.get("trigger") or {}
                    actions = reaction.get("actions")
                    if actions is None:
                        actions = [reaction.get("action") or {}]
                    for target in actions:
                        if (target.get("type") == "NODE"
                                and target.get("destinationId")
                                and trigger.get("type") == "ON_CLICK"):
                            pending_navigation.append(
                                (output, target["destinationId"], node.get("id", "")))
                        else:
                            warnings.append(
                                f"{node.get('id')}: unsupported Figma interaction; review")
                for child in node.get("children", []):
                    visit(child, node, node_id)

            for child in frame.get("children", []):
                visit(child, frame)
            bounds = frame.get("absoluteBoundingBox") or {}
            screens.append({"id": screen_id, "name": frame.get("name", screen_id),
                            "viewport": {"width": max(1, round(bounds.get("width", 1280))),
                                         "height": max(1, round(bounds.get("height", 800)))},
                            "layout": {"mode": "freeform", "overflow_x": "auto", "overflow_y": "auto"},
                            "nodes": nodes,
                            "source": {"provider": "figma", "node_id": frame.get("id", ""),
                                       "page_id": page.get("id", "")}})
    if not screens:
        raise ValueError("No Figma frames found under document pages")
    for node, destination, source_id in pending_navigation:
        if destination in frame_ids and node["type"] == "button":
            node["action"] = {"type": "navigate", "target_screen": frame_ids[destination]}
        else:
            warnings.append(f"{source_id}: navigation not mapped (target or control unsupported)")
    title = name or figma.get("name") or "Imported Figma Design"
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest = {"format": "screencraft", "format_version": "1.0.0",
                "document_id": str(uuid.uuid4()), "document_revision": 1,
                "name": title, "entry": "application.json",
                "created_at": timestamp, "updated_at": timestamp,
                "generator": {"name": "FigmaBridge", "version": "0.1.0"}}
    application = {"application_id": slug(title), "name": title,
                   "start_screen": screens[0]["id"], "default_theme": "light",
                   "screen_order": [s["id"] for s in screens], "screens": screens,
                   "components": [], "themes": {"light": {"tokens": {}}},
                   "datasets": [], "assets": []}
    if figma.get("components"):
        warnings.append("Reusable Figma component definitions are not yet mapped")
    return manifest, application, warnings


def pack(manifest, application):
    """Produce a self-contained SCRAFT-1 ZIP file."""
    data = BytesIO()
    with ZipFile(data, "w", ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        archive.writestr("application.json", json.dumps(application, ensure_ascii=False, indent=2))
    result = data.getvalue()
    validate(result)
    return result


def validate(payload):
    """Validate safe minimal SCRAFT archive and referential consistency."""
    if len(payload) > MAX_BYTES:
        raise ValueError("Archive too large")
    try:
        archive = ZipFile(BytesIO(payload))
    except Exception as exc:
        raise ValueError("Invalid ZIP") from exc
    with archive:
        entries = archive.infolist()
        names = [item.filename for item in entries]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entries")
        if set(names) != {"manifest.json", "application.json"}:
            raise ValueError("Unsupported or missing ZIP entries")
        if any(item.file_size > MAX_BYTES or ((item.external_attr >> 16) & 0o170000) == 0o120000 for item in entries):
            raise ValueError("Unsafe ZIP entry")
        manifest = json.loads(archive.read("manifest.json"))
        app = json.loads(archive.read("application.json"))
    if manifest.get("format") != "screencraft" or manifest.get("entry") != "application.json":
        raise ValueError("Invalid manifest")
    version = manifest.get("format_version", "")
    if not re.fullmatch(r"1\.\d+\.\d+", version):
        raise ValueError("Unsupported SCRAFT version")
    if not isinstance(manifest.get("document_revision"), int) or manifest["document_revision"] < 1:
        raise ValueError("Invalid document revision")
    screens = app.get("screens", [])
    ids = [s["id"] for s in screens]
    if not ids or len(ids) > MAX_SCREENS or len(ids) != len(set(ids)):
        raise ValueError("Invalid screen IDs")
    if app.get("start_screen") not in ids or app.get("screen_order") != ids:
        raise ValueError("Invalid start screen or screen order")
    for screen in screens:
        vp = screen.get("viewport", {})
        if any(not isinstance(vp.get(k), int) or vp[k] <= 0 for k in ("width", "height")):
            raise ValueError("Invalid viewport")
        nodes = screen.get("nodes", [])
        nids = [n["id"] for n in nodes]
        if len(nodes) > MAX_NODES or len(set(nids)) != len(nids):
            raise ValueError("Duplicate or excessive node IDs")
        index = {n["id"]: n for n in nodes}
        for n in nodes:
            if n.get("type") not in COMPONENTS:
                raise ValueError("Unsupported node type")
            pid = n.get("parent_id")
            visited = {n["id"]}
            while pid is not None:
                if pid not in index or pid in visited:
                    raise ValueError("Missing or cyclic parent")
                visited.add(pid)
                pid = index[pid].get("parent_id")
            action = n.get("action")
            if action and action.get("type") not in ACTIONS:
                raise ValueError("Unsafe action")
            if action and action.get("type") == "navigate" and action.get("target_screen") not in ids:
                raise ValueError("Missing navigation target")
    return {"screens": len(screens), "nodes": sum(len(s["nodes"]) for s in screens)}
