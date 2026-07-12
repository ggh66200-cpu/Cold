import data
def handle(m, bot):
    msg = bot.send_message(m.chat.id, "⚖️ أدخل الوزن:")
    bot.register_next_step_handler(msg, calc_buy, bot)

def calc_buy(m, bot):
    weight = float(m.text)
    total_iqd = weight * data.prices['gram_21']
    
    # حساب الـ 100$
    num_100 = int(total_iqd // data.prices['dollar_rate'])
    val_in_dollar = num_100 * 100
    rem_iqd = total_iqd - (num_100 * data.prices['dollar_rate'])
    
    bot.reply_to(m, f"🧾 **فاتورة الشراء:**\nالمبلغ الإجمالي: {total_iqd:,} د.ع\nالاستلام: {val_in_dollar}$ + {rem_iqd:,.0f} د.ع")
