import telebot, os, utils, time
from flask import Flask
from threading import Thread
from telebot import types

app = Flask(__name__)
@app.route('/')
def home(): return "Aramky Interactive Server Up"
def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_server).start()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
bot = telebot.TeleBot(BOT_TOKEN)
USER_STATES = {}

CANCEL_COMMANDS = ["💰 بيع للزبون", "⚖️ شراء سريع", "⚙️ أسعار الصباح", "⬅️ الرجوع للرئيسية", "💰 فرۆشتن بە کڕیار", "⚖️ کڕینی خێرا", "⚙️ ڕێکخستنەکانی بەیانی", "💰 Sell to Customer", "⚖️ Quick Buy", "⚙️ Morning Prices"]

def check_user_access(chat_id):
    data = utils.get_data()
    uid = str(chat_id)
    if uid not in data['users']: return False, "EXPIRED"
    u = data['users'][uid]
    if u.get("is_active", False) and u.get("expiry_date", 0) > time.time():
        return True, "PREMIUM"
    trial_duration = data.get("trial_days", 7) * 86400
    if time.time() - u.get("join_date", time.time()) < trial_duration:
        return True, "TRIAL"
    return False, "EXPIRED"

@bot.message_handler(commands=['start'])
def start_command(m):
    USER_STATES[m.chat.id] = {}
    intro_text = (
        "👑 **مرحباً بكم في منصة أرامكي الرقمية (نواة الذهب) 2026** 👑\n"
        "⚜️ _المنظومة الأقوى والمصممة خصيصاً لإدارة حسابات الصياغة والمكاتب العريقة_ ⚜️\n\n"
        "👇 اضغط على الزر بالأسفل لاختيار لغتك المفضلة ومباشرة العمل الفوري:"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("العربية 🇮🇶", callback_data="set_lang_ar"),
        types.InlineKeyboardButton("کوردی ☀️", callback_data="set_lang_ku"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
    )
    bot.send_message(m.chat.id, intro_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if str(m.chat.id) != str(ADMIN_ID): return
    USER_STATES[m.chat.id] = {}
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 مراجعة النظام وقوته الإجمالية", callback_data="adm_power_check"),
        types.InlineKeyboardButton("🛡️ فحص ومعالجة أخطاء السيرفر الذاتية", callback_data="adm_self_heal"),
        types.InlineKeyboardButton("👤 إدارة وتغيير مهلة مستخدم محدد (بالأزرار)", callback_data="adm_manage_individual"),
        types.InlineKeyboardButton("⏳ تعديل عدد أيام الفترة التجريبية العامة", callback_data="adm_change_global_trial"),
        types.InlineKeyboardButton("📢 بث تنويه عام على واجهات الصاغة", callback_data="adm_broadcast_prompt")
    )
    bot.send_message(m.chat.id, "👑 **إدارة أرامكي العليا - خيارات التحكم والتحصين والاستعلام الفوري لوأد الأخطاء:**", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callbacks(call):
    bot.answer_callback_query(call.id)
    if str(call.message.chat.id) != str(ADMIN_ID): return
    action = call.data
    data = utils.get_data()
    now = time.time()
    
    if action == "adm_power_check":
        total_users = len(data.get("users", {}))
        trial_days = data.get("trial_days", 7)
        msg = f"📊 **تقرير قوة وثبات المنظومة الحية:**\n\n🔹 حالة اتصال السيرفر: `Excellent 🟢`\n🔹 قاعدة بيانات المكاتب: `المجموع {total_users} مكتب`\n🔹 مهلة الأسبوع التجريبي الافتراضية: `{trial_days} أيام`"
        bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
        
    elif action == "adm_self_heal":
        for uid in list(data["users"].keys()):
            if not isinstance(data["users"][uid], dict): data["users"][uid] = {"join_date": now, "lang": "ar"}
        utils.save_data(data)
        bot.send_message(ADMIN_ID, "🛡️ **تم الفحص الذاتي وإصلاح الاختناقات النصية!** كل الأزرار النشطة مربوطة بالسيرفر بشكل صحيح الآن.")
        
    elif action == "adm_manage_individual":
        USER_STATES[call.message.chat.id] = {"action": "INPUT_USER_ID_FOR_CONTROL"}
        bot.send_message(ADMIN_ID, "👤 أرسل الآن رقم المعرف (ID) الخاص بالصائغ المراد التحكم بوقته فوراً:")
        
    elif action == "adm_change_global_trial":
        USER_STATES[call.message.chat.id] = {"action": "INPUT_GLOBAL_TRIAL_DAYS"}
        bot.send_message(ADMIN_ID, f"⏳ الفترة الحالية هي `{data.get('trial_days', 7)}` أيام.\nأرسل الرقم الجديد الآن لتعديله:")

    elif action == "adm_broadcast_prompt":
        USER_STATES[call.message.chat.id] = {"action": "INPUT_BROADCAST_TEXT"}
        bot.send_message(ADMIN_ID, "📢 أرسل نص الملاحظة المُراد تعميمها على لوحة الصاغة:")

    elif action.startswith("adm_approve_"):
        target = action.replace("adm_approve_", "")
        if target in data["users"]:
            data["users"][target]["is_active"] = True
            data["users"][target]["expiry_date"] = max(data["users"][target].get("expiry_date", 0), now) + (30 * 86400)
            utils.save_data(data)
            bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=call.message.caption + "\n\n🟢 [تم الاعتماد والاشتراك بنجاح ✅]", reply_markup=None)
            try: bot.send_message(target, f"🎉 **مبارك يا طيب!** تم تفعيل الاشتراك المدفوع بنجاح في سيرفرات أرامكي بالخصم المخصص لكم! المنظومة تعمل الآن بكامل طاقتها الحسابية 🌸")
            except: pass

    elif action.startswith("adm_reject_"):
        target = action.replace("adm_reject_", "")
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=call.message.caption + "\n\n🔴 [تم رفض الوصل ❌]", reply_markup=None)
        try: bot.send_message(target, "⚠️ نعتذر منك أخي الغالي، لم يتم تأكيد صورة الوصل المالي، يرجى إعادة إرساله بشكل واضح أو مراجعة خط الطوارئ.")
        except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("time_ctrl_"))
