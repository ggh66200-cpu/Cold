import utils

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "أرسل الأسعار (سعر الـ100$ | شراء21 | بيع21 | شراء18 | بيع18):")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        p = [int(x) for x in m.text.split()]
        d = utils.get_data()
        d.update({'usd_100': p[0], 'buy_21': p[1], 'sell_21': p[2], 'buy_18': p[3], 'sell_18': p[4]})
        utils.save_data(d)
        bot.reply_to(m, "✅ تم تحديث الأسعار.")
    except: bot.reply_to(m, "⚠️ خطأ! أرسل 5 أرقام مفصولة بمسافة.")
