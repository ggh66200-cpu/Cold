import utils

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "💰 أرسل وزن الذهب بالجرام لبيعه للزبون:")
    bot.register_next_step_handler(msg, lambda m: calculate(m, bot))

def calculate(m, bot):
    try:
        weight = float(m.text)
        data = utils.get_data()
        price = data.get('sell_21', 87000) # سعر الغرام
        rate_100 = data.get('usd_100', 150000) # سعر الـ 100 دولار
        
        total_iqd = weight * price
        usd_count = int(total_iqd // rate_100) # عدد الأوراق
        remainder = int(total_iqd % rate_100)   # الباقي بالدينار
        
        reply = (f"💎 **حساب البيع للزبون**\n"
                 f"--------------------------\n"
                 f"⚖️ الوزن: {weight} غرام\n"
                 f"💰 الإجمالي: {total_iqd:,} د.ع\n"
                 f"💵 المبلغ بالدولار: {usd_count} ورقة ($100)\n"
                 f"💷 الباقي بالدينار: {remainder:,} د.ع")
        
        bot.send_message(m.chat.id, reply, parse_mode="Markdown")
    except:
        bot.send_message(m.chat.id, "⚠️ خطأ! أرسل رقماً صحيحاً.")
