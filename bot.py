import json
import re
from telebot import TeleBot, types

# توكن البوت الخاص بك
TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = TeleBot(TOKEN)

# 1. دالة ديناميكية لقراءة الإعدادات فورياً لضمان عدم قفل أو تعليق الأسعار
def load_settings():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # إعدادات افتراضية في حال عدم وجود الملف
        return {
            "mithqal_21": 450000,
            "mithqal_18": 380000,
            "labor_21": 10000,
            "labor_18": 10000,
            "usd_100": 150000
        }

# دالة لحفظ الإعدادات الجديدة
def save_settings(settings):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_safe_ascii=False, indent=4)

# 2. رسالة الترحيب الدافئة مع العدد الوهمي 166 لبناء الثقة والاحترافية
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✨ **مرحباً بك في نظام الصياغة العراقي الذكي!** ✨\n\n"
        "🟢 **نشط الآن:** `166` صائغاً في مختلف محافظات العراق يدمجون التكنولوجيا "
        "بمهنتهم العريقة لإدارة حساباتهم بثوانٍ وبدون أخطاء! 💎\n\n"
        "ابدأ الآن بالتحكم ومتابعة حساباتك بكل سهولة وسلاسة عبر الأزرار أدناه 👇"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 بيع للزبون", "⚖️ شراء من زبون")
    markup.row("⚙️ إعدادات الصباح")
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# 3. معالجة الضغط على زر "⚙️ إعدادات الصباح"
@bot.message_handler(func=lambda message: message.text == "⚙️ إعدادات الصباح")
def morning_settings_menu(message):
    data = load_settings()
    
    # كلام جميل يفتح النفس للصباح والرزق
    inspiring_msg = (
        "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n"
        "أهلاً بك يا غالي، نسأل الله أن يفتح عليك أبواب الرزق الحلال ويبارك لك في يومك وعملك! 🌸\n\n"
        "📊 **إعدادات الأسعار الحالية في محلك:**\n"
        "• سعر مثقال 21: `{:,}` دينار\n"
        "• سعر مثقال 18: `{:,}` دينar\n"
        "• صياغة غرام 21: `{:,}` دينار\n"
        "• صياغة غرام 18: `{:,}` دينار\n"
        "• سعر الـ 100 دولار: `{:,}` دينار\n"
        "_________________________________\n\n"
        "✍️ **لتحديث كل الأسعار بلحظة واحدة وبدون تعقيد:**\n"
        "أرسل لي الأرقام الخمسة الجديدة متتالية (كل رقم في سطر أو مفصولة بمسافة) بهذا الترتيب تماماً:\n"
        "1. سعر مثقال 21\n"
        "2. سعر مثقال 18\n"
        "3. صياغة غرام 21\n"
        "4. صياغة غرام 18\n"
        "5. سعر الـ 100 دولار\n\n"
        "💡 *مثال لإرسال القيم:* \n`460000`\n`390000`\n`8000`\n`8000`\n`153000`"
    ).format(
        data.get("mithqal_21", 0),
        data.get("mithqal_18", 0),
        data.get("labor_21", 0),
        data.get("labor_18", 0),
        data.get("usd_100", 0)
    )
    
    sent_msg = bot.send_message(message.chat.id, inspiring_msg, parse_mode="Markdown")
    # توجيه البوت لانتظار الأرقام الخمسة من المستخدم مباشرة
    bot.register_next_step_handler(sent_msg, update_all_settings)

# معالج تحديث القيم الخمسة دفعة واحدة
def update_all_settings(message):
    # استخدام Regex لاستخراج الأرقام فقط من رسالة العميل
    numbers = re.findall(r'\d+', message.text)
    
    if len(numbers) == 5:
        new_settings = {
            "mithqal_21": int(numbers[0]),
            "mithqal_18": int(numbers[1]),
            "labor_21": int(numbers[2]),
            "labor_18": int(numbers[3]),
            "usd_100": int(numbers[4])
        }
        save_settings(new_settings)
        
        success_msg = (
            "✅ **تم تحديث أسعار الصباح بنجاح يا بطل!**\n\n"
            "السيستم الآن يعمل بالقيم الجديدة بالكامل. "
            "جعلها الله فاتحة خير ورزق وبركة لا تنتهي لمكاسبك اليوم! 🕊️✨"
        )
        bot.send_message(message.chat.id, success_msg, parse_mode="Markdown")
    else:
        bot.send_message(
            message.chat.id, 
            "⚠️ **خطأ في الإدخال!** يرجى إرسال 5 أرقام واضحة لنتمكن من تحديث الأسعار بشكل صحيح."
        )

# 4. معالجة عملية الحساب والفعاليات الرياضية مع "حساب الورق" العراقي
def calculate_and_show_invoice(chat_id, caliber, weight, custom_labor=None):
    # تحميل الأسعار ديناميكياً لضمان قراءة آخر تحديث فوراً!
    data = load_settings()
    
    # اختيار السعر بناءً على العيار المختار
    if caliber == 21:
        mithqal_price = data["mithqal_21"]
        labor_price = custom_labor if custom_labor is not None else data["labor_21"]
    else:
        mithqal_price = data["mithqal_18"]
        labor_price = custom_labor if custom_labor is not None else data["labor_18"]
        
    usd_rate = data["usd_100"] # سعر الـ 100 دولار بالدينار العراقي

    # الفعاليات الرياضية للحساب الصافي:
    # 1 مثقال = 5 غرام
    gram_price_raw = int(mithqal_price / 5)  # سعر الغرام الصافي
    total_gram_price = gram_price_raw + labor_price
    total_price_iqd = int(total_gram_price * weight)

    # حساب الورق العراقي الذكي 💵:
    # كل ورقة تساوي قيمة الصرف لـ 100 دولار
    sheets = total_price_iqd // usd_rate
    remainder_iqd = total_price_iqd % usd_rate

    # تنسيق نص حساب الورق
    if sheets > 0:
        paper_text = f"💵 **حساب الورق:** {sheets} ورقة"
        if remainder_iqd > 0:
            paper_text += f" و {remainder_iqd:,} دينار"
    else:
        paper_text = f"💵 **حساب الورق:** {total_price_iqd:,} دينار"

    # عرض الفاتورة بشكل احترافي ومقنع للزبون وبكلام طيب
    invoice_msg = (
        "🧾 **تفاصيل الاحتساب الرياضي والشفافية الذكية:**\n"
        "_________________________________\n\n"
        f"🔸 **العيار وطريقة الحساب:** عيار {caliber} (حساب بالغرام)\n"
        f"🔸 **الوزن المطلوب:** {weight} غرام\n"
        f"🔸 **أجور صياغة الغرام:** {labor_price:,} دينار\n\n"
        "⚙️ **الفعاليات الرياضية لعملية الحساب:**\n"
        f"1. سعر الغرام الصافي (المثقال / 5): `{gram_price_raw:,}` دينار\n"
        f"2. سعر الغرام مع الصياغة: `{total_gram_price:,}` دينار\n"
        f"3. الحساب الكلي بالدينار: {total_gram_price:,} × {weight} \n"
        f"   👈 **المجموع الكلي:** `{total_price_iqd:,}` دينار\n"
        "_________________________________\n\n"
        f"{paper_text}\n"
        "_________________________________\n\n"
        "🌸 **بالخير والبركة عليكم! نسأل الله تعالى أن يجعلها تجارة مباركة ورزقاً وفيراً ومستمراً لكم.** ✨"
    )
    
    bot.send_message(chat_id, invoice_msg, parse_mode="Markdown")
