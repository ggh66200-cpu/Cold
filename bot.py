import os
import re
import time
from datetime import datetime
import telebot
from telebot import types
import utils

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# مخزن مؤقت لحالات المستخدمين
USER_STATE = {}
# مخزن مؤقت لبيانات الحسابات الجارية (العيار والوزن) لكل مستخدم
INVOICE_DATA = {}

# ترند المزايدة التسويقي الأساسي للعملاء
TREND_BASE_NUMBER = 149

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # إذا كان المستخدم هو الأدمن، تظهر له أزرار التحكم الخاصة بالأدمن
    if user_id == ADMIN_ID:
        markup.add(
            types.KeyboardButton("👑 لوحة تحكم الأدمن المركزي"),
            types.KeyboardButton("⚙️ إعدادات الصباح")
        )
    else:
        markup.add(
            types.KeyboardButton("⚙️ إعدادات الصباح"),
            types.KeyboardButton("📊 اللغات / Ziman / Languages")
        )
    markup.add(
        types.KeyboardButton("📥 بيع لزبون"),
        types.KeyboardButton("📤 شراء من زبون")
    )
    return markup

def get_cancel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("❌ إلغاء العملية الحالية"))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if utils.is_action_locked(user_id, delay=2): return

    # تنظيف أي حالات سابقة
    USER_STATE.pop(user_id, None)
    INVOICE_DATA.pop(user_id, None)

    goldsmith = utils.get_goldsmith(user_id)
    
    if not goldsmith:
        welcome_text = (
            "👑 أرامكي للحلول الرقمية | ARAMKY 👑\n\n"
            "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
            "━━━━━━━━━━━━━━━\n\n"
            "📝 خطوة تفعيل المحل وتأمين البيانات البيعية:\n\n"
            "أخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر كل معلومة في سطر منفصل "
            "(اضغط Enter للانتقال لسطر جديد) بهذا الترتيب لتسجيلك بالسيرفر وتثبيت بياناتك على فواتيرك الفخمة الترويجية:\n\n"
            "1️⃣ اسم المحل الرسمي (مثال: صياغة ومجوهرات النخبة)\n"
            "2️⃣ المحافظة والمنطقة (مثال: بغداد - الكاظمية)\n"
            "3️⃣ رقم هاتف المحل المعتمد (مثال: 07700000000)\n\n"
            "💡 هذه البيانات تُخزن بشكل آمن تماماً وتُطبع تلقائياً في ترويسة فواتيرك الفخمة لتبهر زبائنك!"
        )
        USER_STATE[user_id] = "AWAITING_REGISTRATION"
        bot.send_message(message.chat.id, welcome_text, reply_markup=types.ReplyKeyboardRemove())
        return

    if not goldsmith['is_active']:
        expired_text = (
            "👑 ARAMKY | أرامكي للحلول الرقمية 👑\n"
            "⚜️ فرع نواة الذهب لأنظمة الصاغة والأسواق المالية ⚜️\n"
            "━━━━━━━━━━━━━━━\n\n"
            "🛑 باقة شيوخ الكار المطورين (خصم حصري)\n\n"
            "🚫 انتهت الفترة التجريبية المخصصة للمنظومة. للاشتراك وتمديد الصلاحية بالسعر التنافسي المستمر "
            "بقيمة 105,000 دينار عراقي فقط بدلاً من السعر الأساسي 133,000 دينار.\n\n"
            "💳 حساب الإيداع المالي الذهبي للشركة:\n"
            "رقم الماستر كارد الرسمي المعتمد:\n"
            "<code>910400201646</code>\n\n"
            "📸 بعد التحويل، أرسل صورة الوصل لتفعيل حسابك تلقائياً.\n"
            "📞 خط الدعم الفني: 07872180902"
        )
        bot.send_message(message.chat.id, expired_text, parse_mode="HTML")
        return

    bot.send_message(
        message.chat.id, 
        f"✨ أهلاً بك يا شيخ الكار في محلك العامر: {goldsmith['full_name']}\nيرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇", 
        reply_markup=get_main_keyboard(user_id)
    )

