import telebot, os
from flask import Flask
from threading import Thread
import buy, sell, settings, sub, langs

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# تشغيل السيرفر لمنع الخمول
Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    if not sub.is_subscribed(cid): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # استخدام قاموس اللغات من ملف langs
    lang = 'ar' 
    markup.add(langs.TEXTS[lang]['buy'], langs.TEXTS[lang]['sell'], langs.TEXTS[lang]['settings'], "💳 الاشتراك")
    bot.send_message(cid, "💎 **Dubai Master** - النظام جاهز للعمل.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text in ["⚖️ شراء", "⚖️ کڕین", "⚖️ Buy"]: buy.handle(m, bot)
    elif m.text in ["💰 بيع", "💰 فرۆشتن", "💰 Sell"]: sell.handle(m, bot)
    elif m.text in ["☀️ الإعدادات", "☀️ ڕێکخستن", "☀️ Settings"]: settings.handle(m, bot)

bot.infinity_polling()
