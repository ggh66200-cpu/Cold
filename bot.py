import telebot
import os
from flask import Flask
from threading import Thread
import buy, sell, settings, utils

# سيرفر البقاء (Render)
app = Flask('')
@app.route('/')
def home(): return "البوت يعمل بكفاءة!"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
ADMIN_ID = 7305704935 # <--- ضع الـ ID الخاص بك هنا

@bot.message_handler(commands=['start'])
def start(m):
    utils.register_user(m.chat.id)
    data = utils.get_data()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if data['settings']['buy_btn']: markup.add("⚖️ شراء من زبون")
    if data['settings']['sell_btn']: markup.add("💰 بيع للزبون")
    if data['settings']['settings_btn']: markup.add("☀️ الإعدادات الصباحية")
    markup.add("💳 الاشتراك")
    bot.send_message(m.chat.id, "أهلاً بك في نظام الذهب الذكي:", reply_markup=markup)

# أوامر الأدمن
@bot.message_handler(commands=['stats', 'add', 'toggle'])
def admin_commands(m):
    if m.chat.id != ADMIN_ID: return
    cmd = m.text.split()
    if cmd[0] == '/stats': bot.reply_to(m, utils.get_stats())
    elif cmd[0] == '/add': 
        utils.add_subscription(cmd[1], cmd[2])
        bot.reply_to(m, "✅ تم التفعيل.")
    elif cmd[0] == '/toggle':
        utils.toggle_button(cmd[1], cmd[2] == 'True')
        bot.reply_to(m, "✅ تم تغيير الحالة.")

@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "💳 الاشتراك":
        bot.send_message(m.chat.id, "💳 للتحويل الماستر كارد:\n`910400201646`", parse_mode="Markdown")
        return
    if not utils.check_access(m.chat.id):
        bot.send_message(m.chat.id, "❌ انتهت الفترة التجريبية. اشترك للمتابعة.")
        return
    if m.text == "⚖️ شراء من زبون": buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون": sell.handle(m, bot)
    elif m.text == "☀️ الإعدادات الصباحية": settings.handle(m, bot)

bot.infinity_polling()
