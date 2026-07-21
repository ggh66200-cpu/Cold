import os
import re
from datetime import datetime, timedelta
import telebot
from telebot import types
import utils  # ملف العمليات المساعدة وقاعدة البيانات

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# مخازن الحالات المؤقتة لإدارة تدفق الأسئلة العمودية
USER_STATE = {}
INVOICE_DATA = {}
MORNING_STEP = {}
USER_LANG = {}

TREND_BASE_NUMBER = 149  # الرقم الترند التسويقي الأساسي

# قاموس النصوص للغات الثلاث (عربي، كردي، إنجليزي) بشكل عمودي بالكامل
LANG_TEXTS = {
    'ar': {
        'cancel': "❌ إلغاء العملية الحالية",
        'main_welcome': "✨ أهلاً بك يا شيخ الكار في محلك العامر:\n🏛️ {name}\n\nيرجى اختيار العملية الحالية وتوكل على الرزاق 👇",
        'select_carat_sell': "📥 حساب بيع لزبون\nاختر عيار الذهب المطلوب للحساب أدناه 👇",
        'select_carat_buy': "📤 حساب شراء من زبون\nاختر عيار الذهب المستلم للحساب أدناه 👇",
        'input_weight_sell': "⚖️ ممتاز، اخترت عيار {carat}.\nأرسل الآن وزن الذهب بالغرام فقط (مثال: 14.85):",
        'input_mitqal_buy': "⚖️ ممتاز، اخترت عيار {carat}.\nأرسل الآن عدد المثاقيل المتفق عليها مع الزبون للشراء (مثال: 5.5):",
        'input_price_buy': "💰 أرسل الآن سعر مثقال الكسر المعتمد المتفق عليه مع الزبون للشراء (مثال: 440000):",
        'input_wage_buy': "🛠️ أرسل الآن قيمة خصم أجور الكسر للمثقال الواحد (إذا لا يوجد خصم أكتب 0):",
        'loading': "⏳ جاري تحميل وتدقيق العمليات الرياضية وتفقيط النقد..."
    },
    'ku': {
        'cancel': "❌ Labordana Karê Taze",
        'main_welcome': "✨ Bi xêr bî şêxê kar bo daxazên te:\n🏛️ {name}\n\nJi kerema xwe yek ji bişkokan hilbijêre 👇",
        'select_carat_sell': "📥 Hesabê firotanê bo xerîdar\nEyarê zêr hilbijêre 👇",
        'select_carat_buy': "📤 Hesabê kirînê ji xerîdar\nEyarê zêr hilbijêre 👇",
        'input_weight_sell': "⚖️ Baş e, te eyarê {carat} hilbijart.\nNiha tenê kêşeya zêr bi gram bişîne (mînak: 14.85):",
        'input_mitqal_buy': "⚖️ Baş e, te eyarê {carat} hilbijart.\nNiha hejmara mîsqalan bişîne (mînak: 5.5):",
        'input_price_buy': "💰 Niha nirxê mîsqalê zêr yê rêkeftî bişîne (mînak: 440000):",
        'input_wage_buy': "🛠️ Niha heqê kêmkirina şikandinê bo her mîsqalê bişîne (heger tune ye 0 binivîse):",
        'loading': "⏳ Karê hesaban û sehkirinê tê kirin..."
    },
    'en': {
        'cancel': "❌ Cancel Current Operation",
        'main_welcome': "✨ Welcome to your store:\n🏛️ {name}\n\nPlease choose an operation from below 👇",
        'select_carat_sell': "📥 Sell to Customer Calculation\nChoose gold carat below 👇",
        'select_carat_buy': "📤 Buy from Customer Calculation\nChoose gold carat below 👇",
        'input_weight_sell': "⚖️ Excellent, carat {carat} selected.\nSend the gold weight in grams only (e.g., 14.85):",
        'input_mitqal_buy': "⚖️ Excellent, carat {carat} selected.\nSend the total number of Mitqals (e.g., 5.5):",
        'input_price_buy': "💰 Send the agreed price per Mitqal for buying (e.g., 440000):",
        'input_wage_buy': "🛠️ Send the scrap wage deduction per Mitqal (write 0 if none):",
        'loading': "⏳ Calculating financial transactions and bills..."
    }
}

