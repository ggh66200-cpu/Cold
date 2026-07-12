import telebot, buy, sell, settings, random, time
from flask import Flask
from threading import Thread

# امسح القديم وضع هذا السطر فقط:
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))


# تفعيل السيرفر
Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⚖️ شراء من زبون", "💰 بيع للزبون", "☀️ الإعدادات الصباحية")
    bot.send_message(m.chat.id, "💎 **Dubai Master System**\nمرحباً بك. النظام جاهز للعمل.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)
    elif m.text == "☀️ الإعدادات الصباحية": settings.handle(m, bot)

bot.infinity_polling()
