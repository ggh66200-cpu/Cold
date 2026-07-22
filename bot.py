import os
import telebot
from telebot import types
import utils

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

USER_STATE = {}
INVOICE_DATA = {}

# رقم الترند الأساسي
TREND_BASE_NUMBER = 149

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    # إذا كان الحساب هو الأدمن المركزي، تظهر له أزرار التحكم المطلوبة بالكامل
    if user_id == ADMIN_ID:
        markup.add(
            types.KeyboardButton("👑 لوحة تحكم الأدمن المركزي"),
            types.KeyboardButton("⚙️ إدخال أسعار الصباح اليومية"),
            types.KeyboardButton("📥 حساب بيع لزبون"),
            types.KeyboardButton("📤 حساب شراء من زبون"),
            types.KeyboardButton("❌ إلغاء العملية الحالية")
        )
        return markup

    # فحص الصلاحية للعملاء العاديين قبل إعطائهم أزرار الحساب
    goldsmith = utils.get_goldsmith(user_id)
    if goldsmith:
        is_active, _ = utils.check_goldsmith_validity(user_id)
        if not is_active:
            # إذا انتهت الصلاحية، يظهر فقط زر التجديد والإلغاء
            markup.add(
                types.KeyboardButton("💳 إرسال وصل الدفع وتفعيل الاشتراك"),
                types.KeyboardButton("❌ إلغاء العملية الحالية")
            )
            return markup

    markup.add(
        types.KeyboardButton("⚙️ إدخال أسعار الصباح اليومية"),
        types.KeyboardButton("📥 حساب بيع لزبون"),
        types.KeyboardButton("📤 حساب شراء من زبون"),
        types.KeyboardButton("💳 إرسال وصل الدفع وتفعيل الاشتراك"),
        types.KeyboardButton("❌ إلغاء العملية الحالية")
    )
    return markup

def send_subscription_required_message(chat_id, user_id):
    """دالة إرسال رسالة الاشتراك المعسلة والمستقلة عند انتهاء الوقت"""
    msg = (
        "💎 **باقة شيوخ الكار المطورين (خصم حصري)** 💎\n"
        "━━━━━━━━━━━━━━━━━\n"
        "⚠️ **يا فتاح يا عليم يا رزاق يا كريم..**\n"
        "أخي الغالي وصاحب الكار المحترم، انتهت الفترة المخصصة للمنظومة في محلك العامر.\n\n"
        "للاشتراك وتمديد الصلاحية بالسعر التنافسي المستمر والمميز:\n"
        "💰 **بقيمة 105,000 دينار عراقي فقط بدلاً من السعر الأساسي 133,000 دينار (توفير 28,000 دينار عراقي بكل تجديد).**\n\n"
        "🏛️ **حساب الإيداع المالي الذهبي للشركة:**\n"
        "💳 رقم الماستر كارد الرسمي المعتمد: <code>910400201646</code>\n\n"
        "📸 **بعد التحويل، اضغط على زر (إرسال وصل الدفع وتفعيل الاشتراك) بالأسفل وأرسل صورة الوصل لتفعيل حسابك تلقائياً.**\n\n"
        "📞 **خط الدعم الفني ورقم الطوارئ المباشر:** 07872180902\n"
        "🤖 **معرف المنظومة الرسمي:** @GoldenCalc_Bot\n"
        "━━━━━━━━━━━━━━━━━\n"
        "*نحن هنا لخدمة وتسهيل رزقك، متمنين لك تجارة رابحة وبركة لا تنتهي!* ✨"
    )
    bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    USER_STATE.pop(user_id, None) # تنظيف وتصفير لمنع التكرار والتعليق بسبب ضعف نت العراق
    
    goldsmith = utils.get_goldsmith(user_id)
    
    # جلب الفترة التجريبية الحالية المحددة من قبل الأدمن (افتراضياً 7 وإذا غيرها تصير 3)
    trial_days = utils.get_system_setting("trial_days", 7)
    
    if not goldsmith:
        welcome_text = (
            "👑 أرامكي للحلول الرقمية | ARAMKY 👑\n"
            "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "📝 **خطوة تفعيل المحل وتأمين البيانات:**\n"
            "أخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر كل معلومة في سطر منفصل (اضغط Enter للانتقال لسطر جديد) بهذا الترتيب لتسجيلك بالسيرفر:\n\n"
            "1️⃣ اسم المحل الرسمي\n"
            "2️⃣ المحافظة والمنطقة\n"
            "3️⃣ رقم هاتف المحل المعتمد\n\n"
            "👇 اكتبها الآن وأرسلها لتفتح لك الأزرار مباشرة."
        )
        USER_STATE[user_id] = "AWAITING_REGISTRATION"
        bot.send_message(message.chat.id, welcome_text, reply_markup=types.ReplyKeyboardRemove())
        return

    # فحص صلاحية الوقت والنظام يقفل نفسه تلقائياً
    is_active, _ = utils.check_goldsmith_validity(user_id)
    if not is_active:
        send_subscription_required_message(message.chat.id, user_id)
        return

    # حساب رقم الترند المميز بدون إظهار الأشخاص النشطين الفعليين
    trend_number = TREND_BASE_NUMBER + utils.get_total_registered_users_count()

    success_welcome = (
        "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\n"
        "أهلاً ومرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة!\n\n"
        f"🎁 رزقكم مبارك، وتم تفعيل الفترة التجريبية المدتها {trial_days} أيام لك تجتاح بها السوق ميدانياً!\n\n"
        f"🔢 **رقم الصائغ المعتمد: #{trend_number}**\n"
        f"📍 المحل العامر: {goldsmith['full_name']}\n"
        f"🗺️ الموقع: {goldsmith['location']}\n"
        f"📞 الهاتف: {goldsmith['phone']}\n"
        "━━━━━━━━━━━━━━━━━\n"
        "🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇"
    )
    bot.send_message(message.chat.id, success_welcome, reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "❌ إلغاء العملية الحالية")
