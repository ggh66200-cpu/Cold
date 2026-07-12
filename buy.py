import utils, time
def handle(m, bot):
    msg = bot.send_message(m.chat.id, "⚖️ اختر العيار (21 أو 18) ثم الوزن (مثال: 21 10):")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        karat, weight = m.text.split()
        d = utils.get_data()
        price_g = d[f'buy_{karat}'] / 5
        total = float(weight) * price_g
        
        papers = (total // d['usd_100']) * 100
        rem = total - (papers / 100 * d['usd_100'])
        
        bot.reply_to(m, f"🧾 فاتورة شراء:\nالسعر الكلي: {total:,.0f} د.ع\n\nيدفع للزبون:\n💵 {papers}$ \n💴 {rem:,.0f} د.ع")
    except: bot.reply_to(m, "⚠️ خطأ! أرسل العيار والوزن بمسافة.")
