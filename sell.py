import data
def handle(m, bot):
    msg = bot.send_message(m.chat.id, "💰 أدخل الوزن للبيع:")
    bot.register_next_step_handler(msg, calc_sell, bot)

def calc_sell(m, bot):
    weight = float(m.text)
    total = weight * (data.prices['gram_21'] + 2000) # إضافة 2000 أجور صياغة
    bot.reply_to(m, f"🧾 **فاتورة بيع للزبون:**\nالسعر الكلي: {total:,} د.ع")
