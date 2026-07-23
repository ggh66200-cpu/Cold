import os
import re
import telebot
from telebot import types
from flask import Flask
import threading
import utils
import admin

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

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

USER_STATE = {}
INVOICE_DATA = {}

# النصوص العربية والأزرار الكاملة والمشروحة
TEXTS = {
    "welcome": "👋 أهلاً بك في <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع لإدارة حسابات الصياغة محلياً ودولياً.\nالرجاء استخدام الأزرار أدناه للبدء بالعمليات اليومية لمحلك الحلال 👇",
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
    utils.get_goldsmith(user_id)
    USER_STATE.pop(user_id, None)
    markup = get_main_keyboard()
    bot.send_message(message.chat.id, COMPANY_HEADER + TEXTS["welcome"], parse_mode="HTML", reply_markup=markup)

# زر شرح النظام
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

# زر استمارة الاشتراك
@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sub"])
def show_subscription_form(message):
    user_id = message.from_user.id
    USER_STATE[user_id] = "WAITING_RECEIPT"
    sub_text = (
        f"{COMPANY_HEADER}"
        "📝 <b>استمارة الاشتراك وتجديد الصلاحية:</b>\n\n"
        f"🔹 <b>قيمة الاشتراك الشهري:</b> {MONTHLY_PRICE}\n"
        f"🔹 <b>رقم التحويل (ماستر كارد):</b> <code>{MASTER_CARD}</code>\n\n"
        "📸 <b>الخطوة المطلوبة:</b>\n"
        "أرسل **صورة وصل التحويل** (سكرين شوت) هنا في الدردشة ليتم تفعيل اشتراكك من قبل الإدارة فوراً."
    )
    bot.send_message(message.chat.id, sub_text, parse_mode="HTML")

# زر جرد العملاء
@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_clients"])
def show_clients_summary(message):
    user_id = message.from_user.id
    gs = utils.get_goldsmith(user_id)
    summary_text = (
        f"{COMPANY_HEADER}"
        "📊 <b>جرد العمليات والعملاء:</b>\n\n"
        f"🔷 المحل: {gs.get('full_name', 'محلي الموقر')}\n"
        "🟢 الحالة: حسابك مرتبط بقاعدة البيانات السحابية (Supabase) والعمليات مسجلة بأمان."
    )
    bot.send_message(message.chat.id, summary_text, parse_mode="HTML")

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
        "4️⃣ أجور 18 | 5️⃣ سعر صرف 100$ <i>(ملاحظة: سعر الدولار بالدينار هو للبيع والشراء مع الزبون)</i>\n\n"
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

# استقبال الإيصالات من العملاء وتحويلها للأدمن
@bot.message_handler(func=lambda m: USER_STATE.get(m.from_user.id) == "WAITING_RECEIPT", content_types=['photo'])
def process_customer_receipt(message):
    user_id = message.from_user.id
    USER_STATE.pop(user_id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ تفعيل", callback_data=f"approve_sub_{user_id}"), types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_sub_{user_id}"))
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🧾 إيصال جديد مرفق من الصائغ (آيدي): <code>{user_id}</code>", parse_mode="HTML", reply_markup=markup)
    bot.reply_to(message, "✅ تم استلام إيصالك بنجاح، وتم تحويله للإدارة للمراجعة والتفعيل.", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    if not message.text: return
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == TEXTS["btn_sell"]: return customer_sell_init(message)
    if text == TEXTS["btn_buy"]: return customer_buy_init(message)
    if text == TEXTS["btn_prices"]: return morning_prices_start(message)
    if text == TEXTS["btn_info"]: return show_system_info(message)
    if text == TEXTS["btn_sub"]: return show_subscription_form(message)
    if text == TEXTS["btn_clients"]: return show_clients_summary(message)

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
                bot.send_message(message.chat.id, "📊 <b>تم حفظ أسعار الصباح (مع اعتماد سعر الدولار للبيع والشراء) بنجاح!</b>", parse_mode="HTML", reply_markup=get_main_keyboard())
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
    print("🤖 Modular Bot and Admin System is running...")
    
    # تنظيف أي Webhook أو جلسة معلقة لمنع حدوث Conflict
    bot.remove_webhook()
    
    # تشغيل البوت مع تقليل الـ timeout لتجنب التعليق
    bot.infinity_polling(timeout=20, long_polling_timeout=20)
