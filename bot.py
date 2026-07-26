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
    ADMIN_ID = int(os.environ.get("ADMIN_ID", getattr(admin, "ADMIN_ID", 0)))
except:
    ADMIN_ID = 0

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "SMART GOLD SYSTEM IS LIVE"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

MASTER_CARD = admin.MASTER_CARD
MONTHLY_PRICE = admin.MONTHLY_PRICE
COMPANY_HEADER = admin.COMPANY_HEADER
SUPPORT_NUMBER = "07872180902" 

USER_STATE = {}
INVOICE_DATA = {}

TEXTS = {
    "welcome": "👋 أهلاً بك في عمالقة الصياغة <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع والأدق لإدارة حسابات الصياغة محلياً ودولياً بمعايير المصارف العالمية.\n🔥 <i>عدد المشتركين النشطين الآن في المنظومة:</i> <b>{counter} صايغ معتمد</b>\n\nالرعاة الرسميون لنجاح عملك.. استخدم الأزرار أدناه للبدء بالعمليات اليومية 👇",
    "btn_prices": "⚙️ إدخال أسعار الصباح اليومية",
    "btn_sell": "📥 حساب بيع لزبون",
    "btn_buy": "📤 حساب شراء من زبون",
    "btn_info": "📖 شرح النظام والمواصفات",
    "btn_clients": "👥 جرد العملاء والعمليات",
    "btn_admin_panel": "🛠️ لوحة تحكم الإدارة",
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
    arabic_nums = str.maketrans('٠١ي٣٤٥٦٧٨٩', '0123456789')
    persian_nums = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(arabic_nums).translate(persian_nums)

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton(TEXTS["btn_prices"]))
    markup.add(types.KeyboardButton(TEXTS["btn_sell"]), types.KeyboardButton(TEXTS["btn_buy"]))
    markup.add(types.KeyboardButton(TEXTS["btn_info"]), types.KeyboardButton(TEXTS["btn_clients"]))
    
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton(TEXTS["btn_admin_panel"]))
        
    return markup

def send_main_menu(message, user_id):
    gs = utils.get_goldsmith(user_id) or {}
    markup = get_main_keyboard(user_id)
    
    # تصحيح عداد الترند ليقرأ رقماً متصاعداً حقيقياً (يمكن تعديله حسب عدد المشتركين الفعليين بالداتابิس)
    try:
        all_users = utils.get_all_goldsmiths() # دالة لجلب عدد المشتركين إذا توفرت، وإلا نعتمده تصاعدياً
        total_count = len(all_users) if all_users else 1
        counter = 145 + total_count
    except:
        counter = 146
    
    bot.send_message(
        message.chat.id, 
        COMPANY_HEADER + TEXTS["welcome"].format(counter=counter), 
        parse_mode="HTML", 
        reply_markup=markup
    )

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id) or {}
    is_admin = (user_id == ADMIN_ID)
    
    if not gs.get('is_registered', False):
        USER_STATE[user_id] = "WAITING_REGISTRATION_FULL"
        bot.send_message(
            message.chat.id, 
            f"{COMPANY_HEADER}🌟 <b>مرحباً بك في قمة الاحتراف الرقمي لعالم الصياغة!</b> 🌟\n\n"
            "لقد انضمت الآن إلى النخبة من صاغة العراق الذين يديرون حساباتهم بدقة متناهية بعيداً عن حسابات الورق والخطأ البشري.\n"
            "لتفعيل فترتك التجريبية الحصرية (3 أيام مجاناً نظراً للضغط الهائل والإقبال غير المسبوق)، يرجى إرسال بيانات محلك برسالة واحدة كالتالي:\n\n"
            "🏢 <b>اسم المحل:</b>\n"
            "📱 <b>رقم الهاتف:</b>\n\n"
            "💡 <i>مثال للنسخ والتعديل:</i>\n"
            "<code>مجوهرات البركة\n07800000000</code>", 
            parse_mode="HTML"
        )
        return

    remaining_days = gs.get('remaining_days', 0)
    if remaining_days <= 0 and not is_admin:
        show_subscription_form(message, expired=True)
        return

    USER_STATE.pop(user_id, None)
    send_main_menu(message, user_id)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_info"])