def get_str(user_id, key):
    lang = utils.get_goldsmith_lang(user_id) or USER_LANG.get(user_id, 'ar')
    return LANG_TEXTS[lang].get(key, LANG_TEXTS['ar'][key])

# الكيبورد الرئيسي - أزرار عمودية تماماً لتسهيل الاستخدام على الموبايل
def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("👑 لوحة تحكم الأدمن المركزي"))
    
    markup.add(
        types.KeyboardButton("⚙️ إعدادات الصباح"),
        types.KeyboardButton("📥 بيع لزبون"),
        types.KeyboardButton("📤 شراء من زبون"),
        types.KeyboardButton("📊 اللغات / Ziman / Languages"),
        types.KeyboardButton("💳 طلب تجديد الاشتراك")
    )
    return markup

def get_cancel_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton(get_str(user_id, 'cancel')))
    return markup

# 1. رسالة الاستقبال الرسمية والفخمة للمنظومة
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if utils.is_action_locked(user_id, delay=1): return

    USER_STATE.pop(user_id, None)
    INVOICE_DATA.pop(user_id, None)
    MORNING_STEP.pop(user_id, None)

    goldsmith = utils.get_goldsmith(user_id)
    
    if not goldsmith:
        welcome_text = (
            "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "👋 أهلاً بك يا شيخ الكار في النظام الرقمي الأول المخصص لإدارة حسابات محلات الذهب بيعاً وشراءً وتفقيط النقد بالدينار والدولار بلحظات.\n\n"
            "💎 مميزات المنظومة الذكية:\n"
            "🛡️ استقلالية تامة لمحلك بأسعارك اليومية الخاصة بخصوصية كاملة.\n"
            "⚖️ حسابات ذكية للبيع بالغرام وللشراء بالمثقال خطوة بخطوة.\n"
            "🧾 إصدار فواتير فخمة ترويجية تحمل اسم وهاتف محلك لبناء هويتك وتوسيع زبائنك.\n\n"
            "📝 خطوة تفعيل المحل وتأمين حسابك:\n"
            "يرجى إرسال معلومات محلك العامر كل معلومة في سطر منفصل (عمودياً) بهذا الترتيب لتثبيتها بالسيرفر وقاعدة البيانات:\n\n"
            "1️⃣ اسم المحل الرسمي\n"
            "2️⃣ المحافظة والمنطقة\n"
            "3️⃣ رقم هاتف المحل المعتمد"
        )
        USER_STATE[user_id] = "AWAITING_REGISTRATION"
        bot.send_message(message.chat.id, welcome_text, reply_markup=types.ReplyKeyboardRemove())
        return

    # فحص صلاحية الاشتراك والتنبيه أو القفل التلقائي
    is_active, days_left = utils.check_goldsmith_validity(user_id)
    if not is_active:
        expired_text = (
            "⚜️ منظومة نواة الذهب الذكية ⚜️\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "🛑 تنبيه انتهاء الصلاحية وقفل النظام تلقائياً:\n"
            "🚫 لقد انتهت الفترة المخصصة للمنظومة في محلك العامر.\n\n"
            "💳 لتجديد الاشتراك وتفعيل الصلاحية تلقائياً يرجى تحويل رسوم باقة شيوخ الكار المفتوحة، وإرسال صورة الوصل المالي عبر الزر أدناه لتفعيل حسابك مباشرة بكبسة زر من الإدارة.\n\n"
            "🆔 رقم هويتك في النظام: ( <code>{uid}</code> )"
        ).format(uid=user_id)
        bot.send_message(message.chat.id, expired_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        return

    if days_left <= 3:
        bot.send_message(message.chat.id, f"⚠️ <b>تنبيه مبكر:</b> متبقي {days_left} أيام فقط على نهاية صلاحية وقت محلك التجاري، يرجى التجديد لضمان عدم توقف النظام.")

    bot.send_message(
        message.chat.id, 
        get_str(user_id, 'main_welcome').format(name=goldsmith['full_name']), 
        reply_markup=get_main_keyboard(user_id),
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_queries(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data.startswith("set_lang_"):
        lang = call.data.split("_")[2]
        USER_LANG[user_id] = lang
        utils.update_goldsmith_lang(user_id, lang)
        bot.answer_callback_query(call.id, "✅ Done / تم الترتيب")
        bot.send_message(chat_id, "✅ تم ضبط وترتيب لغة المنظومة عمودياً بنجاح.", reply_markup=get_main_keyboard(user_id))
        return

    if call.data.startswith("admin_approve_") and user_id == ADMIN_ID:
        target_uid = int(call.data.split("_")[2])
        utils.modify_goldsmith_subscription(target_uid, 30)
        bot.answer_callback_query(call.id, "🟢 تم تفعيل الحساب")
        bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption=call.message.caption + "\n\n🟢 [تمت الموافقة وتفعيل العميل بنجاح]")
        bot.send_message(target_uid, "📢 <b>تنبيه رسمي من الإدارة العليا:</b>\nتمت مراجعة وصل التحويل المالي وتفعيل صلاحية وقت محلك التجاري بنجاح! توكل على الرزاق ونظم فواتيرك الآن.", parse_mode="HTML")
        return

    if call.data.startswith("admin_reject_") and user_id == ADMIN_ID:
        target_uid = int(call.data.split("_")[2])
        bot.answer_callback_query(call.id, "🔴 تم رفض الطلب")
        bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption=call.message.caption + "\n\n🔴 [تم رفض هذا الطلب]")
        bot.send_message(target_uid, "❌ <b>تنبيه من الدعم الفني:</b>\nتم رفض طلب التفعيل الحالي. يرجى التأكد من إرسال صورة وصل دفع صحيحة أو التواصل معنا مباشرة.", parse_mode="HTML")
        return

    if call.data.startswith("select_carat_"):
        bot.answer_callback_query(call.id)
        data_parts = call.data.split("_")
        mode = data_parts[2]   
        carat = int(data_parts[3]) 
        
        INVOICE_DATA[user_id] = {'carat': carat}
        
        if mode == "sell":
            USER_STATE[user_id] = "AWAITING_WEIGHT_SELL"
            bot.send_message(chat_id, get_str(user_id, 'input_weight_sell').format(carat=carat), reply_markup=get_cancel_keyboard(user_id))
        elif mode == "buy":
            USER_STATE[user_id] = "AWAITING_MITQAL_BUY"
            bot.send_message(chat_id, get_str(user_id, 'input_mitqal_buy').format(carat=carat), reply_markup=get_cancel_keyboard(user_id))

@bot.message_handler(content_types=['photo'])
def handle_incoming_photos(message):
    user_id = message.from_user.id
    if USER_STATE.get(user_id) == "AWAITING_RENEWAL_PROOFS":
        goldsmith = utils.get_goldsmith(user_id)
        caption_text = (
            "🚨 <b>طلب تفعيل اشتراك جديد مستلم:</b>\n\n"
            "👤 اسم الصائغ: {name}\n"
            "🆔 معرف النظام: <code>{uid}</code>\n"
            "📞 الهاتف: {phone}"
        ).format(name=goldsmith['full_name'], uid=user_id, phone=goldsmith['phone'])
        
        admin_markup = types.InlineKeyboardMarkup(row_width=1)
        admin_markup.add(
            types.InlineKeyboardButton("🟢 تفعيل العميل (30 يوم)", callback_data=f"admin_approve_{user_id}"),
            types.InlineKeyboardButton("🔴 رفض وثيقة الوصل المالي", callback_data=f"admin_reject_{user_id}")
        )
        
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption_text, parse_mode="HTML", reply_markup=admin_markup)
        USER_STATE.pop(user_id, None)
        bot.send_message(message.chat.id, "✅ تم إرسال وثيقة التحويل إلى الإدارة بنجاح. سيتم إشعارك وتفعيل النظام تلقائياً خلال دقائق بمجرد التأكيد.", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text in ["❌ إلغاء العملية الحالية", "❌ Labordana Karê Taze", "❌ Cancel Current Operation"]:
        USER_STATE.pop(user_id, None)
        INVOICE_DATA.pop(user_id, None)
        MORNING_STEP.pop(user_id, None)
        bot.send_message(message.chat.id, "📥 تم إلغاء العملية والرجوع للقائمة الرئيسية.", reply_markup=get_main_keyboard(user_id))
        return

    if utils.is_action_locked(user_id, delay=1): return

    # 🔍 التحقق الفوري: هل المستخدم مسجل أصلاً بقاعدة البيانات؟
    goldsmith = utils.get_goldsmith(user_id)

    # 🟢 [منطق العميل المسجل]: إذا ضغط انتر أو أرسل نص عشوائي وهو خارج أي عملية حسابية
    if goldsmith and USER_STATE.get(user_id) not in ["AWAITING_WEIGHT_SELL", "AWAITING_MITQAL_BUY", "AWAITING_PRICE_BUY", "AWAITING_WAGE_BUY", "MORNING_STEP_21_PRICE", "MORNING_STEP_18_PRICE", "MORNING_STEP_21_WAGE", "MORNING_STEP_18_WAGE", "MORNING_STEP_USD_RATE", "AWAITING_RENEWAL_PROOFS"]:
        
        # إذا ضغط على أحد الأزرار الرئيسية لا نقاطعه، دعه يكمل
        if text in ["⚙️ إعدادات الصباح", "📥 بيع لزبون", "📤 شراء من زبون", "📊 اللغات / Ziman / Languages", "💳 طلب تجديد الاشتراك", "👑 لوحة تحكم الأدمن المركزي"]:
            pass 
        else:
            # رد بكلام طيب وإرجاعه للوحة التحكم بدون تصفير أو طلب بيانات
            is_active, _ = utils.check_goldsmith_validity(user_id)
            if not is_active:
                bot.send_message(message.chat.id, "🛑 النظام مقفل لانتهاء الصلاحية. يرجى الضغط على زر طلب التجديد لإرسال الوصل.")
                return
                
            friendly_text = (
                "✨ يا فتاح يا عليم يا رزاق يا كريم... رزقكم مبارك يا شيخ الكار! ✨\n\n"
                "🏛️ محلك العامر (<b>{name}</b>) مفعّل وبأتم الجاهزية.\n"
                "اضغط على الأزرار أدناه مباشرة لإدخال أسعارك الصباحية أو حساب الفواتير بسهولة ودون أي تعقيد 👇"
            ).format(name=goldsmith['full_name'])
            bot.send_message(message.chat.id, friendly_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
            return

    # 🔴 [منطق العميل الجديد]: خطوة التسجيل العمودي مع معالجة وتطهير الأسطر الفارغة
    if not goldsmith and USER_STATE.get(user_id) == "AWAITING_REGISTRATION":
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) >= 3:
            loading_msg = bot.send_message(message.chat.id, get_str(user_id, 'loading'))
            
            shop_name, location, phone = lines[0], lines[1], lines[2]
            utils.register_new_goldsmith(user_id, shop_name, location, phone)
            
            total_goldsmiths = utils.get_total_active_goldsmiths()
            public_total = TREND_BASE_NUMBER + total_goldsmiths
            
            success_text = (
                "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
                "━━━━━━━━━━━━━━━━━\n\n"
                "✨ يا فتاح يا عليم يا رزاق يا كريم ✨\n\n"
                "🎁 رزقكم مبارك، وتم تفعيل الفترة التجريبية بنجاح لك!\n\n"
                "🆔 رقم هويتك الفريد بالنظام: <code>{uid}</code>\n"
                "📍 المحل العامر: {shop}\n"
                "🗺️ الموقع: {loc}\n"
                "📞 الهاتف: {phone}\n\n"
                "👥 المشتركين النشطين في الكار الآن:\n"
                "🥇 {total} صائغ معتمد\n"
                "━━━━━━━━━━━━━━━━━\n"
                "👇 يرجى اختيار العملية المطلوبة من الأزرار أدناه للبدء"
            ).format(uid=user_id, shop=shop_name, loc=location, phone=phone, total=public_total)
            
            USER_STATE.pop(user_id, None)
            try: bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
            except: pass
            bot.send_message(message.chat.id, success_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال البيانات بثلاثة أسطر واضحة (اضغط Enter بين الأسطر): اسم المحل، المحافظة، ثم رقم الهاتف.")
        return

    # فحص صلاحية النظام قبل إكمال العمليات للعملاء المسجلين
    if user_id != ADMIN_ID:
        is_active, _ = utils.check_goldsmith_validity(user_id)
        if not is_active and text != "💳 طلب تجديد الاشتراك":
            bot.send_message(message.chat.id, "🛑 النظام مقفل حالياً لانتهاء صلاحية الاشتراك. اضغط على زر طلب التجديد لإرسال الوصل.")
            return

    # طلب التجديد بإرسال الوصل المالي
    if text == "💳 طلب تجديد الاشتراك":
        USER_STATE[user_id] = "AWAITING_RENEWAL_PROOFS"
        bot.send_message(message.chat.id, "📸 يرجى إرسال صورة واضحة لوصل التحويل المالي أو كشف الدفع المباشر الآن:", reply_markup=get_cancel_keyboard(user_id))
        return

    # لوحة تحكم الأدمن التفاعلية 
    if text == "👑 لوحة تحكم الأدمن المركزي" and user_id == ADMIN_ID:
        total_real = utils.get_total_active_goldsmiths()
        admin_panel_text = (
            "🛡️ لوحة الإدارة العليا للمنظومة\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "📊 إحصائيات النظام الفعلي:\n"
            "👥 عدد الصاغة الفعليين: {total} صائغ نشط.\n"
            "👥 العدد التسويقي الظاهر للعموم: {trend} صائغ معتمد."
        ).format(total=total_real, trend=TREND_BASE_NUMBER + total_real)
        bot.send_message(message.chat.id, admin_panel_text, reply_markup=get_main_keyboard(user_id))
        return

    # إعدادات الصباح العمودية (سؤال وجواب منفصل)
    if text == "⚙️ إعدادات الصباح":
        INVOICE_DATA[user_id] = {}
        USER_STATE[user_id] = "MORNING_STEP_21_PRICE"
        bot.send_message(message.chat.id, "☀️ إعدادات الصباح للأسعار الحرة لمحلك:\n\n🔷 يرجى إرسال سعر مثقال عيار 21 الحالي (أرقام فقط مجردة):", reply_markup=get_cancel_keyboard(user_id))
        return

    if USER_STATE.get(user_id) == "MORNING_STEP_21_PRICE":
        try:
            INVOICE_DATA[user_id]['p21'] = float(text)
            USER_STATE[user_id] = "MORNING_STEP_18_PRICE"
            bot.send_message(message.chat.id, "🔷 ممتاز. الآن أرسل سعر مثقال عيار 18 الحالي (أرقام فقط):", reply_markup=get_cancel_keyboard(user_id))
        except: bot.send_message(message.chat.id, "⚠️ يرجى إدخال سعر صحيح كأرقام فقط.")
        return

    if USER_STATE.get(user_id) == "MORNING_STEP_18_PRICE":
        try:
            INVOICE_DATA[user_id]['p18'] = float(text)
            USER_STATE[user_id] = "MORNING_STEP_21_WAGE"
            bot.send_message(message.chat.id, "🔨 الآن أرسل أجور صياغة غرام عيار 21 (أكتب 0 إذا لا يوجد):", reply_markup=get_cancel_keyboard(user_id))
        except: bot.send_message(message.chat.id, "⚠️ يرجى إدخال أرقام فقط.")
        return

    if USER_STATE.get(user_id) == "MORNING_STEP_21_WAGE":
        try:
            INVOICE_DATA[user_id]['w21'] = float(text)
            USER_STATE[user_id] = "MORNING_STEP_18_WAGE"
            bot.send_message(message.chat.id, "🔨 الآن أرسل أجور صياغة غرام عيار 18 (أكتب 0 إذا لا يوجد):", reply_markup=get_cancel_keyboard(user_id))
        except: bot.send_message(message.chat.id, "⚠️ يرجى إدخال أرقام فقط.")
        return

    if USER_STATE.get(user_id) == "MORNING_STEP_18_WAGE":
        try:
            INVOICE_DATA[user_id]['w18'] = float(text)
            USER_STATE[user_id] = "MORNING_STEP_USD_RATE"
            bot.send_message(message.chat.id, "💵 أخيراً، أرسل سعر صرف الـ 100 دولار الحالي بالدينار (مثال: 153000):", reply_markup=get_cancel_keyboard(user_id))
        except: bot.send_message(message.chat.id, "⚠️ يرجى إدخال أرقام فقط.")
        return

    if USER_STATE.get(user_id) == "MORNING_STEP_USD_RATE":
        try:
            usd = float(text)
            d = INVOICE_DATA[user_id]
            utils.update_goldsmith_prices(user_id, d['p21'], d['p18'], d['w21'], d['w18'], usd)
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            bot.send_message(message.chat.id, "✅ تم حفظ وتثبيت جميع أسعار الصباح الخاصة بمحلك بنجاح وتحديث النظام عمودياً!", reply_markup=get_main_keyboard(user_id))
        except: bot.send_message(message.chat.id, "⚠️ خطأ في الإدخال، يرجى كتابة سعر الدولار بشكل صحيح.")
        return

    # زر خيارات اللغات الفعلي
    if text == "📊 اللغات / Ziman / Languages":
        lang_markup = types.InlineKeyboardMarkup(row_width=1)
        lang_markup.add(
            types.InlineKeyboardButton("🇮🇶 العربية", callback_data="set_lang_ar"),
            types.InlineKeyboardButton("☀️ Kurdî", callback_data="set_lang_ku"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
        )
        bot.send_message(message.chat.id, "🌐 اختر لغة العمل للواجهات البرمجية عمودياً:", reply_markup=lang_markup)
        return

    # حساب بيع لزبون
    if text == "📥 بيع لزبون":
        inline_markup = types.InlineKeyboardMarkup(row_width=1)
        inline_markup.add(
            types.InlineKeyboardButton("👑 عيار 21", callback_data="select_carat_sell_21"),
            types.InlineKeyboardButton("💎 عيار 18", callback_data="select_carat_sell_18")
        )
        bot.send_message(message.chat.id, get_str(user_id, 'select_carat_sell'), reply_markup=inline_markup)
        return

    if USER_STATE.get(user_id) == "AWAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, get_str(user_id, 'loading'))
        prices = utils.get_goldsmith_prices(user_id)
        
        try:
            weight = float(text)
            check_carat = INVOICE_DATA[user_id]['carat']
            
            mitqal_price = prices.get('price_21', 900000) if check_carat == 21 else prices.get('price_18', 450000)
            wage_per_gram = prices.get('wage_21', 10000) if check_carat == 21 else prices.get('wage_1', 1000)
