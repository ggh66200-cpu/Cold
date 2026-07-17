import telebot, os, utils, subscription, time
from flask import Flask
from threading import Thread
from telebot import types

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active & Secure"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_server).start()

# سحب المفاتيح تلقائياً وآمنياً من بيئة السيرفر (Environment Variables)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID') # آيدي المطور/الأدمن 

if not BOT_TOKEN or not ADMIN_ID:
    print("❌ ERROR: BOT_TOKEN or ADMIN_ID is missing from server environment variables!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

USER_STATES = {}

CANCEL_COMMANDS = [
    "💰 بيع للزبون", "⚖️ شراء من زبون", "⚙️ إعدادات الصباح", "⬅️ الرجوع للرئيسية", "/start",
    "💰 فرۆشتن بە کڕیار", "⚖️ کڕین لە کڕیار", "⚙️ ڕێکخستنەکانی بەیانی", "⬅️ گەڕانەوە بۆ سەرەکی",
    "💰 Sell to Customer", "⚖️ Buy from Customer", "⚙️ Morning Settings", "⬅️ Back to Main"
]

# 📋 لوحة تحكم الأدمن (الماستر)
@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if str(m.chat.id) != str(ADMIN_ID):
        return
    
    data = utils.get_data()
    msg = (
        "👑 **لوحة تحكم إدارة حاسبة الصائغ الذكية**\n\n"
        f"⚙️ عدد المشتركين المسجلين: `{len(data['users'])}`\n"
        f"⏳ فترة التجريب المجاني: `{data.get('trial_days', 7)}` أيام\n"
        f"📞 رقم الدعم الفني: `{data.get('support_phone')}`\n"
        f"📢 التنويه العام الحالي: `{(data.get('system_broadcast') or 'لا يوجد')}`\n\n"
        "إليك العمليات المتاحة للإدارة عبر الأوامر السريعة:\n"
        "✏️ لتغيير فترة التجريب: أرسل `/trial_days [العدد]`\n"
        "✏️ لتغيير رقم الدعم: أرسل `/support_phone [الرقم]`\n"
        "📢 لإضافة رسالة تحذير/ملاحظة عامة: أرسل `/broadcast [الرسالة]`\n"
        "❌ لمسح التنويه العام: أرسل `/clear_broadcast`\n"
        "✅ لتفعيل مشترك يدوياً بالآيدي: أرسل `/activate [ID]`"
    )
    bot.send_message(m.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['trial_days', 'support_phone', 'broadcast', 'activate'])
def admin_actions(m):
    if str(m.chat.id) != str(ADMIN_ID): return
    cmd = m.text.split(maxsplit=1)
    if len(cmd) < 2:
        bot.send_message(m.chat.id, "⚠️ يرجى إدخال القيمة المطلوبة مع الأمر.")
        return
        
    action = cmd[0]
    val = cmd[1].strip()
    data = utils.get_data()
    
    if action == "/trial_days":
        try:
            data["trial_days"] = int(val)
            utils.save_data(data)
            bot.send_message(m.chat.id, f"✅ تم تعديل فترة التجريب المجاني إلى: {val} أيام.")
        except:
            bot.send_message(m.chat.id, "⚠️ يرجى إرسال رقم صحيح.")
            
    elif action == "/support_phone":
        data["support_phone"] = val
        utils.save_data(data)
        bot.send_message(m.chat.id, f"✅ تم حفظ رقم الدعم الفني الجديد: {val}")
        
    elif action == "/broadcast":
        data["system_broadcast"] = val
        utils.save_data(data)
        bot.send_message(m.chat.id, "✅ تم تعميم التنويه العام على جميع حسابات الصاغة بنجاح.")
        
    elif action == "/activate":
        uid = str(val)
        if uid in data["users"]:
            data["users"][uid]["is_active"] = True
            data["users"][uid]["expiry_date"] = time.time() + (30 * 24 * 60 * 60) # شهر واحد
            utils.save_data(data)
            bot.send_message(m.chat.id, f"✅ تم تفعيل العميل {uid} بنجاح لمدة 30 يوم!")
            try:
                bot.send_message(uid, "🎉 **مبارك! تم تفعيل اشتراكك الشهري من قبل الإدارة بالكامل.** ✨")
            except: pass
        else:
            bot.send_message(m.chat.id, "⚠️ لم يتم العثور على هذا الآيدي في السيرفر!")

@bot.message_handler(commands=['clear_broadcast'])
def clear_broadcast(m):
    if str(m.chat.id) != str(ADMIN_ID): return
    data = utils.get_data()
    data["system_broadcast"] = ""
    utils.save_data(data)
    bot.send_message(m.chat.id, "✅ تم حذف الرسالة التحذيرية العامة بنجاح.")


# 🎬 شاشة البداية والتسجيل وفحص الصلاحيات
@bot.message_handler(commands=['start'])
def start(m):
    USER_STATES[m.chat.id] = {}
    
    # خطوة 1: اختيار اللغة عبر أزرار شفافة
    welcome_msg = (
        f"👑 **مرحباً بك في نظام الصياغة الذكي العراقي**\n"
        f"👋 بەخێربێن بۆ سیستەمی زیرەکی زێڕینگەری\n"
        f"🌍 Welcome to the Smart Goldsmith System\n\n"
        f"يرجى اختيار لغتك المفضلة لبدء العمل:\n"
        f"تکایە زمانەکەت لە خوارەوە هەڵبژێرە:\n"
        f"Please select your preferred language below:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_ar = types.InlineKeyboardButton("العربية 🇮🇶", callback_data="set_lang_ar")
    btn_ku = types.InlineKeyboardButton("کوردی ☀️", callback_data="set_lang_ku")
    btn_en = types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
    markup.add(btn_ar, btn_ku, btn_en)
    
    bot.send_message(m.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def callback_language(call):
    chat_id = call.message.chat.id
    lang_code = call.data.replace("set_lang_", "")
    utils.set_user_lang(chat_id, lang_code)
    bot.delete_message(chat_id, call.message.message_id)
    
    data = utils.get_data()
    user = data['users'].get(str(chat_id), {})
    
    # خطوة 2: فحص إذا كان اسم المحل مسجلاً، وإلا نطلبه فوراً
    if not user.get("shop_name"):
        USER_STATES[chat_id] = {"action": "REGISTER_SHOP"}
        bot.send_message(chat_id, utils.TRANSLATIONS[lang_code]["req_shop_name"], parse_mode="Markdown")
    else:
        # فحص الصلاحية والدخول
        check_access_and_proceed(chat_id, lang_code)


def check_access_and_proceed(chat_id, lang):
    t = utils.TRANSLATIONS[lang]
    data = utils.get_data()
    has_access, status = subscription.check_user(chat_id)
    
    if has_access:
        user_data = data['users'][str(chat_id)]
        main_welcome = t["welcome"].format(shop_name=user_data["shop_name"], count=data["total_count"])
        utils.send_main_menu(bot, chat_id, main_welcome, lang=lang)
    else:
        # عرض شاشة انتهاء الاشتراك مع زر الدفع بالماستر كارد
        support_phone = data.get("support_phone", "07700000000")
        expired_text = t["expired_msg"].format(support_phone=support_phone)
        
        markup = types.InlineKeyboardMarkup()
        btn_receipt = types.InlineKeyboardButton(t["send_receipt_btn"], callback_data="pay_manual_flow")
        markup.add(btn_receipt)
        bot.send_message(chat_id, expired_text, parse_mode="Markdown", reply_markup=markup)


# استلام صورة الوصل وإرسالها للأدمن للموافقة
@bot.callback_query_handler(func=lambda call: call.data == "pay_manual_flow")
def handle_manual_pay(call):
    chat_id = call.message.chat.id
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]
    
    USER_STATES[chat_id] = {"action": "SENDING_RECEIPT"}
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id, t["awaiting_receipt"], parse_mode="Markdown")


@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    chat_id = m.chat.id
    state_data = USER_STATES.get(chat_id, {})
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]
    
    if state_data.get("action") == "SENDING_RECEIPT":
        # جلب بيانات المستخدم لتقديمها للإدارة بشكل متناسق
        data = utils.get_data()
        user_info = data['users'].get(str(chat_id), {})
        shop_name = user_info.get("shop_name", "غير مسجل")
        
        # فورورد الوصل للأدمن مع الأزرار التفاعلية
        admin_alert = (
            "🚨 **وصل دفع جديد بانتظار الموافقة!**\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 **آيدي العميل:** `{chat_id}`\n"
            f"🏪 **اسم المحل:** `{shop_name}`\n"
            f"⚙️ **اللغة المستعملة:** `{lang}`\n━━━━━━━━━━━━━━━━━━\n"
            "اضغط على الأزرار أدناه لتفعيل العميل يدوياً فوراً 👇"
        )
        
        markup = types.InlineKeyboardMarkup()
        btn_approve = types.InlineKeyboardButton("✅ تفعيل 30 يوم", callback_data=f"adm_approve_{chat_id}")
        btn_reject = types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"adm_reject_{chat_id}")
        markup.add(btn_approve, btn_reject)
        
        # إرسال الصورة للأدمن
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=admin_alert, parse_mode="Markdown", reply_markup=markup)
        
        # الرد على العميل بكلام طيب
        USER_STATES[chat_id] = {}
        bot.send_message(chat_id, t["receipt_sent_admin"], parse_mode="Markdown")
        check_access_and_proceed(chat_id, lang)


