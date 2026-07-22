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

# قاموس اللغات لقلب الفاتورة والواجهة بالكامل حسب اختيار الصائغ
LOCALES = {
    "ar": {
        "welcome": "👋 أهلاً بك في <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع لإدارة حسابات الصياغة محلياً ودولياً.\nالرجاء استخدام الأزرار أدناه للبدء بالعمليات اليومية لمحلك الحلال 👇",
        "invoice_sell": "🧾 <b>فاتورة بيع ذهب للزبون</b> 🧾",
        "shop": "🔷 المحل العامر: ",
        "type": "🔷 العيار ونوع الحساب: عيار {carat} (حساب بالغرام)",
        "weight_req": "🔷 الوزن المطلوب: {w} غرام",
        "weight_tot": "⚖️ الوزن الإجمالي بالجرام: {w} غرام",
        "wage": "🔨 أجور صياغة الغرام: {wage:,.0f} دينار",
        "clean_p": "💰 سعر غرام الذهب الصافي: {p:,.0f} دينار",
        "total_iqd": "💵 <b>السعر الكلي بالدنانير العراقي:</b>\n👉 <b>{total:,.0f} دينار</b>",
        "total_usd": "💵 <b>صافي الحساب بالورق والدينار:</b>\n👉 <b>{usd} ورقة و {rem:,.0f} دينار</b>",
        "footer": "🌸 ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب! 💛"
    },
    "ku": {
        "welcome": "👋خێرهاتی بۆ <b>SMART GOLD SYSTEM</b>\n\nسیستەمی ژیری خێرا بۆ بەڕێوەبردنی ژمێریاری زێڕەنگەری.\nتکایە دوگمەکانی خوارەوە بەکاربهێنە بۆ دەستپێکردن 👇",
        "invoice_sell": "🧾 <b>پسوولەی فرۆشتنی زێڕ</b> 🧾",
        "shop": "🔷 دوکان: ",
        "type": "🔷 عەیار و جۆری ژمارە: عەیاری {carat} (بە گرام)",
        "weight_req": "🔷 کێشی داواکراو: {w} گرام",
        "weight_tot": "⚖️ کۆی گشتی کێش بە گرام: {w} گرام",
        "wage": "🔨 کرێی دروستکردنی گرام: {wage:,.0f} دینار",
        "clean_p": "💰 نرخی گرامی زێڕی ساف: {p:,.0f} دينار",
        "total_iqd": "💵 <b>کۆی گشتی بە دیناری عێراقی:</b>\n👉 <b>{total:,.0f} دینار</b>",
        "total_usd": "💵 <b>کۆی گشتی بە دەفتەر و دینار:</b>\n👉 <b>{usd} وەرەقە و {rem:,.0f} دینار</b>",
        "footer": "🌸 پیرۆز بێت و حەڵاڵتان بێت! خودا بیکاتە مایەی خێر و بەرەکەت بۆ دوکانەکەتان! 💛"
    },
    "en": {
        "welcome": "👋 Welcome to <b>SMART GOLD SYSTEM</b>\n\nThe fastest intelligent system for goldsmith accounts.\nPlease use the buttons below to start daily operations 👇",
        "invoice_sell": "🧾 <b>Customer Gold Sales Invoice</b> 🧾",
        "shop": "🔷 Shop: ",
        "type": "🔷 Carat & Type: Carat {carat} (Gram calculation)",
        "weight_req": "🔷 Requested Weight: {w} grams",
        "weight_tot": "⚖️ Total Weight in Grams: {w} grams",
        "wage": "🔨 Making Charges per Gram: {wage:,.0f} IQD",
        "clean_p": "💰 Pure Gold Price per Gram: {p:,.0f} IQD",
        "total_iqd": "💵 <b>Total Price in Iraqi Dinar (IQD):</b>\n👉 <b>{total:,.0f} IQD</b>",
        "total_usd": "💵 <b>Net Account in USD & IQD:</b>\n👉 <b>{usd} Bills ($100) and {rem:,.0f} IQD</b>",
        "footer": "🌸 Congratulations! May it bring blessing and wide livelihood to your blessed shop! 💛"
    }
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    goldsmith = utils.get_goldsmith(message.from_user.id)
    lang = goldsmith.get("lang", "ar")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_prices = types.KeyboardButton("⚙️ إدخال أسعار الصباح اليومية")
    btn_lang = types.KeyboardButton("🌐 تغيير اللغة / Ziman / Language")
    btn_sell = types.KeyboardButton("📥 حساب بيع لزبون")
    btn_buy = types.KeyboardButton("📤 حساب شراء من زبون")
    
    markup.add(btn_prices, btn_lang, btn_sell, btn_buy)
    
    bot.send_message(message.chat.id, COMPANY_HEADER + LOCALES[lang]["welcome"], parse_mode="HTML", reply_markup=markup)

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
    bot.answer_callback_query(call.id, text="⏳ جاري حفظ إعدادات اللغة...")
    lang_code = call.data.split("_")[1]
    utils.update_goldsmith_lang(call.from_user.id, lang_code)
    
    bot.edit_message_text(f"{COMPANY_HEADER}💾 Done! تم حفظ اللغة وتحديث النظام بنجاح. أرسل /start لرؤية القائمة بلغتك الجديدة.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "⚙️ إدخال أسعار الصباح اليومية")
def morning_prices_start(message):
    user_id = message.from_user.id
    USER_STATE[user_id] = "AWAITING_ALL_PRICES"
    
    instruction = (
        f"{COMPANY_HEADER}"
        "☀️ <b>صباح الرزق والسعادة والبركة يا طيب!</b> ☀️\n\n"
        "💡 <b>مثال توضيحي للكتابة (انسخه وعدل الأرقام):</b>\n"
        "<code>900000\n"
        "850000\n"
        "4500\n"
        "7500\n"
        "153000</code>\n\n"
        "✍️ <b>الترتيب المطلوب بالأسطر:</b>\n"
        "1️⃣ السطر الأول: سعر مثقال عيار 21\n"
        "2️⃣ السطر الثاني: سعر مثقال عيار 18\n"
        "3️⃣ السطر الثالث: أجور صياغة غرام 21\n"
        "4️⃣ السطر الرابع: أجور صياغة غرام 18\n"
        "5️⃣ السطر الخامس: سعر صرف الـ 100 دولار بالدينار\n\n"
        "👉 <i>اكتب الأسعار الآن وأرسلها لتحديث المنظومة بلمحة بصر.</i>"
    )
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "📥 حساب بيع لزبون")
def customer_sell_init(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="calc_sell_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="calc_sell_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>حساب بيع ذهب لزبون:</b>\nاختر عيار الذهب المطلوب أدناه لتسهيل الحساب 👇", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_"))
def handle_calc_buttons(call):
    bot.answer_callback_query(call.id, text="⏳ جاري التحميل...")
    user_id = call.from_user.id
    mode = call.data.split("_")[1]
    carat = int(call.data.split("_")[2])
    
    INVOICE_DATA[user_id] = {'carat': carat}
    
    if mode == "sell":
        USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
        bot.send_message(call.message.chat.id, f"⚖️ <b>عيار {carat} البيع:</b>\nأرسل وزن الذهب بالغرام فقط (مثال: 8.963):", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = USER_STATE.get(user_id)

    if not state:
        return

    if state == "AWAITING_ALL_PRICES":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري حفظ الأسعار الحالية في سبيس...</i>", parse_mode="HTML")
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 5:
            try:
                p21, p18, w21, w18, usd = float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3]), float(lines[4])
                utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
                USER_STATE.pop(user_id, None)
                
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "📊 <b>تم حفظ وتحديث أسعار الصباح بنجاح في قاعدة البيانات!</b>", parse_mode="HTML")
            except:
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "⚠️ خطأ في الأرقام، أرسل 5 أسطر عددية صحيحة.")
        return

    if state == "WAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب الفاتورة بدقة...</i>", parse_mode="HTML")
        try:
            w = float(text)
            carat = INVOICE_DATA[user_id]['carat']
            
            # جلب البيانات الحية المحدثة من سبيس للمستخدم
            prices = utils.get_goldsmith_prices(user_id)
            goldsmith = utils.get_goldsmith(user_id)
            lang = goldsmith.get("lang", "ar")
            tx = LOCALES[lang]
            
            # تصحيح سحب الأسعار والأجور الدقيقة بناءً على العيار المدخل
            m_price = float(prices['price_21']) if carat == 21 else float(prices['price_18'])
            wage = float(prices['wage_21']) if carat == 21 else float(prices['wage_18'])
            
            gram_clean_price = m_price / 5.0
            total_iqd = (gram_clean_price + wage) * w
            
            usd_rate = float(prices['usd_rate'])
            usd_bills = int(total_iqd // usd_rate)
            rem_iqd = total_iqd % usd_rate
            
            invoice = (
                f"{COMPANY_HEADER}"
                f"{tx['invoice_sell']}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['shop']}{goldsmith['full_name']}\n"
                f"{tx['type'].format(carat=carat)}\n"
                f"{tx['weight_req'].format(w=w)}\n"
                f"{tx['weight_tot'].format(w=w)}\n"
                f"{tx['wage'].format(wage=wage)}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['clean_p'].format(p=gram_clean_price)}\n"
                f"{tx['total_iqd'].format(total=total_iqd)}\n\n"
                f"{tx['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['footer']}"
            )
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, invoice, parse_mode="HTML")
        except Exception as e:
            print(f"Calculation Error: {e}")
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال وزن صحيح.")
        return

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