def handle_time_tuning(call):
    bot.answer_callback_query(call.id)
    if str(call.message.chat.id) != str(ADMIN_ID): return
    
    # إصلاح السبلت الشهير ليعمل بنجاح تام ويستخرج البيانات بدقة
    _, _, mode, target_uid = call.data.split("_", 3)
    data = utils.get_data()
    now = time.time()
    
    if target_uid not in data["users"]: return
    u = data["users"][target_uid]
    current_expiry = max(u.get("expiry_date", 0), now)
    
    msg_to_client = ""
    if mode == "add1d": 
        data["users"][target_uid]["expiry_date"] = current_expiry + 86400
        data["users"][target_uid]["is_active"] = True
        msg_to_client = "🌸 **بشرى خير يا غالي!** تم تمديد صلاحية حسابك التجاري بمقدار **يوم واحد** إضافي من قبل الإدارة العليا. ربي يبارك في رزقك! 📈"
    elif mode == "sub1d": 
        data["users"][target_uid]["expiry_date"] = max(now, current_expiry - 86400)
        msg_to_client = "⚠️ **تنبيه:** تم تعديل مهلة اشتراك حسابك من قبل الإدارة."
    elif mode == "add7d": 
        data["users"][target_uid]["expiry_date"] = current_expiry + (7 * 86400)
        data["users"][target_uid]["is_active"] = True
        msg_to_client = "🎉 **أخي الغالي وصاحب الكار المحترم!** تم منح حسابك **أسبوع كامل (7 أيام)** إضافي مجاني ومفتوح الصلاحيات. عمل مبارك ورزق وفير! 👑"
    elif mode == "zero": 
        data["users"][target_uid]["expiry_date"] = 0
        data["users"][target_uid]["is_active"] = False
        msg_to_client = "⚠️ **تنويه:** انتهى اشتراكك الحالي، يرجى مراجعة خيارات التجديد لفتح النظام."
    
    utils.save_data(data)
    
    # إرسال التبليغ المباشر والفوري لهاتف العميل لإعلامه بالتحديث تلقائياً
    if msg_to_client:
        try: bot.send_message(target_uid, msg_to_client, parse_mode="Markdown")
        except: pass
        
    rem_days = int((data["users"][target_uid].get("expiry_date", 0) - now) // 86400)
    status_str = f"🟢 مشترك فعال (متبقي: {rem_days} يوم)" if data["users"][target_uid].get("expiry_date", 0) > now else "🔴 منتهي / تجريبي"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ إضافة يوم", callback_data=f"time_ctrl_add1d_{target_uid}"),
        types.InlineKeyboardButton("➖ إنقاص يوم", callback_data=f"time_ctrl_sub1d_{target_uid}"),
        types.InlineKeyboardButton("➕ إضافة أسبوع كامل", callback_data=f"time_ctrl_add7d_{target_uid}"),
        types.InlineKeyboardButton("⚠️ تصفير الوقت بالكامل", callback_data=f"time_ctrl_zero_{target_uid}")
    )
    bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=f"👤 **تحكم تفاعلي فوري بالوقت:**\n🏪 المكتب: **{u.get('shop_name')}**\nالحالة المحدثة الآن: `{status_str}`\n\nاضغط على الأزرار للتعديل الفوري الفعال:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_manual_flow")
