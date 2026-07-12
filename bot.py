import telebot
import os
import buy, sell, settings, utils

# التوكن يتم سحبه من إعدادات السيرفر (Render Environment)
# تأكد أنك وضعت BOT_TOKEN في إعدادات Render
token = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(token)

# !!! غير هذا الرقم للـ ID الخاص بك لكي تعمل صلاحيات الإدارة !!!
ADMIN_ID = 123456789 

@bot.message_handler(commands=['start'])
def start(m):
    data = utils.get_data()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⚖️ شراء من زبون", "💰 بيع للزبون", "☀️ الإعدادات الصباحية")
    
    welcome_text = data.get('welcome_msg', "أهلاً بك في نظام الذهب الذكي. اختر العملية:")
    bot.send_message(m.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# أمر تفعيل الاشتراكات (فقط للأدمن)
@bot.message_handler(commands=['add'])
def add_sub(m):
    if m.chat.id == ADMIN_ID:
        parts = m.text.split()
        if len(parts) >= 3:
            # مثال: /add 123456789 30
            utils.add_subscription(parts[1], parts[2])
            bot.reply_to(m, f"✅ تم تفعيل اشتراك المستخدم {parts[1]} لمدة {parts[2]} يوم.")
        else:
            bot.reply_to(m, "⚠️ صيغة خاطئة. استخدم الأمر هكذا: /add ID عدد_الأيام")
    else:
        bot.reply_to(m, "❌ عذراً، لا تملك صلاحية الوصول لهذا الأمر.")

# الموزع الرئيسي
@bot.message_handler(func=lambda m: True)
def router(m):
    if m.text == "⚖️ شراء من زبون":
        buy.handle(m, bot)
    elif m.text == "💰 بيع للزبون":
        sell.handle(m, bot)
    elif m.text == "☀️ الإعدادات الصباحية":
        settings.handle(m, bot)

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling()
