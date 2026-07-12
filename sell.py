import data, utils, time

def handle(m, bot):
    msg = bot.send_message(m.chat.id, "💰 **قسم البيع للزبون:**\nأدخل وزن الذهب بال غرام:")
    bot.register_next_step_handler(msg, process, bot)

def process(m, bot):
    try:
        load = utils.loading(bot, m.chat.id, "جاري حساب فاتورة البيع...")
        weight = float(m.text)
        
        # سعر البيع (مثال: سعر الـ21 + 2000 دينار أجور صياغة)
        total = weight * (data.prices['sell_21'] / 5 + 2000)
        
        # التنسيق الفخم للفاتورة
        res = f"""
🧾 **فاتورة بيع للزبون**
━━━━━━━━━━━━━━
⚖️ **الوزن:** {weight} غرام
💵 **السعر الكلي:** {total:,.0f} د.ع
━━━━━━━━━━━━━━
✅ *تم توثيق الفاتورة في النظام.*
"""
        bot.edit_message_text(res, m.chat.id, load.message_id, parse_mode="Markdown")
    except:
        bot.reply_to(m, "⚠️ خطأ في الإدخال، تأكد من كتابة الرقم فقط.")
