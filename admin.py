import telebot
import utils

bot = telebot.TeleBot("8688685639:AAFbZRFFPKoooYAFCbPHLxfH7l9DWt6enFg")
ADMIN_ID = 7305704935 # آيديك

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id == ADMIN_ID:
        data = utils.get_data()
        bot.reply_to(m, f"📊 عدد المستخدمين: {data['total_count']}\nعدد المشتركين: {len(data['subs'])}")

@bot.message_handler(commands=['add'])
def add(m):
    if m.chat.id == ADMIN_ID:
        # الصيغة: /add آيدي أيام
        parts = m.text.split()
        utils.add_subscription(parts[1], parts[2])
        bot.reply_to(m, "✅ تم التفعيل.")

bot.polling()
