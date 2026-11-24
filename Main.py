import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

# 1. مسارات موقع الويب (index.html و admin.html)
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

@app.route("/health")
def health():
    return {"status": "ok", "service": "ARAMKY Gold OS"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
