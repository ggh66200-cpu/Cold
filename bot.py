import os
import re
import telebot
from telebot import types
from flask import Flask
import threading
import utils
import admin

BOT_TOKEN = os.environ.get("BOT_TOKEN")
try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
except:
    ADMIN_ID = 0

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "SMART GOLD SYSTEM IS LIVE"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

MASTER_CARD = admin.MASTER_CARD
MONTHLY_PRICE = admin.MONTHLY_PRICE
COMPANY_HEADER = admin.COMPANY_HEADER
SUPPORT_NUMBER = "07872180902"  # رقم الدعم الفني الذي طلبته

USER_STATE = {}
INVOICE_DATA = {}

TEXTS = {
    "welcome": "👋 أهلاً بك في <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع لإدارة حسابات الصياغة محلياً ودولياً.\n🔥 <i>عدد المشتركين النشطين حالياً في المنظومة:</i> <b>{counter} مشترك</b>\n\nالرجاء استخدام الأزرار أدناه للبدء بالعمليات اليومية لمحلك الحلال 👇",
    "btn_prices": "⚙️ إدخال أسعار الصباح اليومية",
    "btn_sell": "📥 حساب بيع لزبون",
    "btn_buy": "📤 حساب شراء من زبون",
    "btn_info": "📖 شرح النظام",
    "btn_sub": "📝 استمارة الاشتراك",
    "btn_clients": "👥 جرد العملاء والعمليات",
    "invoice_sell": "🧾 <b>فاتورة بيع ذهب للزبون</b> 🧾",
    "invoice_buy": "📥 <b>فاتورة شراء ذهب من الزبون</b> 📥",
    "shop": "🔷 المحل العامر: ",
    "type_sell": "🔷 العيار ونوع الحساب: عيار {carat} (حساب بيع بالغرام)",
    "type_buy": "🔷 العيار ونوع الحساب: عيار {carat} (حساب شراء بالغرام)",
    "weight_req": "🔷 الوزن المطلوب: {w} غرام",
    "weight_tot": "⚖️ الوزن الإجمالي بالجرام: {w} غرام",
    "wage_sell": "🔨 أجور صياغة الغرام (مضافة): {wage:,.0f} دينار",
    "wage_buy": "🔨 كسر أجور الصياغة (مخصومة): {wage:,.0f} دينار",
    "clean_p": "💰 سعر غرام الذهب الصافي: {p:,.0f} دينار",
    "full_p": "💵 سعر الغرام مع أجور الصائغ: {p:,.0f} دينار",
    "total_iqd": "💵 <b>السعر الكلي بالدنانير العراقي:</b>\n👉 <b>{total:,.0f} دينار</b>",
    "total_usd": "💵 <b>صافي الحساب بالورق والدينار:</b>\n👉 <b>{usd} ورقة و {rem:,.0f} دينار</b>",
    "footer": "🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! 💛",
    "req_weight_sell": "⚖️ <b>عيار {carat} (حساب بيع للزبون):</b>\nأرسل وزن الذهب بالغرام فقط (مثال: 8.963):",
    "req_buy_inputs": "📥 <b>عيار {carat} (حساب شراء من زبون):</b>\nيرجى إرسال البيانات المطلوبة بالترتيب في رسالة واحدة (كل قيمة بسطر):\n\n<code>1️⃣ سعر المثقال للشراء\n2️⃣ الوزن بالغرام\n3️⃣ أجور الكسر للغرام</code>\n\n💡 <i>مثال للنسخ والتعديل:</i>\n<code>780000\n15.420\n2000</code>"
}

