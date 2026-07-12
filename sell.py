import data, time, math

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "💰 **قسم البيع للزبون:**\nأدخل الوزن:")
    bot.register_next_step_handler(msg, process_sell, bot)

def process_sell(m, bot):
    load = bot.send_message(m.chat.id, "⏳ جاري معالجة طلب البيع...")
    time.sleep(1.5)
    
    weight = float(m.text)
    total_iqd = weight * (data.prices['sell_21'] / 5)
    
    # الفاتورة
    res = f"🧾 **فاتورة البيع للزبون**\nوزن: {weight} غرام\nالسعر الكلي: {total_iqd:,.0f} د.ع\n\n✅ تم إنجاز الفاتورة رسمياً."
    bot.edit_message_text(res, m.chat.id, load.message_id)
