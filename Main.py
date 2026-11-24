import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

ALLOWED_ROOT_FILES = {
    "index.html",
    "admin.html",
    "sw.js",
    "manifest_b.json",
    "manifest.json",
    "icon.png",
    "aramky-splash-logo.png",
    "aramky-core.js",
}

@app.route("/")
def home():
    if os.path.exists("index.html"):
        return send_from_directory(".", "index.html")
    return "ARAMKY Gold OS Online"

@app.route("/admin.html")
def admin_page():
    if not os.path.exists("admin.html"):
        abort(404, description="admin.html not found")
    return send_from_directory(".", "admin.html")

@app.route("/<path:filename>")
def static_files(filename):
    # منع الوصول إلى ملفات الكود المصدرية أو السرية
    forbidden = {"main.py", "Main.py", "requirements.txt", ".env"}
    if filename in forbidden or filename.startswith("."):
        abort(403)

    if os.path.isfile(filename):
        return send_from_directory(".", filename)

    abort(404)

@app.route("/health")
def health():
    return {"status": "ok", "service": "ARAMKY Gold OS"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