def to_english_numbers(text):
    arabic_nums = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    persian_nums = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(arabic_nums).translate(persian_nums)

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton(TEXTS["btn_prices"]))
    markup.add(types.KeyboardButton(TEXTS["btn_sell"]), types.KeyboardButton(TEXTS["btn_buy"]))
    markup.add(types.KeyboardButton(TEXTS["btn_info"]), types.KeyboardButton(TEXTS["btn_sub"]))
    markup.add(types.KeyboardButton(TEXTS["btn_clients"]))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id) or {}
    
    # التسجيل إذا كان المستخدم جديداً
    if not gs.get('is_registered', False):
        USER_STATE[user_id] = "WAITING_REGISTRATION_FULL"
        bot.send_message(
            message.chat.id, 
            f"{COMPANY_HEADER}📝 <b>أهلاً بك يا طيب في نظام أرامكي للحلول الرقمية</b>\n\n"
            "لتفعيل الفترة المجانية، يرجى إرسال **اسم المحل ورقم الهاتف** في رسالة واحدة.\n\n"
            "💡 <i>مثال:</i>\nمجوهرات البركة - 07800000000", 
            parse_mode="HTML"
        )
        return

    # فحص الاشتراك للمستخدمين المسجلين مسبقاً
    if gs.get('remaining_days', 0) <= 0 and user_id != ADMIN_ID:
        show_subscription_form(message, expired=True)
        return

    # إظهار رسالة الترحيب والأزرار إذا كان الاشتراك فعالاً
    USER_STATE.pop(user_id, None)
    markup = get_main_keyboard()
    db_id = gs.get('id', 1)
    counter = 145 + (int(db_id) if str(db_id).isdigit() else 1)
    bot.send_message(message.chat.id, COMPANY_HEADER + TEXTS["welcome"].format(counter=counter), parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_info"])
def show_system_info(message):
    info_text = (
        f"{COMPANY_HEADER}"
        "📖 <b>شرح النظام ومواصفاته الفنية:</b>\n\n"
        "1️⃣ <b>إدخال أسعار الصباح:</b> لتحديث أسعار الذهب وسعر صرف الدولار المعتمد للبيع والشراء مع الزبون ليومك الحالي.\n"
        "2️⃣ <b>حساب البيع:</b> لاحتساب تكلفة بيع القطعة للزبون بالدينار والدولار (الورق) تلقائياً.\n"
        "3️⃣ <b>حساب الشراء (الكسر):</b> لاحتساب كسر الذهب وأجور الصياغة المخصومة بدقة متناهية.\n"
        "4️⃣ <b>جرد العملاء:</b> لمتابعة وعرض حالة حسابك وحفظ كافة العمليات في قاعدة البيانات السحابية بأمان."
    )
    bot.send_message(message.chat.id, info_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sub"])
def show_subscription_form(message, expired=False):
    user_id = message.from_user.id
    USER_STATE[user_id] = "WAITING_RECEIPT"
    prefix = "⚠️ <b>انتهت فترتك التجريبية أو صلاحية اشتراكك! يرجى التجديد للاستمرار:</b>\n\n" if expired else ""
    sub_text = (
        f"{COMPANY_HEADER}{prefix}"
        "📝 <b>استمارة الاشتراك وتجديد الصلاحية:</b>\n\n"
        f"🔹 <b>قيمة الاشتراك الشهري:</b> {MONTHLY_PRICE}\n"
        f"🔹 <b>رقم التحويل (زين كاش أو ماستر):</b> <code>{MASTER_CARD}</code>\n"
        f"📞 <b>للتواصل والدعم الفني:</b> <code>{SUPPORT_NUMBER}</code>\n\n"
        "📸 <b>الخطوة المطلوبة:</b>\n"
        "أرسل **صورة وصل التحويل** (سكرين شوت) هنا في الدردشة ليتم تفعيل اشتراكك من قبل الإدارة فوراً."
    )
    bot.send_message(message.chat.id, sub_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_clients"])
def show_clients_summary(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id)
    summary_text = (
        f"{COMPANY_HEADER}"
        "📊 <b>جرد العمليات والعملاء:</b>\n\n"
        f"🔷 المحل: {gs.get('full_name', 'محلي الموقر')}\n"
        f"⏳ الأيام المتبقية للاشتراك: <b>{gs.get('remaining_days', 0)} يوم</b>\n"
        "🟢 الحالة: حسابك مرتبط بقاعدة البيانات السحابية (Supabase) والعمليات مسجلة بأمان."
    )
    bot.send_message(message.chat.id, summary_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_prices"])
def morning_prices_start(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id)
    if gs.get('remaining_days', 0) <= 0 and user_id != ADMIN_ID:
        return show_subscription_form(message, expired=True)
    
    USER_STATE[user_id] = "AWAITING_ALL_PRICES"
    instruction = (
        f"{COMPANY_HEADER}"
        "☀️ <b>صباح الرزق والسعادة والبركة يا طيب!</b> ☀️\n\n"
        "💡 <b>مثال توضيحي للكتابة (انسخه وعدل الأرقام):</b>\n"
        "<code>900000\n850000\n4500\n7500\n153000</code>\n\n"
        "✍️ <b>الترتيب المطلوب:</b>\n"
        "1️⃣ سعر مثقال 21 | 2️⃣ سعر مثقال 18 | 3️⃣ أجور 21\n"
        "4️⃣ أجور 18 | 5️⃣ سعر صرف 100$ <i>(ملاحظة: سعر الدولار بالدينار هو للبيع والشراء مع الزبون)</i>\n\n"
        "👉 <i>اكتب الأسعار وأرسلها للتحديث.</i>"
    )
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sell"])
def customer_sell_init(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id)
    if gs.get('remaining_days', 0) <= 0 and user_id != ADMIN_ID:
        return show_subscription_form(message, expired=True)

    USER_STATE.pop(user_id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="sell_21"), types.InlineKeyboardButton("عيار 18", callback_data="sell_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>حساب بيع ذهب لزبون:</b>\nاختر العيار:", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_buy"])
def customer_buy_init(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id)
    if gs.get('remaining_days', 0) <= 0 and user_id != ADMIN_ID:
        return show_subscription_form(message, expired=True)

    USER_STATE.pop(user_id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="buy_21"), types.InlineKeyboardButton("عيار 18", callback_data="buy_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📤 <b>حساب شراء ذهب من زبون:</b>\nاختر العيار:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sell_") or call.data.startswith("buy_"))
def handle_calc_buttons(call):
    bot.answer_callback_query(call.id, text="⏳...")
    user_id = call.from_user.id
    mode = call.data.split("_")[0]     
    carat = int(call.data.split("_")[1]) 
    INVOICE_DATA[user_id] = {'carat': carat, 'mode': mode}
    
    if mode == "sell":
        USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
        bot.send_message(call.message.chat.id, TEXTS["req_weight_sell"].format(carat=carat), parse_mode="HTML")
    elif mode == "buy":
        USER_STATE[user_id] = "WAITING_BUY_ALL_INPUTS"
        bot.send_message(call.message.chat.id, TEXTS["req_buy_inputs"].format(carat=carat), parse_mode="HTML")

# أزرار لوحة تحكم الأدمن للتحكم بالعملاء
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_sub_") or call.data.startswith("reject_sub_") or call.data.startswith("time_"))
def handle_admin_actions(call):
    data = call.data
    if data.startswith("approve_sub_"):
        target_user = int(data.split("_")[2])
        utils.update_goldsmith_subscription(target_user, days=30)
        bot.answer_callback_query(call.id, text="✅ تم تفعيل الاشتراك بنجاح!")
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("➕ إضافة 30 يوم", callback_data=f"time_add_{target_user}"),
            types.InlineKeyboardButton("➖ خصم 30 يوم", callback_data=f"time_sub_{target_user}")
        )
        markup.add(types.InlineKeyboardButton("🛑 تصفير الوقت (إيقاف)", callback_data=f"time_zero_{target_user}"))
        bot.edit_message_caption(f"🧾 تم اعتماد الإيصال وتفعيل اشتراك الصائغ (آيدي): <code>{target_user}</code>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        try:
            bot.send_message(target_user, f"{COMPANY_HEADER}✅ <b>تهانينا! تم تفعيل اشتراكك وتحديث رصيد أيامك بنجاح. يمكنك الآن العمل على النظام.</b>", parse_mode="HTML", reply_markup=get_main_keyboard())
        except:
            pass

    elif data.startswith("reject_sub_"):
        target_user = int(data.split("_")[2])
        bot.answer_callback_query(call.id, text="❌ تم الرفض")
        bot.edit_message_caption(f"🧾 تم الرفض لهذا الوصل للمستخدم (آيدي): <code>{target_user}</code>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        try:
            bot.send_message(target_user, f"{COMPANY_HEADER}❌ <b>عفواً، تم رفض الإيصال المرسل! يرجى التأكد والمحاولة من جديد.</b>", parse_mode="HTML")
        except:
            pass
            
    elif data.startswith("time_"):
        target_user = int(data.split("_")[2])
        action = data.split("_")[1]
        msg_result = ""
        
        if action == "add":
            utils.adjust_goldsmith_days(target_user, 30)
            msg_result = "✅ تم إضافة 30 يوم."
        elif action == "sub":
            utils.adjust_goldsmith_days(target_user, -30)
            msg_result = "➖ تم خصم 30 يوم."
        elif action == "zero":
            utils.adjust_goldsmith_days(target_user, 0, set_zero=True)
            msg_result = "🛑 تم تصفير الأيام وإيقاف الحساب."
            
        bot.answer_callback_query(call.id, text=msg_result)
        current_caption = call.message.caption or ""
        new_caption = f"{current_caption}\n\n{msg_result} للإيدي <code>{target_user}</code>"
        try:
            bot.edit_message_caption(new_caption, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=call.message.reply_markup)
        except:
            pass

@bot.message_handler(content_types=['photo'])
def process_customer_receipt(message):
    user_id = message.from_user.id
    if USER_STATE.get(user_id) == "WAITING_RECEIPT":
        USER_STATE.pop(user_id, None)
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري التحقق من الوصل وإرساله للإدارة...</i>", parse_mode="HTML")
        gs = utils.get_goldsmith(user_id) or {}
        shop_name = gs.get('full_name', 'غير متوفر')
        phone = gs.get('phone', 'غير متوفر')
        
        try:
            photo = message.photo[-1].file_id
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ موافقة (تفعيل شهر)", callback_data=f"approve_sub_{user_id}"),
                types.InlineKeyboardButton("❌ رفض الإيصال", callback_data=f"reject_sub_{user_id}")
            )
            admin_text = f"🚨 <b>طلب اشتراك / تجديد جديد!</b>\n\n👤 المستخدم: <code>{user_id}</code>\n🔷 المحل: {shop_name}\n📱 الهاتف: {phone}\n\nرجاءً قم بمراجعة الإيصال المرفق."
            bot.send_photo(ADMIN_ID, photo, caption=admin_text, parse_mode="HTML", reply_markup=markup)
            
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "✅ <b>تم إرسال الإيصال للإدارة بنجاح! سيتم تفعيل حسابك بمجرد التحقق منه.</b>", parse_mode="HTML")
        except Exception as e:
            bot.edit_message_text(f"⚠️ خطأ في إرسال الوصل: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    text = to_english_numbers(message.text.strip())
    user_id = message.from_user.id
    state = USER_STATE.get(user_id)

    # 1. نظام التسجيل الموحد وإعطاء 3 أيام تلقائياً
    if state == "WAITING_REGISTRATION_FULL":
        loading = bot.send_message(message.chat.id, "⏳ <i>جاري تسجيل الحساب وإعداد قاعدة البيانات...</i>", parse_mode="HTML")
        parts = text.split('-')
        if len(parts) >= 2:
            shop_name = parts[0].strip()
            phone = parts[1].strip()
        else:
            shop_name = text
            phone = "غير محدد"
        
        try:
            # تسجيل المستخدم في قاعدة البيانات
            utils.register_goldsmith_details(user_id, shop_name, phone)
            # إعطاء المستخدم الجديد 3 أيام مجانية لتجربة النظام لكي لا يقفل النظام فوراً
            utils.update_goldsmith_subscription(user_id, days=3) 
            
            USER_STATE.pop(user_id, None)
            bot.delete_message(message.chat.id, loading.message_id)
            bot.send_message(message.chat.id, "✅ <b>تم التسجيل بنجاح! تم تفعيل 3 أيام فترة تجريبية مجانية لمحلك.</b>", parse_mode="HTML")
            # استدعاء الرسالة الترحيبية لتظهر مباشرة
            send_welcome(message)
        except Exception as e:
            bot.edit_message_text(f"⚠️ حدث خطأ أثناء التسجيل: {e}", message.chat.id, loading.message_id)
        return

    # 2. إدخال أسعار الصباح المجمعة
    if state == "AWAITING_ALL_PRICES":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري حفظ الأسعار...</i>", parse_mode="HTML")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) == 5:
            try:
                utils.update_morning_prices(
                    user_id,
                    p21=float(lines[0]),
                    p18=float(lines[1]),
                    w21=float(lines[2]),
                    w18=float(lines[3]),
                    usd_r=float(lines[4]) / 100.0  
                )
                USER_STATE.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "✅ تم حفظ أسعار الصباح بنجاح، ربي يرزقك!")
            except Exception as e:
                bot.edit_message_text(f"⚠️ خطأ في الأرقام: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("⚠️ يرجى إدخال 5 أسطر بالضبط كما في المثال الموضح أعلاه.", message.chat.id, loading_msg.message_id)
        return

    # 3. إدخال وزن البيع
    if state == "WAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب فاتورة البيع...</i>", parse_mode="HTML")
        if re.match(r'^\d+(\.\d+)?$', text):
            try:
                w = float(text)
                carat = INVOICE_DATA[user_id]['carat']
                prices = utils.get_goldsmith_prices(user_id) or {}
                goldsmith = utils.get_goldsmith(user_id) or {}
                
                if carat == 21:
                    gram_price = float(prices.get('m21_price', 0)) / 5.0
                    wage = float(prices.get('m21_wage', 0))
                else:
                    gram_price = float(prices.get('m18_price', 0)) / 5.0
                    wage = float(prices.get('m18_wage', 0))
                    
                gram_full = gram_price + wage
                total_iqd = gram_full * w
                usd_rate = float(prices.get('usd_rate', 1))
                usd_bills = int(total_iqd // usd_rate) if usd_rate > 0 else 0
                rem_iqd = total_iqd % usd_rate if usd_rate > 0 else total_iqd
                
                invoice = (
                    f"{COMPANY_HEADER}{TEXTS['invoice_sell']}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{goldsmith.get('full_name', 'محلي الموقر')}\n"
                    f"{TEXTS['type_sell'].format(carat=carat)}\n"
                    f"{TEXTS['weight_tot'].format(w=w)}\n{TEXTS['wage_sell'].format(wage=wage)}\n"
                    f"━━━━━━━━━━━━━━━━━\n{TEXTS['clean_p'].format(p=gram_price)}\n"
                    f"{TEXTS['full_p'].format(p=gram_full)}\n{TEXTS['total_iqd'].format(total=total_iqd)}\n\n"
                    f"{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            except Exception as e:
                bot.edit_message_text(f"⚠️ خطأ: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("⚠️ أرسل رقماً صحيحاً للوزن.", message.chat.id, loading_msg.message_id)
        return

    # 4. إدخال قيم الشراء دفعة واحدة بناءً على طلبك
    if state == "WAITING_BUY_ALL_INPUTS":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب فاتورة الشراء...</i>", parse_mode="HTML")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        numbers = []
        for line in lines:
            line = re.sub(r'[^\d.]', '', line)
            if line:
                numbers.append(line)
                
        if len(numbers) >= 3:
            # هذا هو الكود الدقيق الذي طلبته 
            try:
                custom_m_price, w, wage = map(float, numbers[:3])
                carat = INVOICE_DATA[user_id]['carat']
                prices = utils.get_goldsmith_prices(user_id) or {}
                goldsmith = utils.get_goldsmith(user_id) or {}
                
                gram_clean_price = custom_m_price / 5.0
                gram_full_price = gram_clean_price - wage
                total_iqd = gram_full_price * w
                usd_rate = float(prices.get('usd_rate', 1))
                usd_bills = int(total_iqd // usd_rate) if usd_rate > 0 else 0
                rem_iqd = total_iqd % usd_rate if usd_rate > 0 else total_iqd
                
                invoice = (
                    f"{COMPANY_HEADER}{TEXTS['invoice_buy']}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{goldsmith.get('full_name', 'محلي الموقر')}\n"
                    f"{TEXTS['type_buy'].format(carat=carat)}\n"
                    f"{TEXTS['weight_tot'].format(w=w)}\n{TEXTS['wage_buy'].format(wage=wage)}\n"
                    f"━━━━━━━━━━━━━━━━━\n{TEXTS['clean_p'].format(p=gram_clean_price)}\n"
                    f"{TEXTS['full_p'].format(p=gram_full_price)}\n{TEXTS['total_iqd'].format(total=total_iqd)}\n\n"
                    f"{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            except Exception as e:
                bot.edit_message_text(f"⚠️ خطأ: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("⚠️ الرجاء إدخال 3 أسطر بالضبط (السعر، الوزن، أجور الكسر) كما هو موضح في المثال.", message.chat.id, loading_msg.message_id)
        return

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
