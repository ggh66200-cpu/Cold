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

# قواميس حفظ البيانات المؤقتة
USER_STATE = {}
INVOICE_DATA = {}
TEMP_DATA = {} # لحفظ خطوات الأسعار والشراء خطوة بخطوة

LOCALES = {
    "ar": {
        "welcome": "👋 أهلاً بك في <b>SMART GOLD SYSTEM</b>\n\nالمنظومة الذكية الأسرع لإدارة حسابات الصياغة محلياً ودولياً.\nالرجاء استخدام الأزرار أدناه للبدء بالعمليات اليومية لمحلك الحلال 👇",
        "btn_prices": "⚙️ إدخال أسعار الصباح اليومية",
        "btn_lang": "🌐 تغيير اللغة / Ziman / Language",
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
    },
    "ku": {
        "welcome": "👋خێرهاتی بۆ <b>SMART GOLD SYSTEM</b>\n\nسیستەمی ژیری خێرا بۆ بەڕێوەبردنی ژمێریاری زێڕەنگەری.\nتکایە دوگمەکانی خوارەوە بەکاربهێنە بۆ دەستپێکردن 👇",
        "btn_prices": "⚙️ تۆمارکردنی نرخەکانی بەیانی",
        "btn_lang": "🌐 گۆڕینی زمان / Language",
        "btn_sell": "📥 ئەژماری فرۆشتن بە کڕیار",
        "btn_buy": "📤 ئەژماری کڕین لە کڕیار",
        "invoice_sell": "🧾 <b>پسوولەی فرۆشتنی زێڕ</b> 🧾",
        "invoice_buy": "📥 <b>پسوولەی کڕینی زێڕ لە کڕیار</b> 📥",
        "shop": "🔷 دوکان: ",
        "type_sell": "🔷 عەیار و جۆری ژمارە: عەیاری {carat} (فرۆشتن بە گرام)",
        "type_buy": "🔷 عەیار و جۆری ژمارە: عەیاری {carat} (کڕین بە گرام)",
        "weight_req": "🔷 کێشی داواکراو: {w} گرام",
        "weight_tot": "⚖️ کۆی گشتی کێش بە گرام: {w} گرام",
        "wage_sell": "🔨 کرێی دروستکردنی گرام (زیادکراو): {wage:,.0f} دينار",
        "wage_buy": "🔨 کرێی داشکاندن (دابەزیو): {wage:,.0f} دينار",
        "clean_p": "💰 نرخی گرامی زێڕی ساف: {p:,.0f} دينار",
        "full_p": "💵 نرخی گرام لەگەڵ کرێی دروستکردن: {p:,.0f} دينار",
        "total_iqd": "💵 <b>کۆی گشتی بە دیناری عێراقی:</b>\n👉 <b>{total:,.0f} دينار</b>",
        "total_usd": "💵 <b>کۆی گشتی بە دەفتەر و دینار:</b>\n👉 <b>{usd} وەرەقە و {rem:,.0f} دينار</b>",
        "footer": "🌸 پیرۆز بێت و حەڵاڵتان بێت! خودا بیکاتە مایەی خێر و بەرەکەت بۆ دوکانەکەتان! 💛",
        "req_weight_sell": "⚖️ <b>عەیاری {carat} (ئەژماری فرۆشتن):</b>\nتکایە کێشی زێڕەکە بە گرام بنێرە (نموونە: 8.963):",
    },
    "en": {
        "welcome": "👋 Welcome to <b>SMART GOLD SYSTEM</b>\n\nThe fastest intelligent system for goldsmith accounts.\nPlease use the buttons below to start daily operations 👇",
        "btn_prices": "⚙️ Enter Daily Morning Prices",
        "btn_lang": "🌐 Change Language / Ziman",
        "btn_sell": "📥 Calculate Sale to Customer",
        "btn_buy": "📤 Calculate Purchase from Customer",
        "invoice_sell": "🧾 <b>Customer Gold Sales Invoice</b> 🧾",
        "invoice_buy": "📥 <b>Purchase Gold From Customer Invoice</b> 📥",
        "shop": "🔷 Shop: ",
        "type_sell": "🔷 Carat & Type: Carat {carat} (Gram Sale)",
        "type_buy": "🔷 Carat & Type: Carat {carat} (Gram Purchase)",
        "weight_req": "🔷 Requested Weight: {w} grams",
        "weight_tot": "⚖️ Total Weight in Grams: {w} grams",
        "wage_sell": "🔨 Making Charges per Gram (Added): {wage:,.0f} IQD",
        "wage_buy": "🔨 Making Charges Deduction (Subtracted): {wage:,.0f} IQD",
        "clean_p": "💰 Pure Gold Price per Gram: {p:,.0f} IQD",
        "full_p": "💵 Gram Price with Making Charges: {p:,.0f} IQD",
        "total_iqd": "💵 <b>Total Price in Iraqi Dinar (IQD):</b>\n👉 <b>{total:,.0f} IQD</b>",
        "total_usd": "💵 <b>Net Account in USD & IQD:</b>\n👉 <b>{usd} Bills ($100) and {rem:,.0f} IQD</b>",
        "footer": "🌸 Congratulations! May it bring blessing and wide livelihood to your blessed shop! 💛",
        "req_weight_sell": "⚖️ <b>Carat {carat} (Sales Calculation):</b>\nSend gold weight in grams only (e.g., 8.963):",
    }
}