# معالجة الضغط على الأزرار الشفافة لتحديث أسعار الصباح واختيار العيارات
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_queries(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    # تحديث أسعار الصباح (خاص بالأدمن فقط)
    if call.data == "update_morning_prices":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "⚠️ عذراً، هذا الإجراء مخصص للمدير المركزي للمنظومة فقط.")
            return
        
        bot.answer_callback_query(call.id)
        USER_STATE[user_id] = "ADMIN_UPDATING_PRICES"
        bot.send_message(chat_id, "⚙️ أرسل الأسعار الجديدة في سطر واحد مفصولة بنقطتين (:) بالترتيب التالي:\n(سعر21:سعر18:أجور21:أجور18:سعر الدولار)\n\nمثال للنسخ والتعديل:\n<code>900000:450000:10000:1000:155000</code>", parse_mode="HTML", reply_markup=get_cancel_keyboard())
    
    # اختيار عيارات البيع والشراء
    elif call.data.startswith("select_carat_"):
        bot.answer_callback_query(call.id)
        data_parts = call.data.split("_")
        mode = data_parts[2]   # sell أو buy
        carat = int(data_parts[3]) # 21 أو 18
        
        if user_id not in INVOICE_DATA:
            INVOICE_DATA[user_id] = {}
        
        INVOICE_DATA[user_id]['carat'] = carat
        
        if mode == "sell":
            USER_STATE[user_id] = "AWAITING_WEIGHT_SELL"
            bot.send_message(chat_id, f"⚖️ ممتاز، اخترت عيار {carat}.\nأرسل الآن وزن الذهب بالغرام فقط (مثال: 14.85)", reply_markup=get_cancel_keyboard())
        elif mode == "buy":
            USER_STATE[user_id] = "AWAITING_WEIGHT_BUY"
            bot.send_message(chat_id, f"⚖️ ممتاز، اخترت عيار {carat}.\nأرسل الآن وزن الذهب مع خصم الصهر مفصولين بنقطتين (:)\nالصيغة: (الوزن:خصم الصهر للغرام)\nمثال: 25.40:5000", reply_markup=get_cancel_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # زر إلغاء العمليات الحالية والعودة للقائمة الرئيسية في أي وقت
    if text == "❌ إلغاء العملية الحالية":
        USER_STATE.pop(user_id, None)
        INVOICE_DATA.pop(user_id, None)
        bot.send_message(message.chat.id, "📥 تم إلغاء العملية بنجاح والرجوع للقائمة الرئيسية.", reply_markup=get_main_keyboard(user_id))
        return

    # حماية ضد التكرار والسبام مع ضعف النت
    if utils.is_action_locked(user_id, delay=3):
        return

    # 1. مرحلة التسجيل وتخزين معلومات المحل
    if USER_STATE.get(user_id) == "AWAITING_REGISTRATION":
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) >= 3:
            loading_msg = bot.send_message(message.chat.id, "⏳ جاري الاتصال بالسيرفر المركزي وتأمين حسابك المعتمد...")
            
            shop_name = lines[0]
            location = lines[1]
            phone = lines[2]
            
            utils.register_new_goldsmith(user_id, shop_name, location, phone)
            total_goldsmiths = utils.get_total_active_goldsmiths()
            goldsmith_data = utils.get_goldsmith(user_id)
            goldsmith_id = goldsmith_data.get('id', '---') if goldsmith_data else '---'

            # معادلة ترند المزايدة التسويقية للعموم
            public_total = TREND_BASE_NUMBER + total_goldsmiths

            success_text = (
                "👑 أرامكي للحلول الرقمية | ARAMKY 👑\n"
                "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
                "━━━━━━━━━━━━━━━\n\n"
                "✨ يا فتاح يا عليم يا رزاق يا كريم ✨\n\n"
                "🎁 رزقكم مبارك، وتم تفعيل الفترة التجريبية المجانية لمدة 7 أيام لك تجتاح بها السوق ميدانياً!\n\n"
                "🔢 رقم الصائغ المعتمد: #️⃣{id}\n"
                "📍 المحل العامر: {shop}\n"
                "🗺️ الموقع: {loc}\n"
                "📞 الهاتف: {phone}\n\n"
                "👥 المشتركين النشطين في الكار الآن:\n"
                "🥇 {total} صائغ معتمد\n"
                "━━━━━━━━━━━━━━━\n"
                "👇 يرجى اختيار العملية المطلوبة من الأزرار أدناه للبدء"
            ).format(id=goldsmith_id, shop=shop_name, loc=location, phone=phone, total=public_total)
            
            USER_STATE.pop(user_id, None)
            
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
            except:
                pass
            
            bot.send_message(message.chat.id, success_text, reply_markup=get_main_keyboard(user_id))
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال البيانات بثلاثة أسطر منفصلة واضحة (الاسم، ثم الموقع، ثم الهاتف) لضمان دقة فواتيرك الفخمة.")
        return

    # 2. لوحة تحكم الأدمن للعدد الحقيقي للشركاء
    if text == "👑 لوحة تحكم الأدمن المركزي" and user_id == ADMIN_ID:
        total_real = utils.get_total_active_goldsmiths()
        admin_panel_text = (
            "🛡️ منظومة نواة الذهب الذكية | لوحة الإدارة العليا\n"
            "━━━━━━━━━━━━━━━\n\n"
            "📊 إحصائيات النظام الفعلية والحقيقية:\n"
            "👥 عدد الصاغة المشتركين الفعليين بالأنظمة: {total} صائغ نشط.\n\n"
            "📣 ملاحظة: الرقم التسويقي الظاهر للعملاء يعتمد على ترند المزايدة ويبدأ من {trend} صائغ فما فوق."
        ).format(total=total_real, trend=TREND_BASE_NUMBER + total_real)
        bot.send_message(message.chat.id, admin_panel_text, reply_markup=get_main_keyboard(user_id))
        return

    # 3. معالجة تحديث أسعار الصباح من قبل الأدمن
    if USER_STATE.get(user_id) == "ADMIN_UPDATING_PRICES" and user_id == ADMIN_ID:
        try:
            parts = text.split(':')
            p21 = float(parts[0])
            p18 = float(parts[1])
            w21 = float(parts[2])
            w18 = float(parts[3])
            usd = float(parts[4])
            
            # تحديث الأسعار في السيرفر/الملف (بفرض أن utils تدعم التحديث أو محاكاة ذلك)
            # ملاحظة: إذا كانت دالة التحديث تتطلب وسيطاً لكل صائغ أو عامة، هنا نقوم بحفظها
            # لتسهيل الأمر سنخزن الإعدادات الحالية للأدمن ليتم محاكاتها أو ربطها بالدالة
            if hasattr(utils, 'update_global_prices'):
                utils.update_global_prices(p21, p18, w21, w18, usd)
            
            USER_STATE.pop(user_id, None)
            bot.send_message(message.chat.id, "✅ تم تحديث أسعار الصباح المركزية في السيرفر بنجاح لجميع المشتركين!", reply_markup=get_main_keyboard(user_id))
        except:
            bot.send_message(message.chat.id, "⚠️ الصيغة خاطئة. يرجى إدخال البيانات مطابقة للمثال تماماً وعاود المحاولة.")
        return

    # 4. عرض أسعار الصباح للمستخدمين
    if text == "⚙️ إعدادات الصباح":
        prices = utils.get_goldsmith_prices(user_id)
        morning_text = (
            "💎 ARAMKY | أرامكي للحلول الرقمية 💎\n"
            "⚜️ فرع نواة الذهب لأنظمة الصاغة والأسواق المالية ⚜️\n"
            "━━━━━━━━━━━━━━━\n\n"
            "☀️ صباح الرزق والبركة والسعادة يا طيب!\n\n"
            "📋 إعدادات الصباح الحالية لمحلك:\n\n"
            "🔷 سعر مثقال عيار 21: {p21:,.0f} دينار\n"
            "🔷 سعر مثقال عيار 18: {p18:,.0f} دينار\n"
            "🔨 أجور صياغة غرام 21: {m21:,.0f} دينار\n"
            "🔨 أجور صياغة غرام 18: {m18:,.0f} دينار\n"
            "💵 سعر الـ 100 دولار: {usd:,.0f} دينار\n"
            "━━━━━━━━━━━━━━━\n"
            "💡 لتحديث الأسعار بلمحة بصر، اضغط على الزر أدناه 👇"
        ).format(
            p21=prices.get('price_21', 900000), p18=prices.get('price_18', 450000),
            m21=prices.get('wage_21', 10000), m18=prices.get('wage_18', 1000),
            usd=prices.get('usd_rate', 155000)
        )
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton("🔄 تحديث أسعار اليوم", callback_data="update_morning_prices"))
        bot.send_message(message.chat.id, morning_text, reply_markup=inline_markup)
        return

    # 5. زر اللغات وقائمة التغيير
    if text == "📊 اللغات / Ziman / Languages":
        lang_markup = types.InlineKeyboardMarkup()
        lang_markup.add(
            types.InlineKeyboardButton("🇮🇶 العربية", callback_data="set_lang_ar"),
            types.InlineKeyboardButton("☀️ Kurdî", callback_data="set_lang_ku"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
        )
        bot.send_message(message.chat.id, "🌐 الرجاء اختيار لغة عمل المنظومة الذكية:\n⚙️ Zimanê botê hilbijêrin:\n🌐 Select system interface language:", reply_markup=lang_markup)
        return

    # 6. بيع لزبون (استبدال الصيغة المعقدة بأزرار العيار)
    if text == "📥 بيع لزبون":
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(
            types.InlineKeyboardButton("👑 عيار 21", callback_data="select_carat_sell_21"),
            types.InlineKeyboardButton("💎 عيار 18", callback_data="select_carat_sell_18")
        )
        bot.send_message(message.chat.id, "📥 حساب بيع لزبون | اختر عيار الذهب المطلوب للحساب أدناه 👇", reply_markup=inline_markup)
        return

    # 7. شراء من زبون (استبدال الصيغة المعقدة بأزرار العيار)
    if text == "📤 شراء من زبون":
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(
            types.InlineKeyboardButton("👑 عيار 21", callback_data="select_carat_buy_21"),
            types.InlineKeyboardButton("💎 عيار 18", callback_data="select_carat_buy_18")
        )
        bot.send_message(message.chat.id, "📤 حساب شراء من زبون | اختر عيار الذهب المستلم للحساب أدناه 👇", reply_markup=inline_markup)
        return

    # 8. استقبال ومعالجة وزن البيع
    if USER_STATE.get(user_id) == "AWAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ جاري تحميل وتدقيق العمليات الرياضية وتفقيط النقد...")
        
        prices = utils.get_goldsmith_prices(user_id)
        goldsmith = utils.get_goldsmith(user_id)
        
        shop_name = goldsmith.get('full_name', 'المحل العامر') if goldsmith else 'المحل العامر'
        shop_loc = goldsmith.get('location', 'العراق') if goldsmith else 'العراق'
        shop_phone = goldsmith.get('phone', '---') if goldsmith else '---'
        
        try:
            weight = float(text)
            check_carat = INVOICE_DATA.get(user_id, {}).get('carat', 21)
            
            mitqal_price = prices.get('price_21', 900000) if check_carat == 21 else prices.get('price_18', 450000)
            wage_per_gram = prices.get('wage_21', 10000) if check_carat == 21 else prices.get('wage_18', 1000)
            
            gram_pure_price = mitqal_price / 5.0
            total_iqd = (gram_pure_price + wage_per_gram) * weight
            
            usd_rate = prices.get('usd_rate', 155000)
            total_usd_bills = int(total_iqd // usd_rate)
            remaining_iqd = total_iqd % usd_rate
            
            # هندسة الفاتورة الفخمة الترويجية المكتملة
            invoice_text = (
                "🏛️ {shop} 🏛️\n"
                "📍 {loc} | 📞 {phone}\n"
                "━━━━━━━━━━━━━━━\n"
                "🧾 فاتورة بيع ذهب معتمدة\n"
                "━━━━━━━━━━━━━━━\n"
                "🔹 صنف الذهب الحسابي: عيار {carat}\n"
                "⚖️ الوزن الإجمالي الموزون: {w} غرام\n"
                "🔨 أجور الصياغة المحددة للغرام: {wage:,.0f} دينار\n"
                "💰 سعر الغرام الصافي لليوم: {g_price:,.0f} دينار\n"
                "━━━━━━━━━━━━━━━\n"
                "💵 إجمالي المبلغ بالدينار العراقي:\n"
                "👈 <b>{total_iqd:,.0f} دينار</b>\n\n"
                "💵 تفقيط النقد بالورق والدينار المحلي:\n"
                "👈 <b>{usd_bills} ورقة (فئة 100$) و {rem_iqd:,.0f} دينار عراقـي</b>\n"
                "━━━━━━━━━━━━━━━\n"
                "✨ ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك! ✨\n\n"
                "🤖 تم الحساب والنشر بواسطة منظومة نواة الذهب الذكية @GoldenCalc_Bot"
            ).format(shop=shop_name, loc=shop_loc, phone=shop_phone, carat=check_carat, w=weight, wage=wage_per_gram, g_price=gram_pure_price, total_iqd=total_iqd, usd_bills=total_usd_bills, rem_iqd=remaining_iqd)
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
            except:
                pass
            bot.send_message(message.chat.id, invoice_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        except Exception as e:
            bot.edit_message_text("⚠️ يرجى إرسال الوزن كرقم صحيح أو عشري فقط (مثال: 12.34). أعد المحاولة أو اضغط إلغاء.", chat_id=message.chat.id, message_id=loading_msg.message_id)
        return

    # 9. استقبال ومعالجة وزن وعيار الشراء
    if USER_STATE.get(user_id) == "AWAITING_WEIGHT_BUY":
        loading_msg = bot.send_message(message.chat.id, "⏳ جاري تحميل وتدقيق العمليات الرياضية وتفقيط النقد...")
        
        prices = utils.get_goldsmith_prices(user_id)
        goldsmith = utils.get_goldsmith(user_id)
        
        shop_name = goldsmith.get('full_name', 'المحل العامر') if goldsmith else 'المحل العامر'
        shop_loc = goldsmith.get('location', 'العراق') if goldsmith else 'العراق'
        shop_phone = goldsmith.get('phone', '---') if goldsmith else '---'
        
        try:
            parts = text.split(':')
            weight = float(parts[0])
            melt_discount = float(parts[1])
            check_carat = INVOICE_DATA.get(user_id, {}).get('carat', 21)
            
            mitqal_buy_price = prices.get('price_21', 900000) if check_carat == 21 else prices.get('price_18', 450000)
            gram_buy_price = (mitqal_buy_price / 5.0) - melt_discount
            total_iqd = gram_buy_price * weight
            
            usd_rate = prices.get('usd_rate', 155000)
            total_usd_bills = int(total_iqd // usd_rate)
            remaining_iqd = total_iqd % usd_rate
            
            # هندسة الفاتورة الفخمة الترويجية المكتملة للشراء
            invoice_text = (
                "🏛️ {shop} 🏛️\n"
                "📍 {loc} | 📞 {phone}\n"
                "━━━━━━━━━━━━━━━\n"
                "🧾 فاتورة شراء ذهب كسر ونفايات\n"
                "━━━━━━━━━━━━━━━\n"
                "🔹 صنف الذهب المستلم: عيار {carat}\n"
                "⚖️ الوزن الإجمالي الموزون: {w} غرام\n"
                "🔥 خصم الصهر والنواقص للجرام: {melt:,.0f} دينار\n"
                "💰 سعر غرام الشراء المعتمد: {g_price:,.0f} دينار\n"
                "━━━━━━━━━━━━━━━\n"
                "💵 المبلغ الكلي المستحق للزبون بالدينار:\n"
                "👈 <b>{total_iqd:,.0f} دينار</b>\n\n"
                "💵 تفقيط النقد بالورق والدينار المحلي:\n"
                "👈 <b>{usd_bills} ورقة (فئة 100$) و {rem_iqd:,.0f} دينار عراقـي</b>\n"
                "━━━━━━━━━━━━━━━\n"
                "🌸 تمت عملية الشراء بنجاح! ربي يعوضكم بالخير والرزق الوفير! ✨\n\n"
                "🤖 تم الحساب والنشر بواسطة منظومة نواة الذهب الذكية @GoldenCalc_Bot"
            ).format(shop=shop_name, loc=shop_loc, phone=shop_phone, carat=check_carat, w=weight, melt=melt_discount, g_price=gram_buy_price, total_iqd=total_iqd, usd_bills=total_usd_bills, rem_iqd=remaining_iqd)
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
            except:
                pass
            bot.send_message(message.chat.id, invoice_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        except Exception as e:
            bot.edit_message_text("⚠️ صيغة خطأ بالإدخال، تأكد من كتابة الوزن ثم النقطتين ثم خصم الصهر بدقة (مثال: 25.4:5000).", chat_id=message.chat.id, message_id=loading_msg.message_id)
        return

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
