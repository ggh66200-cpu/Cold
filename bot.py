import telebot, os, utils, subscription, time
from flask import Flask
from threading import Thread
from telebot import types

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active & Sleeping Disabled"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    print(f"🔥 Flask server is starting on port {port}...")
    app.run(host='0.0.0.0', port=port)

Thread(target=run_server).start()

print("🔑 Connecting to Telegram API...")
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot.remove_webhook()
print("🤖 Telegram Bot has started polling successfully!")

USER_STATES = {}

# قائمة تصفير العمليات في اللغات الثلاث
CANCEL_COMMANDS = [
    # العربية
    "💰 بيع للزبون", "⚖️ شراء من زبون", "⚙️ إعدادات الصباح", "⬅️ الرجوع للرئيسية", "/start",
    # الكردية
    "💰 فرۆشتن بە کڕیار", "⚖️ کڕین لە کڕیار", "⚙️ ڕێکخستنەکانی بەیانی", "⬅️ گەڕانەوە بۆ سەرەکی",
    # الإنجليزية
    "💰 Sell to Customer", "⚖️ Buy from Customer", "⚙️ Morning Settings", "⬅️ Back to Main"
]

@bot.message_handler(commands=['start'])
def start(m):
    USER_STATES[m.chat.id] = {}
    _, count = subscription.check_user(m.chat.id)
    
    # رسالة ترحيبية ذكية تطلب اختيار اللغة عبر أزرار شفافة وتفاعلية فوراً
    welcome_msg = (
        f"👑 **مرحباً بك في نظام الصياغة الذكي**\n"
        f"👋 بەخێربێن بۆ سیستەمی زیرەکی زێڕینگەری\n"
        f"🌍 Welcome to the Smart Goldsmith System\n\n"
        f"👥 العميل رقم / کڕیاری ژمارە: `{count}`\n\n"
        f"الرجاء اختيار لغتك المفضلة أدناه لبدء العمل:\n"
        f"تکایە زمانەکەت لە خوارەوە هەڵبژێرە:\n"
        f"Please select your preferred language below:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_ar = types.InlineKeyboardButton("العربية 🇮🇶", callback_data="set_lang_ar")
    btn_ku = types.InlineKeyboardButton("کوردی ☀️", callback_data="set_lang_ku")
    btn_en = types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
    markup.add(btn_ar, btn_ku, btn_en)
    
    bot.send_message(m.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

# معالجة تغيير وتخزين اللغة فوراً بضغطة زر
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def callback_language(call):
    chat_id = call.message.chat.id
    lang_code = call.data.replace("set_lang_", "")
    
    # حفظ اللغة بالسيرفر للعميل
    utils.set_user_lang(chat_id, lang_code)
    
    # مسح الرسالة القديمة لاختيار اللغة
    bot.delete_message(chat_id, call.message.message_id)
    
    # جلب الرسالة المترجمة حسب اختيار العميل
    t = utils.TRANSLATIONS[lang_code]
    _, count = subscription.check_user(chat_id)
    
    # إرسال تأكيد تفعيل اللغة بنجاح
    bot.send_message(chat_id, t["lang_saved"])
    
    # إظهار القائمة الرئيسية باللغة المختارة فوراً
    main_welcome = t["welcome"].format(count=count)
    utils.send_main_menu(bot, chat_id, main_welcome, lang=lang_code)

@bot.message_handler(func=lambda m: m.text in ["⚙️ إعدادات الصباح", "⚙️ ڕێکخستنەکانی بەیانی", "⚙️ Morning Settings"])
def morning_settings(m):
    chat_id = m.chat.id
    USER_STATES[chat_id] = {}
    
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]
    
    data = utils.get_data()
    s = data['settings']
    
    # عرض رسالة إعدادات الصباح الحالية باللغة المحددة وتصميم معسل يخبل
    msg = t["morning_title"].format(
        mithqal_21=s['mithqal_21'],
        mithqal_18=s['mithqal_18'],
        labor_21=s['labor_21'],
        labor_18=s['labor_18'],
        usd_100=s['usd_100']
    )
           
    markup = types.InlineKeyboardMarkup()
    btn_update = types.InlineKeyboardButton(t["update_btn"], callback_data="start_morning_wizard")
    markup.add(btn_update)
    bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=markup)

