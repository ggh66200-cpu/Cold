import telebot, os, utils, subscription, time
from flask import Flask
from threading import Thread
from telebot import types

# تشغيل الخادم
app = Flask(__name__); Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
USER_STATES = {}

@bot.message_handler(commands=['start'])
def start(m):
    USER_STATES[m.chat.id] = {}
    _, count = subscription.check_user(m.chat.id)
    bot.send_message(m.chat.id, f"👋 أهلاً بك! أنت العميل رقم `{count}`.\nيرجى اختيار اللغة / Please select language / تکایە زمان هەڵبژێرە:\n\n/lang_ar - العربية\n/lang_ku - کوردی\n/lang_en - English", reply_markup=utils.get_keyboard())

@bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات الصباح")
def morning_settings(m):
    data = utils.get_data()['settings']
    msg = (f"☀️ **أسعار الصباح الحالية**:\n"
           f"مثقال 21: `{data['mithqal_21']}`\nمثقال 18: `{data['mithqal_18']}`\n"
           f"صياغة 21: `{data['labor_21']}`\nصياغة 18: `{data['labor_18']}`\n"
           f"الدولار: `{data['usd_100']}`\n\n"
           f"⚠️ **لتحديث الكل بضغطة واحدة، أرسل الأسعار الخمسة متباعدة بمسافة أو بسطر جديد بهذا الترتيب:**\n"
           f"`مثقال21 مثقال18 صياغة21 صياغة18 دولار`\n\nمثال:\n`450000 380000 10000 10000 150000`")
    bot.send_message(m.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: len(m.text.split()) == 5)
def handle_bulk_update(m):
    try:
        vals = [int(v.replace(",", "")) for v in m.text.split()]
        utils.update_all_settings(vals)
        bot.send_message(m.chat.id, "🎉 **تم تحديث جميع الأسعار بلمحة بصر! ربي يبارك برزقك.**")
    except:
        bot.send_message(m.chat.id, "⚠️ خطأ في الصيغة. أرسل الأرقام فقط (5 أرقام).")

# بقية المنطق (البيع والشراء) يبقى كما اتفقنا عليه سابقاً مع استخدام subscription.check_user
bot.infinity_polling()
