import os
import re
import time
from datetime import datetime, timedelta
import telebot
from telebot import types
import utils

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# مخازن مؤقتة لإدارة الحالات والعمليات الحسابية واللغات لكل مستخدم
USER_STATE = {}
INVOICE_DATA = {}
USER_LANG = {} # لتخزين لغة كل مستخدم (ar, ku, en)

TREND_BASE_NUMBER = 149

# قاموس النصوص للغات الثلاث لدعم زر اللغات الفعلي
LANG_TEXTS = {
    'ar': {
        'cancel': "❌ إلغاء العملية الحالية",
        'main_welcome': "✨ أهلاً بك يا شيخ الكار في محلك العامر: {name}\nيرجى اختيار العملية الحالية وتوكل على الرزاق 👇",
        'select_carat_sell': "📥 حساب بيع لزبون\nاختر عيار الذهب المطلوب للحساب أدناه 👇",
        'select_carat_buy': "📤 حساب شراء من زبون\nاختر عيار الذهب المستلم للحساب أدناه 👇",
        'input_weight_sell': "⚖️ ممتاز، اخترت عيار {carat}.\nأرسل الآن وزن الذهب بالغرام فقط (مثال: 14.85):",
        'input_mitqal_buy': "⚖️ ممتاز، اخترت عيار {carat}.\nأرسل الآن عدد المثاقيل المتفق عليها مع الزبون للشراء (مثال: 5.5):",
        'input_price_buy': "💰 أرسل الآن سعر مثقال الكسر المعتمد المتفق عليه مع الزبون للشراء (مثال: 440000):",
        'input_wage_buy': "🛠️ أرسل الآن قيمة خصم أجور الكسر للمثقال الواحد (إذا لا يوجد خصم أكتب 0):"
    },
    'ku': {
        'cancel': "❌ Labordana Karê Taze",
        'main_welcome': "✨ Bi xêr bî şêxê kar bo daxazên te: {name}\nJi kerema xwe yek ji bişkokan hilbijêre 👇",
        'select_carat_sell': "📥 Hesabê firotanê bo xerîdar\nEyarê zêr hilbijêre 👇",
        'select_carat_buy': "📤 Hesabê kirînê ji xerîdar\nEyarê zêr hilbijêre 👇",
        'input_weight_sell': "⚖️ Baş e, te eyarê {carat} hilbijart.\nNiha tenê kêşeya zêr bi gram bişîne (mînak: 14.85):",
        'input_mitqal_buy': "⚖️ Baş e, te eyarê {carat} hilbijart.\nNiha hejmara mîsqalan bişîne (mînak: 5.5):",
        'input_price_buy': "💰 Niha nirxê mîsqalê zêr yê rêkeftî bişîne (mînak: 440000):",
        'input_wage_buy': "🛠️ Niha heqê kêmkirina şikandinê bo her mîsqalê bişîne (heger tune ye 0 binivîse):"
    },
    'en': {
        'cancel': "❌ Cancel Current Operation",
        'main_welcome': "✨ Welcome to your store: {name}\nPlease choose an operation from below 👇",
        'select_carat_sell': "📥 Sell to Customer Calculation\nChoose gold carat below 👇",
        'select_carat_buy': "📤 Buy from Customer Calculation\nChoose gold carat below 👇",
        'input_weight_sell': "⚖️ Excellent, carat {carat} selected.\nSend the gold weight in grams only (e.g., 14.85):",
        'input_mitqal_buy': "⚖️ Excellent, carat {carat} selected.\nSend the total number of Mitqals (e.g., 5.5):",
        'input_price_buy': "💰 Send the agreed price per Mitqal for buying (e.g., 440000):",
        'input_wage_buy': "🛠️ Send the scrap wage deduction per Mitqal (write 0 if none):"
    }
}

def get_str(user_id, key):
    lang = USER_LANG.get(user_id, 'ar')
    return LANG_TEXTS[lang].get(key, LANG_TEXTS['ar'][key])

