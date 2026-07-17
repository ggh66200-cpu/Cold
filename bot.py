import telebot, os, utils, subscription, time
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

if not BOT_TOKEN or not ADMIN_ID:
    print("❌ Missing Tokens!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
USER_STATES = {}

CANCEL_COMMANDS = [
    "💰 بيع للزبون", "⚖️ شراء من زبون", "⚙️ إعدادات الصباح", "⬅️ الرجوع للرئيسية", "/start",
    "💰 فرۆشتن بە کڕیار", "⚖️ کڕین لە کڕیار", "⚙️ ڕێکخستنەکانی بەیانی", "⬅️ گەڕانەوە بۆ سەرەکی"
]

@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if str(m.chat.id) != str(ADMIN_ID): return
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_stats = types.InlineKeyboardButton("📊 عرض الإحصائيات والأعداد", callback_data="adm_view_stats")
    btn_shops = types.InlineKeyboardButton("🏪 كشف أسماء مكاتب الصاغة", callback_data="adm_view_shops")
    btn_broadcast = types.InlineKeyboardButton("📢 تعميم رسالة تحذير عامة", callback_data="adm_trigger_bc")
    btn_clear_bc = types.InlineKeyboardButton("❌ حذف التنويه العام الحالي", callback_data="adm_clear_bc")
    markup.add(btn_stats, btn_shops, btn_broadcast, btn_clear_bc)
    
    msg = "👑 **أهلاً بك في منظومة التحكم المركزية لـ (حاسبة الصائغ الذكية)**\n\nاختر الإجراء من الأسفل 👇"
    bot.send_message(m.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_callbacks(call):
    if str(call.message.chat.id) != str(ADMIN_ID): return
    action = call.data
    data = utils.get_data()
    now = time.time()
    trial_duration = data.get("trial_days", 7) * 24 * 60 * 60
    
    if action == "adm_view_stats":
        trial_count, premium_count, expired_count = 0, 0, 0
        for uid, u in data['users'].items():
            if not isinstance(u, dict): continue
            is_premium = u.get("is_active", False) and (u.get("expiry_date", 0) > now)
            is_trial = not is_premium and ((now - u.get("join_date", now)) < trial_duration)
            if is_premium: premium_count += 1
            elif is_trial: trial_count += 1
            else: expired_count += 1
            
        stat_msg = (
            f"📊 **إحصائيات المنظومة:**\n━━━━━━━━━━━━━━━━━━\n"
            f"🔹 إجمالي الصاغة: `{len(data['users'])}`\n"
            f"🟢 مشتركين فعالين: `{premium_count}`\n"
            f"⏳ بالفترة المجانية: `{trial_count}`\n"
            f"🔴 منتهية الصلاحية: `{expired_count}`"
        )
        bot.send_message(ADMIN_ID, stat_msg, parse_mode="Markdown")
        
    elif action == "adm_view_shops":
        shop_list = "🏪 **كشف أسماء ومواقع مكاتب الصاغة:**\n━━━━━━━━━━━━━━━━━━\n"
        idx = 1
        for uid, u in data['users'].items():
            if isinstance(u, dict) and u.get("shop_name"):
                status_icon = "🟢" if u.get("is_active", False) and (u.get("expiry_date", 0) > now) else "⏳"
                shop_list += f"{idx}. {status_icon} **{u['shop_name']}** (#{u.get('shop_num','---')}) -> {u.get('shop_location','--')}\n"
                idx += 1
        if idx == 1: shop_list += "لا يوجد مكاتب مسجلة حالياً."
        bot.send_message(ADMIN_ID, shop_list, parse_mode="Markdown")
        
    elif action == "adm_trigger_bc":
        USER_STATES[call.message.chat.id] = {"action": "ADMIN_BROADCAST"}
        bot.send_message(ADMIN_ID, "📢 أرسل نص الملاحظة لتعميمها فوراً:")
    elif action == "adm_clear_bc":
        data["system_broadcast"] = ""
        utils.save_data(data)
        bot.send_message(ADMIN_ID, "✅ تم مسح التنويه العام.")

@bot.message_handler(commands=['start'])
def start(m):
    USER_STATES[m.chat.id] = {}
    welcome_msg = "👑 **مرحباً بك في نظام الصياغة الذكي العراقي**\n👋 بەخێربێن بۆ سیستەمی زیرەکی زێڕینگەری\n\nيرجى اختيار لغتك المفضلة لبدء العمل:\nتکایە زمانەکەت لە خوارەوە هەڵبژێرە:"
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_ar = types.InlineKeyboardButton("العربية 🇮🇶", callback_data="set_lang_ar")
    btn_ku = types.InlineKeyboardButton("کوردی ☀️", callback_data="set_lang_ku")
    markup.add(btn_ar, btn_ku)
    bot.send_message(m.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def callback_language(call):
    chat_id = call.message.chat.id
    lang_code = call.data.replace("set_lang_", "")
    utils.set_user_lang(chat_id, lang_code)
    bot.delete_message(chat_id, call.message.message_id)
    
    data = utils.get_data()
    user = data['users'].get(str(chat_id), {})
    if not user.get("shop_name") or not user.get("shop_location"):
        USER_STATES[chat_id] = {"action": "REGISTER_SHOP"}
        bot.send_message(chat_id, utils.TRANSLATIONS[lang_code]["req_shop_name"], parse_mode="Markdown")
    else:
        check_access_and_proceed(chat_id, lang_code)

def check_access_and_proceed(chat_id, lang):
    t = utils.TRANSLATIONS[lang]
    data = utils.get_data()
    has_access, status = subscription.check_user(chat_id)
    
    if has_access:
        user_data = data['users'][str(chat_id)]
        dynamic_count = data.get("base_count", 166) + len(data['users'])
        
        # استدعاء وعرض رقم الصائغ والاسم والموقع ورقم التواصل بالترحيب
        main_welcome = t["welcome"].format(
            shop_num=user_data.get("shop_num", "100"),
            shop_name=user_data.get("shop_name", "مكتب صياغة"),
            shop_location=user_data.get("shop_location", "العراق"),
            shop_phone=user_data.get("shop_phone", "07700000000"),
            count=dynamic_count
        )
        utils.send_main_menu(bot, chat_id, main_welcome, lang=lang)
    else:
        support_phone = data.get("support_phone", "07700000000")
        expired_text = t["expired_msg"].format(support_phone=support_phone)
        markup = types.InlineKeyboardMarkup()
        btn_receipt = types.InlineKeyboardButton(t["send_receipt_btn"], callback_data="pay_manual_flow")
        markup.add(btn_receipt)
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
        shop_name = data['users'].get(str(chat_id), {}).get("shop_name", "غير مسجل")
        admin_alert = f"🚨 **وصل دفع جديد!**\n━━━━━━━━━━━━━━━━━━\n👤 **آيدي:** `{chat_id}`\n🏪 **المحل:** `{shop_name}`"
        markup = types.InlineKeyboardMarkup()
        btn_approve = types.InlineKeyboardButton("✅ تفعيل الحساب يدوياً", callback_data=f"adm_approve_{chat_id}")
        markup.add(btn_approve)
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_alert, parse_mode="Markdown", reply_markup=markup)
        USER_STATES[chat_id] = {}
        bot.send_message(chat_id, utils.TRANSLATIONS[lang]["receipt_sent_admin"], parse_mode="Markdown")
        check_access_and_proceed(chat_id, lang)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_approve_"))
def approve_user_payment(call):
    if str(call.message.chat.id) != str(ADMIN_ID): return
    target_uid = call.data.replace("adm_approve_", "")
    data = utils.get_data()
    if target_uid in data["users"]:
        data["users"][target_uid]["is_active"] = True
        data["users"][target_uid]["expiry_date"] = time.time() + (30 * 24 * 60 * 60)
        utils.save_data(data)
        bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption=call.message.caption + "\n\n🟢 [تم تفعيل الصائغ بنجاح ✅]", reply_markup=None)
        try: bot.send_message(target_uid, "🎉 مبارك يا طيب! تم فحص وصل الدفع وتفعيل حسابك بنجاح تام. 🌸")
        except: pass

@bot.message_handler(func=lambda m: True)
def router(m):
    chat_id = m.chat.id
    text = m.text.strip()
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]
    state_data = USER_STATES.get(chat_id, {})

    if str(chat_id) == str(ADMIN_ID) and state_data.get("action") == "ADMIN_BROADCAST":
        data = utils.get_data()
        data["system_broadcast"] = text
        utils.save_data(data)
        USER_STATES[chat_id] = {}
        bot.send_message(ADMIN_ID, "✅ تم تعميم الملاحظة العامة.")
        return

    # 🔥 هنا يتم استقبال وفحص معلومات المحل الـ 3 وحفظ رقم الصائغ دفعة واحدة
    if state_data.get("action") == "REGISTER_SHOP":
        parts = [p.strip() for p in text.split("-")]
        if len(parts) < 3:
            bot.send_message(chat_id, "⚠️ **يرجى إدخال المعلومات كاملة وبنفس الترتيب وبينهما علامة (-)**\n\nمثال صحيح للنسخ والتعديل:\n`صياغة النجاح - بغداد، المنصور - 07701234567`")
            return
        
        data = utils.get_data()
        uid = str(chat_id)
        
        # توليد رقم صائغ رسمي تصاعدي فريد تلقائياً لكل صائغ يسجل
        generated_num = data.get("base_count", 166) + len(data['users']) + 1
        
        if uid not in data['users']: data['users'][uid] = {}
        data['users'][uid]["shop_name"] = parts[0]
        data['users'][uid]["shop_location"] = parts[1]
        data['users'][uid]["shop_phone"] = parts[2]
        data['users'][uid]["shop_num"] = generated_num
        
        utils.save_data(data)
        USER_STATES[chat_id] = {}
        bot.send_message(chat_id, t["shop_saved"].format(shop_name=parts[0]), parse_mode="Markdown")
        check_access_and_proceed(chat_id, lang)
        return

    if text in CANCEL_COMMANDS:
        USER_STATES[chat_id] = {}
        if text in ["/start", "⬅️ الرجوع للرئيسية", "⬅️ گەڕانەوە بۆ سەرەکی"]:
            check_access_and_proceed(chat_id, lang)
            return
        elif text in ["💰 بيع للزبون", "💰 فرۆشتن بە کڕیار"]:
            USER_STATES[chat_id] = {"action": "SELL", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(chat_id, t["choose_karat"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
            return
        elif text in ["⚖️ شراء من زبون", "⚖️ کڕین لە کڕیار"]:
            USER_STATES[chat_id] = {"action": "BUY", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(chat_id, t["choose_karat_buy"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
            return
        elif text in ["⚙️ إعدادات الصباح", "⚙️ ڕێکخستنەکانی بەیانی"]:
            data = utils.get_data()
            settings = data['settings']
            USER_STATES[chat_id] = {"action": "WIZARD", "state": "AWAITING_BULK"}
            morning_layout = t["morning_title"].format(
                mithqal_21=settings["mithqal_21"], mithqal_18=settings["mithqal_18"],
                labor_21=settings["labor_21"], labor_18=settings["labor_18"], usd_100=settings["usd_100"]
            )
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["update_btn"])
            markup.add(t["back"])
            bot.send_message(chat_id, morning_layout, parse_mode="Markdown", reply_markup=markup)
            return

    has_access, _ = subscription.check_user(chat_id)
    if not has_access:
        check_access_and_proceed(chat_id, lang)
        return

    if not state_data:
        check_access_and_proceed(chat_id, lang)
        return

    action = state_data.get("action")
    state = state_data.get("state")
    data = utils.get_data()
    settings = data['settings']

    if text in ["📝 تحديث الأسعار دفعة واحدة", "📝 نوێکردنەوەی نرخەکان بە یەکجار"]:
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
            "غرام عيار 21": (21, "gram"), "غرام عيار 18": (18, "gram"),
            "مثقال عيار 21": (21, "mithqal"), "مثقال عيار 18": (18, "mithqal"),
            "گرام عەیار 21": (21, "gram"), "گرام عەیار 18": (18, "gram"),
            "مسقاڵ عەیار 21": (21, "mithqal"), "مسقاڵ عەیار 18": (18, "mithqal")
        }
        if text not in mappings: return
        karat, unit = mappings[text]
        state_data["karat"] = karat
        state_data["unit"] = unit
        
        if action == "SELL":
            state_data["state"] = "AWAITING_WEIGHT"
            unit_text = "بالغرام" if unit == "gram" else "بالمثقال" if lang=='ar' else "بە گرام" if unit=="gram" else "بە مسقاڵ"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_weight"].format(text=text, unit_text=unit_text), parse_mode="Markdown", reply_markup=markup)
        elif action == "BUY":
            state_data["state"] = "AWAITING_MITHQAL_PRICE"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["use_morning_price"].format(price=settings[f"mithqal_{karat}"]))
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_price_buy"].format(text=text), parse_mode="Markdown", reply_markup=markup)
        return

    if state == "AWAITING_MITHQAL_PRICE" and action == "BUY":
        if text.startswith("استخدام السعر") or text.startswith("بەکارهێنانی"): price = settings[f"mithqal_{state_data['karat']}"]
        else:
            try: price = float(text.replace(",", ""))
            except: bot.send_message(chat_id, t["invalid_price"]); return
        state_data["mithqal_price"] = price
        state_data["state"] = "AWAITING_LABOR"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("0")
        markup.add(t["back"])
        bot.send_message(chat_id, t["req_labor_buy"], parse_mode="Markdown", reply_markup=markup)
        return

    if state == "AWAITING_LABOR":
        if action == "SELL":
            if text.startswith("استخدام الأجور") or text.startswith("بەکارهێنانی"): labor = settings[f"labor_{state_data['karat']}"]
            else:
                try: labor = float(text.replace(",", ""))
                except: bot.send_message(chat_id, t["invalid_labor"]); return
            state_data["labor"] = labor
            calculate_and_send_sell_invoice(chat_id, state_data, lang)
        elif action == "BUY":
            try: labor = float(text.replace(",", ""))
            except: bot.send_message(chat_id, t["invalid_labor"]); return
            state_data["labor"] = labor
            state_data["state"] = "AWAITING_WEIGHT"
            unit_text = "بالغرام" if state_data["unit"] == "gram" else "بالمثقال" if lang=='ar' else "بە گرام" if state_data["unit"]=="gram" else "بە مسقاڵ"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_weight_buy"].format(unit_text=unit_text), parse_mode="Markdown", reply_markup=markup)
        return

    if state == "AWAITING_WEIGHT":
        try: weight = float(text.replace(",", ""))
        except: bot.send_message(chat_id, t["invalid_weight"]); return
        state_data["weight"] = weight
        if action == "SELL":
            state_data["state"] = "AWAITING_LABOR"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["use_morning_labor"].format(labor=settings[f"labor_{state_data['karat']}"]))
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_labor_sell"], parse_mode="Markdown", reply_markup=markup)
        elif action == "BUY":
            calculate_and_send_buy_invoice(chat_id, state_data, lang)
        return

def calculate_and_send_sell_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    t = utils.TRANSLATIONS[lang]
    try:
        karat, unit, weight, labor = state_data["karat"], state_data["unit"], state_data["weight"], state_data["labor"]
        gram_price = data['settings'][f"mithqal_{karat}"] / 5
        total_grams = weight if unit == "gram" else weight * 5
        unit_text = "غرام" if lang=='ar' else "گرام"
        unit_arabic = "حساب بالغرام" if unit == "gram" else "حساب بالمثقال"
        total_iqd = (gram_price + labor) * total_grams
        paper_text = utils.calculate_paper_and_dinar(total_iqd, data['settings']["usd_100"], lang)
        
        invoice = t["sell_invoice"].format(
            shop_name=data['users'][str(chat_id)].get("shop_name", "مكتب الصياغة"),
            karat=karat, unit_arabic=unit_arabic, weight=f"{weight:.3f}", unit_text=unit_text,
            total_grams=total_grams, labor=labor, gram_price=gram_price, total_iqd=total_iqd, paper_and_dinar_text=paper_text
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
        unit_text = "غرام" if lang=='ar' else "گرام"
        unit_arabic = "حساب بالغرام" if unit == "gram" else "حساب بالمثقال"
        total_iqd = net_gram_price * total_grams
        paper_text = utils.calculate_paper_and_dinar(total_iqd, data['settings']["usd_100"], lang)
        
        invoice = t["buy_invoice"].format(
            shop_name=data['users'][str(chat_id)].get("shop_name", "مكتب الصياغة"),
            karat=karat, unit_arabic=unit_arabic, weight=f"{weight:.3f}", unit_text=unit_text,
            total_grams=total_grams, labor=labor, mithqal_price=mithqal_price, net_gram_price=net_gram_price, total_iqd=total_iqd, paper_and_dinar_text=paper_text
        )
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
    except: USER_STATES[chat_id] = {}; check_access_and_proceed(chat_id, lang)

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
