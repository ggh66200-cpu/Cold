import telebot, os, utils, buy, sell
from flask import Flask
from threading import Thread

# تشغيل سيرفر وهمي للحفاظ على بقاء البوت "أونلاين"
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is working"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

# أمر "التنظيف" السحري
bot.remove_webhook()

@bot.message_handler(commands=['start'])
def start(m):
    utils.register_user(m.chat.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⚖️ شراء من زبون", "💰 بيع للزبون")
    bot.send_message(m.chat.id, "أهلاً بك. النظام جاهز.", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)

# التشغيل بوضع التنبيه (polling)
bot.infinity_polling(timeout=10, long_polling_timeout=5)
