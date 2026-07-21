import os
import re
from datetime import datetime
import telebot
from telebot import types
import utils

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# حالات إدخال البيانات (FSM وهمية متوافقة مع التكرار)
USER_STATE = {}

# ================= القوائم والأزرار الرسمية =================
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("⚙️ إعدادات الصباح"),
        types.KeyboardButton("📊 اللغات / Ziman / Languages")
    )
    markup.add(
        types.KeyboardButton("📥 بيع لزبون"),
        types.KeyboardButton("📤 شراء من زبون")
    )
    return markup

# ================= الأمر الرئيسي /start =================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if utils.is_action_locked(user_id, delay=2): return

    goldsmith = utils.get_goldsmith(user_id)
    
    if not goldsmith:
        welcome_text = (
            "👑 أرامكي للحلول الرقمية | ARAMKY 👑\n\n"
            "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
            "━━━━━━━━━━━━━━━\n\n"
            "📝 خطوة تفعيل المحل وتأمين البيانات\n\n"
            "أخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر كل معلومة في سطر منفصل "
            "(اضغط Enter للانتقال لسطر جديد) بهذا الترتيب لتسجيلك بالسيرفر:\n\n"
            "1️⃣ اسم المحل الرسمي\n"
            "2️⃣ المحافظة والمنطقة\n"
            "3️⃣ رقم هاتف المحل المعتمد"
        )
        USER_STATE[user_id] = "AWAITING_REGISTRATION"
        bot.send_message(message.chat.id, welcome_text, reply_markup=types.ReplyKeyboardRemove())
        return

    # التحقق من الصلاحية والدفع
    if not goldsmith['is_active']:
        expired_text = (
            "👑 ARAMKY | أرامكي للحلول الرقمية 👑\n"
            "⚜️ فرع نواة الذهب لأنظمة الصاغة والأسواق المالية ⚜️\n"
            "━━━━━━━━━━━━━━━\n\n"
            "🛑 باقة شيوخ الكار المطورين (خصم حصري)\n\n"
            "🚫 انتهت الفترة التجريبية المخصصة للمنظومة. للاشتراك وتمديد الصلاحية بالسعر التنافسي المستمر "
            "بقيمة 105,000 دينار عراقي فقط بدلاً من السعر الأساسي 133,000 دينار (توفير 28,000 دينار عراقي بكل تجديد).\n\n"
            "💳 حساب الإيداع المالي الذهبي للشركة:\n"
            "رقم الماستر كارد الرسمي المعتمد:\n"
            "<code>910400201646</code>\n\n"
            "📸 بعد التحويل، اضغط على الزر بالأسفل وأرسل صورة الوصل لتفعيل حسابك تلقائياً.\n"
            "📞 خط الدعم الفني: 07872180902"
        )
        bot.send_message(message.chat.id, expired_text, parse_mode="HTML")
        return

    # الدخول المباشر للوحة المشترك المفعّل
    bot.send_message(
        message.chat.id, 
        f"✨ أهلاً بك يا شيخ الكار في محلك العامر: {goldsmith['full_name']}\nيرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇", 
        reply_markup=get_main_keyboard()
    )

