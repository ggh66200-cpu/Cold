import json, os, time, tempfile, shutil
from telebot import types

DATA_FILE = 'data.json'
SYSTEM_USERNAME = "@GoldenCalc_Bot"

BRAND_HEADER_AR = (
    "👑 **ARAMKY | أرامكي للحلول الرقمية** 👑\n"
    "⚜️ _نظام نواة الذهب لحسابات الصاغة الذكية_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

BRAND_HEADER_KU = (
    "👑 **ARAMKY | چارەسەرە دیجیتاڵییەکان** 👑\n"
    "⚜️ _سیستەمی ناووکی زێڕ بۆ حیساباتی زێڕینگەری_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

BRAND_HEADER_EN = (
    "👑 **ARAMKY | Digital Solutions** 👑\n"
    "⚜️ _Nawat Al-Dhahab Smart Gold System_ 👑\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

TRANSLATIONS = {
    "ar": {
        "welcome": BRAND_HEADER_AR + "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\nمرحباً بك في نظام الصياغة الأسرع والأدق في الأسواق العريقة! 👑\n🎁 تمتلك الآن **فترة تجريبية مجانية مدتها {trial_days} أيام** للاختبار الميداني الفوري!\n\n🔢 **رقم الصائغ:** `#{shop_num}`\n📍 **المحل العامر:** `{shop_name}`\n🗺️ **الموقع:** `{shop_location}`\n📞 **الهاتف:** `{shop_phone}`\n\n👥 **المشتركين النشطين:** `{count} صائغ`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 معرف النظام الرسمي: {sys_user}\nيرجى اختيار العملية المطلوبة من الأزرار أدناه 👇",
        "sell": "💰 بيع للزبون", "buy": "⚖️ شراء سريع", "settings": "⚙️ أسعار الصباح", "back": "⬅️ الرجوع للرئيسية",
        "lang_saved": "🎉 تم تفعيل اللغة العربية بنجاح يا طيب! عساها فاتحة خير وبركة عليك وعلى حلالك. 🌸",
        "req_shop_name": BRAND_HEADER_AR + "📝 **خطوة التسجيل الرسمية للمحل**\n\nأخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك الرسمي **كل معلومة في سطر منفصل (اضغط Enter للانتقال لسطر جديد)** بهذا الترتيب:\n\n1️⃣ اسم المحل\n2️⃣ المحافظة أو المدينة\n3️⃣ رقم هاتف المحل\n\n💡 **مثال للإرسال المباشر:**\nصياغة أرامكي الفاخرة\nبغداد، الكاظمية\n07701234567",
        "shop_saved": "🎉 تم تسجيل محلك باسم **{shop_name}** وتأمين بياناتك بنجاح في السيرفرات! 🌸",
        "morning_title": BRAND_HEADER_AR + "☀️ **إعدادات أسعار الصباح الحالية لمكتبكم:**\n━━━━━━━━━━━━━━━━━━\n🔹 سعر مثقال عيار 21: `{mithqal_21:,.0f} دينار`\n🔹 سعر مثقال عيار 18: `{mithqal_18:,.0f} دينار`\n🔨 أجور غرام 21: `{labor_21:,.0f} دينار`\n🔨 أجور غرام 18: `{labor_18:,.0f} دينار`\n💵 سعر الـ 100 دولار: `{usd_100:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💡 لتحديث الأسعار بسؤال واحد، اضغط على الزر أدناه! 👇",
        "update_btn": "📝 تحديث الأسعار دفعة واحدة",
        "wizard_prompt": "⚙️ أرسل الأسعار الـ 5 الجديدة في رسالة واحدة متباعدة بمسافات:\n`[مثقال 21] [مثقال 18] [صياغة 21] [صياغة 18] [الدولار]`\n⚠️ يجب أن يكون سعر عيار 18 أقل من عيار 21!",
        "sweet_success": "🎉 **تم حفظ الأسعار وتحديث النظام بنجاح تام** 🌸✨",
        "error_format": "⚠️ خطأ في الصيغة! يرجى إدخال أرقام صحيحة وتأكد أن سعر 18 أقل من 21!",
        "choose_karat": "💰 **بيع للزبون**\nاختر طريقة الحساب والعيار المطلوب 👇",
        "choose_karat_buy": "⚖️ **شراء سريع ومبسط من زبون**\nاختر العيار والوحدة لتبدأ التصفية الفورية 👇",
        "karat_21_g": "غرام عيار 21", "karat_18_g": "غرام عيار 18", "karat_21_m": "مثقال عيار 21", "karat_18_m": "مثقال عيار 18",
        "req_weight": "⚖️ لقد اخترت **{text}**.\nالرجاء إرسال الوزن المطلوب ({unit_text}):",
        "req_weight_buy": "⚖️ أرسل الآن الوزن الإجمالي المراد شراؤه مباشرة:",
        "use_morning_labor": "استخدام الأجور الصباحية ({labor:,} دينار)",
        "req_labor_sell": "🔨 أرسل أجور صياغة الغرام الواحد بالدينار:",
        "invalid_labor": "⚠️ يرجى كتابة الأجور كأرقام فقط!",
        "invalid_weight": "⚠️ خطأ! يرجى إدخال رقم صحيح للوزن (مثال: 14.250):",
        "expired_msg": BRAND_HEADER_AR + "✨ **أخي الغالي وصاحب الكار المحترم** ✨\n\nربي يرزقكم الرزق الحلال الواسع والبركة في تجاراتكم ومحلاتكم العامرة دائماً 🌸. نود إعلامكم بأن **الفترة التجريبية المخصصة للمنظومة الذكية قد انتهت**.\n\n👑 للانضمام إلى النخبة وتمديد الصلاحية الكاملة المفتوحة بالسعر التنافسي المخصص والمثبت لأسواق العراق بقيمة **105,000 دينار عراقي** شهرياً فقط.\n\n⚜️💳 **حساب الإيداع المالي الذهبي المباشر (Zain Cash / Master):**\nرقم المحفظة والبطاقة الرسمي المعتمد:\n`910400201646`\n\n📸 بعد إتمام عملية التحويل الطيبة، اضغط على الزر بالأسفل وأرسل صورة الوصل لتفعيل حسابك تلقائياً وبشكل فوري عبر قسم التدقيق.\n📞 خط الدعم الفني المباشر لخدمتكم: `{support_phone}`",
        "send_receipt_btn": "📸 اضغط هنا لإرسال الوصل للتدقيق الفوري",
        "awaiting_receipt": "📝 يرجى الآن إرسال صورة الوصل المالي مباشرة من المعرض للتدقيق الفوري 👇",
        "receipt_sent_admin": "🎉 **تم إرسال وصل الدفع بنجاح إلى قسم التدقيق المالي لشركة أرامكي!**\nجاري مراجعة طلبكم وتفعيل النظام بشكل دائم خلال دقائق معدودة يا طيب. شكراً لثقتكم الغالية بنا! 🌸",
        "sell_invoice": BRAND_HEADER_AR + "🧾 **فاتورة بيع ذهب رقمية**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل:** `{shop_name}`\n🔹 **النوع:** عيار {karat} ({unit_arabic})\n⚖️ **الوزن الصافي:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔨 **أجور الصياغة للجرام:** `{labor:,.0f}` د.ع\n💰 **سعر الغرام الصافي:** `{gram_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **الحساب الإجمالي بالدينار:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **صافي الحساب (بالورقة والدينار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت عبر نظام: {sys_user}\n🌸 **بالبركة والحلال الطيب لعملكم وزبائنكم!** ✨💛",
        "buy_invoice": BRAND_HEADER_AR + "🧾 **فاتورة شراء ذهب رقمية (شراء مبسط)**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل:** `{shop_name}`\n🔹 **النوع:** شراء عيار {karat} ({unit_arabic})\n⚖️ **الوزن المستلم:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔥 **خصم الصهر/الأجور:** `{labor:,.0f}` د.ع\n💰 **سعر شراء المثقال المعتمد:** `{mithqal_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **المبلغ الكلي الصافي المدفوع لكم:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **توزيع الحساب (بالورقة والدينار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت عبر نظام: {sys_user}\n🌸 **ربي يعوضكم بالخير والرزق الواسع الوفير!** ✨"
    },
    "ku": {}, # يتم ملؤها تلقائياً بالوراثة من الملف الأصلي لحفظ الحجم
    "en": {}
}

# نسخ القوالب للغات الأخرى لضمان عدم حدوث Crash في سيرفر الاستضافة
TRANSLATIONS["ku"] = TRANSLATIONS["ar"]
TRANSLATIONS["en"] = TRANSLATIONS["ar"]

def get_data():
    default_settings = {"mithqal_21": 450000, "mithqal_18": 380000, "labor_21": 10000, "labor_18": 10000, "usd_100": 150000}
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        default_data = {"base_count": 166, "trial_days": 7, "system_broadcast": "", "support_phone": "07872180902", "users": {}, "settings": default_settings}
        save_data(default_data)
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    dir_name = os.path.dirname(os.path.abspath(DATA_FILE))
    with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding='utf-8') as tf:
        json.dump(data, tf, ensure_ascii=False, indent=4)
        temp_name = tf.name
    os.replace(temp_name, DATA_FILE)

def get_user_lang(user_id): return get_data()['users'].get(str(user_id), {}).get('lang', 'ar')
def set_user_lang(user_id, lang):
    data = get_data()
    if str(user_id) not in data['users']: data['users'][str(user_id)] = {}
    data['users'][str(user_id)]['lang'] = lang
    save_data(data)

def update_all_settings(vals):
    data = get_data()
    keys = ["mithqal_21", "mithqal_18", "labor_21", "labor_18", "usd_100"]
    for i, k in enumerate(keys): data['settings'][k] = int(vals[i])
    save_data(data)

def calculate_paper_and_dinar(total_iqd, usd_100_rate, lang='ar'):
    if usd_100_rate <= 0: return f"{total_iqd:,.0f} دينار"
    papers = int(total_iqd // usd_100_rate)
    remaining_iqd = int(total_iqd % usd_100_rate)
    result = []
    if papers > 0: result.append(f"`{papers}` ورقة")
    if remaining_iqd > 0: result.append(f"`{remaining_iqd:,.0f}` دينار")
    return " و ".join(result) if result else "0"

def get_keyboard(lang="ar"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(TRANSLATIONS[lang]["sell"], TRANSLATIONS[lang]["buy"])
    markup.add(TRANSLATIONS[lang]["settings"])
    return markup

def get_karat_unit_keyboard(lang="ar"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(TRANSLATIONS[lang]["karat_21_g"], TRANSLATIONS[lang]["karat_18_g"])
    markup.add(TRANSLATIONS[lang]["karat_21_m"], TRANSLATIONS[lang]["karat_18_m"])
    markup.add(TRANSLATIONS[lang]["back"])
    return markup

def send_main_menu(bot, chat_id, text_to_send, lang="ar"):
    data = get_data()
    broadcast = data.get("system_broadcast", "")
    final_text = text_to_send
    if broadcast: final_text = f"📢 **تنويه الإدارة:**\n⚠️ _{broadcast}_\n\n━━━━━━━━━━━━━━━━━━\n\n" + text_to_send
    bot.send_message(chat_id, final_text, parse_mode="Markdown", reply_markup=get_keyboard(lang))
