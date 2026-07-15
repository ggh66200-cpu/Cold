import os
import json
import telebot
from telebot import types

# توكن البوت الخاص بك
TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# مسار ملف الإعدادات المحفوظ على السيرفر
DATA_FILE = "data.json"

# دالة تحميل الإعدادات من السيرفر لضمان قراءة أحدث قيم دائماً
def load_settings():
    default_settings = {
        "mithqal_21": 450000,
        "mithqal_18": 380000,
        "labor_21": 10000,
        "labor_18": 10000,
        "usd_100": 150000
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_settings
    return default_settings

# دالة حفظ الإعدادات على السيرفر لضمان الأمان وعدم الضياع
def save_settings(settings):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

# قاموس مؤقت لتخزين حالات المستخدمين أثناء الإدخال وحساب الفواتير
user_states = {}
user_data = {}

# دالة حساب الورق والدينار العراقي (بدون دنانير)
def calculate_paper_and_dinar(total_iqd, usd_rate):
    if usd_rate <= 0:
        return f"{total_iqd:,.0f} دينار"
    
    # حساب عدد الأوراق (الـ 100 دولار تساوي ورقة)
    # سعر صرف الـ 100 دولار يعادل ورقة كاملة
    papers = int(total_iqd // usd_rate)
    remaining_iqd = int(total_iqd % usd_rate)
    
    result = []
    if papers > 0:
        if papers == 1:
            result.append("1 ورقة")
        elif papers == 2:
            result.append("2 ورقة")
        else:
            result.append(f"{papers} ورقة")
            
    if remaining_iqd > 0:
        result.append(f"{remaining_iqd:,.0f} دينار")
        
    if not result:
        return "0 دينار"
        
    return " و ".join(result)

# لوحة المفاتيح الرئيسية السلسة للبوت
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton("💰 بيع للزبون")
    btn_buy = types.KeyboardButton("⚖️ شراء من زبون")
    btn_settings = types.KeyboardButton("⚙️ إعدادات الصباح")
    markup.add(btn_sell, btn_buy)
    markup.add(btn_settings)
    return markup

# زر الرجوع السريع المتواجد في كل الخطوات
def back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
    return markup

# ترحيب البوت عند تشغيله أو عند الرجوع للرئيسية دون تعليق
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states[message.chat.id] = None
    user_data[message.chat.id] = {}
    
    welcome_text = (
        "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\n"
        "مرحباً بك في نظام الصياغة الذكي الأسرع والأدق في العراق! 👑\n"
        "البوت مصمم بالكامل لتسهيل حسابات البيع والشراء اليومية لمحلك بدقة متناهية وبلمسة زر واحدة.\n\n"
        "👥 **عدد الصاغة النشطين في النظام حالياً:** `166 صائغ`\n\n"
        "نسأل الله العلي القدير أن يبارك في تجارتكم ويفتح لكم أبواب الرزق الحلال الوفير. 🌸\n"
        "يرجى اختيار العملية المطلوبة من الأزرار أدناه 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard(), parse_mode="Markdown")

# معالج الرسائل النصية العام والأزرار
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    # معالجة زر الرجوع الفوري وتصفير أي عملية معلقة
    if text == "⬅️ الرجوع للرئيسية":
        send_welcome(message)
        return

    # 1. قسم إعدادات الصباح (الكلام الطيب وإلغاء الإنجليزي)
    if text == "⚙️ إعدادات الصباح":
        settings = load_settings()
        morning_text = (
            "☀️ **صباح الرزق والبركة والسعادة يا طيب!** ☀️\n"
            "نسأل الله أن يجعل هذا اليوم يوماً مباركاً، مليئاً بالزبائن والخير الوفير لعملكم وحلالكم. 🌸✨\n\n"
            "📋 **إعدادات الصباح الحالية لمحلك:**\n"
            "🔹 سعر مثقال عيار 21: `" + f"{settings['mithqal_21']:,.0f}" + " دينار`\n"
            "🔹 سعر مثقال عيار 18: `" + f"{settings['mithqal_18']:,.0f}" + " دينار`\n"
            "🔨 أجور صياغة غرام 21: `" + f"{settings['labor_21']:,.0f}" + " دينار`\n"
            "🔨 أجور صياغة غرام 18: `" + f"{settings['labor_18']:,.0f}" + " دينار`\n"
            "💵 سعر الـ 100 دولار: `" + f"{settings['usd_100']:,.0f}" + " دينار`\n"
            "_____________________________\n"
            "💡 لتحديث جميع هذه الأسعار بسهولة وبدون تعقيد، يرجى الضغط على الزر أدناه وسنسألك عنها خطوة بخطوة! 👇"
        )
        markup = types.InlineKeyboardMarkup()
        btn_update = types.InlineKeyboardButton("📝 تحديث كل الأسعار", callback_data="start_update_settings")
        markup.add(btn_update)
        bot.send_message(chat_id, morning_text, reply_markup=markup, parse_mode="Markdown")
        return

    # 2. قسم بيع للزبون (حل مشكلة القفل والاحتساب الفوري)
    if text == "💰 بيع للزبون":
        user_states[chat_id] = "SELECT_SELL_TYPE"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("🟡 غرام عيار 21", "🟡 غرام عيار 18")
        markup.add("🔵 مثقال عيار 21", "🔵 مثقال عيار 18")
        markup.add("⬅️ الرجوع للرئيسية")
        
        bot.send_message(
            chat_id, 
            "💰 **بيع للزبون**\n\nيرجى اختيار العيار وطريقة الحساب المفضلة للعملية الحالية من الأزرار أدناه 👇", 
            reply_markup=markup
        )
        return

    # معالجة اختيار العيار في البيع
    if user_states.get(chat_id) == "SELECT_SELL_TYPE" and text in ["🟡 غرام عيار 21", "🟡 غرام عيار 18", "🔵 مثقال عيار 21", "🔵 مثقال عيار 18"]:
        user_data[chat_id] = {"type": text}
        user_states[chat_id] = "INPUT_SELL_WEIGHT"
        
        unit = "المثقال" if "مثقال" in text else "الغرام"
        bot.send_message(
            chat_id, 
            f"⚖️ لقد اخترت {text}.\n\nيرجى إرسال الوزن المطلوب بيعه للزبون (بالأرقام فقط بـ {unit}):", 
            reply_markup=back_keyboard()
        )
        return

    # معالجة إدخال الوزن في البيع
    if user_states.get(chat_id) == "INPUT_SELL_WEIGHT":
        try:
            weight = float(text.replace(",", ""))
            user_data[chat_id]["weight"] = weight
            user_states[chat_id] = "INPUT_SELL_LABOR"
            
            # عرض سعر الصياغة الافتراضي من الصباح في أزرار سريعة ليسهل على المستخدم كبسها مباشرة
            settings = load_settings()
            current_type = user_data[chat_id]["type"]
            default_labor = settings["labor_21"] if "21" in current_type else settings["labor_18"]
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            markup.add(types.KeyboardButton(f"الصياغة الصباحية المعتادة ({default_labor:,.0f} دينار)"))
            markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
            
            bot.send_message(
                chat_id,
                f"🔨 يرجى إدخال أجور صياغة الغرام الواحد بالدينار العراقي:\n\n(أو اضغط على زر الصياغة الصباحية المعتادة أدناه 👇)",
                reply_markup=markup
            )
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال وزن صحيح بالأرقام فقط (مثال: 5.25 أو 10):")
        return

    # معالجة أجور الصياغة في البيع واحتساب الفاتورة النهائية فورا بالأسعار المحدثة ديناميكيا
    if user_states.get(chat_id) == "INPUT_SELL_LABOR":
        settings = load_settings()
        current_type = user_data[chat_id]["type"]
        default_labor = settings["labor_21"] if "21" in current_type else settings["labor_18"]
        
        # التأكد إذا اختار الزر السريع أو أدخل قيمة يدوية
        if "الصياغة الصباحية المعتادة" in text:
            labor = default_labor
        else:
            try:
                labor = float(text.replace(",", "").replace(" دينار", "").strip())
            except ValueError:
                bot.send_message(chat_id, "⚠️ يرجى إدخال أجور صياغة صحيحة بالأرقام أو كبس الزر بالأسفل:")
                return
        
        weight = user_data[chat_id]["weight"]
        
        # تحديد سعر المثقال الصباحي وباقي المعطيات ديناميكياً من السيرفر
        if "21" in current_type:
            mithqal_price = settings["mithqal_21"]
        else:
            mithqal_price = settings["mithqal_18"]
            
        # قاعدة الحساب العراقية الرسمية: سعر الغرام الصافي = سعر المثقال / 5
        gram_price = mithqal_price / 5.0
        
        # تحويل الوزن إلى غرامات في حال كان المدخل بالمثقال (1 مثقال = 5 غرام)
        if "مثقال" in current_type:
            weight_in_grams = weight * 5.0
            display_weight = f"{weight} مثقال ({weight_in_grams:.2f} غرام)"
        else:
            weight_in_grams = weight
            display_weight = f"{weight:.2f} غرام"
            
        # العملية الحسابية للبيع
        total_iqd = (gram_price + labor) * weight_in_grams
        usd_rate = settings["usd_100"]
        
        # حساب التوزيع بالورق والدينار العراقي
        paper_and_dinar_text = calculate_paper_and_dinar(total_iqd, usd_rate)
        
        invoice_text = (
            "🧾 **فاتورة بيع ذهب للزبون**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 العيار والطريقة: `{current_type}`\n"
            f"⚖️ الوزن المطلوب: `{display_weight}`\n"
            f"💰 سعر غرام الذهب الصافي اليوم: `{gram_price:,.0f} دينار`\n"
            f"🔨 أجور الصياغة المعتمدة للغرام: `{labor:,.0f} دينار`\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **إجمالي سعر الفاتورة بالدينار:**\n"
            f"`{total_iqd:,.0f} دينار`\n\n"
            f"💵 **صافي الحساب بالورق والدينار:**\n"
            f"👉 `{paper_and_dinar_text}`\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🌸 **الله يرزقكم ويبارك بحلالكم وتجارتكم يا رب!** ✨"
        )
        
        # تصفير الحالة والعودة للقائمة الرئيسية
        user_states[chat_id] = None
        bot.send_message(chat_id, invoice_text, reply_markup=main_keyboard(), parse_mode="Markdown")
        return

    # 3. قسم شراء من زبون (الاحتساب الفوري)
    if text == "⚖️ شراء من زبون":
        user_states[chat_id] = "SELECT_BUY_TYPE"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("🟢 غرام عيار 21", "🟢 غرام عيار 18")
        markup.add("🔵 مثقال عيار 21", "🔵 مثقال عيار 18")
        markup.add("⬅️ الرجوع للرئيسية")
        
        bot.send_message(
            chat_id, 
            "⚖️ **شراء الذهب من زبون**\n\nيرجى اختيار العيار وطريقة الحساب المفضلة للعملية الحالية من الأزرار أدناه 👇", 
            reply_markup=markup
        )
        return

    # معالجة اختيار العيار في الشراء
    if user_states.get(chat_id) == "SELECT_BUY_TYPE" and text in ["🟢 غرام عيار 21", "🟢 غرام عيار 18", "🔵 مثقال عيار 21", "🔵 مثقال عيار 18"]:
        user_data[chat_id] = {"type": text}
        user_states[chat_id] = "INPUT_BUY_MITHQAL_PRICE"
        
        settings = load_settings()
        default_price = settings["mithqal_21"] if "21" in text else settings["mithqal_18"]
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(types.KeyboardButton(f"استخدام السعر الصباحي المقترح ({default_price:,.0f} دينار للمثقال)"))
        markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
        
        bot.send_message(
            chat_id,
            "💰 الرجاء إدخال سعر شراء المثقال المتفق عليه حالياً بالدينار العراقي:\n\n(أو اضغط على زر السعر الصباحي المقترح أدناه 👇)",
            reply_markup=markup
        )
        return

    # معالجة إدخال سعر الشراء للمثقال
    if user_states.get(chat_id) == "INPUT_BUY_MITHQAL_PRICE":
        settings = load_settings()
        current_type = user_data[chat_id]["type"]
        default_price = settings["mithqal_21"] if "21" in current_type else settings["mithqal_18"]
        
        if "السعر الصباحي المقترح" in text:
            buy_price_mithqal = default_price
        else:
            try:
                buy_price_mithqal = float(text.replace(",", "").replace(" دينار للمثقال", "").strip())
            except ValueError:
                bot.send_message(chat_id, "⚠️ يرجى إدخال السعر بشكل صحيح بالأرقام:")
                return
                
        user_data[chat_id]["buy_price_mithqal"] = buy_price_mithqal
        user_states[chat_id] = "INPUT_BUY_FEES"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(types.KeyboardButton("0 (لا يوجد خصم صهر)"))
        markup.add(types.KeyboardButton("⬅️ الرجوع للرئيسية"))
        
        bot.send_message(
            chat_id,
            "🔥 أدخل أجور الخصم أو الصهر للغرام الواحد بالدينار العراقي:\n\n(أو اضغط على 0 بالأسفل في حال عدم وجود خصم صهر 👇)",
            reply_markup=markup
        )
        return

    # معالجة خصم الصهر في الشراء
    if user_states.get(chat_id) == "INPUT_BUY_FEES":
        try:
            clean_text = text.split("(")[0].strip() # للتعامل مع زر الصفر
            fees = float(clean_text.replace(",", ""))
            user_data[chat_id]["fees"] = fees
            user_states[chat_id] = "INPUT_BUY_WEIGHT"
            
            unit = "المثقال" if "مثقال" in user_data[chat_id]["type"] else "الغرام"
            bot.send_message(
                chat_id,
                f"⚖️ يرجى إدخال الوزن المراد شراؤه من الزبون (بالأرقام بـ {unit}):",
                reply_markup=back_keyboard()
            )
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال أجور الخصم بالأرقام فقط:")
        return

    # معالجة وزن الشراء واحتساب الفاتورة النهائية فورا
    if user_states.get(chat_id) == "INPUT_BUY_WEIGHT":
        try:
            weight = float(text.replace(",", ""))
            settings = load_settings()
            
            current_type = user_data[chat_id]["type"]
            buy_price_mithqal = user_data[chat_id]["buy_price_mithqal"]
            fees = user_data[chat_id]["fees"]
            
            # سعر غرام الشراء الصافي = (سعر المثقال / 5) - أجور الصهر
            gram_buy_price = (buy_price_mithqal / 5.0) - fees
            
            if "مثقال" in current_type:
                weight_in_grams = weight * 5.0
                display_weight = f"{weight} مثقال ({weight_in_grams:.2f} غرام)"
            else:
                weight_in_grams = weight
                display_weight = f"{weight:.2f} غرام"
                
            total_iqd = gram_buy_price * weight_in_grams
            usd_rate = settings["usd_100"]
            
            # حساب التوزيع بالورق والدينار العراقي
            paper_and_dinar_text = calculate_paper_and_dinar(total_iqd, usd_rate)
            
            invoice_text = (
                "🧾 **فاتورة شراء ذهب من زبون**\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"🔹 العيار والطريقة: `{current_type}`\n"
                f"⚖️ الوزن المستلم: `{display_weight}`\n"
                f"💰 سعر الشراء للمثقال المعتمد: `{buy_price_mithqal:,.0f} دينار`\n"
                f"🔥 خصم أجور الصهر للغرام: `{fees:,.0f} دينار`\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"💵 **إجمالي المبلغ المدفوع للزبون بالدينار:**\n"
                f"`{total_iqd:,.0f} دينار`\n\n"
                f"💵 **صافي الحساب بالورق والدينار:**\n"
                f"👉 `{paper_and_dinar_text}`\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                "🌸 **تمت عملية الشراء بنجاح وشفافية مطلقة!** ✨"
            )
            
            user_states[chat_id] = None
            bot.send_message(chat_id, invoice_text, reply_markup=main_keyboard(), parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال وزن صحيح بالأرقام فقط:")
        return

    # معالجة إدخالات تحديث الأسعار الصباحية خطوة بخطوة (الـ Wizard البديل والممتع)
    state = user_states.get(chat_id)
    if state and state.startswith("WIZARD_"):
        try:
            val = float(text.replace(",", ""))
            if val < 0:
                raise ValueError
                
            if state == "WIZARD_MITHQAL_21":
                user_data[chat_id]["mithqal_21"] = val
                user_states[chat_id] = "WIZARD_MITHQAL_18"
                bot.send_message(chat_id, "📝 **الخطوة 2/5:**\nأرسل سعر مثقال عيار 18 الجديد (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_MITHQAL_18":
                user_data[chat_id]["mithqal_18"] = val
                user_states[chat_id] = "WIZARD_LABOR_21"
                bot.send_message(chat_id, "📝 **الخطوة 3/5:**\nأرسل أجور صياغة غرام 21 الجديدة (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_LABOR_21":
                user_data[chat_id]["labor_21"] = val
                user_states[chat_id] = "WIZARD_LABOR_18"
                bot.send_message(chat_id, "📝 **الخطوة 4/5:**\nأرسل أجور صياغة غرام 18 الجديدة (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_LABOR_18":
                user_data[chat_id]["labor_18"] = val
                user_states[chat_id] = "WIZARD_USD_100"
                bot.send_message(chat_id, "📝 **الخطوة 5/5 والأخيرة:**\nأرسل سعر صرف الـ 100 دولار مقابل الدينار حالياً (بالأرقام فقط - دينار):", reply_markup=back_keyboard())
                
            elif state == "WIZARD_USD_100":
                user_data[chat_id]["usd_100"] = val
                
                # حفظ الأسعار الجديدة في السيرفر بملف data.json
                settings = load_settings()
                settings["mithqal_21"] = user_data[chat_id]["mithqal_21"]
                settings["mithqal_18"] = user_data[chat_id]["mithqal_18"]
                settings["labor_21"] = user_data[chat_id]["labor_21"]
                settings["labor_18"] = user_data[chat_id]["labor_18"]
                settings["usd_100"] = user_data[chat_id]["usd_100"]
                save_settings(settings)
                
                # رسالة نجاح مبهجة ودعاء يفتح النفس للرزق الحلال
                success_text = (
                    "🎉 **تحديث رائع وموفق!** 🎉\n"
                    "تم تحديث كافة إعدادات الأسعار الصباحية بنجاح تام وحفظها بأمان على النظام! ✅\n\n"
                    "🍀 **يا رب اجعله صباحاً مباركاً تفيض به الأرزاق الحلال، وييسر لكم به كل صعب!** ✨\n\n"
                    "البوت جاهز تماماً الآن لمباشرة حساباتكم السلسة بالأسعار الجديدة."
                )
                user_states[chat_id] = None
                bot.send_message(chat_id, success_text, reply_markup=main_keyboard(), parse_mode="Markdown")
                
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إدخال قيمة رقمية صحيحة فقط وبدون رموز (مثال: 450000):")
        return

    # في حال إرسال أي نص غير معروف
    bot.send_message(chat_id, "⚠️ يرجى اختيار عملية من القائمة أدناه للبدء 👇", reply_markup=main_keyboard())

# معالجة الضغط على زر "تحديث كل الأسعار" عبر الـ Callback Query
@bot.callback_query_handler(func=lambda call: call.data == "start_update_settings")
def callback_update_settings(call):
    chat_id = call.message.chat.id
    user_states[chat_id] = "WIZARD_MITHQAL_21"
    user_data[chat_id] = {}
    
    # حذف رسالة التحديث القديمة وبدء المعالج بخطوات سلسة للغاية
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(
        chat_id,
        "⚙️ **البدء بتحديث أسعار الصباح**\n\n"
        "📝 **الخطوة 1/5:**\nأرسل سعر مثقال عيار 21 الجديد (بالأرقام فقط - دينار، مثال: 450000):",
        reply_markup=back_keyboard()
    )

# تشغيل البوت بطريقة تمنع توقفه أو نومه نهائيا على السيرفر
if __name__ == '__main__':
    print("🤖 البوت متصل الآن بنجاح ويعمل بأقصى سرعة...")
    bot.infinity_polling()
