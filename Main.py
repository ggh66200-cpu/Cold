import threading
from flask import Flask

app = Flask(__name__)

# 1. مسارات موقع الويب (index.html و admin.html)
@app.route('/')
def home():
    return "ARAMKY Gold OS Online"

@app.route('/admin.html')
def admin_page():
    return open('admin.html', encoding='utf-8').read()

# 2. دالة تشغيل بوت تيليغرام
def run_telegram_bot():
    import telebot
    # ضع توكن بوت تيليغرام الخاص بك هنا
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    bot = telebot.TeleBot(BOT_TOKEN)
    
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "أهلاً بك في بوت حاسبة الذهب - أرامكي 💎")

    print("🤖 Telegram Bot is running...")
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل البوت في مسار خلفي (Background Thread) لكي لا يعطل سيرفر الويب
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل سيرفر الويب (Flask) على البورت الذي يحدده Render
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
