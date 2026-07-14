import utils, time
from telebot import types

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "⚖️ شراء من زبون: اختر العيار:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: step_mithqal_price(m, bot))

def step_mithqal_price(m, bot):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, "💰 أدخل سعر مثقال الشراء المتفق عليه حالياً:")
    bot.register_next_step_handler(msg, lambda m: step_melt_fee(m, bot, karat))

def step_melt_fee(m, bot, karat):
    try:
        mithqal_price = float(m.text)
        msg = bot.send_message(m.chat.id, "🔥 أدخل أجور الخصم أو الصهر (للقطعة أو الغرام) - اكتب 0 إذا لا يوجد:")
        bot.register_next_step_handler(msg, lambda m: step_weight(m, bot, karat, mithqal_price))
    except:
        bot.send_message(m.chat.id, "⚠️ خطأ في الإدخال.")

def step_weight(m, bot, karat, mithqal_price):
    try:
        melt_fee = float(m.text)
        msg = bot.send_message(m.chat.id, "⚖️ أدخل وزن الذهب المراد شراؤه **بالغرام**:")
        bot.register_next_step_handler(msg, lambda m: calc_buy(m, bot, karat, mithqal_price, melt_fee))
    except:
        bot.send_message(m.chat.id, "⚠️ خطأ في الإدخال.")

def calc_buy(m, bot, karat, mithqal_price, melt_fee):
    try:
        weight_gram = float(m.text)
        
        # تأثير جاري التحميل لتعزيز الاحترافية
        loading = bot.send_message(m.chat.id, "⏳ جاري معالجة البيانات الجمركية وحساب الخصم...")
        time.sleep(1.5)
        bot.delete_message(m.chat.id, loading.message_id)
        
        data = utils.get_data()
        
        # حسبة الشراء اليدوية:
        gram_raw_price = mithqal_price / 5  # تقسيم سعر المثقال على 5
        final_buy_price = gram_raw_price - melt_fee  # خصم أجور الصهر
        
        total_iqd = weight_gram * final_buy_price
        
        usd_rate = data['settings']['usd_100']
        usd_count = int(total_iqd // usd_rate)
        remainder = int(total_iqd % usd_rate)
        
        reply = (f"💎 **فاتورة شراء من زبون**\n"
                 f"━━━━━━━━━━━━━━━━━━\n"
                 f"💠 العيار: عيار {karat}\n"
                 f"⚖️ الوزن: {weight_gram} غرام\n"
                 f"🏷 سعر الغرام الصافي: {gram_raw_price:,.0f} د.ع\n"
                 f"🔥 الخصم/أجور الصهر: {melt_fee:,.0f} د.ع\n"
                 f"💵 سعر الشراء النهائي للغرام: {final_buy_price:,.0f} د.ع\n"
                 f"━━━━━━━━━━━━━━━━━━\n"
                 f"💰 إجمالي ما يدفع للزبون: {total_iqd:,.0f} د.ع\n"
                 f"💵 بالدولار: {usd_count} ورقة ($100) + {remainder:,.0f} د.ع")
        
        from bot import show_main_menu
        show_main_menu(m, bot, reply)
    except Exception as e:
        bot.send_message(m.chat.id, "⚠️ حدث خطأ أثناء الحساب. حاول مجدداً.")
