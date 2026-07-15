import telebot, os, utils
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

# الذاكرة المؤقتة لحفظ حالة كل مستخدم لتفادي "اللطشة" والتكرار
USER_STATES = {}

CANCEL_COMMANDS = ["💰 بيع للزبون", "⚖️ شراء من زبون", "⚙️ إعدادات الصباح", "⬅️ الرجوع للرئيسية", "/start"]

# أسماء الإعدادات باللغة العربية لرسالة التحديث الجميلة
KEY_NAMES = {
    "mithqal_21": "سعر مثقال عيار 21",
    "mithqal_18": "سعر مثقال عيار 18",
    "labor_21": "أجور صياغة عيار 21",
    "labor_18": "أجور صياغة عيار 18",
    "usd_100": "سعر الـ 100 دولار"
}

@bot.message_handler(commands=['start'])
def start(m):
    # تصفير حالة المستخدم فوراً عند البدء لمنع التعليق
    USER_STATES[m.chat.id] = {}
    
    is_active, count = utils.check_user(m.chat.id)
    if not is_active:
        bot.send_message(m.chat.id, "⚠️ عذراً، انتهت الفترة التجريبية المجانية (7 أيام). يرجى الاشتراك لتفعيل الخدمة.")
        return
        
    welcome_text = (
        f"👋 **أهلاً بك في نظام الصياغة الذكي**\n\n"
        f"👥 أنت العميل رقم: `{count}` في نظامنا المتكامل.\n"
        f"🎁 لقد حصلت على اشتراك تجريبي مجاني لمدة **7 أيام**.\n\n"
        f"استخدم الأزرار بالأسفل لبدء العمليات فوراً وبكل دقة 👇"
    )
    utils.send_main_menu(bot, m.chat.id, welcome_text)

@bot.message_handler(func=lambda m: m.text == "⚙️ إعدادات الصباح")
def morning_settings(m):
    # تصفير أي عملية حسابية معلقة فوراً
    USER_STATES[m.chat.id] = {}
    
    is_active, _ = utils.check_user(m.chat.id)
    if not is_active: return
    
    data = utils.get_data()
    s = data['settings']
    
    msg = (f"⚙️ **إعدادات الصباح الحالية**\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"🔹 سعر مثقال 21: {s['mithqal_21']:,.0f} د.ع\n"
           f"🔹 سعر مثقال 18: {s['mithqal_18']:,.0f} د.ع\n"
           f"🔨 صياغة غرام 21: {s['labor_21']:,.0f} د.ع\n"
           f"🔨 صياغة غرام 18: {s['labor_18']:,.0f} د.ع\n"
           f"💵 سعر الـ 100 دولار: {s['usd_100']:,.0f} د.ع\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"💡 لتحديث أي قيمة، أرسل الأمر التالي:\n"
           f"`/set [المفتاح] [السعر]`\n\n"
           f"⚙️ **المفاتيح المتاحة:**\n"
           f"• `mithqal_21`\n"
           f"• `mithqal_18`\n"
           f"• `labor_21`\n"
           f"• `labor_18`\n"
           f"• `usd_100`\n\n"
           f"مثال لتحديث الدولار:\n`/set usd_100 153500`")
    bot.send_message(m.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['set'])
