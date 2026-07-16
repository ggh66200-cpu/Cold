import telebot, os, utils, time
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
# جلب توكن البوت بأمان من بيئة السيرفر
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot.remove_webhook()
print("🤖 Telegram Bot has started polling successfully!")

USER_STATES = {}

CANCEL_COMMANDS = ["💰 بيع للزبون", "⚖️ شراء من زبون", "⚙️ إعدادات الصباح", "⬅️ الرجوع للرئيسية", "/start"]

@bot.message_handler(commands=['start'])
def start(m):
    USER_STATES[m.chat.id] = {}
    
    is_active, count = utils.check_user(m.chat.id)
    if not is_active:
        bot.send_message(m.chat.id, "⚠️ عذراً، انتهت الفترة التجريبية المجانية (7 أيام). يرجى الاشتراك لتفعيل الخدمة.")
        return
        
    welcome_text = (
        f"✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\n"
        f"مرحباً بك في نظام الصياغة الذكي الأسرع والأدق في العراق! 👑\n"
        f"البوت مصمم بالكامل لتسهيل حسابات البيع والشراء اليومية لمحلك بدقة متناهية وبلمسة زر واحدة.\n\n"
        f"👥 **عدد الصاغة النشطين في النظام حالياً:** `{count} صائغ`\n\n"
        f"نسأل الله العلي القدير أن يبارك في تجارتكم ويفتح لكم أبواب الرزق الحلال الوفير. 🌸\n"
        f"يرجى اختيار العملية المطلوبة من الأزرار أدناه 👇"
    )
    utils.send_main_menu(bot, m.chat.id, welcome_text)

@bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات الصباح")
def morning_settings(m):
    USER_STATES[m.chat.id] = {}
    
    is_active, _ = utils.check_user(m.chat.id)
    if not is_active: return
    
    data = utils.get_data()
    s = data['settings']
    
    msg = (f"☀️ **صباح الرزق والبركة والسعادة يا طيب!** ☀️\n"
           f"نسأل الله أن يجعل هذا اليوم يوماً مباركاً، مليئاً بالزبائن والخير الوفير لعملكم وحلالكم. 🌸✨\n\n"
           f"📋 **إعدادات الصباح الحالية لمحلك:**\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"🔹 سعر مثقال عيار 21: `{s['mithqal_21']:,.0f} دينار`\n"
           f"🔹 سعر مثقال عيار 18: `{s['mithqal_18']:,.0f} دينار`\n"
           f"🔨 أجور صياغة غرام 21: `{s['labor_21']:,.0f} دينار`\n"
           f"🔨 أجور صياغة غرام 18: `{s['labor_18']:,.0f} دينار`\n"
           f"💵 سعر الـ 100 دولار: `{s['usd_100']:,.0f} دينار`\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"💡 لتحديث جميع هذه الأسعار بسهولة وبدون كتابة أكواد إنجليزية، يرجى الضغط على الزر أدناه وسنسألك عنها خطوة بخطوة! 👇")
           
    markup = types.InlineKeyboardMarkup()
    btn_update = types.InlineKeyboardButton("📝 تحديث كل الأسعار", callback_data="start_morning_wizard")
    markup.add(btn_update)
    bot.send_message(m.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

# معالجة انطلاق معالج التحديث المتتالي (Wizard)
@bot.callback_query_handler(func=lambda call: call.data == "start_morning_wizard")
def callback_update_settings(call):
    chat_id = call.message.chat.id
    USER_STATES[chat_id] = {"action": "WIZARD", "state": "WIZARD_MITHQAL_21"}
    
    bot.delete_message(chat_id, call.message.message_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ الرجوع للرئيسية")
    
    bot.send_message(
        chat_id,
        "⚙️ **البدء بتحديث أسعار الصباح**\n\n"
        "📝 **الخطوة 1/5:**\nأرسل سعر مثقال عيار 21 الجديد (بالأرقام فقط - مثال: 450000):",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def router(m):
    chat_id = m.chat.id
    text = m.text.strip()
    
    is_active, _ = utils.check_user(chat_id)
    if not is_active:
        bot.send_message(chat_id, "⚠️ انتهى اشتراكك التجريبي. يرجى التواصل مع الدعم لتفعيل الحساب.")
        return

    # 1️⃣ معالجة الأوامر الرئيسية المباشرة
    if text in CANCEL_COMMANDS:
        USER_STATES[chat_id] = {} # تصفير الحالة
        
        if text == "/start" or text == "⬅️ الرجوع للرئيسية":
            utils.send_main_menu(bot, chat_id, "✨ تم الرجوع إلى القائمة الرئيسية. اختر العملية المطلوبة أدناه 👇")
            return
            
        elif text == "💰 بيع للزبون":
            USER_STATES[chat_id] = {"action": "SELL", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(
                chat_id, 
                "💰 **بيع للزبون**\n\nاختر طريقة الحساب والعيار المطلوب من الأزرار أدناه 👇", 
                parse_mode="Markdown", 
                reply_markup=utils.get_karat_unit_keyboard()
            )
            return
            
        elif text == "⚖️ شراء من زبون":
            USER_STATES[chat_id] = {"action": "BUY", "state": "CHOOSE_KARAT_OR_UNIT"}
            bot.send_message(
                chat_id, 
                "⚖️ **شراء من زبون**\n\nاختر طريقة الحساب والعيار المطلوب من الأزرار أدناه 👇", 
                parse_mode="Markdown", 
                reply_markup=utils.get_karat_unit_keyboard()
            )
            return

    # 2️⃣ التحقق من وجود حالة نشطة
    state_data = USER_STATES.get(chat_id, {})
    if not state_data:
        utils.send_main_menu(bot, chat_id, "⚠️ يرجى اختيار عملية من القائمة أدناه للبدء 👇")
        return

    action = state_data.get("action")
    state = state_data.get("state")

    # 3️⃣ معالجة الـ Wizard لتحديث الأسعار خطوة بخطوة بالكامل باللغة العربية
    if action == "WIZARD":
        try:
            val = float(text.replace(",", "").replace(" ", ""))
            if val < 0: raise ValueError
            
            if state == "WIZARD_MITHQAL_21":
                state_data["w_mithqal_21"] = val
                state_data["state"] = "WIZARD_MITHQAL_18"
                bot.send_message(chat_id, "📝 **الخطوة 2/5:**\nأدخل سعر مثقال عيار 18 الجديد (بالأرقام فقط):")
                
            elif state == "WIZARD_MITHQAL_18":
                state_data["w_mithqal_18"] = val
                state_data["state"] = "WIZARD_LABOR_21"
                bot.send_message(chat_id, "📝 **الخطوة 3/5:**\nأدخل أجور صياغة غرام 21 الجديدة (بالأرقام فقط):")
                
            elif state == "WIZARD_LABOR_21":
                state_data["w_labor_21"] = val
                state_data["state"] = "WIZARD_LABOR_18"
                bot.send_message(chat_id, "📝 **الخطوة 4/5:**\nأدخل أجور صياغة غرام 18 الجديدة (بالأرقام فقط):")
                
            elif state == "WIZARD_LABOR_18":
                state_data["w_labor_18"] = val
                state_data["state"] = "WIZARD_USD_100"
                bot.send_message(chat_id, "📝 **الخطوة 5/5 والأخيرة:**\nأدخل سعر الـ 100 دولار المعتمد بالدينار (بالأرقام فقط):")
                
            elif state == "WIZARD_USD_100":
                # حفظ البيانات كلها بالسيرفر فوراً
                utils.update_setting("mithqal_21", state_data["w_mithqal_21"])
                utils.update_setting("mithqal_18", state_data["w_mithqal_18"])
                utils.update_setting("labor_21", state_data["w_labor_21"])
                utils.update_setting("labor_18", state_data["w_labor_18"])
                utils.update_setting("usd_100", val)
                
                # الرسالة المعسلة والجميلة التي تفتح النفس
                sweet_msg = (
                    f"🎉 **يا مية هلا وغلا بعيوني! تم الحفظ والحمد لله بنجاح تام** 🌸✨\n\n"
                    f"تم تحديث كافة أسعار الصباح في السيرفر وتأمينها بالكامل.\n"
                    f"عساها فاتحة خير ورزق وفير يملي حلالك وأيامك بركة وسعادة! 💸💛\n"
                    f"ربي يفتحها بوجهك ويجعل كل عملية تسويها اليوم عملية مباركة تسعد خاطرك الطيب وتفرح گلبك الدافئ! 🥰☕"
                )
                USER_STATES[chat_id] = {}
                utils.send_main_menu(bot, chat_id, sweet_msg)
                
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال قيمة رقمية صحيحة فقط (مثال: 450000):")
        return

    # جلب أحدث الإعدادات المسجلة بالسيرفر حالياً (يضمن عدم القفل على القيم القديمة)
    data = utils.get_data()
    settings = data['settings']

    # 4️⃣ اختيار العيار والوحدة
    if state == "CHOOSE_KARAT_OR_UNIT":
        mapping = {
            "غرام عيار 21": (21, "gram"),
            "غرام عيار 18": (18, "gram"),
            "مثقال عيار 21": (21, "mithqal"),
            "مثقال عيار 18": (18, "mithqal")
        }
        
        if text not in mapping:
            bot.send_message(chat_id, "⚠️ يرجى الاختيار من الأزرار المتاحة فقط أو الضغط على رجوع!")
            return
            
        karat, unit = mapping[text]
        state_data["karat"] = karat
        state_data["unit"] = unit
        
        if action == "SELL":
            state_data["state"] = "AWAITING_WEIGHT"
            unit_text = "بالغرام" if unit == "gram" else "بالمثقال"
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("⬅️ الرجوع للرئيسية")
            
            bot.send_message(
                chat_id, 
                f"⚖️ لقد اخترت **{text}**.\n\nالرجاء إرسال الوزن المطلوب بيعه لزبون ({unit_text}):", 
                parse_mode="Markdown", 
                reply_markup=markup
            )
            
        elif action == "BUY":
            state_data["state"] = "AWAITING_MITHQAL_PRICE"
            morning_price = settings[f"mithqal_{karat}"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(f"استخدام السعر الصباحي ({morning_price:,} دينار)")
            markup.add("⬅️ الرجوع للرئيسية")
            
            bot.send_message(
                chat_id, 
                f"💰 لقد اخترت **{text}**.\n\nالرجاء إدخال سعر شراء المثقال المتفق عليه حالياً بالدينار:\n(أو اضغط على زر السعر الصباحي المقترح أدناه 👇)", 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        return

    # 5️⃣ استلام سعر شراء المثقال (شراء فقط)
    if state == "AWAITING_MITHQAL_PRICE" and action == "BUY":
        karat = state_data["karat"]
        morning_price = settings[f"mithqal_{karat}"]
        
        if text.startswith("استخدام السعر الصباحي"):
            price = morning_price
        else:
            try:
                clean_text = text.replace(",", "").replace(" ", "").replace("دينار", "")
                price = float(clean_text)
            except ValueError:
                bot.send_message(chat_id, "⚠️ يرجى كتابة السعر كأرقام فقط (مثال: 450000) أو الضغط على السعر المقترح!")
                return
                
        state_data["mithqal_price"] = price
        state_data["state"] = "AWAITING_LABOR"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("0")
        markup.add("⬅️ الرجوع للرئيسية")
        
        bot.send_message(
            chat_id, 
            "🔥 أدخل أجور الخصم أو الصهر للغرام الواحد بالدينار:\n(اكتب 0 إذا لا يوجد خصم)", 
            parse_mode="Markdown", 
            reply_markup=markup
        )
        return

    # 6️⃣ استلام أجور الصياغة (بيع) أو الصهر (شراء)
    if state == "AWAITING_LABOR":
        karat = state_data["karat"]
        
        if action == "SELL":
            default_labor = settings[f"labor_{karat}"]
            if text.startswith("استخدام الأجور الصباحية"):
                labor = default_labor
            else:
                try:
                    clean_text = text.replace(",", "").replace(" ", "").replace("دينار", "")
                    labor = float(clean_text)
                except ValueError:
                    bot.send_message(chat_id, "⚠️ يرجى كتابة الأجور كأرقام فقط (مثال: 10000)!")
                    return
            
            state_data["labor"] = labor
            calculate_and_send_sell_invoice(chat_id, state_data)
            
        elif action == "BUY":
            try:
                clean_text = text.replace(",", "").replace(" ", "").replace("دينار", "")
                labor = float(clean_text)
            except ValueError:
                bot.send_message(chat_id, "⚠️ يرجى كتابة الخصم كأرقام فقط (مثال: 0)!")
                return
                
            state_data["labor"] = labor
            state_data["state"] = "AWAITING_WEIGHT"
            
            unit_text = "بالغرام" if state_data["unit"] == "gram" else "بالمثقال"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("⬅️ الرجوع للرئيسية")
            
            bot.send_message(
                chat_id, 
                f"⚖️ أدخل الوزن المراد شراؤه من الزبون ({unit_text}):", 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        return

    # 7️⃣ استلام الوزن وحساب الفاتورة النهائية
    if state == "AWAITING_WEIGHT":
        try:
            clean_text = text.replace(",", "").replace(" ", "")
            weight = float(clean_text)
        except ValueError:
            bot.send_message(chat_id, "⚠️ خطأ! يرجى إدخال رقم صحيح للوزن (مثال: 12.5):")
            return
            
        state_data["weight"] = weight
        
        if action == "SELL":
            state_data["state"] = "AWAITING_LABOR"
            default_labor = settings[f"labor_{state_data['karat']}"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(f"استخدام الأجور الصباحية ({default_labor:,} دينار)")
            markup.add("⬅️ الرجوع للرئيسية")
            
            bot.send_message(
                chat_id, 
                f"🔨 أرسل أجور صياغة الغرام الواحد بالدينار:\n(أو اضغط على زر الصياغة الصباحية المعتادة أدناه 👇)", 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        elif action == "BUY":
            calculate_and_send_buy_invoice(chat_id, state_data)
        return


def calculate_and_send_sell_invoice(chat_id, state_data):
    # جلب فوري لأحدث الأسعار من ملف الـ JSON لكسر القفل
    data = utils.get_data()
    settings = data['settings']
    
    # رسالة اللودنج الحركية والفعاليات الرياضية اللطيفة
    loading_msg = bot.send_message(chat_id, "⚖️ جاري حساب الوزن الإجمالي والورق والدينار الحالي... ⚡📊")
    time.sleep(1) # تأخير لمدة ثانية واحدة ليعطي طابع الذكاء والاهتمام بالوزن
    bot.delete_message(chat_id, loading_msg.message_id)
    
    try:
        karat = state_data["karat"]
        unit = state_data["unit"]
        weight = state_data["weight"]
        labor = state_data["labor"]
        
        mithqal_price = settings[f"mithqal_{karat}"]
        usd_100 = settings["usd_100"]
        
        gram_price = mithqal_price / 5
        
        if unit == "gram":
            total_grams = weight
            unit_text = "غرام"
            unit_arabic = "حساب بالغرام"
        else:
            total_grams = weight * 5
            unit_text = "مثقال"
            unit_arabic = "حساب بالمثقال"
            
        total_iqd = (gram_price + labor) * total_grams
        
        # حساب الورق والدينار العراقي (بدون كسور وكلمة دنانير)
        paper_and_dinar_text = utils.calculate_paper_and_dinar(total_iqd, usd_100)
        
        invoice = (
            f"🧾 **فاتورة بيع ذهب للزبون**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **العيار وطريقة الحساب**: عيار {karat} ({unit_arabic})\n"
            f"🔹 **الوزن المطلوب**: `{weight}` {unit_text}\n"
            f"⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.2f}` غرام\n"
            f"🔨 **أجور صياغة الغرام**: `{labor:,.0f} دينار`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 **سعر غرام الذهب الصافي**: `{gram_price:,.0f} دينار`\n"
            f"💵 **السعر الكلي بالدينار العراقي**:\n"
            f"👉 **`{total_iqd:,.0f} دينار`**\n\n"
            f"💵 **صافي الحساب بالورق والدينار**:\n"
            f"👉 **`{paper_and_dinar_text}`**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌸 **ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب!** ✨💛"
        )
        
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice)
        
    except Exception as e:
        print(f"Sell Calculation Error: {e}")
        bot.send_message(chat_id, "⚠️ حدث خطأ أثناء حساب الفاتورة. يرجى إعادة المحاولة.")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "تم تصفير العملية بسبب خطأ.")


def calculate_and_send_buy_invoice(chat_id, state_data):
    # جلب فوري لأحدث الأسعار من ملف الـ JSON لكسر القفل
    data = utils.get_data()
    settings = data['settings']
    
    # رسالة اللودنج الحركية والفعاليات الرياضية اللطيفة
    loading_msg = bot.send_message(chat_id, "🔥 جاري فحص الذهب وخصم أجور الصهر والورق... ⚖️✨")
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
            unit_text = "غرام"
            unit_arabic = "حساب بالغرام"
        else:
            total_grams = weight * 5
            unit_text = "مثقال"
            unit_arabic = "حساب بالمثقال"
            
        total_iqd = net_gram_price * total_grams
        
        # حساب الورق والدينار العراقي (بدون كسور وكلمة دنانير)
        paper_and_dinar_text = utils.calculate_paper_and_dinar(total_iqd, usd_100)
        
        invoice = (
            f"🧾 **فاتورة شراء ذهب من زبون**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **العيار وطريقة الشراء**: عيار {karat} ({unit_arabic})\n"
            f"🔹 **الوزن المستلم**: `{weight}` {unit_text}\n"
            f"⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.2f}` غرام\n"
            f"🔥 **خصم الصهر/أجور الجرام**: `{labor:,.0f} دينار`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 **سعر الشراء المعتمد للمثقال**: `{mithqal_price:,.0f} دينار`\n"
            f"💰 **سعر غرام الشراء الصافي**: `{net_gram_price:,.0f} دينار`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 **المبلغ الكلي المدفوع بالدينار العراقي**:\n"
            f"👉 **`{total_iqd:,.0f} دينار`**\n\n"
            f"💵 **صافي الحساب بالورق والدينار**:\n"
            f"👉 **`{paper_and_dinar_text}`**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌸 **تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير!** ✨"
        )
        
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, invoice)
        
    except Exception as e:
        print(f"Buy Calculation Error: {e}")
        bot.send_message(chat_id, "⚠️ حدث خطأ أثناء حساب الفاتورة. يرجى إعادة المحاولة.")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "تم تصفير العملية بسبب خطأ.")

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
