import telebot
import os
from flask import Flask
from threading import Thread
import buy, sell, settings, utils

# --- كود السيرفر الوهمي (لضمان استمرار عمل البوت) ---
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()
# ----------------------------------------------------

# التوكن يتم سحبه من إعدادات السيرفر
token = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(token)

# ضع الـ ID الخاص بك هنا (الماستر)
ADMIN_ID = 123456789 

@bot.message_handler(commands=['start'])
def start(m):
    # تسجيل المستخدم والتحقق من العدد
    is_new = utils.register_user(m.chat.id)
    data = utils.get_data()
    
    # رسالة الترحيب والاشتراك
    welcome_text = "أهلاً بك في نظام الذهب الذكي. اختر العملية:"
    if data['total_count'] >= 100 and is_new:
        welcome_text = "أهلاً بك في عائلتنا! لدينا أكثر من 100 مستخدم، النظام حالياً يتطلب اشتراكاً بعد 3 أيام تجربة مجانية."
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⚖️ شراء من زبون", "💰 بيع للزبون", "☀️ الإعدادات الصباحية", "💳 الاشتراك")
    
    bot.send_message(m.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['add'])
def add_sub(m):
    if m.chat.id == ADMIN_ID:
        parts = m.text.split()
        if len(parts) >= 3:
            utils.add_subscription(parts[1], parts[2])
            bot.reply_to(m, f"✅ تم تفعيل اشتراك المستخدم {parts[1]}.")
        else:
            bot.reply_to(m, "⚠️ استخدم: /add ID عدد_الأيام")
    else:
        bot.reply_to(m, "❌ ليس لديك صلاحية.")

def show_payment(m):
    text = ("💳 **طرق الاشتراك وتفعيل النظام:**\n\n"
            "اشتراك أسبوعي: 8,000 د.ع\n"
            "اشتراك شهري: 30,000 د.ع\n\n"
            "يرجى تحويل المبلغ على الماستر كارد التالية:\n"
            "`910400201646`\n"  # رقم الماستر كارد الخاص بك
            "بعد التحويل أرسل الوصل.")
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(m):
    # التحقق من الاشتراك قبل السماح بأي عملية
    if m.text != "💳 الاشتراك" and not utils.check_access(m.chat.id):
        bot.send_message(m.chat.id, "❌ انتهت الفترة التجريبية. يرجى الاشتراك للاستمرار. اضغط على زر 💳 الاشتراك.")
        return

    if m.text == "⚖️ شراء من زبون":
        buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون":
        sell.handle(m, bot)
    elif m.text == "☀️ الإعدادات الصباحية":
        settings.handle(m, bot)
    elif m.text == "💳 الاشتراك":
        show_payment(m)

if __name__ == "__main__":
    bot.infinity_polling()
