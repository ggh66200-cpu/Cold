import telebot
import utils

ADMIN_TOKEN = "8688685639:AAFbZRFFPKoooYAFCbPHLxfH7l9DWt6enFg"
bot = telebot.TeleBot(ADMIN_TOKEN)
ADMIN_ID = 7305704935# آيديك أنت

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.chat.id == ADMIN_ID:
        bot.reply_to(m, utils.get_stats())

@bot.message_handler(commands=['approve'])
def approve(m):
    if m.chat.id == ADMIN_ID:
        # /approve ID 30
        parts = m.text.split()
        utils.add_subscription(parts[1], parts[2])
        bot.reply_to(m, "✅ تم تفعيل الاشتراك.")

# هنا تضيف أي أمر تحكم تحتاجه
bot.polling()
