import os
import re
import time
import threading
import urllib.request
import traceback
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from flask import Flask, render_template, Response, send_from_directory

# ==========================================
# ⏸️ تم إيقاف تشغيل بوت التليجرام مؤقتاً
# ==========================================
BOT_DISABLED = True
BOT_TOKEN = None
ADMIN_ID = 0
bot = None

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# ==========================================
# 🌐 مسارات سيرفر الويب وتطبيق PWA (أرامكي)
# ==========================================
@app.route('/')
def web_pos_home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading interface: {e}", 500

@app.route('/admin.html')
def web_admin_panel():
    try:
        return render_template('admin.html')
    except Exception as e:
        return f"Error loading admin panel: {e}", 500

@app.route('/icon.png')
def serve_icon():
    for fname in ('icon.png', 'logo.jpg', 'logo.png'):
        if os.path.exists(fname):
            mimetype = 'image/jpeg' if fname.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
            return send_from_directory('.', fname, mimetype=mimetype)
    return "Icon file not found", 404

@app.route('/<path:filename>')
def serve_static_files(filename):
    if filename in ('bot.py', 'bot_2.py', 'utils.py', 'admin.py') or filename.endswith('.py'):
        return "Forbidden", 403
    if os.path.isfile(filename):
        return send_from_directory('.', filename)
    return "Not found", 404

@app.route('/manifest.json')
def serve_manifest():
    manifest_content = """{
  "name": "ARAMKY | أرامكي للحلول الرقمية",
  "short_name": "أرامكي",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0b0f19",
  "theme_color": "#d4af37",
  "icons": [
    {
      "src": "/icon.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}"""
    return Response(manifest_content, mimetype='application/json')

@app.route('/sw.js')
def serve_sw():
    sw_content = """
    self.addEventListener('install', (e) => {
      console.log('Service Worker Installed');
    });
    self.addEventListener('fetch', (e) => {
      e.respondWith(fetch(e.request));
    });
    """
    return Response(sw_content, mimetype='application/javascript')

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive_ping():
    port = os.environ.get("PORT", 10000)
    url = f"http://127.0.0.1:{port}/"
    while True:
        try:
            time.sleep(300)
            urllib.request.urlopen(url)
        except Exception as e:
            print(f"Keep-alive ping status: {e}")

if __name__ == "__main__":
    keep_alive_thread = threading.Thread(target=keep_alive_ping)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    print("🌐 Telegram bot is paused/disabled. Flask Web Server is running alone successfully with /icon.png enabled.")
    while True:
        time.sleep(1)
