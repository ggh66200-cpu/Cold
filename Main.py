import os
import threading
from flask import Flask, send_from_directory, abort
import telebot

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

# 2. دالة تشغيل بوت تيليغرام
def run_telegram_bot():
    # يقرأ التوكن من Environment Variables في Render، أو يأخذ القيمة الاحتياطية إن وجدت
    bot_token = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE").strip()

    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ Warning: BOT_TOKEN is not set in Environment Variables!")
        return

    bot = telebot.TeleBot(bot_token)

    @bot.message_handler(commands=["start"])
    def send_welcome(message):
        bot.reply_to(message, "أهلاً بك في بوت حاسبة الذهب - أرامكي 💎")

    print("🤖 Telegram Bot is running...")
    # skip_pending=True لتجنب معالجة رسائل قديمة متراكمة عند إعادة التشغيل
    bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)

if __name__ == "__main__":
    # تشغيل البوت في مسار خلفي (Background Thread) لكي لا يعطل سيرفر الويب
    bot_thread = threading.Thread(target=run_telegram_bot, name="TelegramBotThread")
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل سيرفر الويب (Flask) على البورت الذي يحدده Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
