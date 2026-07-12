import utils

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "☀️ **الإعدادات الصباحية**\nأرسل الأسعار بهذا الترتيب (بينها مسافة):\n\nسعر الـ100$  شراء21  بيع21\n\nمثال: 150000 480000 485000")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        prices = m.text.split()
        if len(prices) != 3:
            bot.reply_to(m, "⚠️ يجب إرسال 3 أرقام بالضبط.")
            return
        
        data = utils.get_data()
        data['usd_100'] = int(prices[0])
        data['buy_21'] = int(prices[1])
        data['sell_21'] = int(prices[2])
        
        utils.save_data(data)
        bot.reply_to(m, "✅ تم تحديث الأسعار بنجاح وتم حفظها في النظام.")
    except:
        bot.reply_to(m, "⚠️ خطأ في الإدخال، تأكد من كتابة الأرقام بشكل صحيح.")
