import utils
from telebot import types

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "💰 بيع: اختر العيار:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: ask_weight(m, bot))

def ask_weight(m, bot):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, f"✅ عيار {karat}. أرسل الوزن (بالمثقال):")
    bot.register_next_step_handler(msg, lambda m: calc(m, bot, karat))

def calc(m, bot, karat):
    try:
        weight_mithqal = float(m.text)
        weight_gram = weight_mithqal * 5
        data = utils.get_data()
        settings = data['settings']
        
        # استخراج العمليات الحسابية
        mithqal_price = settings[f"mithqal_{karat}"]
        gram_raw_price = mithqal_price / 5
        gram_final_price = gram_raw_price + settings['labor_gram']
        
        total_iqd = weight_gram * gram_final_price
        
        usd = int(total_iqd // settings['usd_100'])
        rem = int(total_iqd % settings['usd_100'])
        
        # ترتيب الفاتورة مثل الصورة 1000003601.jpg
        reply = (f"💎 فاتورة البيع\n"
                 f"------------------\n"
                 f"💠 العيار: {karat}\n"
                 f"⚖️ الوزن: {weight_mithqal} مثقال\n"
                 f"🏷 سعر المثقال الكلي: {(gram_final_price * 5):,} د.ع\n"
                 f"💰 الإجمالي: {total_iqd:,} د.ع\n"
                 f"💵 المبلغ: {usd} ورقة ($100) + {rem:,} د.ع")
        
        from bot import get_main_markup
        bot.send_message(m.chat.id, reply, reply_markup=get_main_markup(m.chat.id))
    except:
        bot.send_message(m.chat.id, "⚠️ أرسل رقماً صحيحاً.")
