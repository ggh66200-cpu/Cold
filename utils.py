import time

def loading(bot, chat_id, text="جاري المعالجة..."):
    msg = bot.send_message(chat_id, f"⏳ {text}")
    time.sleep(1)
    return msg

def format_invoice(trend, weight, total, papers, rem):
    return f"""
✨ **فاتورة رسمية | Dubai Master**
━━━━━━━━━━━━━━
🆔 **الترند:** `{trend}`
⚖️ **الوزن:** {weight} غرام
💵 **المبلغ:** {total:,.0f} د.ع
━━━━━━━━━━━━━━
💰 **التصفية:** {papers}$
↩️ **الباقي:** {rem:,.0f} د.ع
━━━━━━━━━━━━━━
✅ *تم الحفظ في السجلات.*
"""
