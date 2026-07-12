import utils, time
def handle(m, bot):
    msg = bot.send_message(m.chat.id, "💰 اختر العيار والوزن وأجور الصياغة (مثال: 21 10 5000):")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        karat, weight, ujra = m.text.split()
        d = utils.get_data()
        # سعر الغرام (السعر الصافي + الأجور)
        price_g = (d[f'sell_{karat}'] / 5) + int(ujra)
        total = float(weight) * price_g
        
        bot.reply_to(m, f"🧾 فاتورة بيع:\nالسعر الكلي: {total:,.0f} د.ع\n(شامل صياغة {ujra} للغرام)")
    except: bot.reply_to(m, "⚠️ خطأ! أرسل العيار، الوزن، والأجور بمسافات.")
