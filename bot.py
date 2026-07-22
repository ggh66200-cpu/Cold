import os
import telebot
from telebot import types
from flask import Flask
import threading
import utils

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "SMART GOLD SYSTEM IS LIVE"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

COMPANY_HEADER = (
    "💎 <b>أرامكي للحلول الرقمية | ARAMKY</b> 💎\n"
    "⚜️ <i>فرع نواة الذهب لأنظمة الصاغة والأسواق المالية</i> ⚜️\n"
    "━━━━━━━━━━━━━━━━━\n"
)

USER_STATE = {}
INVOICE_DATA = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_prices = types.KeyboardButton("⚙️ إدخال أسعار الصباح اليومية")
    btn_lang = types.KeyboardButton("🌐 تغيير اللغة / Ziman / Language")
    btn_sell = types.KeyboardButton("📥 حساب بيع لزبون")
    btn_buy = types.KeyboardButton("📤 حساب شراء من زبون")
    
    markup.add(btn_prices, btn_lang, btn_sell, btn_buy)
    
    welcome_text = (
        f"{COMPANY_HEADER}"
        "👋 أهلاً بك في <b>SMART GOLD SYSTEM</b>\n\n"
        "المنظومة الذكية الأسرع لإدارة حسابات الصياغة محلياً ودولياً.\n"
        "الرجاء استخدام الأزرار أدناه للبدء بالعمليات اليومية لمحلك الحلال 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=markup)

# ─── معالجة قائمة اللغات (بدون علامات وأعلام) ───
@bot.message_handler(func=lambda message: message.text == "🌐 تغيير اللغة / Ziman / Language")
def change_language_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("العربية (العراق)", callback_data="lang_ar"),
        types.InlineKeyboardButton("Kurdî (کوردی)", callback_data="lang_ku"),
        types.InlineKeyboardButton("English", callback_data="lang_en")
    )
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}🌐 يرجى اختيار لغة واجهة النظام المفضلة لمحلك الحلال:\n⚙️ Choose your language:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_lang_selection(call):
    # إشعار جاري التحميل الفوري
    bot.answer_callback_query(call.id, text="⏳ جاري التحميل وحفظ إعدادات اللغة...")
    
    lang_code = call.data.split("_")[1]
    utils.update_goldsmith_lang(call.from_user.id, lang_code)
    
    bot.edit_message_text(f"{COMPANY_HEADER}💾 تم حفظ إعدادات اللغة بنجاح في قاعدة البيانات سبيس! جميع فواتيرك القادمة ستتوافق مع اختيارك الجديد.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

# ─── معالجة أسعار الصباح مع أمثلة وشرح كامل ───
@bot.message_handler(func=lambda message: message.text == "⚙️ إدخال أسعار الصباح اليومية")
def morning_prices_start(message):
    user_id = message.from_user.id
    USER_STATE[user_id] = "AWAITING_ALL_PRICES"
    
    instruction = (
        f"{COMPANY_HEADER}"
        "☀️ <b>صباح الرزق والسعادة والبركة يا طيب!</b> ☀️\n\n"
        "📋 <b>شرح طريقة إدخال الأسعار اليومية:</b>\n"
        "يرجى كتابة الأسعار الحالية لمحلك وإرسالها في رسالة واحدة تحتوي على 5 أسطر مرقمة متتالية كما في المثال أدناه.\n\n"
        "💡 <b>مثال توضيحي للكتابة (انسخه وعدل الأرقام):</b>\n"
        "<code>900000\n"
        "450000\n"
        "10000\n"
        "1000\n"
        "155000</code>\n\n"
        "✍️ <b>الترتيب المطلوب بالأسطر:</b>\n"
        "1️⃣ السطر الأول: سعر مثقال عيار 21\n"
        "2️⃣ السطر الثاني: سعر مثقال عيار 18\n"
        "3️⃣ السطر الثالث: أجور صياغة غرام 21\n"
        "4️⃣ السطر الرابع: أجور صياغة غرام 18\n"
        "5️⃣ السطر الخامس: سعر صرف الـ 100 دولار بالدينار\n\n"
        "👉 <i>اكتب الأسعار الآن وأرسلها لتحديث المنظومة بلمحة بصر.</i>"
    )
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

# ─── معالجة حساب البيع والشراء ───
@bot.message_handler(func=lambda message: message.text == "📥 حساب بيع لزبون")
def customer_sell_init(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="calc_sell_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="calc_sell_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>حساب بيع ذهب لزبون:</b>\nاختر عيار الذهب المطلوب أدناه لتسهيل الحساب 👇", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📤 حساب شراء من زبون")
def customer_buy_init(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="calc_buy_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="calc_buy_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📤 <b>حساب شراء ذهب (كسر) من زبون:</b>\nاختر العيار المستلم من الزبون أدناه 👇", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_"))
def handle_calc_buttons(call):
    bot.answer_callback_query(call.id, text="⏳ جاري التحميل... يرجى إدخال البيانات المطلوبة")
    user_id = call.from_user.id
    mode = call.data.split("_")[1]
    carat = int(call.data.split("_")[2])
    
    INVOICE_DATA[user_id] = {'carat': carat}
    
    if mode == "sell":
        USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
        bot.send_message(call.message.chat.id, f"⚖️ <b>عيار {carat} البيع:</b>\nأرسل وزن الذهب بالغرام فقط (مثال: 4.963):", parse_mode="HTML")
    elif mode == "buy":
        USER_STATE[user_id] = "WAITING_LOGICAL_BUY"
        bot.send_message(call.message.chat.id, (
            f"📥 <b>حساب شراء عيار {carat} من زبون:</b>\n"
            "يرجى إرسال تفاصيل الشراء في رسالة واحدة مرتبة عمودياً (3 أسطر):\n\n"
            "<code>900000\n"
            "4.963\n"
            "0</code>\n\n"
            "1️⃣ سعر الشراء المعتمد للمثقال\n"
            "2️⃣ الوزن الإجمالي بالغرام\n"
            "3️⃣ خصم الصهر/أجور الجرام (اكتب 0 إذا لا يوجد)"
        ), parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = USER_STATE.get(user_id)

    if not state:
        return

    if state == "AWAITING_ALL_PRICES":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري التحميل ومعالجة الحسابات وحفظ الأسعار الحالية في سبيس...</i>", parse_mode="HTML")
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 5:
            try:
                p21, p18, w21, w18, usd = float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3]), float(lines[4])
                utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
                USER_STATE.pop(user_id, None)
                
                success_msg = (
                    f"{COMPANY_HEADER}"
                    f"📊 <b>إعدادات الصباح الحالية لمحلك:</b>\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"🔷 سعر مثقال عيار 21: {p21:,.0f} دينار\n"
                    f"🔷 سعر مثقال عيار 18: {p18:,.0f} دينار\n"
                    f"🔨 أجور صياغة غرام 21: {w21:,.0f} دينار\n"
                    f"🔨 أجور صياغة غرام 18: {w18:,.0f} دينار\n"
                    f"💵 سعر الـ 100 دولار: {usd:,.0f} دينار\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"💡 <i>تم الحفظ بنجاح! لتحديث جميع هذه الأسعار، اضغط على زر الإعدادات مجدداً.</i>"
                )
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, success_msg, parse_mode="HTML")
            except:
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "⚠️ خطأ في الأرقام المرسلة، يرجى إدخال أرقام صحيحة وعمودية كما في المثال.")
        return

    if state == "WAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب الفاتورة وجلب البيانات...</i>", parse_mode="HTML")
        try:
            w = float(text)
            carat = INVOICE_DATA[user_id]['carat']
            prices = utils.get_goldsmith_prices(user_id)
            goldsmith = utils.get_goldsmith(user_id)
            
            m_price = prices['price_21'] if carat == 21 else prices['price_18']
            wage = prices['wage_21'] if carat == 21 else prices['wage_18']
            
            gram_clean_price = m_price / 5.0
            total_iqd = (gram_clean_price + wage) * w
            
            usd_rate = prices['usd_rate']
            usd_bills = int(total_iqd // usd_rate)
            rem_iqd = total_iqd % usd_rate
            
            invoice = (
                f"{COMPANY_HEADER}"
                f"🧾 <b>فاتورة بيع ذهب للزبون</b> 🧾\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"🔷 المحل العامر: {goldsmith['full_name']}\n"
                f"🔷 العيار ونوع الحساب: عيار {carat} (حساب بالغرام)\n"
                f"🔷 الوزن المطلوب: {w} غرام\n"
                f"⚖️ الوزن الإجمالي بالجرام: {w} غرام\n"
                f"🔨 أجور صياغة الغرام: {wage:,.0f} دينار\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"💰 سعر غرام الذهب الصافي: {gram_clean_price:,.0f} دينار\n"
                f"💵 <b>السعر الكلي بالدنانير العراقي:</b>\n"
                f"👉 <b>{total_iqd:,.0f} دينار</b>\n\n"
                f"💵 <b>صافي الحساب بالورق والدينار:</b>\n"
                f"👉 <b>{usd_bills} ورقة و {rem_iqd:,.0f} دينار</b>\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! 💛"
            )
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, invoice, parse_mode="HTML")
        except:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال وزن صحيح (رقم فقط).")
        return

    if state == "WAITING_LOGICAL_BUY":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري معالجة الكسر واحتساب الفاتورة...</i>", parse_mode="HTML")
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            try:
                agreed_mitqal_p = float(lines[0])
                weight_grams = float(lines[1])
                discount_per_gram = float(lines[2])
                
                prices = utils.get_goldsmith_prices(user_id)
                goldsmith = utils.get_goldsmith(user_id)
                carat = INVOICE_DATA[user_id]['carat']
                
                agreed_gram_p = agreed_mitqal_p / 5.0
                net_gram_p = agreed_gram_p - discount_per_gram
                total_iqd = net_gram_p * weight_grams
                
                usd_bills = int(total_iqd // prices['usd_rate'])
                rem_iqd = total_iqd % prices['usd_rate']
                
                invoice = (
                    f"{COMPANY_HEADER}"
                    f"🧾 <b>فاتورة شراء ذهب من زبون</b> 🧾\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"🔷 المحل العامر: {goldsmith['full_name']}\n"
                    f"🔷 العيار وطريقة الشراء: عيار {carat} (حساب بالغرام)\n"
                    f"🔷 الوزن المستلم: {weight_grams} غرام\n"
                    f"⚖️ الوزن الإجمالي بالجرام: {weight_grams} غرام\n"
                    f"🔥 خصم الصهر/أجور الجرام: {discount_per_gram:,.0f} دينار\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"💰 سعر الشراء المعتمد للمثقال: {agreed_mitqal_p:,.0f} دينار\n"
                    f"💰 سعر غرام الشراء الصافي: {net_gram_p:,.0f} دينار\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"💵 <b>المبلغ الكلي المدفوع بالدينار العراقي:</b>\n"
                    f"👉 <b>{total_iqd:,.0f} دينار</b>\n\n"
                    f"💵 <b>صافي الحساب بالورق والدينار:</b>\n"
                    f"👉 <b>{usd_bills} ورقة و {rem_iqd:,.0f} دينار</b>\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"🌸 تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير! ✨"
                )
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            except:
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "⚠️ تأكد من إدخال الأسطر الثلاثة بشكل صحيح.")
        return

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("تم تشغيل البوت بنجاح...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