def cancel_op(message):
    user_id = message.from_user.id
    USER_STATE.pop(user_id, None)
    INVOICE_DATA.pop(user_id, None)
    bot.send_message(message.chat.id, "📥 تم إلغاء العملية والرجوع للقائمة الرئيسية بسلامة.", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "👑 لوحة تحكم الأدمن المركزي")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ زيادة وقت عميل (إضافة أيام)", callback_data="adm_add_days"),
        types.InlineKeyboardButton("➖ تقليص وقت عميل (خصم أيام)", callback_data="adm_sub_days"),
        types.InlineKeyboardButton("⏱️ تحويل الفترة التجريبية إلى 3 أيام", callback_data="adm_set_trial_3"),
        types.InlineKeyboardButton("⏱️ تحويل الفترة التجريبية إلى 7 أيام", callback_data="adm_set_trial_7"),
        types.InlineKeyboardButton("🔒 قفل حساب عميل فوراً", callback_data="adm_lock_user")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك يا مدير.. اختر إجراء التحكم بالعملاء والفترات الزمنية:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "⚙️ إدخال أسعار الصباح اليومية")
def morning_prices_start(message):
    user_id = message.from_user.id
    is_active, _ = utils.check_goldsmith_validity(user_id)
    if not is_active and user_id != ADMIN_ID:
        send_subscription_required_message(message.chat.id, user_id)
        return
        
    USER_STATE[user_id] = "AWAITING_ALL_PRICES"
    instruction = (
        "💎 **أرامكي للحلول الرقمية | فرع نواة الذهب** 💎\n"
        "☀️ **صباح الرزق والسعادة والبركة يا طيب!** ☀️\n\n"
        "نسأل الله أن يجعل هذا اليوم مباركاً، مليئاً بالخير الوفير لعملكم وحلالكم الطيب.\n\n"
        "📋 يرجى إرسال إعدادات الصباح الحالية لمحلك في **رسالة واحدة فقط** مرتبة عمودياً (أرقام فقط):\n\n"
        "1️⃣ سعر مثقال عيار 21\n"
        "2️⃣ سعر مثقال عيار 18\n"
        "3️⃣ أجور صياغة غرام 21 (اكتب 0 إذا لا يوجد)\n"
        "4️⃣ أجور صياغة غرام 18 (اكتب 0 إذا لا يوجد)\n"
        "5️⃣ سعر صرف الـ 100 دولار بالدينار (مثال: 155000)\n\n"
        "💡 لتحديث جميع هذه الأسعار بلمحة بصر وسؤال واحد، أرسلها الآن عمودياً."
    )
    bot.send_message(message.chat.id, instruction)

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    if USER_STATE.get(user_id) == "AWAITING_RENEWAL_PROOFS":
        goldsmith = utils.get_goldsmith(user_id)
        caption_text = f"🚨 **طلب تفعيل اشتراك جديد واصل الماستر كارد:**\n\n الصائغ: {goldsmith['full_name']}\n🆔 المعرف الرقمي: <code>{user_id}</code>\n📞 الهاتف: {goldsmith['phone']}"
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("🟢 تفعيل (30 يوم حقيقي)", callback_data=f"approve_30_{user_id}"),
            types.InlineKeyboardButton("🔴 رفض وثيقة الوصل", callback_data=f"reject_0_{user_id}")
        )
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption_text, parse_mode="HTML", reply_markup=admin_markup)
        USER_STATE.pop(user_id, None)
        bot.send_message(message.chat.id, "✅ تم استلام صورة الوصل المالي بنجاح يا طيب. جاري النقر والتفعيل من قبل الإدارة بلحظات.", reply_markup=get_main_keyboard(user_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def handle_admin_approvals(call):
    if call.from_user.id != ADMIN_ID: return
    data_parts = call.data.split("_")
    action = data_parts[0]
    days = int(data_parts[1])
    target_uid = int(data_parts[2])
    
    if action == "approve":
        utils.modify_goldsmith_subscription(target_uid, days)
        bot.send_message(target_uid, "📢 **بشرى سارة لشيوخ الصاغة:** تمت مراجعة الوصل المالي يدويّاً وتفعيل صلاحية المنظومة لمحلك بالكامل بنجاح! الرزق الوفير والمبارك تمنياتنا لك.", parse_mode="HTML")
        bot.edit_message_caption("🟢 [تم التفعيل بنجاح بضغطة زر]", chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif action == "reject":
        bot.send_message(target_uid, "❌ **تنبيه الإدارة:** لم نتمكن من تأكيد وثيقة الوصل المرسلة. يرجى مراجعة عملية الدفع وإعادة الإرسال أو التواصل مباشرة مع خط الطوارئ.")
        bot.edit_message_caption("🔴 [تم رفض الوصل وإلغاء التفعيل]", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_panel_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data
    bot.answer_callback_query(call.id)
    
    if action == "adm_add_days":
        USER_STATE[ADMIN_ID] = "ADMIN_EXPECTING_ADD"
        bot.send_message(call.message.chat.id, "👤 أرسل يوزر (معرف) العميل وعدد الأيام المراد زيادتها بفراغ كالتالي:\n`123456789 7`")
    elif action == "adm_sub_days":
        USER_STATE[ADMIN_ID] = "ADMIN_EXPECTING_SUB"
        bot.send_message(call.message.chat.id, "👤 أرسل يوزر العميل وعدد الأيام المراد خصمها بفراغ كالتالي:\n`123456789 5`")
    elif action == "adm_lock_user":
        USER_STATE[ADMIN_ID] = "ADMIN_EXPECTING_LOCK"
        bot.send_message(call.message.chat.id, "🔒 أرسل يوزر العميل المراد قفل حسابه فوراً وإنهاء مدته:")
    elif action == "adm_set_trial_3":
        utils.set_system_setting("trial_days", 3)
        bot.send_message(call.message.chat.id, "✅ تم تعديل النظام بنجاح! الفترة التجريبية للعملاء الجدد أصبحت الآن (3 أيام) وتغيرت بالرسالة الترحيبية تلقائياً.")
    elif action == "adm_set_trial_7":
        utils.set_system_setting("trial_days", 7)
        bot.send_message(call.message.chat.id, "✅ تم تعديل النظام بنجاح! الفترة التجريبية للعملاء الجدد أصبحت الآن (7 أيام) وتغيرت بالرسالة الترحيبية تلقائياً.")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = USER_STATE.get(user_id)

    if text == "💳 إرسال وصل الدفع وتفعيل الاشتراك":
        USER_STATE[user_id] = "AWAITING_RENEWAL_PROOFS"
        bot.send_message(message.chat.id, "📸 من فضلك أخي الغالي، التقط صورة واضحة لوصل التحويل أو الدفع وأرسلها هنا مباشرة:")
        return

    # أفعال الأدمن لتعديل وقت العميل يدوياً وفحص النظام
    if user_id == ADMIN_ID and state in ["ADMIN_EXPECTING_ADD", "ADMIN_EXPECTING_SUB", "ADMIN_EXPECTING_LOCK"]:
        try:
            if state == "ADMIN_EXPECTING_LOCK":
                target = int(text)
                utils.modify_goldsmith_subscription(target, -999) # تصفير الأيام بالكامل لقفل الحساب
                bot.send_message(ADMIN_ID, f"🔒 تم قفل حساب العميل رقم {target} بنجاح وسيطالبه بالنظام بالدفع فوراً.")
            else:
                parts = text.split()
                target_uid, days = int(parts[0]), int(parts[1])
                if state == "ADMIN_EXPECTING_SUB": days = -days
                utils.modify_goldsmith_subscription(target_uid, days)
                bot.send_message(ADMIN_ID, f"✅ تم تعديل وقت العميل بنجاح. صافي الأيام المعدلة: {days} يوم.")
            USER_STATE.pop(ADMIN_ID, None)
        except:
            bot.send_message(ADMIN_ID, "⚠️ صيغة خاطئة. تأكد من إدخال البيانات بشكل صحيح أرقام فقط وفراغات بينها.")
        return

    # تسجيل العميل
    if state == "AWAITING_REGISTRATION":
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            utils.register_new_goldsmith(user_id, lines[0], lines[1], lines[2])
            USER_STATE.pop(user_id, None)
            # الانتقال لرسالة البداية لعرض رقم الترند بعد التحديث
            start_command(message)
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إرسال البيانات بـ 3 أسطر منفصلة تماماً (اسم المحل، الموقع، الهاتف) كما هو مطلوب.")
        return

    # إدخال الأسعار الصباحية
    if state == "AWAITING_ALL_PRICES":
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 5:
            try:
                p21, p18, w21, w18, usd = float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3]), float(lines[4])
                utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
                USER_STATE.pop(user_id, None)
                bot.send_message(message.chat.id, "✅ **تم حفظ أسعار الصباح بنجاح!**\nالمنظومة الآن جاهزة تماماً لحساب الفواتير بدقة مرنة وسلاسة مطلقة.", reply_markup=get_main_keyboard(user_id))
            except:
                bot.send_message(message.chat.id, "⚠️ خطأ بالأرقام، يرجى إدخال قيم رقمية صحيحة فقط.")
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال الأسطر الخمسة كاملة وبشكل عمودي متسلسل.")
        return

    # فحص الصلاحية قبل تنفيذ الحسابات
    is_active, _ = utils.check_goldsmith_validity(user_id)
    if not is_active and user_id != ADMIN_ID:
        send_subscription_required_message(message.chat.id, user_id)
        return

    if text == "📥 حساب بيع لزبون":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("عيار 21", callback_data="calc_sell_21"),
                   types.InlineKeyboardButton("عيار 18", callback_data="calc_sell_18"))
        bot.send_message(message.chat.id, "📥 حساب بيع لزبون:\nاختر عيار الذهب المطلوب أدناه لتسهيل الحساب 👇", reply_markup=markup)
        return

    if text == "📤 حساب شراء من زبون":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("عيار 21", callback_data="calc_buy_21"),
                   types.InlineKeyboardButton("عيار 18", callback_data="calc_buy_18"))
        bot.send_message(message.chat.id, "📤 حساب شراء من زبون:\nاختر العيار المستلم من الزبون أدناه 👇", reply_markup=markup)
        return

    # معالجة الوزن والناتج النهائي للبيع
    if state == "WAITING_WEIGHT_SELL":
        try:
            w = float(text)
            carat = INVOICE_DATA[user_id]['carat']
            prices = utils.get_goldsmith_prices(user_id)
            goldsmith = utils.get_goldsmith(user_id)
            
            m_price = prices['price_21'] if carat == 21 else prices['price_18']
            wage = prices['wage_21'] if carat == 21 else prices['wage_18']
            
            total_iqd = ((m_price / 5.0) + wage) * w
            usd_rate = prices['usd_rate']
            usd_bills = int(total_iqd // usd_rate)
            rem_iqd = total_iqd % usd_rate
            
            invoice = (
                f"💎 ARAMKY | فرع نواة الذهب 💎\n"
                f"🏛️ **المحل العامر: {goldsmith['full_name']}**\n"
                f"🧾 **فاتورة بيع ذهب للزبون**\n"
                "━━━━━━━━━━━━━━━━━\n"
                f"🔷 العيار ونوع الحساب: عيار {carat} (حساب بالغرام)\n"
                f"⚖️ الوزن المطلوب: {w} غرام\n"
                f"⚖️ الوزن الإجمالي بالجرام: {w} غرام\n"
                f"🔨 أجور صياغة الغرام: {wage:,.0f} دينار\n"
                "━━━━━━━━━━━━━━━━━\n"
                f"💰 سعر غرام الذهب الصافي: {(m_price / 5.0):,.0f} دينار\n"
                f"💵 **السعر الكلي بالدينار العراقي:**\n"
                f"👉 <b>{total_iqd:,.0f} دينار</b>\n\n"
                f"💵 **صافي الحساب بالورق والدينار:**\n"
                f"👉 <b>{usd_bills} ورقة و {rem_iqd:,.0f} دينار</b>\n"
                "━━━━━━━━━━━━━━━━━\n"
                f"🆔 رقم يوزر الصائغ: <code>{user_id}</code>\n"
                "🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! 💛"
            )
            USER_STATE.pop(user_id, None)
            bot.send_message(message.chat.id, invoice, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        except:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال وزن غرامات صحيح (رقم فقط).")
        return

    # معالجة الشراء
    if state == "WAITING_MITQAL_BUY":
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            try:
                mitqals = float(lines[0])
                agreed_p = float(lines[1])
                discount = float(lines[2]) # قيمة الخصم (تقبل 0 بشكل طبيعي جداً وسلس)
                
                prices = utils.get_goldsmith_prices(user_id)
                goldsmith = utils.get_goldsmith(user_id)
                
                total_iqd = (agreed_p - discount) * mitqals
                usd_bills = int(total_iqd // prices['usd_rate'])
                rem_iqd = total_iqd % prices['usd_rate']
                
                invoice = (
                    f"💎 ARAMKY | فرع نواة الذهب 💎\n"
                    f"🏛️ **المحل العامر: {goldsmith['full_name']}**\n"
                    f"🧾 **فاتورة شراء ذهب من زبون**\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"🔷 العيار وطريقة الشراء: عيار {INVOICE_DATA[user_id]['carat']} (حساب بالمثقال)\n"
                    f"⚖️ الوزن المستلم: {mitqals} مثقال\n"
                    f"⚖️ الوزن الإجمالي بالجرام: {(mitqals * 5.0)} غرام\n"
                    f"🔥 خصم الصهر/أجور الجرام: {discount:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"💰 سعر الشراء المعتمد للمثقال: {agreed_p:,.0f} دينار\n"
                    f"💰 سعر غرام الشراء الصافي: {((agreed_p - discount) / 5.0):,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"💵 **المبلغ الكلي المدفوع بالدينار العراقي:**\n"
                    f"👉 <b>{total_iqd:,.0f} دينار</b>\n\n"
                    f"💵 **صافي الحساب بالورق والدينار:**\n"
                    f"👉 <b>{usd_bills} ورقة و {rem_iqd:,.0f} دينار</b>\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"🆔 رقم يوزر الصائغ: <code>{user_id}</code>\n"
                    "🌸 تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير! ✨"
                )
                USER_STATE.pop(user_id, None)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
            except:
                bot.send_message(message.chat.id, "⚠️ تأكد من صحة أرقام الحسابات المرسلة.")
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال الأسطر الثلاثة كاملة للشراء.")
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_"))
def handle_calc_buttons(call):
    user_id = call.from_user.id
    mode = call.data.split("_")[1]
    carat = int(call.data.split("_")[2])
    
    INVOICE_DATA[user_id] = {'carat': carat}
    bot.answer_callback_query(call.id)
    
    if mode == "sell":
        USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
        bot.send_message(call.message.chat.id, f"⚖️ عيار {carat} البيع:\nأرسل الآن وزن الذهب بالغرام فقط (مثال: 4.963):")
    elif mode == "buy":
        USER_STATE[user_id] = "WAITING_MITQAL_BUY"
        bot.send_message(call.message.chat.id, (
            f"📥 عيار {carat} الشراء من زبون:\n"
            "يرجى إرسال تفاصيل الشراء في رسالة واحدة مرتبة عمودياً (3 أسطر):\n\n"
            "1️⃣ عدد المثاقيل\n"
            "2️⃣ سعر مثقال الكسر المتفق عليه\n"
            "3️⃣ خصم أجور الكسر للمثقال (اكتب 0 إذا لا يوجد)"
        ))

if __name__ == "__main__":
    bot.infinity_polling()
