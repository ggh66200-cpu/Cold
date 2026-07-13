import utils, time
from telebot import types

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "⚖️ اختر عيار الذهب للشراء:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: ask_weight(m, bot, "buy"))

def ask_weight(m, bot, action):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, f"✅ تم اختيار عيار {karat}. أرسل الوزن بالجرام:")
    bot.register_next_step_handler(msg, lambda m: calc(m, bot, action, karat))

def calc(m, bot, action, karat):
    try:
        wait_msg = bot.send_message(m.chat.id, "⏳ جاري معالجة الحساب بدقة...")
        time.sleep(1.5) # خدعة التحميل لتعطي هيبة للعمل
        weight = float(m.text)
        data = utils.get_data()
        price = data.get(f"{action}_{karat}", 85000)
        rate_100 = data.get('usd_100', 150000)
        
        total_iqd = weight * price
        usd_count = int(total_iqd // rate_100)
        remainder = int(total_iqd % rate_100)
        
        reply = (f"💎 **فاتورة الشراء من الزبون**\n"
                 f"--------------------------\n"
                 f"💠 العيار: {karat}\n"
                 f"⚖️ الوزن: {weight} غرام\n"
                 f"🏷 سعر الغرام: {price:,} د.ع\n"
                 f"💰 الإجمالي: {total_iqd:,} د.ع\n"
                 f"💵 المبلغ: {usd_count} ورقة ($100)\n"
                 f"💷 الباقي: {remainder:,} د.ع")
        bot.edit_message_text(reply, m.chat.id, wait_msg.message_id, parse_mode="Markdown")
    except: bot.send_message(m.chat.id, "⚠️ خطأ! أرسل رقماً صحيحاً.")
