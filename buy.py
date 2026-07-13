import utils
from telebot import types

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "⚖️ شراء: اختر العيار:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: get_weight(m, bot, "buy"))

def get_weight(m, bot, action):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, f"✅ عيار {karat}. أرسل الوزن (بالمثقال):")
    bot.register_next_step_handler(msg, lambda m: calc(m, bot, action, karat))

def calc(m, bot, action, karat):
    try:
        mithqal = float(m.text)
        data = utils.get_data()
        price = data.get(f"buy_{karat}", 800000)
        
        total = mithqal * price
        usd = int(total // data['usd_100'])
        rem = int(total % data['usd_100'])
        
        reply = (f"💎 **فاتورة الشراء**\n"
                 f"-----------------\n"
                 f"💠 العيار: {karat}\n"
                 f"⚖️ الوزن: {mithqal} مثقال\n"
                 f"💰 الإجمالي: {total:,} د.ع\n"
                 f"💵 المبلغ: {usd} ورقة ($100) + {rem:,} د.ع")
        bot.send_message(m.chat.id, reply, parse_mode="Markdown")
    except: bot.send_message(m.chat.id, "⚠️ خطأ! أرسل رقماً صحيحاً.")
