"""Conservative responsive metadata import.

Figma constraint rules are hints, not evidence of a responsive CSS breakpoint.
Keep explicit device-sized frames as independent screens until a designer
approves grouping. Do not automatically overwrite desktop node geometry.
"""
import re


def annotate_responsive(figma, application):
    frames = {}
    def visit(node):
        if not isinstance(node, dict):
            return
        if node.get("id"):
            frames[node["id"]] = node
        for child in node.get("children") or []:
            visit(child)
    visit(figma.get("document") or figma)

    warnings = []
    for screen in application.get("screens", []):
        title = screen.get("name", "")
        width = screen.get("viewport", {}).get("width", 0)
        inferred = ("mobile" if width and width < 768 else
                    "tablet" if 768 <= width < 1024 else "desktop")
        screen.setdefault("source", {})["figma_viewport_class"] = inferred
        screen["source"]["responsive_group_hint"] = re.sub(
            r"(?i)(?:^|[ /_\-])(?:mobile|tablet|desktop|phone|laptop)(?:$|[ /_\-])",
            " ", title).strip(" /_-") or title

        for node in screen.get("nodes", []):
            source = frames.get(node.get("props", {}).get("figma_node_id"), {})
            constraints = source.get("constraints")
            sizing = {}
            for source_key, target_key in (("layoutSizingHorizontal", "horizontal"),
                                           ("layoutSizingVertical", "vertical")):
                if source.get(source_key) in ("FIXED", "HUG", "FILL"):
                    sizing[target_key] = source[source_key].lower()
            if isinstance(constraints, dict) and constraints:
                node.setdefault("props", {})["figma_constraints"] = {
                    k: v for k, v in constraints.items() if k in ("horizontal", "vertical")
                }
            if sizing:
                node.setdefault("props", {})["figma_sizing"] = sizing
                if sizing.get("horizontal") == "fill":
                    node.setdefault("layout", {})["width"] = "fill"
                if sizing.get("vertical") == "fill":
                    node.setdefault("layout", {})["height"] = "fill"

    hints = {}
    for screen in application.get("screens", []):
        label = screen["source"]["responsive_group_hint"].lower()
        hints.setdefault(label, []).append(screen)
    for group in hints.values():
        if len(group) > 1:
            identifiers = ", ".join(screen["id"] for screen in group)
            warnings.append(f"Possible responsive variants ({identifiers}); kept as separate screens pending approval")
    return warnings
