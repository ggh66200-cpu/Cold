import data, utils, time

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "⚖️ أدخل وزن الذهب:")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        load = utils.loading(bot, m.chat.id)
        weight = float(m.text)
        total = weight * (data.prices['buy_21'] / 5)
        
        # معادلة الـ 100 دولار
        papers = (total // data.prices['usd_100']) * 100
        rem = total - (papers * (data.prices['usd_100'] / 100))
        
        invoice = utils.format_invoice(int(time.time()), weight, total, papers, rem)
        bot.edit_message_text(invoice, m.chat.id, load.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(m, "⚠️ خطأ في الإدخال، تأكد من الأرقام.")