# ================= معالجة النصوص والتسجيل الحركي =================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # 1. معالجة التسجيل
    if USER_STATE.get(user_id) == "AWAITING_REGISTRATION":
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) >= 3:
            shop_name = lines[0]
            location = lines[1]
            phone = lines[2]
            
            # حفظ في سوبابيس عبر utils
            utils.register_new_goldsmith(user_id, shop_name, location, phone)
            
            # جلب البيانات المحدثة للعرض الفاخر
            total_goldsmiths = utils.get_total_active_goldsmiths()
            goldsmith_data = utils.get_goldsmith(user_id)
            goldsmith_id = goldsmith_data.get('id', '---') if goldsmith_data else '---'

            success_text = (
                "👑 أرامكي للحلول الرقمية | ARAMKY 👑\n"
                "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
                "━━━━━━━━━━━━━━━\n\n"
                "✨ يا فتاح يا عليم يا رزاق يا كريم ✨\n\n"
                "أهلاً ومرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة!\n\n"
                "🎁 رزقكم مبارك، وتم تفعيل الفترة التجريبية المجانية المدة لها 7 أيام لك تجتاح بها السوق ميدانياً!\n\n"
                "🔢 رقم الصائغ المعتمد: #️⃣{id}\n"
                "📍 المحل العامر: {shop}\n"
                "🗺️ الموقع: {loc}\n"
                "📞 الهاتف: {phone}\n\n"
                "👥 المشتركين النشطين في الكار الآن:\n"
                "🥇 {total} صائغ\n"
                "━━━━━━━━━━━━━━━\n"
                "👇 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق"
            ).format(id=goldsmith_id, shop=shop_name, loc=location, phone=phone, total=total_goldsmiths)
            
            USER_STATE.pop(user_id, None)
            bot.send_message(message.chat.id, success_text, reply_markup=get_main_keyboard())
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال البيانات بثلاثة أسطر واضحة (الاسم، ثم الموقع، ثم الهاتف).")
        return

    # 2. أزرار القائمة الرئيسية
    if text == "⚙️ إعدادات الصباح":
        # جلب الأسعار الحالية المخزنة للصائغ في utils
        prices = utils.get_goldsmith_prices(user_id)
        morning_text = (
            "💎 ARAMKY | أرامكي للحلول الرقمية 💎\n"
            "⚜️ فرع نواة الذهب لأنظمة الصاغة والأسواق المالية ⚜️\n"
            "━━━━━━━━━━━━━━━\n\n"
            "☀️ صباح الرزق والبركة والسعادة يا طيب!\n"
            "نسأل الله أن يجعل هذا اليوم مباركاً، مليئاً بالخير الوفير لعملكم وحلالكم الطيب. ✨\n\n"
            "📋 إعدادات الصباح الحالية لمحلك:\n\n"
            "🔷 سعر مثقال عيار 21: {p21:,.0f} دينار\n"
            "🔷 سعر مثقال عيار 18: {p18:,.0f} دينار\n"
            "🔨 أجور صياغة غرام 21: {m21:,.0f} دينار\n"
            "🔨 أجور صياغة غرام 18: {m18:,.0f} دينار\n"
            "💵 سعر الـ 100 دولار: {usd:,.0f} دينار\n"
            "━━━━━━━━━━━━━━━\n"
            "💡 لتحديث جميع هذه الأسعار بلمحة بصر وسؤال واحد، اضغط على الزر أدناه 👇"
        ).format(
            p21=prices.get('price_21', 900000), p18=prices.get('price_18', 450000),
            m21=prices.get('wage_21', 10000), m18=prices.get('wage_18', 1000),
            usd=prices.get('usd_rate', 155000)
        )
        
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton("🔄 تحديث أسعار اليوم", callback_data="update_morning_prices"))
        bot.send_message(message.chat.id, morning_text, reply_markup=inline_markup)

    elif text == "📥 بيع لزبون":
        USER_STATE[user_id] = "CALC_SELL"
        bot.send_message(message.chat.id, "⚖️ أرسل البيانات لحساب الفاتورة بالصيغة التالية:\n(الوزن بالغرام:العيار)\nمثال: 4.963:18")

    elif text == "📤 شراء من زبون":
        USER_STATE[user_id] = "CALC_BUY"
        bot.send_message(message.chat.id, "🔥 أرسل البيانات لحساب الشراء بالصيغة التالية:\n(الوزن بالغرام:العيار:خصم الصهر للغرام)\nمثال: 478.963:18:35000")

    # 3. معالجة عمليات الحساب المباشرة
    elif USER_STATE.get(user_id) in ["CALC_SELL", "CALC_BUY"]:
        current_state = USER_STATE.get(user_id)
        prices = utils.get_goldsmith_prices(user_id)
        goldsmith = utils.get_goldsmith(user_id)
        shop_name = goldsmith.get('full_name', 'المحل العامر') if goldsmith else 'المحل العامر'
        
        try:
            parts = text.split(':')
            weight = float(parts[0])
            check_carat = int(parts[1])
            
            if current_state == "CALC_SELL":
                # خوارزمية الصاغة للبيع
                mitqal_price = prices.get('price_21', 900000) if check_carat == 21 else prices.get('price_18', 450000)
                wage_per_gram = prices.get('wage_21', 10000) if check_carat == 21 else prices.get('wage_18', 1000)
                
                # سعر الغرام الصافي = سعر المثقال ÷ 5
                gram_pure_price = mitqal_price / 5.0
                total_iqd = (gram_pure_price + wage_per_gram) * weight
                
                # خوارزمية العرف العراقي للتفقيط (بدون تقريب كسور)
                usd_rate = prices.get('usd_rate', 155000)
                total_usd_bills = int(total_iqd // usd_rate)
                remaining_iqd = total_iqd % usd_rate
                
                invoice_text = (
                    "🔷 ARAMKY | أرامكي للحلول الرقمية 🔷\n"
                    "⚜️ فرع نواة الذهب لأنظمة الصاغة والأسواق المالية ⚜️\n"
                    "━━━━━━━━━━━━━━━\n\n"
                    "🧾 فاتورة بيع ذهب للزبون\n"
                    "━━━━━━━━━━━━━━━\n"
                    "🔹 المحل العامر: {shop}\n"
                    "🔹 العيار ونوع الحساب: عيار {carat} (حساب بالغرام)\n"
                    "🔹 الوزن المطلوب: {w} غرام\n"
                    "⚖️ الوزن الإجمالي بالجرام: {w} غرام\n"
                    "🔨 أجور صياغة الغرام: {wage:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━\n"
                    "💰 سعر غرام الذهب الصافي: {g_price:,.0f} دينار\n"
                    "💵 السعر الكلي بالدينار العراقي:\n"
                    "👈 {total_iqd:,.0f} دينار\n\n"
                    "💵 صافي الحساب بالورق والدينار:\n"
                    "👈 {usd_bills} ورقة و {rem_iqd:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━\n"
                    "🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! ✨"
                ).format(
                    shop=shop_name, carat=check_carat, w=weight, wage=wage_per_gram,
                    g_price=gram_pure_price, total_iqd=total_iqd, usd_bills=total_usd_bills, rem_iqd=remaining_iqd
                )
                
            elif current_state == "CALC_BUY":
                # خوارزمية الصاغة للشراء
                melt_discount = float(parts[2])
                mitqal_buy_price = prices.get('price_21', 900000) if check_carat == 21 else prices.get('price_18', 450000)
                gram_buy_price = (mitqal_buy_price / 5.0) - melt_discount
                total_iqd = gram_buy_price * weight
                
                usd_rate = prices.get('usd_rate', 155000)
                total_usd_bills = int(total_iqd // usd_rate)
                remaining_iqd = total_iqd % usd_rate
                
                invoice_text = (
                    "🔷 ARAMKY | أرامكي للحلول الرقمية 🔷\n"
                    "⚜️ فرع نواة الذهب لأنظمة الصاغة والأسواق المالية ⚜️\n"
                    "━━━━━━━━━━━━━━━\n\n"
                    "🧾 فاتورة شراء ذهب من زبون\n"
                    "━━━━━━━━━━━━━━━\n"
                    "🔹 المحل العامر: {shop}\n"
                    "🔹 العيار وطريقة الشراء: عيار {carat} (حساب بالغرام)\n"
                    "🔹 الوزن المستلم: {w} غرام\n"
                    "⚖️ الوزن الإجمالي بالجرام: {w} غرام\n"
                    "🔥 خصم الصهر/أجور الجرام: {melt:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━\n"
                    "💰 سعر الشراء المعتمد للمثقال: {m_price:,.0f} دينار\n"
                    "💰 سعر غرام الشراء الصافي: {g_price:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━\n"
                    "💵 المبلغ الكلي المدفوع بالدينار العراقي:\n"
                    "👈 {total_iqd:,.0f} دينار\n\n"
                    "💵 صافي الحساب بالورق والدينار:\n"
                    "👈 {usd_bills} ورقة و {rem_iqd:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━\n"
                    "🌸 تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير! ✨"
                ).format(
                    shop=shop_name, carat=check_carat, w=weight, melt=melt_discount,
                    m_price=mitqal_buy_price, g_price=gram_buy_price, total_iqd=total_iqd,
                    usd_bills=total_usd_bills, rem_iqd=remaining_iqd
                )
                
            USER_STATE.pop(user_id, None)
            bot.send_message(message.chat.id, invoice_text, reply_markup=get_main_keyboard())
        except Exception as e:
            bot.send_message(message.chat.id, "⚠️ صيغة خطأ بالإدخال، تأكد من الفصل باستخدام النقطتين (:) بدقة.")

# ================= لوحة تحكم الإدارة (ADMIN PANEL) =================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🟢 تفعيل / 🔴 إلغاء صائغ", callback_data="admin_toggle_user"),
        types.InlineKeyboardButton("⏱️ تعديل صلاحية صائغ محدد", callback_data="admin_change_user_trial")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك في لوحة تحكم إدارة منظومة نواة الذهب:", reply_markup=markup)

# ================= معالجة كولباك إعدادات الصباح والتحديث المباشر =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    if call.data == "update_morning_prices":
        USER_STATE[user_id] = "SET_MORNING"
        bot.send_message(call.message.chat.id, "✏️ أرسل الأسعار الجديدة بفراغات متتالية بالصيغة التالية:\n(مثقال21 مثقال18 أجور21 أجور18 صرف100دولار)\nمثال:\n900000 450000 10000 1000 155000")
    
    # إدارة الأدمن
    elif call.data == "admin_toggle_user" and user_id == ADMIN_ID:
        msg = bot.send_message(call.message.chat.id, "أرسل الـ ID لتغيير حالته:")
        bot.register_next_step_handler(msg, process_toggle)

def process_toggle(message):
    try:
        t_id = int(message.text.strip())
        u = utils.get_goldsmith(t_id)
        if u:
            ns = not u['is_active']
            utils.update_goldsmith_status(t_id, ns)
            bot.send_message(message.chat.id, f"✅ تم تحديث حالة الصائغ إلى: {'🟢 مفعّل' if ns else '🔴 مقفل'}")
    except:
        bot.send_message(message.chat.id, "خطأ في المعالجة.")

# ================= بيئة تشغيل السيرفر المستقرة 24 ساعة =================
if __name__ == "__main__":
    import threading
    from http.server import SimpleHTTPRequestHandler, HTTPServer

    def run_dummy_server():
        try:
            port = int(os.environ.get("PORT", 8080))
            server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
            server.serve_forever()
        except Exception as e:
            print(f"Server Error: {e}")

    threading.Thread(target=run_dummy_server, daemon=True).start()
    bot.infinity_polling()
    
