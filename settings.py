import data

def handle(m, bot):
    msg = bot.send_message(m.chat.id, 
        "☀️ **تحديث الأسعار الصباحية:**\nأرسل الأسعار في رسالة واحدة مفصولة بمسافات:\n\n`سعر_100$ شراء_21 بيع_21`", 
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, save, bot)

def save(m, bot):
    try:
        p = m.text.split()
        data.prices['usd_100'] = int(p[0])
        data.prices['buy_21'] = int(p[1])
        data.prices['sell_21'] = int(p[2])
        bot.reply_to(m, "✅ **تم تحديث الأسعار رسمياً في النظام.**\nالنظام الآن يعمل بالأسعار الجديدة.")
    except:
        bot.reply_to(m, "❌ فشل التحديث. تأكد من إدخال 3 أرقام فقط.")
