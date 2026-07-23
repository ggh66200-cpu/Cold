import os
import re
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
        "<code>900000\n"
        "850000\n"
        "4500\n"
        "7500\n"
        "153000</code>\n\n"
        "✍️ <b>الترتيب المطلوب بالأسطر لقاعدة البيانات:</b>\n"
        "1️⃣ السطر الأول: سعر مثقال عيار 21\n"
        "2️⃣ السطر الثاني: سعر مثقال عيار 18\n"
        "3️⃣ السطر الثالث: أجور صياغة غرام 21\n"
        "4️⃣ السطر الرابع: أجور صياغة غرام 18\n"
        "5️⃣ السطر الخامس: سعر صرف الـ 100 دولار بالدينار\n\n"
        "👉 <i>اكتب الأسعار الحالية الآن وأرسلها لتحديث المنظومة فوراً.</i>"
    )
    bot.send_message(message.chat.id, instruction, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_sell"])
def customer_sell_init(message):
    USER_STATE.pop(message.from_user.id, None)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عيار 21", callback_data="sell_21"),
               types.InlineKeyboardButton("عيار 18", callback_data="sell_18"))
    bot.send_message(message.chat.id, f"{COMPANY_HEADER}📥 <b>حساب بيع ذهب لزبون:</b>\nاختر عيار الذهب المطلوب أدناه لتسهيل الحساب 👇", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and message.text.strip() == TEXTS["btn_buy"])
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
    
    if mode == "sell":
        USER_STATE[user_id] = "WAITING_WEIGHT_SELL"
        bot.send_message(call.message.chat.id, TEXTS["req_weight_sell"].format(carat=carat), parse_mode="HTML")
    elif mode == "buy":
        USER_STATE[user_id] = "WAITING_BUY_ALL_INPUTS"
        bot.send_message(call.message.chat.id, TEXTS["req_buy_inputs"].format(carat=carat), parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    if not message.text:
        return
        
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == TEXTS["btn_sell"]:
        customer_sell_init(message)
        return
    if text == TEXTS["btn_buy"]:
        customer_buy_init(message)
        return
    if text == TEXTS["btn_prices"]:
        morning_prices_start(message)
        return

    state = USER_STATE.get(user_id)
    if not state:
        return

    if state == "AWAITING_ALL_PRICES":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري الحفظ في قاعدة البيانات...</i>", parse_mode="HTML")
        
        english_text = to_english_numbers(text)
        numbers = re.findall(r'\d+(?:\.\d+)?', english_text)
        
        if len(numbers) >= 5:
            try:
                p21 = float(numbers[0])
                p18 = float(numbers[1])
                w21 = float(numbers[2])
                w18 = float(numbers[3])
                usd = float(numbers[4])
                
                if usd <= 0:
                    bot.delete_message(message.chat.id, loading_msg.message_id)
                    bot.send_message(message.chat.id, "⚠️ عذراً، سعر الصرف لا يمكن أن يكون صفراً لتجنب أخطاء الحساب.")
                    return
                
                utils.update_goldsmith_prices(user_id, p21, p18, w21, w18, usd)
                USER_STATE.pop(user_id, None)
                markup = get_main_keyboard()
                
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, "📊 <b>تم حفظ وتحديث أسعار الصباح بنجاح!</b>", parse_mode="HTML", reply_markup=markup)
            except Exception as e:
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, f"⚠️ <b>حدث خطأ أثناء الحفظ في قاعدة البيانات:</b>\n\n<code>{str(e)}</code>", parse_mode="HTML")
        else:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, f"⚠️ البوت استخرج {len(numbers)} رقم فقط. تأكد من إرسال 5 أرقام.")
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
                    f"{COMPANY_HEADER}"
                    f"{TEXTS['invoice_sell']}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{goldsmith.get('full_name', 'محلي الموقر')}\n"
                    f"{TEXTS['type_sell'].format(carat=carat)}\n"
                    f"{TEXTS['weight_req'].format(w=w)}\n"
                    f"{TEXTS['weight_tot'].format(w=w)}\n"
                    f"{TEXTS['wage_sell'].format(wage=wage)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['clean_p'].format(p=gram_clean_price)}\n"
                    f"{TEXTS['full_p'].format(p=gram_full_price)}\n"
                    f"{TEXTS['total_iqd'].format(total=total_iqd)}\n\n"
                    f"{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['footer']}"
                )
                
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            except Exception as e:
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, f"⚠️ خطأ أثناء توليد الفاتورة:\n<code>{str(e)}</code>", parse_mode="HTML")
        else:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "⚠️ لم يتم التعرف على أي أرقام، يرجى كتابة الوزن بصورة صحيحة.")
        return

    if state == "WAITING_BUY_ALL_INPUTS":
        loading_msg = bot.send_message(message.chat.id, "⏳ <i>جاري احتساب الفاتورة...</i>", parse_mode="HTML")
        english_text = to_english_numbers(text)
        numbers = re.findall(r'\d+(?:\.\d+)?', english_text)
        
        if len(numbers) >= 3:
            try:
                custom_m_price = float(numbers[0])
                w = float(numbers[1])
                wage = float(numbers[2])
                
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
                    f"{COMPANY_HEADER}"
                    f"{TEXTS['invoice_buy']}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['shop']}{goldsmith.get('full_name', 'محلي الموقر')}\n"
                    f"{TEXTS['type_buy'].format(carat=carat)}\n"
                    f"{TEXTS['weight_tot'].format(w=w)}\n"
                    f"{TEXTS['wage_buy'].format(wage=wage)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['clean_p'].format(p=gram_clean_price)}\n"
                    f"{TEXTS['full_p'].format(p=gram_full_price)}\n"
                    f"{TEXTS['total_iqd'].format(total=total_iqd)}\n\n"
                    f"{TEXTS['total_usd'].format(usd=usd_bills, rem=rem_iqd)}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{TEXTS['footer']}"
                )
                
                USER_STATE.pop(user_id, None)
                INVOICE_DATA.pop(user_id, None)
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, invoice, parse_mode="HTML")
            except Exception as e:
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_message(message.chat.id, f"⚠️ خطأ أثناء توليد الفاتورة:\n<code>{str(e)}</code>", parse_mode="HTML")
        else:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, f"⚠️ البوت استخرج {len(numbers)} أرقام فقط. يرجى إرسال 3 أسطر.")
        return

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
    
