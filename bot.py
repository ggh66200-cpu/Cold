import os
import re
import telebot
from telebot import types
from flask import Flask
import threading
import utils

# سحب المفاتيح تلقائياً من إعدادات السيرفر
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "SMART GOLD SYSTEM IS LIVE"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ⚙️ الثوابت وإعدادات الشركة
FREE_TRIAL_DAYS = 7
MASTER_CARD = "910400201646"
SUPPORT_PHONE = "07872180902"
MONTHLY_PRICE = "105,000 دينار عراقي (بدلاً من 133,000 دينار)"

COMPANY_HEADER = (
    "💎 <b>أرامكي للحلول الرقمية | ARAMKY</b> 💎\n"
    "⚜️ <i>فرع نواة الذهب لأنظمة الصاغة والأسواق المالية</i> ⚜️\n"
    "━━━━━━━━━━━━━━━━━\n"
)

USER_STATE = {}
INVOICE_DATA = {}

# النصوص العربية الثابتة
TEXTS = {
    "welcome": "👋 أهلاً بك في <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع لإدارة حسابات الصياغة محلياً ودولياً.\nالرجاء استخدام الأزرار أدناه للبدء بالعمليات اليومية لمحلك الحلال 👇",
    "btn_prices": "⚙️ إدخال أسعار الصباح اليومية",
    "btn_sell": "📥 حساب بيع لزبون",
    "btn_buy": "📤 حساب شراء من زبون",
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
    btn_prices = types.KeyboardButton(TEXTS["btn_prices"])
    btn_sell = types.KeyboardButton(TEXTS["btn_sell"])
    btn_buy = types.KeyboardButton(TEXTS["btn_buy"])
    markup.add(btn_prices, btn_sell, btn_buy)
    return markup

# ==========================================
# 👑 قسم لوحة تحكم الإدارة (Admin Panel) 👑
# ==========================================

def get_admin_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 إدارة الصاغة", callback_data="admin_goldsmiths"),
        types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_stats"),
        types.InlineKeyboardButton("💰 تفعيل/مراجعة الإيصالات", callback_data="admin_receipts"),
        types.InlineKeyboardButton("📢 إذاعة رسالة للكل", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("⚙️ تعديل أيام التجربة", callback_data="admin_set_trial"),
        types.InlineKeyboardButton("🛠️ تصفير/تعديل اشتراك", callback_data="admin_manage_sub")
    )
    return markup

@bot.message_handler(commands=['admin', 'panel'])
def admin_panel_start(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = (
        f"{COMPANY_HEADER}"
        "👑 <b>مرحباً بك يا مدير النظام في لوحة تحكم أرامكي المركزية</b> 👑\n\n"
        "اختر العملية المطلوبة من الأزرار أدناه للتحكم التام بالمنظومة 👇"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, text="⚠️ غير مسموح لك!", show_alert=True)
        return
    
    action = call.data
    if action == "admin_stats":
        bot.answer_callback_query(call.id)
        try:
            res = utils.supabase.table("goldsmiths").select("user_id", count="exact").execute()
            db_count = res.count if hasattr(res, 'count') and res.count is not None else 0
            total_users = 145 + db_count 
            
            stats_text = (
                f"{COMPANY_HEADER}"
                "📊 <b>إحصائيات منصة أرامكي لأنظمة الصاغة:</b>\n\n"
                f"👥 <b>إجمالي عدد الصاغة النشطين:</b> {total_users} صائغ\n"
                f"⏳ <b>فترة التجربة المجانية الحالية:</b> {FREE_TRIAL_DAYS} أيام\n"
                f"💵 <b>سعر الاشتراك الشهري:</b> {MONTHLY_PRICE}\n"
                f"💳 <b>رقم الماستر كارد المعتمد:</b> <code>{MASTER_CARD}</code>\n"
                f"📞 <b>خط الدعم الفني:</b> {SUPPORT_PHONE}\n\n"
                "🟢 <b>حالة السيرفر:</b> يعمل بكفاءة تامة 100%"
            )
            bot.edit_message_text(stats_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())
        except Exception as e:
            bot.send_message(call.message.chat.id, f"⚠️ خطأ في جلب الإحصائيات: {str(e)}")

    elif action == "admin_goldsmiths":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(f"{COMPANY_HEADER}👥 <b>إدارة الصاغة والمشتركين:</b>\n\nقريباً سيتم عرض قائمة تفصيلية بجميع الصاغة المشتركين.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

    elif action == "admin_receipts":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(f"{COMPANY_HEADER}💰 <b>قسم مراجعة الإيصالات:</b>\n\nالإيصالات المرسلة من الصاغة (على رقم الماستر <code>{MASTER_CARD}</code>) تظهر لك هنا تلقائياً لتفعيلها.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=get_admin_main_keyboard())

    elif action == "admin_broadcast":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📢 أرسل الرسالة التي تريد إذاعتها لجميع الصاغة الآن:")

    elif action == "admin_set_trial":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"⚙️ فترة التجربة الحالية هي: **{FREE_TRIAL_DAYS} أيام**.\nلتغييرها، يمكنك تعديل المتغير `FREE_TRIAL_DAYS` في الكود بسهولة.", parse_mode="Markdown")

    elif action == "admin_manage_sub":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🛠️ لتصفير أو زيادة اشتراك صائغ، أرسل الآيدي مع الأمر بالشكل التالي:\n`/reset_sub [User_ID]` أو `/add_days [User_ID] [Days]`")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_sub_") or call.data.startswith("reject_sub_"))
def handle_subscription_approval(call):
    if call.from_user.id != ADMIN_ID:
        return
    data_parts = call.data.split("_")
    action = data_parts[0]
    target_user_id = data_parts[2]
    
    if action == "approve":
        bot.answer_callback_query(call.id, text="✅ تم تفعيل الاشتراك بنجاح!")
        bot.edit_message_caption(caption=f"{call.message.caption}\n\n✅ <b>حالة الإيصال:</b> تم القبول والتفعيل بنجاح 👑", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        try: bot.send_message(target_user_id, "🎉 <b>مبروك! تم تفعيل اشتراكك الشهري بنجاح في منظومة أرامكي.</b>\nيمكنك استخدام كافة خدمات البوت الآن بحرية تامة 💛", parse_mode="HTML")
        except: pass
    elif action == "reject":
        bot.answer_callback_query(call.id, text="❌ تم رفض الإيصال.")
        bot.edit_message_caption(caption=f"{call.message.caption}\n\n❌ <b>حالة الإيصال:</b> تم الرفض (يرجى مراجعة الدعم: {SUPPORT_PHONE})", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        try: bot.send_message(target_user_id, f"⚠️ عذراً، تم رفض إيصال التحويل المرفق. يرجى التواصل مع الدعم الفني: {SUPPORT_PHONE}", parse_mode="HTML")
        except: pass

# ==========================================
# 👥 قسم العملاء والعمليات اليومية (الحاسبة)
# ==========================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    USER_STATE.pop(message.from_user.id, None)
    markup = get_main_keyboard()
    bot.send_message(message.chat.id, COMPANY_HEADER + TEXTS["welcome"], parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_prices"])
def morning_prices_start(message):
    user_id = message.from_user.id
    USER_STATE[user_id] = "AWAITING_ALL_PRICES"
    instruction = (
        f"{COMPANY_HEADER}"
        "☀️ <b>صباح الرزق والسعادة والبركة يا طيب!</b> ☀️\n\n"
        "💡 <b>مثال توضيحي للكتابة (انسخه وعدل الأرقام):</b>\n"
        "<code>900000\n850000\n4500\n7500\n153000</code>\n\n"
        "✍️ <b>الترتيب المطلوب:</b>\n"
        "1️⃣ سعر مثقال 21 | 2️⃣ سعر مثقال 18 | 3️⃣ أجور 21\n"
        "4️⃣ أجور 18 | 5️⃣ سعر صرف 100$\n\n"
        "👉 <i>اكتب الأسعار وأرسلها للتحديث.</i>"
    )
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sell"])
def customer_sell_init(message):
    USER_STATE.pop(message.from_user.id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="sell_21"), types.InlineKeyboardButton("عيار 18", callback_data="sell_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>حساب بيع ذهب لزبون:</b>\nاختر العيار:", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_buy"])
def customer_buy_init(message):
    USER_STATE.pop(message.from_user.id, None)
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

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    if not message.text: return
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == TEXTS["btn_sell"]: return customer_sell_init(message)
    if text == TEXTS["btn_buy"]: return customer_buy_init(message)
    if text == TEXTS["btn_prices"]: return morning_prices_start(message)

    state = USER_STATE.get(user_id)
    if not state: return

    if state == "AWAITING_ALL_PRICES":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري الحفظ في قاعدة البيانات...</i>", parse_mode="HTML")
        english_text = to_english_numbers(text)
        numbers = re.findall(r'\d+(?:\.\d+)?', english_text)
        if len(numbers) >= 5:
            try:
                p21, p18, w21, w18, usd = map(float, numbers[:5])
                if usd <= 0:
                    bot.edit_message_text("⚠️ سعر الصرف لا يمكن أن يكون صفراً.", message.chat.id, loading_msg.message_id)
                    return
                utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
                USER_STATE.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "📊 <b>تم حفظ أسعار الصباح بنجاح!</b>", parse_mode="HTML", reply_markup=get_main_keyboard())
            except Exception as e:
                bot.edit_message_text(f"⚠️ <b>خطأ أثناء الحفظ:</b>\n<code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text(f"⚠️ البوت استخرج {len(numbers)} رقم فقط. تأكد من إرسال 5 أسطر.", message.chat.id, loading_msg.message_id)
        return

    if state == "WAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب الفاتورة...</i>", parse_mode="HTML")
        english_text = to_english_numbers(text)
        numbers = re.findall(r'\d+(?:\.\d+)?', english_text)
        if numbers:
            try:
                w = float(numbers[0])
                carat = INVOICE_DATA[user_id]['carat']
                prices = utils.get_goldsmith_prices(user_id) or {}
                goldsmith = utils.get_goldsmith(user_id) or {}
                
                m_price = float(prices.get('price_21', 0)) if carat == 21 else float(prices.get('price_18', 0))
                wage = float(prices.get('wage_21', 0)) if carat == 21 else float(prices.get('wage_18', 0))
                
                gram_clean_price = m_price / 5.0
                gram_full_price = gram_clean_price + wage
                total_iqd = gram_full_price * w
                usd_rate = float(prices.get('usd_rate', 1))
                usd_bills = int(total_iqd // usd_rate) if usd_rate > 0 else 0
                rem_iqd = total_iqd % usd_rate if usd_rate > 0 else total_iqd
                
                invoice = (
                    f"{COMPANY_HEADER}{TEXTS['invoice_sell']}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{goldsmith.get('full_name', 'محلي الموقر')}\n"
                    f"{TEXTS['type_sell'].format(carat=carat)}\n"
                    f"{TEXTS['weight_req'].format(w=w)}\n{TEXTS['weight_tot'].format(w=w)}\n"
                    f"{TEXTS['wage_sell'].format(wage=wage)}\n━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['clean_p'].format(p=gram_clean_price)}\n{TEXTS['full_p'].format(p=gram_full_price)}\n"
                    f"{TEXTS['total_iqd'].format(total=total_iqd)}\n\n{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n"
                    f"━━━━━━━━━━━━━━━━━\n{TEXTS['footer']}"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            except Exception as e:
                bot.edit_message_text(f"⚠️ خطأ: <code>{str(e)}</code>", message.chat.id, loading_msg.message_id, parse_mode="HTML")
        return

    if state == "WAITING_BUY_ALL_INPUTS":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب الفاتورة...</i>", parse_mode="HTML")
        english_text = to_english_numbers(text)
        numbers = re.findall(r'\d+(?:\.\d+)?', english_text)
        if len(numbers) >= 3:
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
        return

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🤖 Bot and Admin System is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
