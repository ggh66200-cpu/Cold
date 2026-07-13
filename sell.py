import telebot, os, utils, buy, sell
from flask import Flask
from threading import Thread

Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
ADMIN_ID = 123456789 # ضع الـ ID الخاص بك هنا

@bot.message_handler(commands=['start'])
def start(m):
    utils.register_user(m.chat.id)
    data = utils.get_data()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if data['settings'].get('buy_btn'): markup.add("⚖️ شراء من زبون")
    if data['settings'].get('sell_btn'): markup.add("💰 بيع للزبون")
    bot.send_message(m.chat.id, "أهلاً بك في نظام الذهب الاحترافي.", reply_markup=markup)

@bot.message_handler(commands=['setprice'])
def set_price(m):
    if m.chat.id != ADMIN_ID: return
    try:
        _, key, val = m.text.split()
        utils.update_price(key, val)
        bot.reply_to(m, f"✅ تم تحديث {key} إلى {val}")
    except: bot.reply_to(m, "⚠️ خطأ! استخدم: /setprice [المفتاح] [القيمة]")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id != ADMIN_ID: return
    data = utils.get_data()
    bot.reply_to(m, f"📊 عدد المستخدمين: {data['total_count']}")

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)

bot.infinity_polling()
