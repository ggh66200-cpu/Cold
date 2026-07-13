import utils
from telebot import types

def show_menu(m, bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⚖️ شراء من زبون", "💰 بيع للزبون")
    bot.send_message(m.chat.id, "العودة للقائمة الرئيسية:", reply_markup=markup)

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "💰 اختر عيار الذهب للبيع للزبون:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: ask_weight(m, bot, "sell"))

def ask_weight(m, bot, action):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, f"✅ اخترت عيار {karat}. أرسل الوزن بالمثقال:")
    bot.register_next_step_handler(msg, lambda m: calc(m, bot, action, karat))

def calc(m, bot, action, karat):
    try:
        mithqal = float(m.text)
        weight_grams = mithqal * 5 
        data = utils.get_data()
        price = data.get(f"{action}_{karat}", 87000)
        fees = data.get('labor_fees', 5000) * mithqal # أجور الصياغة للمثقال الواحد
        rate_100 = data.get('usd_100', 150000)
        
        total_iqd = (weight_grams * price) + fees
        usd_count = int(total_iqd // rate_100)
        remainder = int(total_iqd % rate_100)
        
        reply = (f"💎 **فاتورة البيع (للزبون)**\n"
                 f"--------------------------\n"
                 f"💠 العيار: {karat}\n"
                 f"⚖️ الوزن: {mithqal} مثقال\n"
                 f"🏷 سعر الصياغة: {fees:,} د.ع\n"
                 f"💰 الإجمالي (ذهب + صياغة): {total_iqd:,} د.ع\n"
                 f"💵 المبلغ: {usd_count} ورقة ($100) + {remainder:,} د.ع")
        bot.send_message(m.chat.id, reply, parse_mode="Markdown")
        show_menu(m, bot)
    except: bot.send_message(m.chat.id, "⚠️ خطأ! أرسل رقماً صحيحاً.")
