import telebot, os, utils, time
from flask import Flask
from threading import Thread
from telebot import types

app = Flask(__name__)
@app.route('/')
def home(): return "Active"
def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_server).start()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')

bot = telebot.TeleBot(BOT_TOKEN)
USER_STATES = {}

CANCEL_COMMANDS = [
    "💰 بيع للزبون", "⚖️ شراء سريع", "⚙️ أسعار الصباح", "⬅️ الرجوع للرئيسية", "/start",
    "💰 فرۆشتن بە کڕیار", "⚖️ کڕینی خێرا", "⚙️ ڕێکخستنەکانی بەیانی", "⬅️ گەڕانەوە بۆ سەرەکی",
    "💰 Sell to Customer", "⚖️ Quick Buy", "⚙️ Morning Prices", "⬅️ Back to Main"
]

def check_user_access(chat_id):
    data = utils.get_data()
    uid = str(chat_id)
    if uid not in data['users']: return False, "EXPIRED"
    u = data['users'][uid]
    if u.get("is_active", False) and u.get("expiry_date", 0) > time.time():
        return True, "PREMIUM"
    trial_duration = data.get("trial_days", 7) * 24 * 60 * 60
    if time.time() - u.get("join_date", time.time()) < trial_duration:
        return True, "TRIAL"
    return False, "EXPIRED"