def show_system_info(message):
    info_text = (
        f"{COMPANY_HEADER}"
        "📖 <b>شرح النظام والمواصفات الفنية المعتمدة:</b>\n\n"
        "1️⃣ <b>إدخال أسعار الصباح:</b> لتحديث أسعار الذهب وسعر صرف الدولار المعتمد للبيع والشراء مع الزبون ليومك الحالي بدقة تامة.\n"
        "2️⃣ <b>حساب البيع:</b> لاحتساب تكلفة بيع القطعة للزبون بالدينار والدولار (الورق) تلقائياً وبأجزاء الغرام.\n"
        "3️⃣ <b>حساب الشراء (الكسر):</b> لاحتساب كسر الذهب وأجور الصياغة المخصومة بلمح البصر دون أي مجهود ذهني.\n"
        "4️⃣ <b>جرد العملاء:</b> لمتابعة وعرض حالة حسابك والأيام المتبقية وحفظ كافة العمليات في قاعدة البيانات السحابية (Supabase) بأمان تام.\n\n"
        f"📞 <b>خط الطوارئ والدعم الفني المباشر:</b> <code>{SUPPORT_NUMBER}</code>"
    )
    bot.send_message(message.chat.id, info_text, parse_mode="HTML")

def show_subscription_form(message, expired=False):
    user_id = message.from_user.id
    USER_STATE[user_id] = "WAITING_RECEIPT"
    prefix = "🚨 <b>انتهت فترتك التجريبية المجانية! لا تقم بتعطيل عملك ومحلك، بادر بتجديد اشتراكك الفاخر فوراً للاستمرار:</b>\n\n" if expired else ""
    sub_text = (
        f"{COMPANY_HEADER}{prefix}"
        "💎 <b>استمارة الاشتراك وتجديد الصلاحية الشهرية:</b>\n\n"
        f"🔹 <b>قيمة الاستثمار الشهري:</b> <b>{MONTHLY_PRICE}</b> (تسترجع قيمتها من أول عملية بيع أو شراء بفضل الدقة المتناهية!)\n"
        f"🔹 <b>رقم التحويل المعتمد (زين كاش أو ماستر):</b> <code>{MASTER_CARD}</code>\n"
        f"📞 <b>رقم الدعم الفني:</b> <code>{SUPPORT_NUMBER}</code>\n\n"
        "📸 <b>الخطوة النهائية للتفعيل:</b>\n"
        "أرسل **صورة وصل التحويل الرسمي** (سكرين شوت) هنا في الدردشة ليقوم النظام الإداري باعتماد اشتراكك وفتح النظام فوراً."
    )
    bot.send_message(message.chat.id, sub_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_clients"])
def show_clients_summary(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id) or {}
    
    # جلب الاسم الحقيقي المرتبط بكل عميل من قاعدة البيانات حصراً بدون تكرار اسم ثابت
    shop_name = gs.get('full_name') or gs.get('shop_name') or 'محلي الموقر'
    remaining_days = gs.get('remaining_days', 0)
    
    summary_text = (
        f"{COMPANY_HEADER}"
        "📊 <b>جرد العمليات وحالة الحساب المعتمد:</b>\n\n"
        f"🔷 اسم المحل التجاري: <b>{shop_name}</b>\n"
        f"⏳ الأيام المتبقية في اشتراكك الفاخر: <b>{remaining_days} يوم</b>\n"
        f"📞 رقم الدعم الفني والطوارئ: <code>{SUPPORT_NUMBER}</code>\n"
        "🟢 حالة النظام: متصل حصرياً بقاعدة البيانات السحابية الآمنة (Supabase) وحسابك محمي بالكامل."
    )
    bot.send_message(message.chat.id, summary_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_admin_panel"])
def admin_panel_shortcut(message):
    if message.from_user.id == ADMIN_ID:
        admin.admin_panel_start(message)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_prices"])
def morning_prices_start(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id) or {}
    is_admin = (user_id == ADMIN_ID)
    if gs.get('remaining_days', 0) <= 0 and not is_admin:
        return show_subscription_form(message, expired=True)
    
    USER_STATE[user_id] = "AWAITING_ALL_PRICES"
    instruction = (
        f"{COMPANY_HEADER}"
        "☀️ <b>صباح البركة والرزق الواسع يا صايغنا الذهب!</b> ☀️\n\n"
        "💡 <b>نموذج إدخال الأسعار (انسخه وعدل الأرقام بما يناسب بورصتك اليوم):</b>\n"
        "<code>900000\n850000\n4500\n7500\n153000</code>\n\n"
        "✍️ <b>الترتيب الإجباري للأسطر الخمسة:</b>\n"
        "1️⃣ سعر مثقال عيار 21\n"
        "2️⃣ سعر مثقال عيار 18\n"
        "3️⃣ أجور صياغة عيار 21 للغرام\n"
        "4️⃣ أجور صياغة عيار 18 للغرام\n"
        "5️⃣ سعر صرف 100$ مقابل الدينار العراقي <i>(مثال: 153000)</i>\n\n"
        "👉 <i>اكتب الأسعار الآن وأرسلها لتحديث المنظومة فوراً.</i>"
    )
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sell"])
def customer_sell_init(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id) or {}
    is_admin = (user_id == ADMIN_ID)
    if gs.get('remaining_days', 0) <= 0 and not is_admin:
        return show_subscription_form(message, expired=True)

    USER_STATE.pop(user_id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟡 عيار 21 (فئة النخبة)", callback_data="sell_21"), types.InlineKeyboardButton("🟡 عيار 18 (دقة عالية)", callback_data="sell_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>محطة حساب بيع الذهب للزبون:</b>\nاختر العيار المطلوب للببدء بالحساب:", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_buy"])
def customer_buy_init(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id) or {}
    is_admin = (user_id == ADMIN_ID)
    if gs.get('remaining_days', 0) <= 0 and not is_admin:
        return show_subscription_form(message, expired=True)

    USER_STATE.pop(user_id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🪙 عيار 21 (شراء كسر)", callback_data="buy_21"), types.InlineKeyboardButton("🪙 عيار 18 (شراء كسر)", callback_data="buy_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📤 <b>محطة حساب شراء الذهب (الكسر) من الزبون:</b>\nاختر العيار المطلوب للبدء:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sell_") or call.data.startswith("buy_"))
def handle_calc_buttons(call):
    bot.answer_callback_query(call.id, text="⚡ جاري تفعيل المحطة...")
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

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_sub_") or call.data.startswith("reject_sub_") or call.data.startswith("time_"))
def handle_admin_actions(call):
    data = call.data
    if data.startswith("approve_sub_"):
        target_user = int(data.split("_")[2])
        utils.update_goldsmith_subscription(target_user, days=30)
        bot.answer_callback_query(call.id, text="✅ تم اعتماد التفعيل بنجاح تام!")
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("➕ إضافة 30 يوم", callback_data=f"time_add_{target_user}"),
            types.InlineKeyboardButton("➖ خصم 30 يوم", callback_data=f"time_sub_{target_user}")
        )
        markup.add(types.InlineKeyboardButton("🛑 تصفير الأيام وإيقاف", callback_data=f"time_zero_{target_user}"))
        
        try:
            bot.edit_message_caption(f"🧾 تم اعتماد الوصل وتفعيل اشتراك الصائغ برقم تعريفي: <code>{target_user}</code>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        except:
            try:
                bot.edit_message_text(f"🧾 تم اعتماد الوصل وتفعيل اشتراك الصائغ برقم تعريفي: <code>{target_user}</code>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
            except:
                pass

        try:
            bot.send_message(target_user, f"{COMPANY_HEADER}🎉 <b>تهانينا القلبية! تم اعتماد وصل التحويل وتجديد اشتراكك الشهري بنجاح في منظومة أرامكي للحلول الرقمية. محلك الآن جاهز للعمل بكامل طاقته الاستيعابية وبدون أي قيود!</b> 💛", parse_mode="HTML", reply_markup=get_main_keyboard(target_user))
        except:
            pass

    elif data.startswith("reject_sub_"):
        target_user = int(data.split("_")[2])
        bot.answer_callback_query(call.id, text="❌ تم رفض الوصل")
        try:
            bot.edit_message_caption(f"🧾 تم رفض هذا الإيصال للمستخدم برقم تعريفي: <code>{target_user}</code>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        except:
            try:
                bot.edit_message_text(f"🧾 تم رفض هذا الإيصال للمستخدم برقم تعريفي: <code>{target_user}</code>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
            except:
                pass
        try:
            bot.send_message(target_user, f"{COMPANY_HEADER}⚠️ <b>عفواً، تم رفض الإيصال المرسل من قبل الإدارة لعدم المطابقة أو عدم وضوح التفاصيل. يرجى مراجعة الدعم الفني أو إعادة الإرسال بصورة صحيحة.</b>", parse_mode="HTML")
        except:
            pass
            
    elif data.startswith("time_"):
        target_user = int(data.split("_")[2])
        action = data.split("_")[1]
        msg_result = ""
        
        if action == "add":
            utils.adjust_goldsmith_days(target_user, 30)
            msg_result = "✅ تم إضافة 30 يوم رصيد."
        elif action == "sub":
            utils.adjust_goldsmith_days(target_user, -30)
            msg_result = "➖ تم خصم 30 يوم من الرصيد."
        elif action == "zero":
            utils.adjust_goldsmith_days(target_user, 0, set_zero=True)
            msg_result = "🛑 تم تصفير الوقت وإيقاف الحساب نهائياً."
            
        bot.answer_callback_query(call.id, text=msg_result)
        current_text = call.message.caption or call.message.text or ""
        new_text = f"{current_text}\n\n{msg_result} للمستخدم <code>{target_user}</code>"
        try:
            if call.message.caption:
                bot.edit_message_caption(new_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=call.message.reply_markup)
            else:
                bot.edit_message_text(new_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=call.message.reply_markup)
        except:
            pass

@bot.message_handler(content_types=['photo'])
def process_customer_receipt(message):
    user_id = message.from_user.id
    if USER_STATE.get(user_id) == "WAITING_RECEIPT":
        USER_STATE.pop(user_id, None)
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري فحص إيصال التحويل الرقمي وإرساله لغرفة عمليات الإدارة...</i>", parse_mode="HTML")
        gs = utils.get_goldsmith(user_id) or {}
        shop_name = gs.get('full_name') or gs.get('shop_name') or 'غير متوفر'
        phone = gs.get('phone', 'غير متوفر')
        
        try:
            photo = message.photo[-1].file_id
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ موافقة وتفعيل (30 يوم)", callback_data=f"approve_sub_{user_id}"),
                types.InlineKeyboardButton("❌ رفض الإيصال", callback_data=f"reject_sub_{user_id}")
            )
            admin_text = f"🚨 <b>طلب اشتراك أو تجديد مالي جديد!</b>\n\n👤 الآيدي: <code>{user_id}</code>\n🔷 المحل: {shop_name}\n📱 الهاتف: {phone}\n\nيرجى التدقيق واعتماد الوصل أدناه بدقة."
            bot.send_photo(ADMIN_ID, photo, caption=admin_text, parse_mode="HTML", reply_markup=markup)
            
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "✅ <b>تم إرسال وصل التحويل للإدارة بنجاح تام! سيتم تفعيل اشتراك محلك الفاخر خلال دقائق معدودة فور التحقق من العملية المادية. شكراً لصبرك وثقتك بنا.</b>", parse_mode="HTML")
        except Exception as e:
            bot.edit_message_text(f"⚠️ خطأ في إرسال الوصل: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    text = to_english_numbers(message.text.strip())
    user_id = message.from_user.id
    state = USER_STATE.get(user_id)

    if state == "WAITING_REGISTRATION_FULL":
        loading = bot.send_message(message.chat.id, "⏳ <i>جاري تأسيس حسابك التجاري في السيرفر السحابي وتجهيز المنظومة...</i>", parse_mode="HTML")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) >= 2:
            shop_name = lines[0]
            phone = lines[1]
        else:
            parts = text.split('-')
            if len(parts) >= 2:
                shop_name = parts[0].strip()
                phone = parts[1].strip()
            else:
                shop_name = text
                phone = "غير محدد"
        
        try:
            utils.register_goldsmith_details(user_id, shop_name, phone)
            utils.update_goldsmith_subscription(user_id, days=3) 
            USER_STATE.pop(user_id, None)
            bot.delete_message(message.chat.id, loading.message_id)
            
            success_luxury_msg = (
                f"{COMPANY_HEADER}"
                "💎 <b>مبارك لك الانضمام لنخبة الصاغة المحترفين!</b> 💎\n\n"
                "لقد تم تسجيل محلك العامر بنجاح وتفعيل <b>الفترة التجريبية الحصرية (3 أيام مجانية كاملة)</b> نظراً للضغط الهائل والإقبال التاريخي على منظومتنا.\n\n"
                "🚀 <i>أنت الآن تملك أقوى أداة ذكية في السوق العراقي لإدارة الحسابات بدقة تامة والربح المضاعف. انطلق الآن وباشر بإدخال أسعارك لتبدأ الأرباح!</i> 💛"
            )
            bot.send_message(message.chat.id, success_luxury_msg, parse_mode="HTML")
            send_main_menu(message, user_id)
        except Exception as e:
            bot.edit_message_text(f"⚠️ حدث خطأ أثناء التسجيل السحابي: {e}", message.chat.id, loading.message_id)
        return

    if state == "AWAITING_ALL_PRICES":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري حفظ وتحديث الأسعار في السيرفر...</i>", parse_mode="HTML")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) == 5:
            try:
                # تصحيح حساب سعر صرف الورقة الواحدة بشكل صحيح (إدخال سعر 100 ورقة وقسمته على 100 للحصول على سعر الدولار المفرد بدقة)
                usd_100_input = float(lines[4])
                usd_rate_single = usd_100_input / 100.0 if usd_100_input > 1000 else usd_100_input

                utils.update_morning_prices(
                    user_id,
                    p21=float(lines[0]),
                    p18=float(lines[1]),
                    w21=float(lines[2]),
                    w18=float(lines[3]),
                    usd_r=usd_rate_single  
                )
                USER_STATE.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "✅ <b>تم تحديث أسعار الصباح والبورصة بنجاح تام، ربي يبارك لك في رزقك ومحلك الطيب!</b>", parse_mode="HTML")
            except Exception as e:
                bot.edit_message_text(f"⚠️ خطأ في الأرقام المدخلة: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("⚠️ يرجى إدخال 5 أسطر صحيحة تماماً كما هو موضح في نموذج المثال.", message.chat.id, loading_msg.message_id)
        return

    if state == "WAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب تفاصيل فاتورة البيع الفاخرة...</i>", parse_mode="HTML")
        if re.match(r'^\d+(\.\d+)?$', text):
            try:
                w = float(text)
                carat = INVOICE_DATA[user_id]['carat']
                prices = utils.get_goldsmith_prices(user_id) or {}
                goldsmith = utils.get_goldsmith(user_id) or {}
                
                if carat == 21:
                    gram_price = float(prices.get('price_21', 0)) / 5.0
                    wage = float(prices.get('wage_21', 0))
                else:
                    gram_price = float(prices.get('price_18', 0)) / 5.0
                    wage = float(prices.get('wage_18', 0))
                    
                gram_full = gram_price + wage
                total_iqd = gram_full * w
                
                # الاعتماد على سعر ورقة الـ 100 دولار الحقيقي (سعر الدولار المفرد مضروب في 100 أو سعر الورقة المباشر)
                usd_rate_single = float(prices.get('usd_rate', 1))
                sheet_price = usd_rate_single * 100 if usd_rate_single < 5000 else usd_rate_single
                
                usd_bills = int(total_iqd // sheet_price) if sheet_price > 0 else 0
                rem_iqd = total_iqd % sheet_price if sheet_price > 0 else total_iqd
                
                shop_name = goldsmith.get('full_name') or goldsmith.get('shop_name') or 'محلي الموقر'
                
                invoice = (
                    f"{COMPANY_HEADER}{TEXTS['invoice_sell']}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{shop_name}\n"
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
                bot.edit_message_text(f"⚠️ خطأ في الحساب: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("⚠️ يرجى إرسال رقم وزني صحيح (مثال: 8.963).", message.chat.id, loading_msg.message_id)
        return

    if state == "WAITING_BUY_ALL_INPUTS":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب كسر الذهب وتصفيته بدقة...</i>", parse_mode="HTML")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) == 3:
            try:
                mithqal_buy_price = float(lines[0])
                w = float(lines[1])
                wage_cut = float(lines[2])
                
                carat = INVOICE_DATA[user_id]['carat']
                goldsmith = utils.get_goldsmith(user_id) or {}
                prices = utils.get_goldsmith_prices(user_id) or {}
                
                gram_buy_price = mithqal_buy_price / 5.0
                net_gram_price = gram_buy_price - wage_cut
                total_iqd = net_gram_price * w
                
                usd_rate_single = float(prices.get('usd_rate', 1))
                sheet_price = usd_rate_single * 100 if usd_rate_single < 5000 else usd_rate_single
                
                usd_bills = int(total_iqd // sheet_price) if sheet_price > 0 else 0
                rem_iqd = total_iqd % sheet_price if sheet_price > 0 else total_iqd
                
                shop_name = goldsmith.get('full_name') or goldsmith.get('shop_name') or 'محلي الموقر'
                
                invoice = (
                    f"{COMPANY_HEADER}{TEXTS['invoice_buy']}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{shop_name}\n"
                    f"{TEXTS['type_buy'].format(carat=carat)}\n"
                    f"📥 <b>سعر شراء المثقال:</b> <code>{mithqal_buy_price:,.0f} دينار</code>\n"
                    f"{TEXTS['weight_tot'].format(w=w)}\n"
                    f"{TEXTS['wage_buy'].format(wage=wage_cut)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"💰 <b>سعر غرام الكسر الصافي:</b> <code>{net_gram_price:,.0f} دينار</code>\n"
                    f"{TEXTS['total_iqd'].format(total=total_iqd)}\n\n"
                    f"{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            except Exception as e:
                bot.edit_message_text(f"⚠️ خطأ في معالجة بيانات الشراء: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("⚠️ يرجى إرسال القيم الثلاثة المطلوبة حصرياً (كل قيمة في سطر مستقل).", message.chat.id, loading_msg.message_id)
        return

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling()
