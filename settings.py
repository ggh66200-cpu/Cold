import data
def handle(m, bot):
    msg = bot.send_message(m.chat.id, "أرسل الأسعار بهذا الترتيب (بدون فواصل):\nسعر الـ100$  سعر غرام21  سعر غرام18")
    bot.register_next_step_handler(msg, save_prices)

def save_prices(m, bot):
    try:
        p = m.text.split()
        data.prices['dollar_rate'] = int(p[0])
        data.prices['gram_21'] = int(p[1])
        data.prices['gram_18'] = int(p[2])
        bot.reply_to(m, "✅ تم تحديث الأسعار!")
    except: bot.reply_to(m, "❌ خطأ في الإدخال، تأكد من الأرقام.")
