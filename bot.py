import telebot, os, buy, sell, settings, langs
from flask import Flask
from threading import Thread

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

Thread(target=lambda: Flask(__name__).run(host='0.0.0.0', port=8080)).start()

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⚖️ شراء", "💰 بيع", "☀️ الإعدادات")
    bot.send_message(m.chat.id, "💎 **Dubai Master**\nالنظام جاهز:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء": buy.handle(m, bot)
    elif m.text == "💰 بيع": sell.handle(m, bot)
    elif m.text == "☀️ الإعدادات": settings.handle(m, bot)

bot.infinity_polling()