# الكيبوردات مرتبة بشكل عمودي (واحد تحت الآخر) تماماً
def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("👑 لوحة تحكم الأدمن المركزي"))
        markup.add(types.KeyboardButton("⚙️ تعديل أيام اشتراك العميل"))
    
    markup.add(types.KeyboardButton("⚙️ إعدادات الصباح"))
    markup.add(types.KeyboardButton("📥 بيع لزبون"))
    markup.add(types.KeyboardButton("📤 شراء من زبون"))
    markup.add(types.KeyboardButton("📊 اللغات / Ziman / Languages"))
    return markup

def get_cancel_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(get_str(user_id, 'cancel')))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if utils.is_action_locked(user_id, delay=2): return

    USER_STATE.pop(user_id, None)
    INVOICE_DATA.pop(user_id, None)

    goldsmith = utils.get_goldsmith(user_id)
    
    if not goldsmith:
        welcome_text = (
            "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "👋 أهلاً بك يا شيخ الكار في النظام الرقمي الأول المخصص لإدارة حسابات محلات الذهب بيعاً وشراءً وتفقيط النقد بالدينار والدولار بلحظات.\n\n"
            "💎 مميزات المنظومة الذكية:\n"
            "🛡️ استقلالية تامة لمحلك بأسعارك اليومية الخاصة.\n"
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

    # فحص صلاحية الاشتراك والتنبيه
    is_active, days_left = utils.check_goldsmith_validity(user_id) 
    if not is_active:
        expired_text = (
            "⚜️ منظومة نواة الذهب الذكية ⚜️\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "🛑 تنبيه انتهاء الصلاحية:\n"
            "🚫 لقد انتهت الفترة المخصصة للمنظومة في محلك العامر.\n\n"
            "💳 لتجديد الاشتراك وتفعيل الصلاحية تلقائياً يرجى تحويل رسوم باقة شيوخ الكار المفتوحة، وإرسال الوصل المالي للدعم الفني مباشرة لاستمرار عمل النظام الفخم دون انقطاع.\n\n"
            "📞 خط الدعم الفني المباشر: 07872180902"
        )
        bot.send_message(message.chat.id, expired_text)
        return

    # رسالة تنبيه قبل انتهاء الاشتراك (إذا بقي 3 أيام أو أقل)
    if days_left <= 3:
        bot.send_message(message.chat.id, f"⚠️ <b>تنبيه مبكر:</b> باقي {days_left} يوم فقط على نهاية الاشتراك التجريبي/السنوي لمحلك، يرجى مراجعة الإدارة لضمان عدم توقف الفواتير الفخمة.")

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
    
    # معالجة تغيير زر اللغات الفعلي
    if call.data.startswith("set_lang_"):
        lang = call.data.split("_")[2]
        USER_LANG[user_id] = lang
        bot.answer_callback_query(call.id, "✅ Done / تم الترتيب")
        bot.send_message(chat_id, "✅ تم ضبط وترتيب لغة المنظومة عمودياً بنجاح.", reply_markup=get_main_keyboard(user_id))
        return

    # اختيار عيارات البيع والشراء (مرتبة عمودياً بالـ Inline)
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

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text in ["❌ إلغاء العملية الحالية", "❌ Labordana Karê Taze", "❌ Cancel Current Operation"]:
        USER_STATE.pop(user_id, None)
        INVOICE_DATA.pop(user_id, None)
        bot.send_message(message.chat.id, "📥 تم إلغاء العملية والرجوع للقائمة الرئيسية.", reply_markup=get_main_keyboard(user_id))
        return

    if utils.is_action_locked(user_id, delay=3): return

    # 1. مرحلة التسجيل العمودي
    if USER_STATE.get(user_id) == "AWAITING_REGISTRATION":
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) >= 3:
            loading_msg = bot.send_message(message.chat.id, "⏳ jari tahmil wa tadqiq al-amalyat...")
            
            shop_name, location, phone = lines[0], lines[1], lines[2]
            utils.register_new_goldsmith(user_id, shop_name, location, phone)
            
            total_goldsmiths = utils.get_total_active_goldsmiths()
            public_total = TREND_BASE_NUMBER + total_goldsmiths
            
            success_text = (
                "⚜️ منظومة نواة الذهب الذكية لشيوخ الصاغة ⚜️\n"
                "━━━━━━━━━━━━━━━━━\n\n"
                "✨ يا فتاح يا عليم يا رزاق يا كريم ✨\n\n"
                "🎁 رزقكم مبارك، وتم تفعيل الفترة التجريبية بنجاح لك لتجتاح بها السوق ميدانياً!\n\n"
                "📍 المحل العامر: {shop}\n"
                "🗺️ الموقع: {loc}\n"
                "📞 الهاتف: {phone}\n\n"
                "👥 المشتركين النشطين في الكار الآن:\n"
                "🥇 {total} صائغ معتمد\n"
                "━━━━━━━━━━━━━━━━━\n"
                "👇 يرجى اختيار العملية المطلوبة من الأزرار أدناه للبدء"
            ).format(shop=shop_name, loc=location, phone=phone, total=public_total)
            
            USER_STATE.pop(user_id, None)
            try: bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
            except: pass
            bot.send_message(message.chat.id, success_text, reply_markup=get_main_keyboard(user_id))
        else:
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال البيانات بثلاثة أسطر منفصلة (عمودية): الاسم، ثم الموقع، ثم الهاتف لضمان تسجيلك المعتمد.")
        return

    # 2. لوحة تحكم الأدمن والتحكم بالوقت (موجب / سالب)
    if text == "👑 لوحة تحكم الأدمن المركزي" and user_id == ADMIN_ID:
        total_real = utils.get_total_active_goldsmiths()
        admin_panel_text = (
            "🛡️ لوحة الإدارة العليا للمنظومة\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            "📊 إحصائيات النظام الفعلي:\n"
            "👥 عدد الصاغة الفعليين: {total} صائغ نشط.\n"
            "👥 العدد التسويقي الظاهر للعموم: {trend} صائغ.\n\n"
            "💡 لتغيير وقت اشتراك أي عميل (زيادة أو نقصان أيام)، اضغط على زر التعديل من القائمة أدناه."
        ).format(total=total_real, trend=TREND_BASE_NUMBER + total_real)
        bot.send_message(message.chat.id, admin_panel_text, reply_markup=get_main_keyboard(user_id))
        return

    if text == "⚙️ تعديل أيام اشتراك العميل" and user_id == ADMIN_ID:
        USER_STATE[user_id] = "ADMIN_INPUT_MODIFICATION"
        bot.send_message(message.chat.id, "✏️ أرسل معرف الصائغ (الـ ID الرقمي) تتبعه بعدد الأيام (بالموجب للزيادة أو بالسالب للنقصان) مفصولين بنقطتين.\n\nمثال لإضافة 30 يوم: <code>12345678:30</code>\nمثال لإنقاص 7 أيام: <code>12345678:-7</code>", parse_mode="HTML", reply_markup=get_cancel_keyboard(user_id))
        return

    if USER_STATE.get(user_id) == "ADMIN_INPUT_MODIFICATION" and user_id == ADMIN_ID:
        try:
            parts = text.split(':')
            target_user = int(parts[0])
            days_to_add = int(parts[1])
            
            utils.modify_goldsmith_subscription(target_user, days_to_add)
            USER_STATE.pop(user_id, None)
            
            bot.send_message(message.chat.id, f"✅ تم تعديل الاشتراك بنجاح للصائغ بنحو ({days_to_add}) يوماً وتم تحديث السيرفر الرسمي.", reply_markup=get_main_keyboard(user_id))
            # إرسال إشعار تلقائي وفوري للعميل بالتعديل الجديد للوقت المجاني
            bot.send_message(target_user, f"📢 <b>تنبيه رسمي من الإدارة العليا:</b>\nتم تحديث صلاحية وقت محلك التجاري المجاني في السيرفر بنحو ({days_to_add}) يوماً إضافياً! توكل على الرزاق ونظم فواتيرك الفخمة الآن.", parse_mode="HTML")
        except:
            bot.send_message(message.chat.id, "⚠️ خطأ في الصيغة، يرجى إرسال الـ ID ثم الأيام كالمثال تماماً.")
        return

    # 3. إعدادات الصباح المستقلة والعمودية لكل عميل
    if text == "⚙️ إعدادات الصباح":
        prices = utils.get_goldsmith_prices(user_id)
        morning_text = (
            "☀️ صباح الرزق والبركة يا طيب!\n\n"
            "📋 إعدادات الصباح الحالية لمحلك:\n\n"
            "🔷 سعر مثقال عيار 21:\n👈 {p21:,.0f} دينار\n\n"
            "🔷 سعر مثقال عيار 18:\n👈 {p18:,.0f} دينار\n\n"
            "🔨 أجور صياغة غرام 21:\n👈 {m21:,.0f} دينار\n\n"
            "🔨 أجور صياغة غرام 18:\n👈 {m18:,.0f} دينار\n\n"
            "💵 سعر الـ 100 دولار:\n👈 {usd:,.0f} دينار\n"
            "━━━━━━━━━━━━━━━━━\n"
            "✏️ لتعديل أسعار محلك الحرة، أرسل الأسعار الجديدة في سطر واحد مفصولة بنقطتين (:) كالتالي تماماً:\n"
            "<code>900000:450000:10000:1000:155000</code>"
        ) .format(
            p21=prices.get('price_21', 900000), p18=prices.get('price_18', 450000),
            m21=prices.get('wage_21', 10000), m18=prices.get('wage_18', 1000),
            usd=prices.get('usd_rate', 155000)
        )
        USER_STATE[user_id] = "CUSTOMER_UPDATING_PRICES"
        bot.send_message(message.chat.id, morning_text, parse_mode="HTML", reply_markup=get_cancel_keyboard(user_id))
        return

    if USER_STATE.get(user_id) == "CUSTOMER_UPDATING_PRICES":
        try:
            parts = text.split(':')
            p21, p18, w21, w18, usd = float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
            USER_STATE.pop(user_id, None)
            bot.send_message(message.chat.id, "✅ تم حفظ أسعار الصباح الخاصة بمحلك بنجاح عمودياً!", reply_markup=get_main_keyboard(user_id))
        except:
            bot.send_message(message.chat.id, "⚠️ صيغة الإدخال غير مطابقة للمثال، أعد المحاولة بدقة.")
        return

    # 4. زر خيارات اللغات الفعلي
    if text == "📊 اللغات / Ziman / Languages":
        lang_markup = types.InlineKeyboardMarkup(row_width=1) # قائمة عمودية تماماً
        lang_markup.add(
            types.InlineKeyboardButton("🇮🇶 العربية", callback_data="set_lang_ar"),
            types.InlineKeyboardButton("☀️ Kurdî", callback_data="set_lang_ku"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
        )
        bot.send_message(message.chat.id, "🌐 اختر لغة العمل للواجهات البرمجية عمودياً:\n⚙️ Zimanê botê hilbijêrin:\n🌐 Select system interface language:", reply_markup=lang_markup)
        return

    # 5. بيع لزبون (واحد جوة واحد بالغرام)
    if text == "📥 بيع لزبون":
        inline_markup = types.InlineKeyboardMarkup(row_width=1)
        inline_markup.add(
            types.InlineKeyboardButton("👑 عيار 21", callback_data="select_carat_sell_21"),
            types.InlineKeyboardButton("💎 عيار 18", callback_data="select_carat_sell_18")
        )
        bot.send_message(message.chat.id, get_str(user_id, 'select_carat_sell'), reply_markup=inline_markup)
        return

    if USER_STATE.get(user_id) == "AWAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ jari tahmil wa tadqiq al-amalyat...")
        prices = utils.get_goldsmith_prices(user_id)
        goldsmith = utils.get_goldsmith(user_id)
        
        try:
            weight = float(text)
            check_carat = INVOICE_DATA[user_id]['carat']
            
            mitqal_price = prices.get('price_21', 900000) if check_carat == 21 else prices.get('price_18', 450000)
            wage_per_gram = prices.get('wage_21', 10000) if check_carat == 21 else prices.get('wage_18', 1000)
            
            gram_pure_price = mitqal_price / 5.0
            total_iqd = (gram_pure_price + wage_per_gram) * weight
            
            usd_rate = prices.get('usd_rate', 155000)
            total_usd_bills = int(total_iqd // usd_rate)
            remaining_iqd = total_iqd % usd_rate
            
            invoice_text = (
                "🏛️ {shop} 🏛️\n"
                "📍 {loc} | 📞 {phone}\n"
                "━━━━━━━━━━━━━━━━━\n"
                "🧾 فاتورة بيع ذهب معتمدة\n"
                "━━━━━━━━━━━━━━━━━\n"
                "🔹 صنف الذهب الحسابي:\n👈 عيار {carat}\n\n"
                "⚖️ الوزن الإجمالي الموزون:\n👈 {w} غرام\n\n"
                "🔨 أجور الصياغة للغرام:\n👈 {wage:,.0f} دينار\n\n"
                "💰 سعر الغرام الصافي:\n👈 {g_price:,.0f} دينار\n"
                "━━━━━━━━━━━━━━━━━\n"
                "💵 المبلغ بالدينار العراقي:\n"
                "👈 <b>{total_iqd:,.0f} دينار</b>\n\n"
                "💵 تفقيط النقد بالورق والدينار:\n"
                "👈 <b>{usd_bills} ورقـة ($100) و {rem_iqd:,.0f} دينار</b>\n"
                "━━━━━━━━━━━━━━━━━\n"
                "✨ ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك! ✨\n\n"
                "🤖 تم الحساب والنشر بواسطة منظومة نواة الذهب الذكية @GoldenCalc_Bot"
            ).format(shop=goldsmith['full_name'], loc=goldsmith['location'], phone=goldsmith['phone'], carat=check_carat, w=weight, wage=wage_per_gram, g_price=gram_pure_price, total_iqd=total_iqd, usd_bills=total_usd_bills, rem_iqd=remaining_iqd)
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            try: bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
            except: pass
            bot.send_message(message.chat.id, invoice_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        except:
            bot.edit_message_text("⚠️ يرجى إرسال الوزن كأرقام مجردة فقط.", chat_id=message.chat.id, message_id=loading_msg.message_id)
        return

    # 6. شراء من زبون (واحد جوة واحد بالمثقال + سعر الكسر المتفق عليه + خصم أجور اختياري)
    if text == "📤 شراء من زبون":
        inline_markup = types.InlineKeyboardMarkup(row_width=1)
        inline_markup.add(
            types.InlineKeyboardButton("👑 عيار 21", callback_data="select_carat_buy_21"),
            types.InlineKeyboardButton("💎 عيار 18", callback_data="select_carat_buy_18")
        )
        bot.send_message(message.chat.id, get_str(user_id, 'select_carat_buy'), reply_markup=inline_markup)
        return

    if USER_STATE.get(user_id) == "AWAITING_MITQAL_BUY":
        try:
            mitqals = float(text)
            INVOICE_DATA[user_id]['mitqals'] = mitqals
            USER_STATE[user_id] = "AWAITING_PRICE_BUY"
            bot.send_message(message.chat.id, get_str(user_id, 'input_price_buy'), reply_markup=get_cancel_keyboard(user_id))
        except:
            bot.send_message(message.chat.id, "⚠️ يرجى كتابة عدد المثاقيل كأرقام فقط (مثال: 4 أو 3.5).")
        return

    if USER_STATE.get(user_id) == "AWAITING_PRICE_BUY":
        try:
            agreed_mitqal_price = float(text)
            INVOICE_DATA[user_id]['agreed_price'] = agreed_mitqal_price
            USER_STATE[user_id] = "AWAITING_WAGE_BUY"
            bot.send_message(message.chat.id, get_str(user_id, 'input_wage_buy'), reply_markup=get_cancel_keyboard(user_id))
        except:
            bot.send_message(message.chat.id, "⚠️ يرجى كتابة سعر مثقال الكسر كأرقام مجردة فقط.")
        return

    if USER_STATE.get(user_id) == "AWAITING_WAGE_BUY":
        loading_msg = bot.send_message(message.chat.id, "⏳ jari tahmil wa tadqiq al-amalyat...")
        prices = utils.get_goldsmith_prices(user_id)
        goldsmith = utils.get_goldsmith(user_id)
        
        try:
            wage_discount_per_mitqal = float(text)
            mitqals = INVOICE_DATA[user_id]['mitqals']
            agreed_mitqal_price = INVOICE_DATA[user_id]['agreed_price']
            check_carat = INVOICE_DATA[user_id]['carat']
            
            # العملية الرياضية المخصصة: (سعر المثقال المعتمد ناقص خصم الأجور) مضروباً بعدد المثاقيل
            final_mitqal_price = agreed_mitqal_price - wage_discount_per_mitqal
            total_iqd = final_mitqal_price * mitqals
            
            usd_rate = prices.get('usd_rate', 155000)
            total_usd_bills = int(total_iqd // usd_rate)
            remaining_iqd = total_iqd % usd_rate
            
            invoice_text = (
                "🏛️ {shop} 🏛️\n"
                "📍 {loc} | 📞 {phone}\n"
                "━━━━━━━━━━━━━━━━━\n"
                "🧾 فاتورة شراء ذهب كسر\n"
                "━━━━━━━━━━━━━━━━━\n"
                "🔹 صنف الذهب المستلم:\n👈 عيار {carat}\n\n"
                "⚖️ الكمية الموزونة:\n👈 {m} مثقال\n\n"
                "💰 سعر المثقال المتفق عليه:\n👈 {p_mitqal:,.0f} دينار\n\n"
                "🛠️ الخصم المحسوب للمثقال:\n👈 {wage:,.0f} دينار\n"
                "━━━━━━━━━━━━━━━━━\n"
                "💵 المبلغ المستحق للزبون بالدينار:\n"
                "👈 <b>{total_iqd:,.0f} دينار</b>\n\n"
                "💵 تفقيط النقد بالورق والدينار:\n"
                "👈 <b>{usd_bills} ورقـة ($100) و {rem_iqd:,.0f} دينار</b>\n"
                "━━━━━━━━━━━━━━━\n"
                "🌸 تمت عملية الشراء بنجاح! وعوضكم الله بالخير الوفير! ✨\n\n"
                "🤖 تم الحساب والنشر بواسطة منظومة نواة الذهب الذكية @GoldenCalc_Bot"
            ).format(shop=goldsmith['full_name'], loc=goldsmith['location'], phone=goldsmith['phone'], carat=check_carat, m=mitqals, p_mitqal=agreed_mitqal_price, wage=wage_discount_per_mitqal, total_iqd=total_iqd, usd_bills=total_usd_bills, rem_iqd=remaining_iqd)
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            try: bot.delete_message(chat_id=message.chat.id, message_id=loading_msg.message_id)
            except: pass
            bot.send_message(message.chat.id, invoice_text, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
        except:
            bot.edit_message_text("⚠️ خطأ في إدخال الخصم، يرجى كتابة رقم صحيح فقط.", chat_id=message.chat.id, message_id=loading_msg.message_id)
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
