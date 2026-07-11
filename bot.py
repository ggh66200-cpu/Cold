import telebot, os, json
from flask import Flask
from threading import Thread
from datetime import datetime

# قراءة المفاتيح من إعدادات السيرفر مباشرة
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_ID')
bot = telebot.TeleBot(TOKEN)

# (أضف هنا كود الـ Flask كما فعلنا سابقاً ليعمل السيرفر)
# ... [كود الـ Flask هنا] ...

def is_admin(cid): return str(cid) == ADMIN_CHAT_ID

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    cid = str(message.chat.id)
    
    # 1. استثناء الأدمن
    if is_admin(cid):
        process_gold(message)
        return

    # 2. فحص الاشتراك الإجباري
    if not is_subscribed(cid):
        bot.reply_to(message, "⚠️ اشتراكك منتهي. يرجى الضغط على 'تفعيل اشتراك' للاستمرار.")
        return

    # تنفيذ باقي الأوامر...
