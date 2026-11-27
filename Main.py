import os
import re
from flask import Flask, jsonify, send_from_directory, abort, make_response, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=BASE_DIR,
    static_url_path=""
)

ALLOWED_STATIC_FILES = {
    "index.html",
    "admin.html",
    "aramky-core.js",
    "aramky-i18n.js",
    "main.js",
    "sw.js",
    "icon.png",
    "manifest.json",
}

SAFE_SHOWCASE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{4,48}$")


def _serve_html_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(filepath):
        abort(404)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}


def _read_supabase_env():
    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    supabase_key = (
        os.environ.get("SUPABASE_KEY", "").strip()
        or os.environ.get("SUPABASE_ANON_KEY", "").strip()
    )
    supabase_table = os.environ.get("SUPABASE_TABLE", "aramky_stores_data").strip() or "aramky_stores_data"
    render_api_base = os.environ.get("RENDER_API_BASE", "").strip()

    missing = []
    if not supabase_url:
        missing.append("SUPABASE_URL")
    if not supabase_key:
        missing.append("SUPABASE_KEY")

    return {
        "configured": len(missing) == 0,
        "missing": missing,
        "supabaseUrl": supabase_url,
        "supabaseKey": supabase_key,
        "supabaseAnonKey": supabase_key,
        "supabaseTable": supabase_table,
        "renderApiBase": render_api_base,
    }


@app.route("/")
def home():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.isfile(index_path):
        return _serve_html_file("index.html")
    return "ARAMKY Gold OS Online", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/admin.html")
def admin_page():
    return _serve_html_file("admin.html")


@app.route("/ARAMKY/<showcase_id>")
def aramky_showcase_route(showcase_id):
    clean_id = (showcase_id or "").strip()
    if not SAFE_SHOWCASE_ID_RE.match(clean_id):
        abort(404)
    return _serve_html_file("index.html")


@app.route("/api/showcase/ARAMKY/<showcase_id>", methods=["GET"])
def api_aramky_showcase_meta(showcase_id):
    clean_id = (showcase_id or "").strip()
    if not SAFE_SHOWCASE_ID_RE.match(clean_id):
        return jsonify({"ok": False, "error": "invalid_showcase_id"}), 400
    env = _read_supabase_env()
    return jsonify({
        "ok": True,
        "brand": "ARAMKY",
        "showcaseId": clean_id,
        "cloudReady": env["configured"],
    }), 200


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
@app.route("/api/config", methods=["GET"])
def api_supabase_config():
    env = _read_supabase_env()
    return jsonify({
        "ok": env["configured"],
        "configured": env["configured"],
        "missing": env["missing"],
        "supabaseUrl": env["supabaseUrl"],
        "supabaseKey": env["supabaseKey"],
        "supabaseAnonKey": env["supabaseAnonKey"],
        "supabaseTable": env["supabaseTable"],
        "renderApiBase": env["renderApiBase"],
    }), 200


@app.route("/api/health", methods=["GET"])
def api_health():
    env = _read_supabase_env()
    return jsonify({
        "status": "ok",
        "supabaseConfigured": env["configured"],
        "missingEnv": env["missing"],
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
    env = _read_supabase_env()
    if not env["configured"]:
        print(f"[ARAMKY WARN] متغيرات البيئة ناقصة في Render: {', '.join(env['missing'])} — سيعمل الخادم بالوضع الآمن دون توقف.")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
