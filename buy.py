import utils
from telebot import types

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "⚖️ شراء (إدخال يدوي): اختر العيار:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: step_weight(m, bot))

def step_weight(m, bot):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, f"أرسل الوزن (بالمثقال):")
    bot.register_next_step_handler(msg, lambda m: step_price(m, bot, karat))

def step_price(m, bot, karat):
    try:
        weight_mithqal = float(m.text)
        msg = bot.send_message(m.chat.id, "أرسل سعر المثقال الكلي (مثال: 450000):")
        bot.register_next_step_handler(msg, lambda m: step_melt(m, bot, karat, weight_mithqal))
    except: bot.send_message(m.chat.id, "خطأ في الوزن.")

def step_melt(m, bot, karat, weight_mithqal):
    try:
        mithqal_price = float(m.text)
        msg = bot.send_message(m.chat.id, "أرسل أجور الصهر للغرام (اكتب 0 إذا لا يوجد):")
        bot.register_next_step_handler(msg, lambda m: calc_final(m, bot, karat, weight_mithqal, mithqal_price))
    except: bot.send_message(m.chat.id, "خطأ في السعر.")

def calc_final(m, bot, karat, weight_mithqal, mithqal_price):
    try:
        melt_fee = float(m.text)
        weight_gram = weight_mithqal * 5
        data = utils.get_data()
        
        # الحسبة المطلوبة
        gram_raw_price = mithqal_price / 5
        gram_final_price = gram_raw_price - melt_fee
        
        total_iqd = weight_gram * gram_final_price
        
        usd = int(total_iqd // data['settings']['usd_100'])
        rem = int(total_iqd % data['settings']['usd_100'])
        
        reply = (f"💎 فاتورة الشراء\n"
                 f"------------------\n"
                 f"💠 العيار: {karat}\n"
                 f"⚖️ الوزن: {weight_mithqal} مثقال\n"
                 f"🏷 سعر الشراء للمثقال الصافي: {(gram_final_price * 5):,} د.ع\n"
                 f"💰 الإجمالي: {total_iqd:,} د.ع\n"
                 f"💵 المبلغ: {usd} ورقة ($100) + {rem:,} د.ع")
        
        from bot import get_main_markup
        bot.send_message(m.chat.id, reply, reply_markup=get_main_markup(m.chat.id))
    except: bot.send_message(m.chat.id, "خطأ في الإدخال.")