# لوحة التحكم الخارقة للآدمن لقراءة المكاتب والتعديل الفردي والجمعي بالساعات والأيام
@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if str(m.chat.id) != str(ADMIN_ID): return
    USER_STATES[m.chat.id] = {}
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 إحصائيات المنظومة العامة", callback_data="adm_stats"),
        types.InlineKeyboardButton("🏪 كشف المكاتب وحالة الاشتراكات", callback_data="adm_shops"),
        types.InlineKeyboardButton("👤 التحكم بحساب عميل محدد (ID)", callback_data="adm_control_user"),
        types.InlineKeyboardButton("➕ إضافة وقت لجميع المشتركين معاً (جمعي)", callback_data="adm_add_bulk"),
        types.InlineKeyboardButton("📢 بث تنويه عام على واجهات الصاغة", callback_data="adm_bc"),
        types.InlineKeyboardButton("❌ إزالة التنويه الحالي", callback_data="adm_clear_bc")
    )
    bot.send_message(m.chat.id, "👑 **لوحة تحكم الإدارة العليا لأرامكي (نواة الذهب)**\nتحكم بالكامل في الأيام، الساعات، الاشتراكات الفردية والجمعية:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_clicks(call):
    if str(call.message.chat.id) != str(ADMIN_ID): return
    action = call.data
    data = utils.get_data()
    now = time.time()
    
    if action == "adm_stats":
        t_count, p_count, e_count = 0, 0, 0
        trial_dur = data.get("trial_days", 7) * 86400
        for uid, u in data['users'].items():
            if not isinstance(u, dict): continue
            if u.get("is_active", False) and u.get("expiry_date", 0) > now: p_count += 1
            elif (now - u.get("join_date", now)) < trial_dur: t_count += 1
            else: e_count += 1
        bot.send_message(ADMIN_ID, f"📊 **تقرير الحسابات الحالي:**\n\n🟢 بريميوم فعال: `{p_count}`\n⏳ فترة تجريبية: `{t_count}`\n🔴 منتهي الصلاحية: `{e_count}`\n\nإجمالي المكاتب المسجلة: `{len(data['users'])}`", parse_mode="Markdown")

    elif action == "adm_shops":
        lines = "🏪 **كشف المشتركين وتفاصيل انتهاء الصلاحية:**\n━━━━━━━━━━━━━━━━━━\n"
        for uid, u in data['users'].items():
            if not isinstance(u, dict) or "shop_name" not in u: continue
            exp = u.get("expiry_date", 0)
            if u.get("is_active", False) and exp > now:
                rem_days = int((exp - now) // 86400)
                rem_hours = int(((exp - now) % 86400) // 3600)
                status = f"🟢 فعال بريميوم (باقي: {rem_days} يوم و {rem_hours} ساعة)"
            else:
                status = "🔴 منتهي الاشتراك / تجريبي"
            lines += f"🆔 `{uid}` | **{u['shop_name']}**\n📞 {u.get('shop_phone','--')} | {status}\n\n"
        bot.send_message(ADMIN_ID, lines[:4000], parse_mode="Markdown")

    elif action == "adm_control_user":
        USER_STATES[call.message.chat.id] = {"action": "ADM_REQ_USER_ID"}
        bot.send_message(ADMIN_ID, "👤 أرسل الآن رقم المعرف (ID) الخاص بالعميل الذي تريد فحصه والتحكم بوصل وقته:")

    elif action == "adm_add_bulk":
        USER_STATES[call.message.chat.id] = {"action": "ADM_REQ_BULK_TIME"}
        bot.send_message(ADMIN_ID, "➕ **إضافة وقت جماعي لكافة المشتركين في السيرفر دفعة واحدة**\nأرسل الوقت بالصيغة التالية: الرقم متبوعاً بحرف (d للأيام) أو (h للساعات).\n\n💡 **أمثلة:**\n`5d` لإضافة 5 أيام للجميع\n`12h` لإضافة 12 ساعة للجميع")

    elif action == "adm_bc":
        USER_STATES[call.message.chat.id] = {"action": "ADM_BROADCAST_TEXT"}
        bot.send_message(ADMIN_ID, "📢 أرسل نص الملاحظة المُراد تعميمها على لوحة المفاتيح:")

    elif action == "adm_clear_bc":
        data["system_broadcast"] = ""
        utils.save_data(data)
        bot.send_message(ADMIN_ID, "✅ تم مسح التنويه العام من واجهات المستخدمين.")

    elif action.startswith("adm_approve_"):
        target = action.replace("adm_approve_", "")
        if target in data["users"]:
            data["users"][target]["is_active"] = True
            data["users"][target]["expiry_date"] = max(data["users"][target].get("expiry_date", 0), time.time()) + (30 * 86400)
            utils.save_data(data)
            bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=call.message.caption + "\n\n🟢 [تم التفعيل والترقية بنجاح ✅]", reply_markup=None)
            try: bot.send_message(target, f"🎉 **مبارك يا طيب!** تم فحص وتدقيق الوصل المالي بنجاح، وتم ترقية حسابك وتفعيل النظام بشكل رسمي وآمن في خوادم أرامكي! 🌸\nرابط النظام: {utils.SYSTEM_USERNAME}")
            except: pass

    elif action.startswith("adm_reject_"):
        target = action.replace("adm_reject_", "")
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=call.message.caption + "\n\n🔴 [تم رفض هذا الوصل ❌]", reply_markup=None)
        try: bot.send_message(target, "⚠️ **أخي الغالي صاحب المحل المحترم:**\nنعتذر منك، لم يتم تأكيد صورة هذا الوصل المالي من قبل الإدارة، يرجى إعادة إرسال الوصل الصحيح أو التواصل مع الدعم الفني.")
        except: pass

@bot.message_handler(commands=['start'])
def start(m):
    USER_STATES[m.chat.id] = {}
    welcome_text = (
        "👑 **ARAMKY | أرامكي للحلول الرقمية** 👑\n"
        "⚜️ فرع نواة الذهب لأنظمة الصياغة وحسابات الأسواق ⚜️\n\n"
        "الرجاء اختيار لغتك المفضلة لبدء تشغيل النظام الفوري:\n"
        "تکایە زمانەکەت لە خوارەوە هەڵبژێرە:\n"
        "Please choose your preferred language below:"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("العربية 🇮🇶", callback_data="set_lang_ar"),
        types.InlineKeyboardButton("کوردی ☀️", callback_data="set_lang_ku"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
    )
    bot.send_message(m.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def callback_language(call):
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
    has_access, status_type = check_user_access(chat_id)
    
    if has_access:
        u_data = data['users'][str(chat_id)]
        dyn_count = data.get("base_count", 166) + len(data['users'])
        
        main_msg = t["welcome"].format(
            shop_num=u_data.get("shop_num", "100"),
            shop_name=u_data.get("shop_name", "مكتب صياغة"),
            shop_location=u_data.get("shop_location", "العراق"),
            shop_phone=u_data.get("shop_phone", "07700000000"),
            count=dyn_count,
            sys_user=utils.SYSTEM_USERNAME
        )
        utils.send_main_menu(bot, chat_id, main_msg, lang=lang)
    else:
        s_phone = data.get("support_phone", "07872180902")
        expired_text = t["expired_msg"].format(support_phone=s_phone, sys_user=utils.SYSTEM_USERNAME)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t["send_receipt_btn"], callback_data="pay_manual_flow"))
        bot.send_message(chat_id, expired_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_manual_flow")
def handle_manual_pay(call):
    chat_id = call.message.chat.id
    lang = utils.get_user_lang(chat_id)
    USER_STATES[chat_id] = {"action": "SENDING_RECEIPT"}
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id, utils.TRANSLATIONS[lang]["awaiting_receipt"], parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    chat_id = m.chat.id
    state_data = USER_STATES.get(chat_id, {})
    lang = utils.get_user_lang(chat_id)
    
    if state_data.get("action") == "SENDING_RECEIPT":
        data = utils.get_data()
        s_name = data['users'].get(str(chat_id), {}).get("shop_name", "غير مسجل")
        alert = f"🚨 **طلب تفعيل اشتراك بريميوم جديد!**\n━━━━━━━━━━━━━━━━━━\n👤 **المعرف الخاص بالعميل:** `{chat_id}`\n🏪 **المكتب الصائغ:** `{s_name}`"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ اعتماد وترقية الحساب", callback_data=f"adm_approve_{chat_id}"),
            types.InlineKeyboardButton("❌ رفض وإشعار الصائغ", callback_data=f"adm_reject_{chat_id}")
        )
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=alert, parse_mode="Markdown", reply_markup=markup)
        
        USER_STATES[chat_id] = {}
        bot.send_message(chat_id, utils.TRANSLATIONS[lang]["receipt_sent_admin"], parse_mode="Markdown")
        return

