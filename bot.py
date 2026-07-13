import telebot, os, utils, buy, sell
from flask import Flask
from threading import Thread

# تشغيل سيرفر للبقاء أونلاين
Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot.remove_webhook() # لمنع التعارض

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⚖️ شراء من زبون", "💰 بيع للزبون")
    bot.send_message(m.chat.id, "النظام جاهز. اختر العملية:", reply_markup=markup)

@bot.message_handler(commands=['setprice'])
def set_price(m):
    try:
        _, key, val = m.text.split()
        utils.update_price(key, val)
        bot.reply_to(m, f"✅ تم تحديث {key} إلى {val}")
    except: bot.reply_to(m, "خطأ! استخدم: /setprice [المفتاح] [القيمة]")

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)

bot.infinity_polling(timeout=60, long_polling_timeout=60)
