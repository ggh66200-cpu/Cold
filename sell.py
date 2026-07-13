import utils
from telebot import types

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "💰 بيع: اختر العيار:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: get_weight(m, bot, "sell"))

def get_weight(m, bot, action):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, f"✅ عيار {karat}. أرسل الوزن (بالمثقال):")
    bot.register_next_step_handler(msg, lambda m: calc(m, bot, action, karat))

def calc(m, bot, action, karat):
    try:
        mithqal = float(m.text)
        data = utils.get_data()
        # المعادلة الصارمة: (سعر البيع + الصياغة للمثقال)
        price_mithqal = data.get(f"sell_{karat}", 900000)
        labor_mithqal = data.get(f"labor_{karat}", 60000)
        
        total = mithqal * (price_mithqal + labor_mithqal)
        usd = int(total // data['usd_100'])
        rem = int(total % data['usd_100'])
        
        reply = (f"💎 **فاتورة البيع**\n"
                 f"-----------------\n"
                 f"💠 العيار: {karat}\n"
                 f"⚖️ الوزن: {mithqal} مثقال\n"
                 f"🏷 سعر المثقال الكلي: {(price_mithqal + labor_mithqal):,} د.ع\n"
                 f"💰 الإجمالي: {total:,} د.ع\n"
                 f"💵 المبلغ: {usd} ورقة ($100) + {rem:,} د.ع")
        bot.send_message(m.chat.id, reply, parse_mode="Markdown")
    except: bot.send_message(m.chat.id, "⚠️ خطأ! أرسل رقماً صحيحاً.")