@bot.message_handler(func=lambda m: True)
def router(m):
    chat_id = m.chat.id
    text = m.text.strip()
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]
    state_data = USER_STATES.get(chat_id, {})
    current_action = state_data.get("action", "")

    # معالجة المدخلات الخاصة بالآدمن
    if str(chat_id) == str(ADMIN_ID):
        if current_action == "ADM_BROADCAST_TEXT":
            data = utils.get_data()
            data["system_broadcast"] = text
            utils.save_data(data)
            USER_STATES[chat_id] = {}
            bot.send_message(ADMIN_ID, "✅ تم تعميم الرسالة بنجاح.")
            return
            
        elif current_action == "ADM_REQ_USER_ID":
            data = utils.get_data()
            if text in data["users"]:
                u = data["users"][text]
                exp = u.get("expiry_date", 0)
                status_str = f"فعال بريميوم لغاية: {time.ctime(exp)}" if exp > time.time() else "منتهي الصلاحية أو تجريبي"
                state_data["target_uid"] = text
                state_data["action"] = "ADM_SET_TIME_FOR_USER"
                bot.send_message(ADMIN_ID, f"🏪 مكتب: **{u.get('shop_name')}**\nحالة الاشتراك الحالي: `{status_str}`\n\nأرسل الآن الوقت المراد إضافته للحساب (مثلاً `10d` لـ 10 أيام أو `12h` لـ 12 ساعة):")
            else:
                bot.send_message(ADMIN_ID, "❌ لم يتم العثور على هذا الـ ID في النظام!")
                USER_STATES[chat_id] = {}
            return

        elif current_action == "ADM_SET_TIME_FOR_USER":
            data = utils.get_data()
            target = state_data.get("target_uid")
            try:
                amount = int(text[:-1])
                unit = text[-1].lower()
                seconds_to_add = (amount * 86400) if unit == 'd' else (amount * 3600) if unit == 'h' else 0
                if seconds_to_add == 0: raise ValueError
                
                data["users"][target]["is_active"] = True
                data["users"][target]["expiry_date"] = max(data["users"][target].get("expiry_date", 0), time.time()) + seconds_to_add
                utils.save_data(data)
                bot.send_message(ADMIN_ID, f"✅ بنجاح، تم إضافة الوقت للمشترك `{target}`.")
                try: bot.send_message(target, "🎉 شريكنا العزيز الطيب، تم تمديد وتحديث فترة صلاحية اشتراككم من قبل الإدارة العليا لأرامكي!")
                except: pass
            except:
                bot.send_message(ADMIN_ID, "⚠️ خطأ في الصيغة! استخدم مثلاً 5d أو 12h.")
            USER_STATES[chat_id] = {}
            return

        elif current_action == "ADM_REQ_BULK_TIME":
            data = utils.get_data()
            try:
                amount = int(text[:-1])
                unit = text[-1].lower()
                sec = (amount * 86400) if unit == 'd' else (amount * 3600) if unit == 'h' else 0
                if sec == 0: raise ValueError
                
                for uid in data["users"]:
                    data["users"][uid]["is_active"] = True
                    data["users"][uid]["expiry_date"] = max(data["users"][uid].get("expiry_date", 0), time.time()) + sec
                utils.save_data(data)
                bot.send_message(ADMIN_ID, f"✅ تم بنجاح إضافة `{text}` كهدية لجميع المشتركين في قاعدة البيانات!")
            except:
                bot.send_message(ADMIN_ID, "⚠️ صيغة خاطئة! يرجى المحاولة مجدداً.")
            USER_STATES[chat_id] = {}
            return

    # التسجيل التتابعي (شيء تحت شيء مرتب جداً ومبسط)
    if current_action.startswith("REGISTER_STEP_"):
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

    if text in CANCEL_COMMANDS:
        USER_STATES[chat_id] = {}
        if text in ["/start", "⬅️ الرجوع للرئيسية", "⬅️ گەڕانەوە بۆ سەرەکی", "⬅️ Back to Main"]:
            check_access_and_proceed(chat_id, lang)
            return
        elif text in ["💰 بيع للزبون", "💰 فرۆشتن بە کڕیار", "💰 Sell to Customer"]:
            USER_STATES[chat_id] = {"action": "SELL", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(chat_id, t["choose_karat"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
            return
        elif text in ["⚖️ شراء سريع", "⚖️ کڕینی خێرا", "⚖️ Quick Buy"]:
            USER_STATES[chat_id] = {"action": "BUY", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(chat_id, t["choose_karat_buy"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
            return
        elif text in ["⚙️ أسعار الصباح", "⚙️ ڕێکخستنەکانی بەیانی", "⚙️ Morning Prices"]:
            data = utils.get_data()
            s = data['settings']
            USER_STATES[chat_id] = {"action": "WIZARD", "state": "AWAITING_BULK"}
            layout = t["morning_title"].format(
                mithqal_21=s["mithqal_21"], mithqal_18=s["mithqal_18"],
                labor_21=s["labor_21"], labor_18=s["labor_18"], usd_100=s["usd_100"]
            )
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["update_btn"])
            markup.add(t["back"])
            bot.send_message(chat_id, layout, parse_mode="Markdown", reply_markup=markup)
            return

    has_access, _ = check_user_access(chat_id)
    if not has_access:
        check_access_and_proceed(chat_id, lang)
        return

    state = state_data.get("state")
    action = state_data.get("action")
    data = utils.get_data()
    settings = data['settings']

    if text in ["📝 تحديث الأسعار دفعة واحدة", "📝 نوێکردنەوەی نرخەکان بە یەکجار", "📝 Update All Prices At Once"]:
        bot.send_message(chat_id, t["wizard_prompt"], parse_mode="Markdown")
        return

    if action == "WIZARD" and state == "AWAITING_BULK":
        try:
            vals = [int(v.replace(",", "")) for v in text.split()]
            if len(vals) != 5: raise ValueError
            if vals[1] >= vals[0]: raise ValueError
            utils.update_all_settings(vals)
            USER_STATES[chat_id] = {}
            utils.send_main_menu(bot, chat_id, t["sweet_success"], lang=lang)
        except:
            bot.send_message(chat_id, t["error_format"], parse_mode="Markdown")
        return

    if state == "CHOOSE_KARAT_OR_UNIT":
        mappings = {
            "غرام عيار 21": (21, "gram"), "غرام عيار 18": (18, "gram"), "مثقال عيار 21": (21, "mithqal"), "مثقال عيار 18": (18, "mithqal"),
            "گرام عەیار 21": (21, "gram"), "گرام عەیار 18": (18, "gram"), "مسقاڵ عەیار 21": (21, "mithqal"), "مسقاڵ عەیار 18": (18, "mithqal"),
            "21 Karat Gram": (21, "gram"), "18 Karat Gram": (18, "gram"), "21 Karat Mithqal": (21, "mithqal"), "18 Karat Mithqal": (18, "mithqal")
        }
        if text not in mappings: return
        karat, unit = mappings[text]
        state_data["karat"] = karat
        state_data["unit"] = unit
        
        if action == "SELL":
            state_data["state"] = "AWAITING_WEIGHT"
            u_txt = "بالغرام" if unit == "gram" else "بالمثقال"
            if lang == 'ku': u_txt = "بە گرام" if unit == "gram" else "بە مسقاڵ"
            elif lang == 'en': u_txt = "in Grams" if unit == "gram" else "in Mithqals"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_weight"].format(text=text, unit_text=u_txt), parse_mode="Markdown", reply_markup=markup)
        elif action == "BUY":
            # دمج وتبسيط عملية الشراء: نقفز فوراً إلى طلب الوزن واعتماد السعر الصباحي كخيار افتراضي ذكي
            state_data["mithqal_price"] = settings[f"mithqal_{karat}"]
            state_data["labor"] = 0 # القيمة الافتراضية الصفرية
            state_data["state"] = "BUY_STREAMLINED_WEIGHT"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_weight_buy"], parse_mode="Markdown", reply_markup=markup)
        return

    if action == "BUY" and state == "BUY_STREAMLINED_WEIGHT":
        try: weight = float(text.replace(",", ""))
        except: bot.send_message(chat_id, t["invalid_weight"]); return
        state_data["weight"] = weight
        calculate_and_send_buy_invoice(chat_id, state_data, lang)
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

def calculate_and_send_sell_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    t = utils.TRANSLATIONS[lang]
    try:
        karat, unit, weight, labor = state_data["karat"], state_data["unit"], state_data["weight"], state_data["labor"]
        gram_price = data['settings'][f"mithqal_{karat}"] / 5
        total_grams = weight if unit == "gram" else weight * 5
        unit_text = "غرام" if lang=='ar' else "گرام" if lang=='ku' else "g"
        unit_arabic = "حساب بالغرام" if unit == "gram" else "حساب بالمثقال"
        total_iqd = (gram_price + labor) * total_grams
        paper_text = utils.calculate_paper_and_dinar(total_iqd, data['settings']["usd_100"], lang)
        
        invoice = t["sell_invoice"].format(
            shop_name=data['users'][str(chat_id)].get("shop_name", "مكتب صياغة"),
            karat=karat, unit_arabic=unit_arabic, weight=f"`{weight:.3f}`", unit_text=unit_text,
            total_grams=total_grams, labor=labor, gram_price=gram_price, total_iqd=total_iqd,
            paper_and_dinar_text=paper_text, sys_user=utils.SYSTEM_USERNAME
        )
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
    except Exception as e: USER_STATES[chat_id] = {}; check_access_and_proceed(chat_id, lang)

def calculate_and_send_buy_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    t = utils.TRANSLATIONS[lang]
    try:
        karat, unit, weight, labor, mithqal_price = state_data["karat"], state_data["unit"], state_data["weight"], state_data["labor"], state_data["mithqal_price"]
        gram_purchase_price = mithqal_price / 5
        net_gram_price = gram_purchase_price - labor
        total_grams = weight if unit == "gram" else weight * 5
        unit_text = "غرام" if lang=='ar' else "گرام" if lang=='ku' else "g"
        unit_arabic = "حساب بالغرام" if unit == "gram" else "حساب بالمثقال"
        total_iqd = net_gram_price * total_grams
        paper_text = utils.calculate_paper_and_dinar(total_iqd, data['settings']["usd_100"], lang)
        
        invoice = t["buy_invoice"].format(
            shop_name=data['users'][str(chat_id)].get("shop_name", "مكتب صياغة"),
            karat=karat, unit_arabic=unit_arabic, weight=f"`{weight:.3f}`", unit_text=unit_text,
            total_grams=total_grams, labor=labor, mithqal_price=mithqal_price, net_gram_price=net_gram_price,
            total_iqd=total_iqd, paper_and_dinar_text=paper_text, sys_user=utils.SYSTEM_USERNAME
        )
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
    except Exception as e: USER_STATES[chat_id] = {}; check_access_and_proceed(chat_id, lang)

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
