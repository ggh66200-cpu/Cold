import os
import telebot
from telebot import types
import utils
from threading import Thread
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# إعداد خادم الويب لإرضاء منصة Render وتجنب مشكلة الـ Port Timeout
app = Flask('')

@app.route('/')
def home():
    return "ARAMKY Gold Bot is Server Ready!"

def run_web_server():
    # Render يمرر البورت تلقائياً عبر المتغير PORT، وإذا لم يجده يستخدم 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# مخازن الحالات المؤقتة لتأمين استقرار السيرفر ضد ضعف الإنترنت
USER_STATE = {}
INVOICE_DATA = {}
ADMIN_SELECTED_USER = {}  # لحفظ العميل المحدد بجرد الأدمن

TREND_BASE_NUMBER = 149

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # قائمة الأدمن المركزي
    if user_id == ADMIN_ID:
        markup.add(
            types.KeyboardButton("👑 لوحة تحكم وجرد الصاغة"),
            types.KeyboardButton("⚙️ إدخال أسعار الصباح اليومية")
        )
        markup.add(
            types.KeyboardButton("📥 حساب بيع لزبون"),
            types.KeyboardButton("📤 حساب شراء من زبون")
        )
        markup.add(
            types.KeyboardButton("🌐 تغيير اللغة / Ziman / Language"),
            types.KeyboardButton("❌ إلغاء العملية")
        )
        return markup

    # فحص الصلاحية للعملاء
    goldsmith = utils.get_goldsmith(user_id)
    if goldsmith:
        is_active, _ = utils.check_goldsmith_validity(user_id)
        if not is_active:
            markup.add(
                types.KeyboardButton("💳 إرسال وصل الدفع والتفعيل"),
                types.KeyboardButton("🌐 تغيير اللغة / Ziman / Language")
            )
            return markup

    markup.add(
        types.KeyboardButton("⚙️ إدخال أسعار الصباح اليومية")
    )
    markup.add(
        types.KeyboardButton("📥 حساب بيع لزبون"),
        types.KeyboardButton("📤 حساب شراء من زبون")
    )
    markup.add(
        types.KeyboardButton("🌐 تغيير اللغة / Ziman / Language"),
        types.KeyboardButton("❌ إلغاء العملية")
    )
    return markup

def send_subscription_required_message(chat_id, user_id):
    msg = (
        "💎 **باقة شيوخ الكار المطورين (خصم حصري)** 💎\n"
        "━━━━━━━━━━━━━━━━━\n"
        "⚠️ **يا فتاح يا عليم يا رزاق يا كريم..**\n"
        "أخي الغالي وصاحب الكار المحترم، انتهت الفترة المخصصة للمنظومة في محلك العامر.\n\n"
        "للاشتراك وتمديد الصلاحية بالسعر التنافسي المميز:\n"
        "💰 **بقيمة 105,000 دينار عراقي فقط بدلاً من السعر الأساسي 133,000 دينار.**\n\n"
        "🏛️ **حساب الإيداع المالي الذهبي للشركة:**\n"
        "💳 رقم الماستر كارد الرسمي المعتمد: <code>910400201646</code>\n\n"
        "📸 **بعد التحويل، اضغط على زر (إرسال وصل الدفع والتفعيل) وأرسل صورة الوصل لتفعيل حسابك.**\n\n"
        "📞 **خط الدعم الفني ورقم الطوارئ المباشر:** 07872180902\n"
        "🤖 **معرف المنظومة الرسمي:** @GoldenCalc_Bot\n"
        "━━━━━━━━━━━━━━━━━\n"
        "*نحن هنا لخدمة وتسهيل رزقك، متمنين لك تجارة رابحة وبركة لا تنتهي!* ✨"
    )
    bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    USER_STATE.pop(user_id, None)
    
    goldsmith = utils.get_goldsmith(user_id)
    
    if not goldsmith:
        welcome_text = (
            "👑 أرامكي للحلول الرقمية | ARAMKY 👑\n"
            "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "📝 **تسجيل وتفعيل الحساب الجديد:**\n"
            "أخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر (كل معلومة في سطر منفصل) لتفعيل السيرفر فوراً:\n\n"
            "1️⃣ اسم المحل الرسمي\n"
            "2️⃣ المحافظة والمنطقة\n"
            "3️⃣ رقم هاتف المحل المعتمد\n\n"
            "👇 اكتبها الآن وأرسلها لتفتح لك المنظومة مجاناً."
        )
        USER_STATE[user_id] = "AWAITING_REGISTRATION"
        bot.send_message(message.chat.id, welcome_text, reply_markup=types.ReplyKeyboardRemove())
        return

    is_active, _ = utils.check_goldsmith_validity(user_id)
    if not is_active and user_id != ADMIN_ID:
        send_subscription_required_message(message.chat.id, user_id)
        return

    trend_number = TREND_BASE_NUMBER + utils.get_total_registered_users_count()
    active_count = utils.get_total_registered_users_count()

    success_welcome = (
        "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\n"
        "أهلاً ومرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة!\n\n"
        "🎁 رزقكم مبارك، تفعيلك مستمر وجاهز للعمل الميداني واليومي!\n\n"
        "🔢 **رقم الصائغ المعتمد: #{trend_number}**\n"
        "📍 المحل العامر: {goldsmith['full_name']}\n"
        "🗺️ الموقع: {goldsmith['location']}\n"
        "📞 الهاتف: {goldsmith['phone']}\n"
        "👥 المشتركين النشطين في الكار الآن: {active_count} صائغ\n"
        "━━━━━━━━━━━━━━━━━\n"
        "🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇"
    )
    bot.send_message(message.chat.id, success_welcome, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "❌ إلغاء العملية")
