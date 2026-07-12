import data, time, math

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "⚖️ **قسم الشراء:**\nأدخل الوزن بالـ غرام:")
    bot.register_next_step_handler(msg, process_buy, bot)

def process_buy(m, bot):
    # خدعة التحميل
    load = bot.send_message(m.chat.id, "⏳ جاري الاتصال بالبورصة...")
    time.sleep(1.5)
    bot.edit_message_text("🧮 يتم تصفية الحساب...", m.chat.id, load.message_id)
    time.sleep(1)
    
    # المعادلات
    weight = float(m.text)
    total_iqd = weight * (data.prices['buy_21'] / 5)
    
    # منطق الـ 100$
    papers = math.ceil(total_iqd / data.prices['usd_100']) * 100
    rem_iqd = (papers * (data.prices['usd_100']/100)) - total_iqd
    
    trend = f"TRND-{int(time.time())}" # رقم الترند
    
    # النتيجة النهائية
    res = f"✅ **تمت العملية بنجاح**\n🆔 الترند: {trend}\n\n💰 المبلغ الكلي: {total_iqd:,.0f} د.ع\n💵 التصفية: {papers}$ \n↩️ الباقي بالدينار: {rem_iqd:,.0f} د.ع"
    bot.edit_message_text(res, m.chat.id, load.message_id)