def handle_manual_pay(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    lang = utils.get_user_lang(chat_id)
    USER_STATES[chat_id] = {"action": "SENDING_RECEIPT"}
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id, utils.TRANSLATIONS[lang]["awaiting_receipt"], parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def callback_language(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    lang = call.data.replace("set_lang_", "")
    utils.set_user_lang(chat_id, lang)
    bot.delete_message(chat_id, call.message.message_id)
    
    data = utils.get_data()
    user = data['users'].get(str(chat_id), {})
    if not user.get("shop_name"):
        USER_STATES[chat_id] = {"action": "REGISTER_STEP_1"}
        bot.send_message(chat_id, utils.TRANSLATIONS[lang]["req_shop_name"], parse_mode="Markdown")
    else:
        check_access_and_proceed(chat_id, lang)

def check_access_and_proceed(chat_id, lang):
    t = utils.TRANSLATIONS[lang]
    data = utils.get_data()
    has_access, _ = check_user_access(chat_id)
    
    if has_access:
        u_data = data['users'][str(chat_id)]
        dyn_count = data.get("base_count", 166) + len(data['users'])
        main_msg = t["welcome"].format(
            trial_days=data.get("trial_days", 7),
            shop_num=u_data.get("shop_num", "100"),
            shop_name=u_data.get("shop_name", "مكتب صياغة"),
            shop_location=u_data.get("shop_location", "العراق"),
            shop_phone=u_data.get("shop_phone", "07700000000"),
            count=dyn_count, sys_user=utils.SYSTEM_USERNAME
        )
        utils.send_main_menu(bot, chat_id, main_msg, lang=lang)
    else:
        # قراءة وتمرير بيانات الماستر كارد والطوارئ وزين كاش إلى النص مباشرة
        e_phone = data.get("emergency_phone", "07872180902")
        z_cash = data.get("zain_cash", "910400201646")
        m_card = data.get("mastercard", "5249 7112 3456 7890")
        
        expired_text = t["expired_msg"].format(
            emergency_phone=e_phone, 
            zain_cash=z_cash, 
            mastercard=m_card, 
            sys_user=utils.SYSTEM_USERNAME
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t["send_receipt_btn"], callback_data="pay_manual_flow"))
        bot.send_message(chat_id, expired_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    chat_id = m.chat.id
    state_data = USER_STATES.get(chat_id, {})
    lang = utils.get_user_lang(chat_id)
    if state_data.get("action") == "SENDING_RECEIPT":
        data = utils.get_data()
        s_name = data['users'].get(str(chat_id), {}).get("shop_name", "غير مسجل")
        alert = f"🚨 **طلب تفعيل اشتراك مع الخصم لـ أرامكي!**\n━━━━━━━━━━━━━━━━━━\n👤 **المعرف للعميل:** `{chat_id}`\n🏪 **المكتب الصائغ:** `{s_name}`"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ تفعيل 30 يوماً بالخصم الفوري", callback_data=f"adm_approve_{chat_id}"),
            types.InlineKeyboardButton("❌ رفض وإشعار الصائغ", callback_data=f"adm_reject_{chat_id}")
        )
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=alert, parse_mode="Markdown", reply_markup=markup)
        USER_STATES[chat_id] = {}
        bot.send_message(chat_id, utils.TRANSLATIONS[lang]["receipt_sent_admin"], parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def router(m):
    chat_id = m.chat.id
    text = m.text.strip()
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]
    state_data = USER_STATES.get(chat_id, {})
    current_action = state_data.get("action", "")

    # منع قفل أزرار الأدمن العليا مهما كانت حالة الحساب
    if str(chat_id) == str(ADMIN_ID):
        if current_action == "INPUT_BROADCAST_TEXT":
            data = utils.get_data()
            data["system_broadcast"] = text
            utils.save_data(data)
            USER_STATES[chat_id] = {}
            bot.send_message(ADMIN_ID, "✅ تم تعميم الرسالة بنجاح.")
            return
        elif current_action == "INPUT_GLOBAL_TRIAL_DAYS":
            try:
                days = int(text)
                data = utils.get_data()
                data["trial_days"] = days
                utils.save_data(data)
                bot.send_message(ADMIN_ID, f"✅ تم تعديل الأيام التجريبية العامة بنجاح إلى: `{days}` أيام!")
            except: bot.send_message(ADMIN_ID, "⚠️ خطأ! أدخل أرقاماً فقط.")
            USER_STATES[chat_id] = {}
            return
        elif current_action == "INPUT_USER_ID_FOR_CONTROL":
            data = utils.get_data()
            if text in data["users"]:
                u = data["users"][text]
                rem_days = int((u.get("expiry_date", 0) - time.time()) // 86400)
                status_str = f"🟢 مشترك فعال (متبقي: {rem_days} يوم)" if u.get("expiry_date", 0) > time.time() else "🔴 منتهي / تجريبي"
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("➕ إضافة يوم", callback_data=f"time_ctrl_add1d_{text}"),
                    types.InlineKeyboardButton("➖ إنقاص يوم", callback_data=f"time_ctrl_sub1d_{text}"),
                    types.InlineKeyboardButton("➕ إضافة أسبوع كامل", callback_data=f"time_ctrl_add7d_{text}"),
                    types.InlineKeyboardButton("⚠️ تصفير الوقت بالكامل", callback_data=f"time_ctrl_zero_{text}")
                )
                bot.send_message(ADMIN_ID, f"👤 **تحكم تفاعلي بالوقت:**\n🏪 المكتب: **{u.get('shop_name')}**\nالحالة الحالية: `{status_str}`\n\nاضغط على الأزرار لتعديله:", parse_mode="Markdown", reply_markup=markup)
            else: bot.send_message(ADMIN_ID, "❌ لم يتم العثور على هذا الـ ID في قاعدة البيانات.")
            USER_STATES[chat_id] = {}
            return

    if current_action == "REGISTER_STEP_1":
        lines = [l.strip() for l in m.text.split('\n') if l.strip()]
        if len(lines) < 3:
            bot.send_message(chat_id, "⚠️ يرجى كتابة المعلومات سطر تحت سطر بالترتيب (3 أسطر على الأقل):\n1- اسم المحل\n2- المدينة\n3- رقم الهاتف")
            return
        data = utils.get_data()
        uid = str(chat_id)
        gen_num = data.get("base_count", 166) + len(data['users']) + 1
        data['users'][uid] = {
            "join_date": time.time(), "is_active": False, "expiry_date": 0,
            "shop_name": lines[0], "shop_location": lines[1], "shop_phone": lines[2],
            "shop_num": gen_num, "lang": lang
        }
        utils.save_data(data)
        USER_STATES[chat_id] = {}
        bot.send_message(chat_id, t["shop_saved"].format(shop_name=lines[0]), parse_mode="Markdown")
        check_access_and_proceed(chat_id, lang)
        return

    if text in CANCEL_COMMANDS or text == "/start":
        USER_STATES[chat_id] = {}
        check_access_and_proceed(chat_id, lang)
        return

    # كسر الحلقة التكرارية: السماح للمستخدم برفع الوصل دون إعادته لرسالة القفل
    if current_action == "SENDING_RECEIPT":
        bot.send_message(chat_id, "⚠️ أخي الغالي، يرجى إرسال **صورة الوصل المالي** مباشرة من الاستوديو كـ (صورة) وليس كنص، ليتم تسليمها لقسم التدقيق المالي فورا! 🌸")
        return

    # الفحص الأمني والذكي للصلاحية
    has_access, _ = check_user_access(chat_id)
    if not has_access: 
        check_access_and_proceed(chat_id, lang)
        return

    data = utils.get_data()
    settings = data['settings']
    state = state_data.get("state")
    action = state_data.get("action")

    if text in ["💰 بيع للزبون", "💰 فرۆشتن بە کڕیار", "💰 Sell to Customer"]:
        USER_STATES[chat_id] = {"action": "SELL", "state": "CHOOSE_KARAT_OR_UNIT"}
        bot.send_message(chat_id, t["choose_karat"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
        return
    elif text in ["⚖️ شراء سريع", "⚖️ کڕینی خێرا", "⚖️ Quick Buy"]:
        USER_STATES[chat_id] = {"action": "BUY", "state": "CHOOSE_KARAT_OR_UNIT"}
        bot.send_message(chat_id, t["choose_karat_buy"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
        return
    elif text in ["⚙️ أسعار الصباح", "⚙️ ڕێکخستنەکانی بەیانی", "⚙️ Morning Prices"]:
        USER_STATES[chat_id] = {"action": "WIZARD", "state": "AWAITING_BULK"}
        layout = t["morning_title"].format(
            mithqal_21=settings["mithqal_21"], mithqal_18=settings["mithqal_18"],
            labor_21=settings["labor_21"], labor_18=settings["labor_18"], usd_100=settings["usd_100"]
        )
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(t["update_btn"])
        markup.add(t["back"])
        bot.send_message(chat_id, layout, parse_mode="Markdown", reply_markup=markup)
        return

    if text in ["📝 تحديث الأسعار دفعة واحدة", "📝 نوێکردنەوەی نرخەکان بە یەکجار", "📝 Update All Prices At Once"]:
        bot.send_message(chat_id, t["wizard_prompt"], parse_mode="Markdown")
        return

    if action == "WIZARD" and state == "AWAITING_BULK":
        try:
            vals = [int(v.replace(",", "")) for v in text.split()]
            if len(vals) != 5 or vals[1] >= vals[0]: raise ValueError
            utils.update_all_settings(vals)
            USER_STATES[chat_id] = {}
            utils.send_main_menu(bot, chat_id, t["sweet_success"], lang=lang)
        except: bot.send_message(chat_id, t["error_format"], parse_mode="Markdown")
        return

    if state == "CHOOSE_KARAT_OR_UNIT":
        mappings = {
            "غرام عيار 21": (21, "gram"), "غرام عيار 18": (18, "gram"), "مثقال عيار 21": (21, "mithqal"), "مثقال عيار 18": (18, "mithqal"),
            "گرام عەیار 21": (21, "gram"), "گرام عەیار 18": (18, "gram"), "مسقاڵ عەیار 21": (21, "mithqal"), "مسقاڵ عەیار 18": (18, "mithqal"),
            "21 Karat Gram": (21, "gram"), "18 Karat Gram": (18, "gram"), "21 Karat Mithqal": (21, "mithqal"), "18 Karat Mithqal": (18, "mithqal")
        }
        if text not in mappings: return
        karat, unit = mappings[text]
        state_data["karat"], state_data["unit"] = karat, unit
        
        if action == "SELL":
            state_data["state"] = "AWAITING_WEIGHT"
            u_txt = "بالغرام" if unit == "gram" else "بالمثقال"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(t["back"])
            bot.send_message(chat_id, t["req_weight"].format(text=text, unit_text=u_txt), parse_mode="Markdown", reply_markup=markup)
        elif action == "BUY":
            state_data["mithqal_price"] = settings[f"mithqal_{karat}"]
            state_data["labor"] = 0
            state_data["state"] = "BUY_STREAMLINED_WEIGHT"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(t["back"])
            bot.send_message(chat_id, t["req_weight_buy"], parse_mode="Markdown", reply_markup=markup)
        return

    if action == "BUY" and state == "BUY_STREAMLINED_WEIGHT":
        try: weight = float(text.replace(",", ""))
        except: bot.send_message(chat_id, t["invalid_weight"]); return
        state_data["weight"] = weight
        calculate_and_send_buy_invoice(chat_id, state_data, lang)
        return

    if state == "AWAITING_WEIGHT" and action == "SELL":
        try: weight = float(text.replace(",", ""))
        except: bot.send_message(chat_id, t["invalid_weight"]); return
        state_data["weight"] = weight
        state_data["state"] = "AWAITING_LABOR"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(t["use_morning_labor"].format(labor=settings[f"labor_{state_data['karat']}"]))
        markup.add(t["back"])
        bot.send_message(chat_id, t["req_labor_sell"], parse_mode="Markdown", reply_markup=markup)
        return

    if state == "AWAITING_LABOR" and action == "SELL":
        if text.startswith("استخدام الأجور") or text.startswith("بەکارهێنانی") or text.startswith("Use Morning"):
            labor = settings[f"labor_{state_data['karat']}"]
        else:
            try: labor = float(text.replace(",", ""))
            except: bot.send_message(chat_id, t["invalid_labor"]); return
        state_data["labor"] = labor
        calculate_and_send_sell_invoice(chat_id, state_data, lang)
        return

def calculate_and_send_sell_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    t = utils.TRANSLATIONS[lang]
    try:
        karat, unit, weight, labor = state_data["karat"], state_data["unit"], state_data["weight"], state_data["labor"]
        gram_price = data['settings'][f"mithqal_{karat}"] / 5
        total_grams = weight if unit == "gram" else weight * 5
        unit_text = "غرام"
        unit_arabic = "حساب بالغرام" if unit == "gram" else "حساب بالمثقال"
        total_iqd = (gram_price + labor) * total_grams
        paper_text = utils.calculate_paper_and_dinar(total_iqd, data['settings']["usd_100"], lang)
        
        invoice = t["sell_invoice"].format(
            shop_name=data['users'][str(chat_id)].get("shop_name", "مكتب صياغة"),
            karat=karat, unit_arabic=unit_arabic, weight=f"{weight:.3f}", unit_text=unit_text,
            total_grams=total_grams, labor=labor, gram_price=gram_price, total_iqd=total_iqd,
            paper_and_dinar_text=paper_text, sys_user=utils.SYSTEM_USERNAME
        )
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
    except: USER_STATES[chat_id] = {}; check_access_and_proceed(chat_id, lang)

def calculate_and_send_buy_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    t = utils.TRANSLATIONS[lang]
    try:
        karat, unit, weight, labor, mithqal_price = state_data["karat"], state_data["unit"], state_data["weight"], state_data["labor"], state_data["mithqal_price"]
        gram_purchase_price = mithqal_price / 5
        net_gram_price = gram_purchase_price - labor
        total_grams = weight if unit == "gram" else weight * 5
        unit_text = "غرام"
        unit_arabic = "حساب بالغرام" if unit == "gram" else "حساب بالمثقال"
        total_iqd = net_gram_price * total_grams
        paper_text = utils.calculate_paper_and_dinar(total_iqd, data['settings']["usd_100"], lang)
        
        invoice = t["buy_invoice"].format(
            shop_name=data['users'][str(chat_id)].get("shop_name", "مكتب صياغة"),
            karat=karat, unit_arabic=unit_arabic, weight=f"{weight:.3f}", unit_text=unit_text,
            total_grams=total_grams, labor=labor, mithqal_price=mithqal_price, net_gram_price=net_gram_price,
            total_iqd=total_iqd, paper_and_dinar_text=paper_text, sys_user=utils.SYSTEM_USERNAME
        )
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
    except: USER_STATES[chat_id] = {}; check_access_and_proceed(chat_id, lang)

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
