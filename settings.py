import data
def handle(m, bot):
    msg = bot.send_message(m.chat.id, "☀️ **إعدادات الصباح:**\nأرسل الأسعار (مسافات): \n(سعر الـ100$، شراء21، بيع21)")
    bot.register_next_step_handler(msg, save, bot)

def save(m, bot):
    p = m.text.split()
    data.prices.update({'usd_100': int(p[0]), 'buy_21': int(p[1]), 'sell_21': int(p[2])})
    bot.reply_to(m, "✅ **تم حفظ الإعدادات الصباحية رسمياً في النظام.**")
