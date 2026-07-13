import telebot, os, utils, buy, sell
from flask import Flask
from threading import Thread

# تشغيل السيرفر (لإبقاء البوت حياً على Render)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running"
def run_flask(): app.run(host='0.0.0.0', port=8080)
Thread(target=run_flask).start()

# إعداد البوت
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
ADMIN_ID = 123456789 # ضع الـ ID الخاص بك

@bot.message_handler(commands=['start'])
def start(m):
    utils.register_user(m.chat.id)
    data = utils.get_data()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if data['settings'].get('buy_btn'): markup.add("⚖️ شراء من زبون")
    if data['settings'].get('sell_btn'): markup.add("💰 بيع للزبون")
    bot.send_message(m.chat.id, "أهلاً بك. النظام جاهز للعمل.", reply_markup=markup)

# الدوال الأخرى (setprice, stats, router) كما هي في ردودي السابقة...
# لا تنسَ وضع دالة router ودالة bot.infinity_polling() في نهاية الملف
@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)

bot.infinity_polling(timeout=60, long_polling_timeout=60)
