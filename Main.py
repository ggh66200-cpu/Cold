import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

BLOCKED_FILES = {
    "main.py",
    "Main.py",
    "requirements.txt",
    "Procfile",
    "package.json",
    ".env",
}

@app.route("/")
def home():
    if os.path.isfile("index.html"):
        return send_from_directory(".", "index.html")
    return "ARAMKY Gold OS Online"

@app.route("/admin.html")
def admin_page():
    if os.path.isfile("admin.html"):
        return send_from_directory(".", "admin.html")
    abort(404)

@app.route("/<path:filename>")
def serve_file(filename):
    clean = filename.lstrip("/")
    if not clean or clean.startswith(".") or os.path.basename(clean) in BLOCKED_FILES:
        abort(403)
    full_path = os.path.abspath(os.path.join(".", clean))
    root_path = os.path.abspath(".")
    if not full_path.startswith(root_path + os.sep) and full_path != root_path:
        abort(403)
    if os.path.isfile(full_path):
        return send_from_directory(".", clean)
    abort(404)

@app.route("/health")
def health():
    return {"status": "ok", "service": "ARAMKY Gold OS"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
