import utils, time
from telebot import types

def handle(m, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("عيار 21", "عيار 18")
    msg = bot.send_message(m.chat.id, "💰 بيع للزبون: اختر العيار المطلوب:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: ask_weight(m, bot))

def ask_weight(m, bot):
    karat = "21" if "21" in m.text else "18"
    msg = bot.send_message(m.chat.id, f"✅ عيار {karat}. أرسل الوزن الحالي **بالغرام**:")
    bot.register_next_step_handler(msg, lambda m: calc(m, bot, karat))

def calc(m, bot, karat):
    try:
        weight_gram = float(m.text)
        
        # حركة جاري التحميل الذكية لإعطاء هيبة وفخامة للبرنامج
        loading = bot.send_message(m.chat.id, "⏳ جاري الاتصال بالسيرفر وحساب التكلفة...")
        time.sleep(1.5)
        bot.delete_message(m.chat.id, loading.message_id)
        
        data = utils.get_data()
        settings = data['settings']
        
        # الحسبة الصارمة للبيع:
        mithqal_price = settings[f"mithqal_{karat}"]
        gram_raw_price = mithqal_price / 5  # تقسيم سعر المثقال على 5
        labor_gram = settings[f"labor_{karat}"]  # أجور الصياغة للغرام
        
        final_gram_price = gram_raw_price + labor_gram  # جمع السعر مع الصياغة
        total_iqd = weight_gram * final_gram_price  # الضرب في الوزن بالغرام
        
        usd_rate = settings['usd_100']
        usd_count = int(total_iqd // usd_rate)
        remainder = int(total_iqd % usd_rate)
        
        reply = (f"💎 **فاتورة البيع للزبون**\n"
                 f"━━━━━━━━━━━━━━━━━━\n"
                 f"💠 العيار: عيار {karat}\n"
                 f"⚖️ الوزن: {weight_gram} غرام\n"
                 f"🏷 سعر الغرام الصافي: {gram_raw_price:,.0f} د.ع\n"
                 f"🔨 أجور الصياغة (للغرام): {labor_gram:,.0f} د.ع\n"
                 f"💵 سعر الغرام النهائي: {final_gram_price:,.0f} د.ع\n"
                 f"━━━━━━━━━━━━━━━━━━\n"
                 f"💰 الإجمالي بالدينار: {total_iqd:,.0f} د.ع\n"
                 f"💵 الإجمالي بالدولار: {usd_count} ورقة ($100) + {remainder:,.0f} د.ع")
        
        from bot import show_main_menu
        show_main_menu(m, bot, reply)
    except Exception as e:
        bot.send_message(m.chat.id, "⚠️ خطأ! يرجى إدخال رقم صحيح للوزن.")
