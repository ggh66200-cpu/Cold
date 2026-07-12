import telebot, os
from flask import Flask
from threading import Thread
import langs, sub, buy, sell, settings

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# تشغيل السيرفر
Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    if not sub.is_subscribed(cid): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⚖️ شراء", "💰 بيع", "☀️ الإعدادات", "🌐 اللغة", "💳 الاشتراك")
    bot.send_message(cid, "💎 Dubai Master System", reply_markup=markup)

# توجيه الأوامر للملفات المختصة
@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text in ["⚖️ شراء", "Buy", "کڕین"]: buy.handle(m, bot)
    elif m.text in ["💰 بيع", "Sell", "فرۆشتن"]: sell.handle(m, bot)
    elif m.text in ["☀️ الإعدادات"]: settings.handle(m, bot)
    # وهكذا لباقي الأزرار...

bot.infinity_polling()