def get_main_keyboard(lang):
    tx = LOCALES.get(lang, LOCALES["ar"])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_prices = types.KeyboardButton(tx["btn_prices"])
    btn_lang = types.KeyboardButton(tx["btn_lang"])
    btn_sell = types.KeyboardButton(tx["btn_sell"])
    btn_buy = types.KeyboardButton(tx["btn_buy"])
    markup.add(btn_prices, btn_lang, btn_sell, btn_buy)
    return markup

def get_all_btn_texts(key):
    return [LOCALES["ar"][key].strip(), LOCALES["ku"][key].strip(), LOCALES["en"][key].strip()]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    USER_STATE.pop(message.from_user.id, None)
    goldsmith = utils.get_goldsmith(message.from_user.id)
    lang = goldsmith.get("lang", "ar")
    markup = get_main_keyboard(lang)
    bot.send_message(message.chat.id, COMPANY_HEADER + LOCALES[lang]["welcome"], parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.strip() in get_all_btn_texts("btn_lang"))
def change_language_menu(message):
    USER_STATE.pop(message.from_user.id, None)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("العربية (العراق)", callback_data="lang_ar"),
        types.InlineKeyboardButton("Kurdî (کوردی)", callback_data="lang_ku"),
        types.InlineKeyboardButton("English", callback_data="lang_en")
    )
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}🌐 يرجى اختيار لغة واجهة النظام المفضلة لمحلك الحلال:\n⚙️ Choose your language:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_lang_selection(call):
    bot.answer_callback_query(call.id, text="⏳...")
    lang_code = call.data.split("_")[1]
    utils.update_goldsmith_lang(call.from_user.id, lang_code)
    
    markup = get_main_keyboard(lang_code)
    bot.edit_message_text(f"{COMPANY_HEADER}💾 Done! تم حفظ اللغة وتحديث أزرار النظام بنجاح باللغة الجديدة.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
    bot.send_message(call.message.chat.id, LOCALES[lang_code]["welcome"], parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.strip() in get_all_btn_texts("btn_prices"))
def morning_prices_start(message):
    user_id = message.from_user.id
    USER_STATE[user_id] = "WAITING_P21"
    TEMP_DATA[user_id] = {}
    
    bot.send_message(
        message.chat.id, 
        f"{COMPANY_HEADER}☀️ <b>تحديث أسعار الصباح</b>\n\n💰 <b>الخطوة 1/5: سعر مثقال عيار 21</b>\nأرسل السعر كـ رقم فقط (مثال: 900000):", 
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: message.text.strip() in get_all_btn_texts("btn_sell"))
def customer_sell_init(message):
    USER_STATE.pop(message.from_user.id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="sell_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="sell_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>حساب بيع ذهب لزبون:</b>\nاختر عيار الذهب المطلوب أدناه لتسهيل الحساب 👇", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.strip() in get_all_btn_texts("btn_buy"))
def customer_buy_init(message):
    USER_STATE.pop(message.from_user.id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="buy_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="buy_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📤 <b>حساب شراء ذهب من زبون:</b>\nاختر عيار الذهب المراد شراؤه من الزبون 👇", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sell_") or call.data.startswith("buy_"))
def handle_calc_buttons(call):
    bot.answer_callback_query(call.id, text="⏳...")
    user_id = call.from_user.id
    
    mode = call.data.split("_")[0]     
    carat = int(call.data.split("_")[1]) 
    
    INVOICE_DATA[user_id] = {'carat': carat, 'mode': mode}
    TEMP_DATA[user_id] = {}
    
    goldsmith = utils.get_goldsmith(user_id)
    lang = goldsmith.get("lang", "ar")
    tx = LOCALES[lang]
    
    if mode == "sell":
        USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
        bot.send_message(call.message.chat.id, tx["req_weight_sell"].format(carat=carat), parse_mode="HTML")
    elif mode == "buy":
        USER_STATE[user_id] = "WAITING_BUY_PRICE"
        bot.send_message(call.message.chat.id, f"📥 <b>عيار {carat} (حساب شراء من زبون):</b>\n\n1️⃣ <b>الخطوة الأولى:</b> أرسل سعر شراء المثقال كـ رقم فقط (مثال: 780000):", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = USER_STATE.get(user_id)

    # حماية الأزرار الرئيسية
    if text in get_all_btn_texts("btn_sell"):
        customer_sell_init(message)
        return
    if text in get_all_btn_texts("btn_buy"):
        customer_buy_init(message)
        return
    if text in get_all_btn_texts("btn_lang"):
        change_language_menu(message)
        return
    if text in get_all_btn_texts("btn_prices"):
        morning_prices_start(message)
        return

    if not state:
        return

    # --- معالجة خطوات إدخال الأسعار الصباحية ---
    if state == "WAITING_P21":
        try:
            TEMP_DATA[user_id]['p21'] = float(text)
            USER_STATE[user_id] = "WAITING_P18"
            bot.send_message(message.chat.id, "💰 <b>الخطوة 2/5: سعر مثقال عيار 18</b>\nأرسل السعر كـ رقم فقط:", parse_mode="HTML")
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ خطأ! أرسل أرقاماً فقط.")
        return

    if state == "WAITING_P18":
        try:
            TEMP_DATA[user_id]['p18'] = float(text)
            USER_STATE[user_id] = "WAITING_W21"
            bot.send_message(message.chat.id, "🔨 <b>الخطوة 3/5: أجور صياغة غرام 21</b>\nأرسل الأجور كـ رقم فقط (مثال: 4500):", parse_mode="HTML")
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ خطأ! أرسل أرقاماً فقط.")
        return

    if state == "WAITING_W21":
        try:
            TEMP_DATA[user_id]['w21'] = float(text)
            USER_STATE[user_id] = "WAITING_W18"
            bot.send_message(message.chat.id, "🔨 <b>الخطوة 4/5: أجور صياغة غرام 18</b>\nأرسل الأجور كـ رقم فقط (مثال: 7500):", parse_mode="HTML")
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ خطأ! أرسل أرقاماً فقط.")
        return

    if state == "WAITING_W18":
        try:
            TEMP_DATA[user_id]['w18'] = float(text)
            USER_STATE[user_id] = "WAITING_USD"
            bot.send_message(message.chat.id, "💵 <b>الخطوة 5/5: سعر صرف الـ 100 دولار</b>\nأرسل السعر كـ رقم فقط (مثال: 153000):", parse_mode="HTML")
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ خطأ! أرسل أرقاماً فقط.")
        return

    if state == "WAITING_USD":
        try:
            usd = float(text)
            if usd <= 0:
                bot.send_message(message.chat.id, "⚠️ سعر الصرف لا يمكن أن يكون صفر. أدخل رقماً صحيحاً:")
                return
                
            p21 = TEMP_DATA[user_id]['p21']
            p18 = TEMP_DATA[user_id]['p18']
            w21 = TEMP_DATA[user_id]['w21']
            w18 = TEMP_DATA[user_id]['w18']
            
            loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري حفظ الأسعار الحالية...</i>", parse_mode="HTML")
            utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
            
            USER_STATE.pop(user_id, None)
            TEMP_DATA.pop(user_id, None)
            
            goldsmith = utils.get_goldsmith(user_id)
            lang = goldsmith.get("lang", "ar")
            markup = get_main_keyboard(lang)
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "📊 <b>تم حفظ وتحديث أسعار الصباح بنجاح!</b>", parse_mode="HTML", reply_markup=markup)
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ خطأ! أرسل أرقاماً فقط.")
        return

    # --- معالجة فاتورة البيع ---
    if state == "WAITING_WEIGHT_SELL":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب الفاتورة...</i>", parse_mode="HTML")
        try:
            w = float(text)
            carat = INVOICE_DATA[user_id]['carat']
            
            prices = utils.get_goldsmith_prices(user_id)
            goldsmith = utils.get_goldsmith(user_id)
            lang = goldsmith.get("lang", "ar")
            tx = LOCALES[lang]
            
            m_price = float(prices['price_21']) if carat == 21 else float(prices['price_18'])
            wage = float(prices['wage_21']) if carat == 21 else float(prices['wage_18'])
            
            gram_clean_price = m_price / 5.0
            gram_full_price = gram_clean_price + wage
            total_iqd = gram_full_price * w
            
            usd_rate = float(prices['usd_rate'])
            usd_bills = int(total_iqd // usd_rate) if usd_rate > 0 else 0
            rem_iqd = total_iqd % usd_rate if usd_rate > 0 else total_iqd
            
            invoice = (
                f"{COMPANY_HEADER}"
                f"{tx['invoice_sell']}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['shop']}{goldsmith.get('full_name', 'محلي الموقر')}\n"
                f"{tx['type_sell'].format(carat=carat)}\n"
                f"{tx['weight_req'].format(w=w)}\n"
                f"{tx['weight_tot'].format(w=w)}\n"
                f"{tx['wage_sell'].format(wage=wage)}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['clean_p'].format(p=gram_clean_price)}\n"
                f"{tx['full_p'].format(p=gram_full_price)}\n"
                f"{tx['total_iqd'].format(total=total_iqd)}\n\n"
                f"{tx['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['footer']}"
            )
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, invoice, parse_mode="HTML")
        except ValueError:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "⚠️ يرجى إدخال وزن صحيح كـ رقم فقط.")
        return

    # --- معالجة خطوات فاتورة الشراء من الزبون ---
    if state == "WAITING_BUY_PRICE":
        try:
            TEMP_DATA[user_id]['buy_price'] = float(text)
            USER_STATE[user_id] = "WAITING_BUY_WEIGHT"
            bot.send_message(message.chat.id, "⚖️ <b>الخطوة 2/3:</b> أرسل وزن الذهب بالغرام (مثال: 15.420):", parse_mode="HTML")
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ خطأ! أرسل رقماً صحيحاً فقط.")
        return

    if state == "WAITING_BUY_WEIGHT":
        try:
            TEMP_DATA[user_id]['buy_weight'] = float(text)
            USER_STATE[user_id] = "WAITING_BUY_WAGE"
            bot.send_message(message.chat.id, "🔨 <b>الخطوة 3/3:</b> أرسل أجور كسر الغرام (الداشكان) كـ رقم فقط (مثال: 2000):", parse_mode="HTML")
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ خطأ! أرسل الوزن كـ رقم صحيح.")
        return

    if state == "WAITING_BUY_WAGE":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب الفاتورة...</i>", parse_mode="HTML")
        try:
            wage = float(text)
            custom_m_price = TEMP_DATA[user_id]['buy_price']
            w = TEMP_DATA[user_id]['buy_weight']
            
            carat = INVOICE_DATA[user_id]['carat']
            prices = utils.get_goldsmith_prices(user_id)
            goldsmith = utils.get_goldsmith(user_id)
            lang = goldsmith.get("lang", "ar")
            tx = LOCALES[lang]
            
            gram_clean_price = custom_m_price / 5.0
            gram_full_price = gram_clean_price - wage
            total_iqd = gram_full_price * w
            
            usd_rate = float(prices['usd_rate'])
            usd_bills = int(total_iqd // usd_rate) if usd_rate > 0 else 0
            rem_iqd = total_iqd % usd_rate if usd_rate > 0 else total_iqd
            
            invoice = (
                f"{COMPANY_HEADER}"
                f"{tx['invoice_buy']}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['shop']}{goldsmith.get('full_name', 'محلي الموقر')}\n"
                f"{tx['type_buy'].format(carat=carat)}\n"
                f"{tx['weight_tot'].format(w=w)}\n"
                f"{tx['wage_buy'].format(wage=wage)}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['clean_p'].format(p=gram_clean_price)}\n"
                f"{tx['full_p'].format(p=gram_full_price)}\n"
                f"{tx['total_iqd'].format(total=total_iqd)}\n\n"
                f"{tx['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{tx['footer']}"
            )
            
            USER_STATE.pop(user_id, None)
            INVOICE_DATA.pop(user_id, None)
            TEMP_DATA.pop(user_id, None)
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, invoice, parse_mode="HTML")
        except ValueError:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "⚠️ خطأ! يرجى إرسال أجور الكسر كـ رقم فقط.")
        return

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
