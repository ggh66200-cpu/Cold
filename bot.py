import telebot, os, utils, buy, sell
from flask import Flask
from threading import Thread

# السيرفر لمنع النوم
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is awake!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot.remove_webhook()

def get_main_markup(user_id):
    data = utils.get_data()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 بيع للزبون", "⚖️ شراء من زبون")
    if user_id == data.get('admin_id'):
        markup.add("⚙️ إعدادات الصباح")
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    is_active, count = utils.check_user(m.chat.id)
    if not is_active:
        bot.send_message(m.chat.id, "⚠️ عذراً، انتهت فترة التجربة المجانية (7 أيام). يرجى الاشتراك.")
        return
    
    markup = get_main_markup(m.chat.id)
    bot.send_message(m.chat.id, f"👋 أهلاً بك في نظام الذهب الاحترافي.\nأنت العميل رقم: {count}\n\nالنظام جاهز، اختر العملية:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def router(m):
    is_active, _ = utils.check_user(m.chat.id)
    if not is_active:
        bot.send_message(m.chat.id, "⚠️ اشتراكك المجاني انتهى. يرجى التجديد.")
        return

    if m.text == "💰 بيع للزبون":
        sell.handle(m, bot)
    elif m.text == "⚖️ شراء من زبون":
        buy.handle(m, bot)
    elif m.text == "⚙️ إعدادات الصباح":
        data = utils.get_data()
        if m.chat.id == data.get('admin_id'):
            # رسالة مساعدة سريعة للمدير
            msg = (f"⚙️ **إعدادات الصباح الحالية:**\n"
                   f"مثقال 21: {data['settings']['mithqal_21']:,}\n"
                   f"مثقال 18: {data['settings']['mithqal_18']:,}\n"
                   f"أجور الغرام: {data['settings']['labor_gram']:,}\n"
                   f"الدولار: {data['settings']['usd_100']:,}\n\n"
                   f"لتغيير أي قيمة، أرسل الأمر بهذا الشكل:\n"
                   f"`/set usd_100 152000`")
            bot.send_message(m.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['set'])
def set_setting(m):
    data = utils.get_data()
    if m.chat.id == data.get('admin_id'):
        try:
            _, key, val = m.text.split()
            utils.update_setting(key, val)
            bot.reply_to(m, f"✅ تم تحديث {key} بنجاح!")
        except:
            bot.reply_to(m, "خطأ في الإدخال.")

bot.infinity_polling(timeout=60, long_polling_timeout=60)
