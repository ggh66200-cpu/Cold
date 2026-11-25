import os
from flask import Flask, jsonify, send_from_directory, abort, make_response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=BASE_DIR,
    static_url_path=""
)

ALLOWED_STATIC_FILES = {
    "index.html",
    "admin.html",
    "admin_3.html",
    "aramky-core.js",
    "aramky-i18n.js",
    "main.js",
    "sw.js",
    "icon.png",
    "manifest.json",
    "manifest_5.json",
}


def _serve_html_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(filepath):
        abort(404)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/")
def home():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.isfile(index_path):
        return _serve_html_file("index.html")
    return "ARAMKY Gold OS Online", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/admin.html")
def admin_page():
    return _serve_html_file("admin.html")


@app.route("/admin_3.html")
def admin_v3_page():
    return _serve_html_file("admin_3.html")


@app.route("/sw.js")
def service_worker():
    sw_path = os.path.join(BASE_DIR, "sw.js")
    if not os.path.isfile(sw_path):
        abort(404)
    resp = make_response(send_from_directory(BASE_DIR, "sw.js", mimetype="application/javascript"))
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.route("/api/supabase-config", methods=["GET"])
def api_supabase_config():
    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    supabase_key = (
        os.environ.get("SUPABASE_KEY", "").strip()
        or os.environ.get("SUPABASE_ANON_KEY", "").strip()
    )
    supabase_table = os.environ.get("SUPABASE_TABLE", "aramky_stores_data").strip() or "aramky_stores_data"

    return jsonify({
        "ok": bool(supabase_url and supabase_key),
        "supabaseUrl": supabase_url,
        "supabaseKey": supabase_key,
        "supabaseTable": supabase_table,
    }), 200


@app.route("/<path:filename>")
def serve_static_asset(filename):
    clean_name = os.path.basename(filename)
    if clean_name not in ALLOWED_STATIC_FILES:
        abort(404)
    filepath = os.path.join(BASE_DIR, clean_name)
    if not os.path.isfile(filepath):
        abort(404)
    return send_from_directory(BASE_DIR, clean_name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