# عند طلب تحديث الأسعار يرسل البوت سؤالاً واحداً مرتباً وموضحاً
@bot.callback_query_handler(func=lambda call: call.data == "start_morning_wizard")
def callback_update_settings(call):
    chat_id = call.message.chat.id
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]
    
    USER_STATES[chat_id] = {"action": "WIZARD", "state": "AWAITING_BULK"}
    bot.delete_message(chat_id, call.message.message_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(t["back"])
    
    bot.send_message(
        chat_id,
        t["wizard_prompt"],
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def router(m):
    chat_id = m.chat.id
    text = m.text.strip()
    lang = utils.get_user_lang(chat_id)
    t = utils.TRANSLATIONS[lang]

    # 1️⃣ معالجة إلغاء العمليات والرجوع للقائمة الرئيسية
    if text in CANCEL_COMMANDS:
        USER_STATES[chat_id] = {}
        
        if text in ["/start", "⬅️ الرجوع للرئيسية", "⬅️ گەڕانەوە بۆ سەرەکی", "⬅️ Back to Main"]:
            _, count = subscription.check_user(chat_id)
            utils.send_main_menu(bot, chat_id, t["welcome"].format(count=count), lang=lang)
            return
            
        elif text in ["💰 بيع للزبون", "💰 فرۆشتن بە کڕیار", "💰 Sell to Customer"]:
            USER_STATES[chat_id] = {"action": "SELL", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(
                chat_id, 
                t["choose_karat"], 
                parse_mode="Markdown", 
                reply_markup=utils.get_karat_unit_keyboard(lang)
            )
            return
            
        elif text in ["⚖️ شراء من زبون", "⚖️ کڕین لە کڕیار", "⚖️ Buy from Customer"]:
            USER_STATES[chat_id] = {"action": "BUY", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(
                chat_id, 
                t["choose_karat_buy"], 
                parse_mode="Markdown", 
                reply_markup=utils.get_karat_unit_keyboard(lang)
            )
            return

    state_data = USER_STATES.get(chat_id, {})
    if not state_data:
        _, count = subscription.check_user(chat_id)
        utils.send_main_menu(bot, chat_id, t["welcome"].format(count=count), lang=lang)
        return

    action = state_data.get("action")
    state = state_data.get("state")

    # 2️⃣ معالجة التحديث السريع والدفعة الواحدة (السؤال الواحد)
    if action == "WIZARD" and state == "AWAITING_BULK":
        try:
            vals = [int(v.replace(",", "")) for v in text.split()]
            if len(vals) != 5:
                raise ValueError
            
            # تحديث الكل وحفظه بالسيرفر فورا
            utils.update_all_settings(vals)
            USER_STATES[chat_id] = {}
            utils.send_main_menu(bot, chat_id, t["sweet_success"], lang=lang)
        except ValueError:
            bot.send_message(chat_id, t["error_format"], parse_mode="Markdown")
        return

    data = utils.get_data()
    settings = data['settings']

    # 3️⃣ اختيار العيار والوحدة
    if state == "CHOOSE_KARAT_OR_UNIT":
        # قواميس التوافق اللغوي لربط ضغطات المستخدم بالعيار والوحدة المطلوبة
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
            bot.send_message(chat_id, "⚠️ Please choose from the buttons only!")
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
            
            bot.send_message(
                chat_id, 
                t["req_weight"].format(text=text, unit_text=unit_text), 
                parse_mode="Markdown", 
                reply_markup=markup
            )
            
        elif action == "BUY":
            state_data["state"] = "AWAITING_MITHQAL_PRICE"
            morning_price = settings[f"mithqal_{karat}"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["use_morning_price"].format(price=morning_price))
            markup.add(t["back"])
            
            bot.send_message(
                chat_id, 
                t["req_price_buy"].format(text=text), 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        return

    # 4️⃣ استلام سعر شراء المثقال (شراء فقط)
    if state == "AWAITING_MITHQAL_PRICE" and action == "BUY":
        karat = state_data["karat"]
        morning_price = settings[f"mithqal_{karat}"]
        
        if text.startswith("استخدام السعر الصباحي") or text.startswith("بەکارهێنانی") or text.startswith("Use Morning"):
            price = morning_price
        else:
            try:
                clean_text = text.replace(",", "").replace(" ", "").replace("دينار", "").replace("IQD", "")
                price = float(clean_text)
            except ValueError:
                bot.send_message(chat_id, t["invalid_price"])
                return
                
        state_data["mithqal_price"] = price
        state_data["state"] = "AWAITING_LABOR"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("0")
        markup.add(t["back"])
        
        bot.send_message(
            chat_id, 
            t["req_labor_buy"], 
            parse_mode="Markdown", 
            reply_markup=markup
        )
        return

    # 5️⃣ استلام أجور الصياغة (بيع) أو الخصم والصهر (شراء)
    if state == "AWAITING_LABOR":
        karat = state_data["karat"]
        
        if action == "SELL":
            default_labor = settings[f"labor_{karat}"]
            if text.startswith("استخدام الأجور الصباحية") or text.startswith("بەکارهێنانی") or text.startswith("Use Morning"):
                labor = default_labor
            else:
                try:
                    clean_text = text.replace(",", "").replace(" ", "").replace("دينار", "").replace("IQD", "")
                    labor = float(clean_text)
                except ValueError:
                    bot.send_message(chat_id, t["invalid_labor"])
                    return
            
            state_data["labor"] = labor
            calculate_and_send_sell_invoice(chat_id, state_data, lang)
            
        elif action == "BUY":
            try:
                clean_text = text.replace(",", "").replace(" ", "").replace("دينار", "").replace("IQD", "")
                labor = float(clean_text)
            except ValueError:
                bot.send_message(chat_id, t["invalid_labor"])
                return
                
            state_data["labor"] = labor
            state_data["state"] = "AWAITING_WEIGHT"
            
            unit_text = "بالغرام" if state_data["unit"] == "gram" else "بالمثقال"
            if lang == "ku": unit_text = "بە گرام" if state_data["unit"] == "gram" else "بە مسقاڵ"
            elif lang == "en": unit_text = "in grams" if state_data["unit"] == "gram" else "in mithqal"
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["back"])
            
            bot.send_message(
                chat_id, 
                t["req_weight_buy"].format(unit_text=unit_text), 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        return

    # 6️⃣ استلام الوزن النهائي وحساب الفاتورة
    if state == "AWAITING_WEIGHT":
        try:
            clean_text = text.replace(",", "").replace(" ", "")
            weight = float(clean_text)
        except ValueError:
            bot.send_message(chat_id, t["invalid_weight"])
            return
            
        state_data["weight"] = weight
        
        if action == "SELL":
            state_data["state"] = "AWAITING_LABOR"
            default_labor = settings[f"labor_{state_data['karat']}"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(t["use_morning_labor"].format(labor=default_labor))
            markup.add(t["back"])
            
            bot.send_message(
                chat_id, 
                t["req_labor_sell"], 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        elif action == "BUY":
            calculate_and_send_buy_invoice(chat_id, state_data, lang)
        return


def calculate_and_send_sell_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    settings = data['settings']
    t = utils.TRANSLATIONS[lang]
    
    # رسالة لودنج رياضية حركية تفتح النفس وتدوم ثانية واحدة لتعطي فخامة للنظام
    loading_msg = bot.send_message(chat_id, t["loading_sell"])
    time.sleep(1)
    bot.delete_message(chat_id, loading_msg.message_id)
    
    try:
        karat = state_data["karat"]
        unit = state_data["unit"]
        weight = state_data["weight"]
        labor = state_data["labor"]
        
        mithqal_price = settings[f"mithqal_{karat}"]
        usd_100 = settings["usd_100"]
        
        # غرام الذهب الصافي = سعر المثقال / 5
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
        
        # حساب الورق والدينار بدقة بليغة بدون كلمة "دنانير" ومراعاة لغة المستخدم
        paper_and_dinar_text = utils.calculate_paper_and_dinar(total_iqd, usd_100, lang)
        
        invoice = t["sell_invoice"].format(
            karat=karat,
            unit_arabic=unit_arabic,
            weight=weight,
            unit_text=unit_text,
            total_grams=total_grams,
            labor=labor,
            gram_price=gram_price,
            total_iqd=total_iqd,
            paper_and_dinar_text=paper_and_dinar_text
        )
        
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice, lang=lang)
        
    except Exception as e:
        print(f"Sell Calculation Error: {e}")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "⚠️ Error.", lang=lang)


def calculate_and_send_buy_invoice(chat_id, state_data, lang):
    data = utils.get_data()
    settings = data['settings']
    t = utils.TRANSLATIONS[lang]
    
    loading_msg = bot.send_message(chat_id, t["loading_buy"])
    time.sleep(1)
    bot.delete_message(chat_id, loading_msg.message_id)
    
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
            karat=karat,
            unit_arabic=unit_arabic,
            weight=weight,
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
        print(f"Buy Calculation Error: {e}")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "⚠️ Error.", lang=lang)

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
