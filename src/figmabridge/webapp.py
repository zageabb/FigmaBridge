"""Small standalone Flask UI. API credentials are never persisted."""
from io import BytesIO
import json
import os

from flask import Flask, flash, redirect, render_template_string, request, send_file, url_for, jsonify
from .core import convert, pack, MAX_BYTES

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FigmaBridge</title><style>
body{font:16px system-ui;margin:0;background:#f3f5f8;color:#172033}
main{max-width:760px;margin:7vh auto;padding:30px;background:white;border-radius:14px}
label{display:block;margin:16px 0 8px;font-weight:600}
input,button{font:inherit}input[type=file]{max-width:100%}
button{padding:12px 22px;background:#2257ce;color:white;border:0;border-radius:8px;cursor:pointer}
p{line-height:1.6}.muted{color:#596579}.warning{color:#9a3412}</style></head><body>
<main><h1>FigmaBridge</h1><p class="muted">Import Figma REST JSON and create a portable ScreenCraft .scraft file.</p>
{% with msgs = get_flashed_messages() %}{% for m in msgs %}<p class="warning">{{m}}</p>{% endfor %}{% endwith %}
<form action="{{ url_for('import_json') }}" method="post" enctype="multipart/form-data">
<label for="file">Figma JSON export</label><input required type="file" accept=".json,application/json" name="file" id="file">
<label for="name">Application name (optional)</label><input name="name" id="name" maxlength="120">
<p><button type="submit">Convert to .scraft</button>
<button type="submit" formaction="{{ url_for('inspect_json') }}" formtarget="_blank" style="background:#475569">Inspect first</button></p>
</form><p class="muted">Source: Application-Standard SCRAFT-1. No upload content is retained by this app.</p>
</main></body></html>"""


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES
    app.secret_key = os.environ.get("FIGMABRIDGE_SESSION_KEY", os.urandom(32))

    @app.get("/")
    def index():
        return render_template_string(PAGE)

    @app.post("/import")
    def import_json():
        attachment = request.files.get("file")
        if not attachment or not attachment.filename.lower().endswith(".json"):
            flash("Select a JSON export")
            return redirect(url_for("index"))
        try:
            figma = json.loads(attachment.stream.read(MAX_BYTES + 1))
            manifest, application, warnings = convert(figma, request.form.get("name") or None)
            result = pack(manifest, application)
        except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
            flash(f"Import failed: {exc}")
            return redirect(url_for("index"))
        response = send_file(BytesIO(result), mimetype="application/vnd.screencraft+zip",
                             as_attachment=True, download_name="application.scraft")
        response.headers["X-Import-Warnings"] = str(len(warnings))
        return response

    @app.post("/api/inspect")
    def inspect_json():
        """Return a reviewable import report without producing an archive."""
        attachment = request.files.get("file")
        if not attachment or not attachment.filename.lower().endswith(".json"):
            return jsonify({"error": "Select a JSON export"}), 400
        try:
            figma = json.loads(attachment.stream.read(MAX_BYTES + 1))
            _, application, warnings = convert(figma, request.form.get("name") or None)
        except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({
            "name": application["name"],
            "screens": [{"id": screen["id"], "name": screen["name"],
                         "viewport": screen["viewport"], "nodes": len(screen["nodes"])}
                        for screen in application["screens"]],
            "warnings": warnings,
            "warning_count": len(warnings),
            "format_version": "1.0.0",
        })

    @app.get("/health")
    def health():
        return {"status": "ok", "app": "FigmaBridge"}

    return app


app = create_app()