# معالجة قرارات الأدمن من خلال الأزرار التفاعلية للوصل
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_decision(call):
    if str(call.message.chat.id) != str(ADMIN_ID): return
    action_data = call.data.replace("adm_", "")
    
    data = utils.get_data()
    
    if action_data.startswith("approve_"):
        target_uid = action_data.replace("approve_", "")
        if target_uid in data["users"]:
            data["users"][target_uid]["is_active"] = True
            data["users"][target_uid]["expiry_date"] = time.time() + (30 * 24 * 60 * 60)
            utils.save_data(data)
            
            bot.edit_message_caption(
                chat_id=ADMIN_ID,
                message_id=call.message.message_id,
                caption=call.message.caption + "\n\n🟢 **[تمت الموافقة والتفعيل للعميل بنجاح ✅]**",
                reply_markup=None
            )
            try:
                bot.send_message(target_uid, "🎉 **مبارك يا طيب! تم فحص وصل الدفع الخاص بك وتفعيل حسابك بنجاح تام.**\nنتمنى لك عملاً مباركاً وربحاً وفيراً! 🌸")
            except: pass
            
    elif action_data.startswith("reject_"):
        target_uid = action_data.replace("reject_", "")
        bot.edit_message_caption(
            chat_id=ADMIN_ID,
            message_id=call.message.message_id,
            caption=call.message.caption + "\n\n🔴 **[تم رفض طلب الدفع هذا ❌]**",
            reply_markup=None
        )
        try:
            bot.send_message(target_uid, "⚠️ **تنويه من الإدارة:** عذراً أخي الغالي، لم نتمكن من التحقق من وصل التحويل المرسل، يرجى إعادة إرساله بشكل واضح أو مراسلة الدعم الفني مباشرة.")
        except: pass