def update_val(m):
    USER_STATES[m.chat.id] = {} # تصفير الحالة
    try:
        parts = m.text.split()
        if len(parts) != 3:
            bot.reply_to(m, "⚠️ صيغة خاطئة. اكتبها هكذا: `/set usd_100 153000`")
            return
        key, val = parts[1], parts[2]
        
        if key not in KEY_NAMES:
            bot.reply_to(m, "⚠️ المفتاح غير صحيح. يرجى التأكد من المفاتيح المتاحة في إعدادات الصباح.")
            return
            
        utils.update_setting(key, val)
        
        # ✨ رسالة الحفظ الحلوة والمعسلة التي تفتح النفس ✨
        arabic_name = KEY_NAMES.get(key, key)
        sweet_msg = (
            f"🎉 **يا مية هلا وغلا بعيوني! تم الحفظ والحمد لله** 🌸✨\n\n"
            f"لقد قمت بتحديث **{arabic_name}** بنجاح وتثبيته على القيمة الجديدة: \n"
            f"💰 `{int(val):,}` د.ع\n\n"
            f"عساها فاتحة خير ورزق وفير يملي حلالك وأيامك بركة وسعادة! 💸💛 "
            f"ربي يفتحها بوجهك، ويجعل كل صفقة تسويها اليوم صفقة مباركة تسعد خاطرك الطيب وتفرح گلبك الدافئ! 🥰☕"
        )
        bot.send_message(m.chat.id, sweet_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Set Error: {e}")
        bot.reply_to(m, "⚠️ حدث خطأ في إدراج البيانات. يرجى إرسال رقم صحيح.")

@bot.message_handler(func=lambda m: True)
def router(m):
    chat_id = m.chat.id
    text = m.text.strip()
    
    is_active, _ = utils.check_user(chat_id)
    if not is_active:
        bot.send_message(chat_id, "⚠️ انتهى اشتراكك التجريبي. يرجى التواصل مع الدعم لتفعيل الحساب.")
        return

    # 1️⃣ معالجة الأوامر الرئيسية المباشرة (والتي تقوم بإلغاء أي عملية معلقة فوراً)
    if text in CANCEL_COMMANDS:
        USER_STATES[chat_id] = {} # تصفير الحالة تماماً
        
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

    # 2️⃣ التحقق من وجود حالة نشطة للمستخدم
    state_data = USER_STATES.get(chat_id, {})
    if not state_data:
        utils.send_main_menu(bot, chat_id, "⚠️ يرجى اختيار عملية من القائمة أدناه للبدء 👇")
        return

    action = state_data.get("action")
    state = state_data.get("state")
    data = utils.get_data()
    settings = data['settings']

    # 3️⃣ تنفيذ خطوة: اختيار العيار والوحدة
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
            markup.add(f"استخدام السعر الصباحي ({morning_price:,} د.ع)")
            markup.add("⬅️ الرجوع للرئيسية")
            
            bot.send_message(
                chat_id, 
                f"💰 لقد اخترت **{text}**.\n\nالرجاء إدخال سعر شراء المثقال المتفق عليه حالياً بالدنانير:\n(أو اضغط على زر السعر الصباحي المقترح أدناه 👇)", 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        return

    # 4️⃣ تنفيذ خطوة: استلام سعر شراء المثقال (خاص بالشراء فقط)
    if state == "AWAITING_MITHQAL_PRICE" and action == "BUY":
        karat = state_data["karat"]
        morning_price = settings[f"mithqal_{karat}"]
        
        if text.startswith("استخدام السعر الصباحي"):
            price = morning_price
        else:
            try:
                clean_text = text.replace(",", "").replace(" ", "").replace("د.ع", "")
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
            "🔥 أدخل أجور الخصم أو الصهر للغرام الواحد بالدنانير:\n(اكتب 0 إذا لا يوجد خصم)", 
            parse_mode="Markdown", 
            reply_markup=markup
        )
        return

    # 5️⃣ تنفيذ خطوة: استلام أجور الصياغة (بيع) أو الصهر (شراء)
    if state == "AWAITING_LABOR":
        karat = state_data["karat"]
        
        if action == "SELL":
            default_labor = settings[f"labor_{karat}"]
            if text.startswith("استخدام الأجور الصباحية"):
                labor = default_labor
            else:
                try:
                    clean_text = text.replace(",", "").replace(" ", "").replace("د.ع", "")
                    labor = float(clean_text)
                except ValueError:
                    bot.send_message(chat_id, "⚠️ يرجى كتابة الأجور كأرقام فقط (مثال: 10000)!")
                    return
            
            state_data["labor"] = labor
            # ننتقل الآن لحساب الفاتورة النهائية للبيع مباشرة
            calculate_and_send_sell_invoice(chat_id, state_data, settings)
            
        elif action == "BUY":
            try:
                clean_text = text.replace(",", "").replace(" ", "").replace("د.ع", "")
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

    # 6️⃣ تنفيذ خطوة: استلام الوزن وحساب الفاتورة النهائية
    if state == "AWAITING_WEIGHT":
        try:
            clean_text = text.replace(",", "").replace(" ", "")
            weight = float(clean_text)
        except ValueError:
            bot.send_message(chat_id, "⚠️ خطأ! يرجى إدخال رقم صحيح للوزن (مثال: 12.5):")
            return
            
        state_data["weight"] = weight
        
        if action == "SELL":
            # في البيع، استلام الوزن كان في الخطوة الثانية، والآن نسأل عن الصياغة
            state_data["state"] = "AWAITING_LABOR"
            default_labor = settings[f"labor_{state_data['karat']}"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(f"استخدام الأجور الصباحية ({default_labor:,} د.ع)")
            markup.add("⬅️ الرجوع للرئيسية")
            
            bot.send_message(
                chat_id, 
                f"🔨 أرسل أجور صياغة الغرام الواحد بالدنانير:\n(أو اضغط على زر الصياغة الصباحية المعتادة أدناه 👇)", 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        elif action == "BUY":
            # في الشراء، استلام الوزن هو الخطوة الأخيرة، نحسب الفاتورة مباشرة
            calculate_and_send_buy_invoice(chat_id, state_data, settings)
        return


def calculate_and_send_sell_invoice(chat_id, state_data, settings):
    try:
        karat = state_data["karat"]
        unit = state_data["unit"]
        weight = state_data["weight"]
        labor = state_data["labor"]
        
        mithqal_price = settings[f"mithqal_{karat}"]
        usd_100 = settings["usd_100"]
        
        # 📌 الحسابات الدقيقة للذهب العراقي:
        # سعر غرام الذهب الصافي = سعر المثقال مقسوماً على 5
        gram_price = mithqal_price / 5
        
        if unit == "gram":
            total_grams = weight
            unit_text = "غرام"
            unit_arabic = "حساب بالغرام"
        else:
            total_grams = weight * 5 # المثقال الواحد يساوي 5 غرامات
            unit_text = "مثقال"
            unit_arabic = "حساب بالمثقال"
            
        # السعر الكلي بالدينار = (سعر الغرام الصافي + أجور الصياغة للغرام) * الوزن الإجمالي بالجرامات
        total_iqd = (gram_price + labor) * total_grams
        total_usd = total_iqd / (usd_100 / 100)
        
        invoice = (
            f"🧾 **فاتورة بيع ذهب للزبون**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **العيار وطريقة الحساب**: عيار {karat} ({unit_arabic})\n"
            f"🔹 **الوزن المطلوب**: `{weight}` {unit_text}\n"
            f"⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.2f}` غرام\n"
            f"🔨 **أجور صياغة الغرام**: `{labor:,.0f}` د.ع\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 **سعر غرام الذهب الصافي**: `{gram_price:,.0f}` د.ع\n"
            f"💸 **السعر الكلي بالدينار**: **`{total_iqd:,.0f}` د.ع**\n"
            f"💵 **السعر الكلي بالدولار**: **`${total_usd:,.2f}`**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌸 **شكراً لتعاملكم معنا ونسأل الله أن يبارك لكم في رزقكم!** ✨"
        )
        
        USER_STATES[chat_id] = {} # تصفير الحالة لسلامة العملية التالية
        utils.send_main_menu(bot, chat_id, invoice)
        
    except Exception as e:
        print(f"Sell Calculation Error: {e}")
        bot.send_message(chat_id, "⚠️ حدث خطأ أثناء حساب الفاتورة. يرجى إعادة المحاولة.")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "تم تصفير العملية بسبب خطأ.")


def calculate_and_send_buy_invoice(chat_id, state_data, settings):
    try:
        karat = state_data["karat"]
        unit = state_data["unit"]
        weight = state_data["weight"]
        labor = state_data["labor"] # أجور الخصم أو الصهر للجرام الواحد
        mithqal_price = state_data["mithqal_price"]
        usd_100 = settings["usd_100"]
        
        # 📌 الحسابات الدقيقة لشراء الذهب:
        # سعر غرام الشراء الصافي = سعر شراء المثقال مقسوماً على 5
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
        total_usd = total_iqd / (usd_100 / 100)
        
        invoice = (
            f"🧾 **فاتورة شراء ذهب من زبون**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **العيار وطريقة الشراء**: عيار {karat} ({unit_arabic})\n"
            f"🔹 **الوزن المستلم**: `{weight}` {unit_text}\n"
            f"⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.2f}` غرام\n"
            f"🔥 **خصم الصهر/أجور الجرام**: `{labor:,.0f}` د.ع\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 **سعر الشراء المتفق عليه للمثقال**: `{mithqal_price:,.0f}` د.ع\n"
            f"💰 **سعر غرام الشراء الصافي**: `{net_gram_price:,.0f}` د.ع\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💸 **المبلغ الكلي المدفوع بالدينار**: **`{total_iqd:,.0f}` د.ع**\n"
            f"💵 **المبلغ الكلي بالدولار**: **`${total_usd:,.2f}`**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌸 **تمت عملية الشراء بنجاح وشفافية مطلقة!** ✨"
        )
        
        USER_STATES[chat_id] = {} # تصفير الحالة
        utils.send_main_menu(bot, chat_id, invoice)
        
    except Exception as e:
        print(f"Buy Calculation Error: {e}")
        bot.send_message(chat_id, "⚠️ حدث خطأ أثناء حساب الفاتورة. يرجى إعادة المحاولة.")
        USER_STATES[chat_id] = {}
        utils.send_main_menu(bot, chat_id, "تم تصفير العملية بسبب خطأ.")

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