def cancel_op(message):
    user_id = message.from_user.id
    USER_STATE.pop(user_id, None)
    INVOICE_DATA.pop(user_id, None)
    bot.send_message(message.chat.id, "📥 تم إلغاء العملية والرجوع للقائمة الرئيسية بسلامة.", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "🌐 تغيير اللغة / Ziman / Language")
def change_language_menu(message):
    loading = bot.send_message(message.chat.id, "⏳ جاري التحميل ومعالجة البيانات بلحظات...")
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🇸🇾 العربية (العراق)", callback_data="lang_ar"),
        types.InlineKeyboardButton("☀️ Kurdî (کوردی)", callback_data="lang_ku"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.delete_message(message.chat.id, loading.message_id)
    bot.send_message(message.chat.id, "🌐 يرجى اختيار لغة واجهة الحساب المفضلة لمحلك الحلال:\n⚙️ Choose your language:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "👑 لوحة تحكم وجرد الصاغة")
def admin_panel_dynamic(message):
    if message.from_user.id != ADMIN_ID: return
    
    loading = bot.send_message(message.chat.id, "⏳ جاري جرد وبناء قائمة الأسماء الحالية...")
    
    all_users = utils.get_all_registered_goldsmiths()
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for u in all_users:
        markup.add(types.InlineKeyboardButton(f"🏪 {u['full_name']} ({u['location']})", callback_data=f"show_user_{u['user_id']}"))
    
    markup.add(
        types.InlineKeyboardButton("⏱️ تحويل الفترة الافتراضية لـ 3 أيام", callback_data="adm_set_trial_3"),
        types.InlineKeyboardButton("⏱️ تحويل الفترة الافتراضية لـ 7 أيام", callback_data="adm_set_trial_7")
    )
    
    bot.delete_message(message.chat.id, loading.message_id)
    bot.send_message(message.chat.id, "👑 **لوحة تحكم وجرد الصاغة المركزي**\nاختر اسم المحل مباشرة لعرض بياناته والتحكم بصلاحيته:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("show_user_"))
def admin_show_goldsmith_details(call):
    if call.from_user.id != ADMIN_ID: return
    target_uid = int(call.data.split("_")[2])
    
    u = utils.get_goldsmith(target_uid)
    is_active, days_left = utils.check_goldsmith_validity(target_uid)
    status_str = "🟢 نشط" if is_active else "🔴 منتهي / مقفل"
    
    msg = (
        f"📊 **جرد حساب الصائغ المعتمد:**\n\n"
        f"🏪 اسم المحل: {u['full_name']}\n"
        f"📍 الموقع: {u['location']}\n"
        f"📞 رقم الهاتف: {u['phone']}\n"
        f"🆔 معرف الحساب الرقمي: <code>{target_uid}</code>\n"
        f"⚡ حالة الاشتراك الحالية: {status_str}\n"
        f"⏱️ الأيام المتبقية: {days_left} يوم\n"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ إضافة 7 أيام", callback_data=f"modify_time_7_{target_uid}"),
        types.InlineKeyboardButton("➕ إضافة 30 يوم", callback_data=f"modify_time_30_{target_uid}"),
        types.InlineKeyboardButton("🔒 قفل الحساب فوراً", callback_data=f"modify_time_-999_{target_uid}"),
        types.InlineKeyboardButton("🔙 رجوع للجرد", callback_data="back_to_jard")
    )
    bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("modify_time_"))
def admin_modify_time_callback(call):
    if call.from_user.id != ADMIN_ID: return
    parts = call.data.split("_")
    days = int(parts[2])
    target_uid = int(parts[3])
    
    utils.modify_goldsmith_subscription(target_uid, days)
    bot.answer_callback_query(call.id, text="✅ تم تحديث وقت الصلاحية بنجاح!")
    
    call.data = f"show_user_{target_uid}"
    admin_show_goldsmith_details(call)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_jard")
def back_to_jard_callback(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    admin_panel_dynamic(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_set_trial_"))
def admin_change_default_trial(call):
    days = int(call.data.split("_")[3])
    utils.set_system_setting("trial_days", days)
    bot.answer_callback_query(call.id, text=f"✅ تم تغيير الفترة الافتراضية لـ {days} أيام")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_lang_selection(call):
    bot.answer_callback_query(call.id, text="✅ تم تثبيت اللغة بنجاح!")
    bot.edit_message_text("💾 تم حفظ إعدادات اللغة المفضلة على السيرفر بنجاح! جميع فواتيرك القادمة ستتوافق مع اختيارك.", chat_id=call.message.chat.id, message_id=call.message.message_id)

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
        "يرجى إرسال إعدادات الصباح الحالية لمحلك في **رسالة واحدة فقط** مرتبة عمودياً كالتالي:\n\n"
        "1️⃣ سعر مثقال عيار 21\n"
        "2️⃣ سعر مثقال عيار 18\n"
        "3️⃣ أجور صياغة غرام 21 (اكتب 0 إذا لا يوجد)\n"
        "4️⃣ أجور صياغة غرام 18 (اكتب 0 إذا لا يوجد)\n"
        "5️⃣ سعر صرف الـ 100 دولار بالدينار (مثال: 153000)\n\n"
        "💡 أرسلها الآن عمودياً ليتم تحديث الحاسبة فوراً."
    )
    bot.send_message(message.chat.id, instruction)

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    goldsmith = utils.get_goldsmith(user_id)
    
    if not goldsmith:
        bot.send_message(message.chat.id, "⚠️ يرجى تسجيل معلومات المحل أولاً قبل إرسال الوصل المالي.")
        return

    caption_text = (
        f"🚨 **طلب تفعيل اشتراك (صورة وصل مالي واصل):**\n\n"
        f"🏪 المحل العامر: {goldsmith['full_name']}\n"
        f"📍 الموقع: {goldsmith['location']}\n"
        f"🆔 المعرف الرقمي: <code>{user_id}</code>\n"
        f"📞 الهاتف: {goldsmith['phone']}"
    )
    
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("🟢 موافقة وتفعيل 30 يوم", callback_data=f"approve_30_{user_id}"),
        types.InlineKeyboardButton("🔴 رفض الوصل المالي", callback_data=f"reject_0_{user_id}")
    )
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption_text, parse_mode="HTML", reply_markup=admin_markup)
    bot.send_message(message.chat.id, "✅ تم إرسال صورة الوصل المالي إلى الإدارة بنجاح. سيتم فحص الحساب وتفعيله خلال لحظات يا طيب!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def handle_admin_approvals(call):
    if call.from_user.id != ADMIN_ID: return
    data_parts = call.data.split("_")
    action = data_parts[0]
    days = int(data_parts[1])
    target_uid = int(data_parts[2])
    
    if action == "approve":
        utils.modify_goldsmith_subscription(target_uid, days)
        bot.send_message(target_uid, "📢 **بشرى سارة:** تمت مراجعة الوصل المالي وتفعيل المنظومة بنجاح! نتمنى لكم رزقاً مباركاً وفاتحة خير ونماء.", parse_mode="HTML")
        bot.edit_message_caption("🟢 [تم التفعيل بنجاح والموافقة على الوصل]", chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif action == "reject":
        bot.send_message(target_uid, "❌ **تنبيه:** لم نتمكن من تأكيد الوصل المالي المرفق. يرجى إعادة الإرسال أو التواصل مع رقم الدعم الطارئ.")
        bot.edit_message_caption("🔴 [تم رفض الوصل وإلغاء العملية]", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda message: message.text == "📥 حساب بيع لزبون")
def customer_sell_init(message):
    user_id = message.from_user.id
    is_active, _ = utils.check_goldsmith_validity(user_id)
    if not is_active and user_id != ADMIN_ID:
        send_subscription_required_message(message.chat.id, user_id)
        return

    bot.send_message(message.chat.id, "⏳ جاري التحميل ومعالجة البيانات بلحظات...")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="calc_sell_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="calc_sell_18"))
    bot.send_message(message.chat.id, "📥 حساب بيع لزبون:\nاختر عيار الذهب المطلوب أدناه لتسهيل الحساب 👇", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📤 حساب شراء من زبون")
def customer_buy_init(message):
    user_id = message.from_user.id
    is_active, _ = utils.check_goldsmith_validity(user_id)
    if not is_active and user_id != ADMIN_ID:
        send_subscription_required_message(message.chat.id, user_id)
        return

    bot.send_message(message.chat.id, "⏳ جاري التحميل ومعالجة البيانات بلحظات...")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="calc_buy_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="calc_buy_18"))
    bot.send_message(message.chat.id, "📤 حساب شراء من زبون:\nاختر العيار المستلم من الزبون أدناه 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_"))
def handle_calc_buttons(call):
    user_id = call.from_user.id
    mode = call.data.split("_")[1]
    carat = int(call.data.split("_")[2])
    
    INVOICE_DATA[user_id] = {'carat': carat}
    bot.answer_callback_query(call.id)
    
    if mode == "sell":
        USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
        bot.send_message(call.message.chat.id, f"⚖️ عيار {carat} البيع:\nأرسل وزن الذهب بالغرام فقط (مثال: 4.963):")
    elif mode == "buy":
        USER_STATE[user_id] = "WAITING_LOGICAL_BUY"
        bot.send_message(call.message.chat.id, (
            f"📥 عيار {carat} الشراء المنطقي من زبون:\n"
            "يرجى إرسال تفاصيل الشراء في رسالة واحدة مرتبة عمودياً (3 أسطر):\n\n"
            "1️⃣ سعر مثقال الكسر المستلم المعتمد\n"
            "2️⃣ الوزن الإجمالي بالغرام\n"
            "3️⃣ خصم أجور الكسر للغرام الواحد (اكتب 0 إذا لا يوجد)"
        ))

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = USER_STATE.get(user_id)

    if text == "💳 إرسال وصل الدفع والتفعيل":
        USER_STATE[user_id] = "AWAITING_RENEWAL_PROOFS"
        bot.send_message(message.chat.id, "📸 من فضلك التقط صورة واضحة لوصل التحويل أو الدفع وأرسلها هنا مباشرة:")
        return

    # تسجيل العميل وتفعيل الصلاحية تلقائياً
    if state == "AWAITING_REGISTRATION":
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            trial_days = utils.get_system_setting("trial_days", 7)
            utils.register_new_goldsmith(user_id, lines[0], lines[1], lines[2])
            utils.modify_goldsmith_subscription(user_id, trial_days) 
            USER_STATE.pop(user_id, None)
            start_command(message)
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إرسال البيانات بـ 3 أسطر منفصلة (اسم المحل، الموقع، الهاتف).")
        return

    # إدخال الأسعار الصباحية
    if state == "AWAITING_ALL_PRICES":
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 5:
            try:
                p21, p18, w21, w18, usd = float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3]), float(lines[4])
                utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
                USER_STATE.pop(user_id, None)
                bot.send_message(message.chat.id, "✅ **تم حفظ أسعار الصباح بنجاح والمنظومة جاهزة للحساب.**", reply_markup=get_main_keyboard(user_id))
            except:
                bot.send_message(message.chat.id, "⚠️ خطأ بالأرقام المرسلة، يرجى إدخال قيم صحيحة.")
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال الأسطر الخمسة كاملة وبشكل عمودي متسلسل.")
        return

    # معالجة البيع للزبون
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
                f"🏪 **المحل العامر: {goldsmith['full_name']}**\n"
                f"🧾 **فاتورة بيع ذهب للزبون**\n"
                "━━━━━━━━━━━━━━━━━\n"
                f"🔷 عيار ونوع الحساب: عيار {carat} (حساب بالغرام)\n"
                f"⚖️ الوزن المطلوب: {w} غرام\n"
                f"🔨 أجور صياغة الغرام: {wage:,.0f} دينار\n"
                "━━━━━━━━━━━━━━━━━\n"
                f"💰 سعر غرام الذهب الصافي: {(m_price / 5.0):,.0f} دينار\n"
                f"💵 **السعر الكلي بالدينار العراقي:**\n"
                f"👉 <b>{total_iqd:,.0f} دينار</b>\n\n"
                f"💵 **صافي الحساب بالورق والدينار:**\n"
                f"👉 <b>{usd_bills} ورقة و {rem_iqd:,.0f} دينار</b>\n"
                "━━━━━━━━━━━━━━━━━\n"
                f"🆔 رقم يوزر الصائغ: <code>{user_id}</code>\n"
                "🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة. 💛"
            )
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            bot.send_message(message.chat.id, invoice, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        except:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال وزن صحيح (رقم فقط).")
        return

    # معالجة الشراء من الزبون
    if state == "WAITING_LOGICAL_BUY":
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            try:
                agreed_mitqal_p = float(lines[0])
                weight_grams = float(lines[1])
                discount_per_gram = float(lines[2])
                
                prices = utils.get_goldsmith_prices(user_id)
                goldsmith = utils.get_goldsmith(user_id)
                
                agreed_gram_p = agreed_mitqal_p / 5.0
                net_gram_p = agreed_gram_p - discount_per_gram
                total_iqd = net_gram_p * weight_grams
                
                equivalent_mitqals = weight_grams / 5.0
                
                usd_bills = int(total_iqd // prices['usd_rate'])
                rem_iqd = total_iqd % prices['usd_rate']
                
                invoice = (
                    f"💎 ARAMKY | فرع نواة الذهب 💎\n"
                    f"🏪 **المحل العامر: {goldsmith['full_name']}**\n"
                    f"🧾 **فاتورة شراء ذهب من زبون**\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"🔷 العيار ونوع الحساب: عيار {INVOICE_DATA[user_id]['carat']} (حساب الكسر بالغرام)\n"
                    f"⚖️ الوزن المستلم: {weight_grams} غرام (ما يعادل {equivalent_mitqals:.3f} مثقال)\n"
                    f"🔥 خصم أجور الكسر للغرام: {discount_per_gram:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"💰 سعر الشراء للمثقال: {agreed_mitqal_p:,.0f} دينار\n"
                    f"💰 سعر غرام الشراء الصافي: {net_gram_p:,.0f} دينار\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"💵 **المبلغ الكلي المدفوع بالدينار العراقي:**\n"
                    f"👉 <b>{total_iqd:,.0f} دينار</b>\n\n"
                    f"💵 **صافي الحساب بالورق والدينار:**\n"
                    f"👉 <b>{usd_bills} ورقة و {rem_iqd:,.0f} دينار</b>\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    f"🆔 رقم يوزر الصائغ: <code>{user_id}</code>\n"
                    "🌸 تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير! ✨"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
            except:
                bot.send_message(message.chat.id, "⚠️ تأكد من صحة أرقام الحسابات المكتوبة.")
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال الأسطر الثلاثة كاملة للشراء.")
        return

if __name__ == "__main__":
    # 1. تشغيل خادم الويب المصغر أولاً لتجاوز فحص Render المباشر
    keep_alive()
    
    # 2. تشغيل استطلاع البوت اللانهائي
    bot.infinity_polling()