# الموجه العام للرسائل
@bot.message_handler(func=lambda m: True)
def router(m):
    chat_id = m.chat.id
    text = m.text.strip()
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]

    # 1️⃣ معالجة تسجيل اسم المحل
    state_data = USER_STATES.get(chat_id, {})
    if state_data.get("action") == "REGISTER_SHOP":
        data = utils.get_data()
        data['users'][str(chat_id)]["shop_name"] = text
        utils.save_data(data)
        
        USER_STATES[chat_id] = {}
        bot.send_message(chat_id, t["shop_saved"].format(shop_name=text), parse_mode="Markdown")
        check_access_and_proceed(chat_id, lang)
        return

    # 2️⃣ تصفير والرجوع
    if text in CANCEL_COMMANDS:
        USER_STATES[chat_id] = {}
        if text in ["/start", "⬅️ الرجوع للرئيسية", "⬅️ گەڕانەوە بۆ سەرەکی", "⬅️ Back to Main"]:
            check_access_and_proceed(chat_id, lang)
            return
            
        elif text in ["💰 بيع للزبون", "💰 فرۆشتن بە کڕیار", "💰 Sell to Customer"]:
            USER_STATES[chat_id] = {"action": "SELL", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(chat_id, t["choose_karat"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
            return
            
        elif text in ["⚖️ شراء من زبون", "⚖️ کڕین لە کڕیار", "⚖️ Buy from Customer"]:
            USER_STATES[chat_id] = {"action": "BUY", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(chat_id, t["choose_karat_buy"], parse_mode="Markdown", reply_markup=utils.get_karat_unit_keyboard(lang))
            return

    # فحص الاشتراك للمحافظة على أمان البيانات في العمليات الأخرى
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

    # 3️⃣ تحديث الأسعار الصباحية مع الفحص (18 دائماً أقل من 21)
    if action == "WIZARD" and state == "AWAITING_BULK":
        try:
            vals = [int(v.replace(",", "")) for v in text.split()]
            if len(vals) != 5:
                raise ValueError
            
            # شرط الأمان الذهبي: عيار 18 دائماً سعره أقل من عيار 21
            if vals[1] >= vals[0]:
                raise ValueError("price_validation_failed")
                
            utils.update_all_settings(vals)
            USER_STATES[chat_id] = {}
            utils.send_main_menu(bot, chat_id, t["sweet_success"], lang=lang)
        except:
            bot.send_message(chat_id, t["error_format"], parse_mode="Markdown")
        return

    # 4️⃣ اختيار العيار والوحدة
    if state == "CHOOSE_KARAT_OR_UNIT":
        mapping_ar = {
            "غرام عيار 21": (21, "gram"), "غرام عيار 18": (18, "gram"),
            "مثقال عيار 21": (21, "mithqal"), "مثقال عيار 18": (18, "mithqal")
        }
        mapping_ku = {
            "گرام عەیار 21": (21, "gram"), "گرام عەیار 18": (18, "gram"),
            "مسقاڵ عەیار 21": (21, "mithqal"), "مسقاڵ عەیار 18": (18, "mithqal")
        }
        mapping_en = {
            "Gram Karat 21": (21, "gram"), "Gram Karat 18": (18, "gram"),
            "Mithqal Karat 21": (21, "mithqal"), "Mithqal Karat 18": (18, "mithqal")
        }
        
        all_mappings = {**mapping_ar, **mapping_ku, **mapping_en}
        if text not in all_mappings:
            bot.send_message(chat_id, "⚠️ Choose from the buttons!")
            return
            
        karat, unit = all_mappings[text]
        state_data["karat"] = karat
        state_data["unit"] = unit
        
        if action == "SELL":
            state_data["state"] = "AWAITING_WEIGHT"
            unit_text = "بالغرام" if unit == "gram" else "بالمثقال"
            if lang == "ku": unit_text = "بە گرام" if unit == "gram" else "بە مسقاڵ"
            elif lang == "en": unit_text = "in grams" if unit == "gram" else "in mithqal"
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_weight"].format(text=text, unit_text=unit_text), parse_mode="Markdown", reply_markup=markup)
            
        elif action == "BUY":
            state_data["state"] = "AWAITING_MITHQAL_PRICE"
            morning_price = settings[f"mithqal_{karat}"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["use_morning_price"].format(price=morning_price))
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_price_buy"].format(text=text), parse_mode="Markdown", reply_markup=markup)
        return

    # 5️⃣ استلام سعر شراء المثقال (شراء من زبون)
    if state == "AWAITING_MITHQAL_PRICE" and action == "BUY":
        karat = state_data["karat"]
        morning_price = settings[f"mithqal_{karat}"]
        
        if text.startswith("استخدام السعر") or text.startswith("بەکارهێنانی") or text.startswith("Use Morning"):
            price = morning_price
        else:
            try:
                price = float(text.replace(",", ""))
            except:
                bot.send_message(chat_id, t["invalid_price"])
                return
                
        state_data["mithqal_price"] = price
        state_data["state"] = "AWAITING_LABOR"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("0")
        markup.add(t["back"])
        bot.send_message(chat_id, t["req_labor_buy"], parse_mode="Markdown", reply_markup=markup)
        return

    # 6️⃣ استلام أجور صياغة أو الخصم
    if state == "AWAITING_LABOR":
        karat = state_data["karat"]
        if action == "SELL":
            default_labor = settings[f"labor_{karat}"]
            if text.startswith("استخدام الأجور") or text.startswith("بەکارهێنانی") or text.startswith("Use Morning"):
                labor = default_labor
            else:
                try:
                    labor = float(text.replace(",", ""))
                except:
                    bot.send_message(chat_id, t["invalid_labor"])
                    return
            state_data["labor"] = labor
            calculate_and_send_sell_invoice(chat_id, state_data, lang)
            
        elif action == "BUY":
            try:
                labor = float(text.replace(",", ""))
            except:
                bot.send_message(chat_id, t["invalid_labor"])
                return
            state_data["labor"] = labor
            state_data["state"] = "AWAITING_WEIGHT"
            
            unit_text = "بالغرام" if state_data["unit"] == "gram" else "بالمثقال"
            if lang == "ku": unit_text = "بە گرام" if state_data["unit"] == "gram" else "بە مسقاڵ"
            elif lang == "en": unit_text = "in grams" if state_data["unit"] == "gram" else "in mithqal"
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_weight_buy"].format(unit_text=unit_text), parse_mode="Markdown", reply_markup=markup)
        return

    # 7️⃣ استلام الوزن (3 مراتب عشرية بدون أي تقريب)
    if state == "AWAITING_WEIGHT":
        try:
            weight = float(text.replace(",", ""))
        except:
            bot.send_message(chat_id, t["invalid_weight"])
            return
            
        state_data["weight"] = weight
        if action == "SELL":
            state_data["state"] = "AWAITING_LABOR"
            default_labor = settings[f"labor_{state_data['karat']}"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["use_morning_labor"].format(labor=default_labor))
            markup.add(t["back"])
            bot.send_message(chat_id, t["req_labor_sell"], parse_mode="Markdown", reply_markup=markup)
        elif action == "BUY":
            calculate_and_send_buy_invoice(chat_id, state_data, lang)
        return


# دوال العمليات الحسابية والفواتير (3 مراتب عشرية بالوزن بالكامل)
def calculate_and_send_sell_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    settings = data['settings']
    t = utils.TRANSLATIONS[lang]
    shop_name = data['users'][str(chat_id)].get("shop_name", "مكتب الصياغة")
    
    loading = bot.send_message(chat_id, t["loading_sell"])
    time.sleep(1)
    bot.delete_message(chat_id, loading.message_id)
    
    try:
        karat = state_data["karat"]
        unit = state_data["unit"]
        weight = state_data["weight"]
        labor = state_data["labor"]
        
        mithqal_price = settings[f"mithqal_{karat}"]
        usd_100 = settings["usd_100"]
        
        gram_price = mithqal_price / 5
        
        if unit == "gram":
            total_grams = weight
            unit_text = "غرام" if lang in ["ar", "ku"] else "grams"
            unit_arabic = "حساب بالغرام" if lang == "ar" else ("حساب بە گرام" if lang == "ku" else "Gram Account")
        else:
            total_grams = weight * 5
            unit_text = "مثقال" if lang in ["ar", "ku"] else "mithqal"
            unit_arabic = "حساب بالمثقال" if lang == "ar" else ("حساب بە مسقاڵ" if lang == "ku" else "Mithqal Account")
            
        total_iqd = (gram_price + labor) * total_grams
        paper_and_dinar_text = utils.calculate_paper_and_dinar(total_iqd, usd_100, lang)
        
        # تنسيق وعرض الأوزان بـ .3f لمنع التقريب نهائياً
        invoice = t["sell_invoice"].format(
            shop_name=shop_name,
            karat=karat,
            unit_arabic=unit_arabic,
            weight=f"{weight:.3f}",
            unit_text=unit_text,
            total_grams=total_grams, # تُعرض بقيمتها الحقيقية وبـ 3 مراتب بالأسفل
            labor=labor,
            gram_price=gram_price,
            total_iqd=total_iqd,
            paper_and_dinar_text=paper_and_dinar_text
        )
        
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
    except Exception as e:
        print(f"Sell Calc Error: {e}")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "⚠️ Error.", lang=lang)

def calculate_and_send_buy_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    settings = data['settings']
    t = utils.TRANSLATIONS[lang]
    shop_name = data['users'][str(chat_id)].get("shop_name", "مكتب الصياغة")
    
    loading = bot.send_message(chat_id, t["loading_buy"])
    time.sleep(1)
    bot.delete_message(chat_id, loading.message_id)
    
    try:
        karat = state_data["karat"]
        unit = state_data["unit"]
        weight = state_data["weight"]
        labor = state_data["labor"]
        mithqal_price = state_data["mithqal_price"]
        usd_100 = settings["usd_100"]
        
        gram_purchase_price = mithqal_price / 5
        net_gram_price = gram_purchase_price - labor
        
        if unit == "gram":
            total_grams = weight
            unit_text = "غرام" if lang in ["ar", "ku"] else "grams"
            unit_arabic = "حساب بالغرام" if lang == "ar" else ("حساب بە گرام" if lang == "ku" else "Gram Account")
        else:
            total_grams = weight * 5
            unit_text = "مثقال" if lang in ["ar", "ku"] else "mithqal"
            unit_arabic = "حساب بالمثقال" if lang == "ar" else ("حساب بە مسقاڵ" if lang == "ku" else "Mithqal Account")
            
        total_iqd = net_gram_price * total_grams
        paper_and_dinar_text = utils.calculate_paper_and_dinar(total_iqd, usd_100, lang)
        
        invoice = t["buy_invoice"].format(
            shop_name=shop_name,
            karat=karat,
            unit_arabic=unit_arabic,
            weight=f"{weight:.3f}",
            unit_text=unit_text,
            total_grams=total_grams,
            labor=labor,
            mithqal_price=mithqal_price,
            net_gram_price=net_gram_price,
            total_iqd=total_iqd,
            paper_and_dinar_text=paper_and_dinar_text
        )
        
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
    except Exception as e:
        print(f"Buy Calc Error: {e}")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "⚠️ Error.", lang=lang)

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
