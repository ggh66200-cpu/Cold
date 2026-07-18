import json, os, time, tempfile, shutil
from telebot import types

DATA_FILE = 'data.json'

# الهوية الرسمية الموحدة لشركة أرامكي
BRAND_HEADER_AR = (
    "💎 **ARAMKY | أرامكي للحلول الرقمية** 💎\n"
    "⚜️ _فرع نواة الذهب لأنظمة الصاغة والأسواق المالية_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

BRAND_HEADER_KU = (
    "💎 **ARAMKY | چارەسەرە دیجیتاڵییەکان** 💎\n"
    "⚜️ _لقی ناووکی زێڕ بۆ سیستەمی زێڕینگەری_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

TRANSLATIONS = {
    "ar": {
        "welcome": BRAND_HEADER_AR + "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\nمرحباً بك في نظام الصياغة الذكي الأسرع والأدق في العراق! 👑\n\n🔢 **رقم الصائغ المخول:** `#{shop_num}`\n📍 **محلكم العامر:** `{shop_name}`\n🗺️ **الموقع الحالي:** `{shop_location}`\n📞 **رقم التواصل:** `{shop_phone}`\n\n👥 **الصاغة النشطين حالياً:** `{count} صائغ`\n━━━━━━━━━━━━━━━━━━━━━━\nنسأل الله العلي القدير أن يبارك في تجارتكم ويفتح لكم أبواب الرزق الحلال الوفير. 🌸\nيرجى اختيار العملية المطلوبة من الأزرار أدناه 👇",
        "sell": "💰 بيع للزبون",
        "buy": "⚖️ شراء من زبون",
        "settings": "⚙️ إعدادات الصباح",
        "back": "⬅️ الرجوع للرئيسية",
        "lang_saved": "🎉 تم تفعيل اللغة العربية بنجاح يا طيب! عساها فاتحة خير عليك. 🌸",
        "req_shop_name": BRAND_HEADER_AR + "📝 **خطوة التسجيل الرسمية للمحل**\n\nأخي الغالي وصاحب المحل الطيب، يرجى إرسال معلومات محلك الصائغ الرسمي في **رسالة واحدة تفصل بينها علامة (-)** بهذا الترتيب الدقيق:\n\n`[اسم المحل] - [الموقع أو المدينة] - [رقم الهاتف]`\n\n💡 **مثال للنسخ والتعديل وإرساله مباشرة:**\n`صياغة النجاح - بغداد، الكاظمية - 07701234567`",
        "shop_saved": "🎉 تم تسجيل محلك باسم **{shop_name}** وتأمين بياناتك الرسمية بنجاح في السيرفر! 🌸",
        "morning_title": BRAND_HEADER_AR + "☀️ **صباح الرزق والبركة والسعادة يا طيب!** ☀️\n\nنسأل الله أن يجعل هذا اليوم مباركاً، مليئاً بالخير الوفير لعملكم وحلالكم الطيب. 🌸✨\n\n📋 **إعدادات الصباح الحالية لمحلك:**\n━━━━━━━━━━━━━━━━━━\n🔹 سعر مثقال عيار 21: `{mithqal_21:,.0f} دينار`\n🔹 سعر مثقال عيار 18: `{mithqal_18:,.0f} دينار`\n🔨 أجور صياغة غرام 21: `{labor_21:,.0f} دينار`\n🔨 أجور صياغة غرام 18: `{labor_18:,.0f} دينار`\n💵 سعر الـ 100 دولار: `{usd_100:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💡 لتحديث جميع هذه الأسعار بلمحة بصر وسؤال واحد، اضغط على الزر أدناه! 👇",
        "update_btn": "📝 تحديث الأسعار دفعة واحدة",
        "wizard_prompt": "⚙️ **تحديث أسعار الصباح بلمحة واحدة**\n\nيا مية هلا بيك! أرسل لي الأسعار الـ 5 الجديدة في رسالة واحدة متباعدة بمسافات بهذا الترتيب الدقيق:\n\n`[مثقال 21] [مثقال 18] [صياغة 21] [صياغة 18] [الدولار]`\n\n💡 **ملاحظة:** يجب أن يكون سعر عيار 18 أقل دائماً من عيار 21.\n\n**مثال للنسخ والتعديل:**\n`450000 380000 10000 10000 153000`",
        "sweet_success": "🎉 **تم حفظ الأسعار والحمد لله بنجاح تام** 🌸✨\n\nتم تحديث كافة أسعار الصباح في السيرفر وتأمينها بالكامل وعساها فاتحة خير ورزق وفير! 💸",
        "error_format": "⚠️ خطأ في الصيغة! يرجى إدخل 5 أرقام صحيحة متباعدة بمسافات، وتأكد أن سعر عيار 18 أقل من عيار 21!\n\nمثال:\n`450000 380000 10000 10000 153000`",
        "choose_karat": "💰 **بيع للزبون**\n\nاختر طريقة الحساب والعيار المطلوب من الأزرار أدناه 👇",
        "choose_karat_buy": "⚖️ **شراء من زبون**\n\nاختر طريقة الحساب والعيار المطلوب من الأزرار أدناه 👇",
        "karat_21_g": "غرام عيار 21", "karat_18_g": "غرام عيار 18", "karat_21_m": "مثقال عيار 21", "karat_18_m": "مثقال عيار 18",
        "req_weight": "⚖️ لقد اخترت **{text}**.\n\nالرجاء إرسال الوزن المطلوب بيعه لزبون ({unit_text}):",
        "req_weight_buy": "⚖️ أدخل الوزن المراد شراؤه من الزبون ({unit_text}):",
        "req_price_buy": "💰 لقد اخترت **{text}**.\n\nالرجاء إدخال سعر شراء المثقال المتفق عليه حالياً بالدينار:",
        "use_morning_price": "استخدام السعر الصباحي ({price:,} دينار)",
        "use_morning_labor": "استخدام الأجور الصباحية ({labor:,} دينار)",
        "req_labor_buy": "🔥 أدخل أجور الخصم أو الصهر للغرام الواحد بالدينار:",
        "req_labor_sell": "🔨 أرسل أجور صياغة الغرام الواحد بالدينار:",
        "loading_sell": "⚖️ جاري حساب الوزن الإجمالي والورق والدينار الحالي... ⚡📊",
        "loading_buy": "🔥 جاري فحص الذهب وخصم أجور الصهر والورق... ⚖️✨",
        "invalid_price": "⚠️ يرجى كتابة السعر كأرقام فقط أو الضغط على السعر المقترح!",
        "invalid_labor": "⚠️ يرجى كتابة الأجور كأرقام فقط!",
        "invalid_weight": "⚠️ خطأ! يرجى إدخال رقم صحيح للوزن (مثال: 12.345):",
        "expired_msg": BRAND_HEADER_AR + "🚫 **انتهت الفترة التجريبية للنظام!**\n\nأخي الغالي وصاحب المحل الطيب، لتفعيل اشتراكك الشهري والاستمرار بالاستفادة من حاسبة الصائغ الذكية، يرجى إرسال قيمة الاشتراك وقدرها **105,000 دينار عراقي**.\n\n💳 **طريقة الدفع يدوياً:**\nيرجى التحويل إلى رقم الماستر كارد الرسمي للشركة:\n`910400201646`\n\n📸 **خطوة التفعيل:**\nبعد التحويل، قم بالضغط على زر **'إرسال وصل الدفع 📸'** أدناه وأرسل صورة الوصل.\n\n📞 **خط الطوارئ والدعم الفني المباشر للشركة:** `{support_phone}`",
        "send_receipt_btn": "📸 إرسال وصل الدفع الرسمى",
        "awaiting_receipt": "📝 يرجى الآن إرسال **صورة الوصل المالي** مباشرة ليتم فحصها وتفعيل حسابكم بشكل رسمي فوراً 👇",
        "receipt_sent_admin": "🎉 تم إرسال وصل الدفع بنجاح للإدارة! جاري تدقيق الوصل وتفعيل حسابك خلال دقائق معدودة يا طيب. شكراً لثقتك بنا! 🌸",
        "sell_invoice": BRAND_HEADER_AR + "🧾 **فاتورة بيع ذهب للزبون**\n━━━━━━━━━━━━━━━━━━\n🔹 **المحل العامر**: `{shop_name}`\n🔹 **العيار ونوع الحساب**: عيار {karat} ({unit_arabic})\n🔹 **الوزن المطلوب**: `{weight}` {unit_text}\n⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.3f}` غرام\n🔨 **أجور صياغة الغرام**: `{labor:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💰 **سعر غرام الذهب الصافي**: `{gram_price:,.0f} دينار`\n💵 **السعر الكلي بالدينار العراقي**:\n👉 **`{total_iqd:,.0f} دينار`**\n\n💵 **صافي الحساب بالورق والدينار**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب!** ✨💛",
        "buy_invoice": BRAND_HEADER_AR + "🧾 **فاتورة شراء ذهب من زبون**\n━━━━━━━━━━━━━━━━━━\n🔹 **المحل العامر**: `{shop_name}`\n🔹 **العيار وطريقة الشراء**: عيار {karat} ({unit_arabic})\n🔹 **الوزن المستلم**: `{weight}` {unit_text}\n⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.3f}` غرام\n🔥 **خصم الصهر/أجور الجرام**: `{labor:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💰 **سعر الشراء المعتمد للمثقال**: `{mithqal_price:,.0f} دينار`\n💰 **سعر غرام الشراء الصافي**: `{net_gram_price:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💵 **المبلغ الكلي المدفوع بالدينار العراقي**:\n👉 **`{total_iqd:,.0f} دينار`**\n\n💵 **صافي الحساب بالورق والدينار**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير!** ✨"
    },
    "ku": {
        "welcome": BRAND_HEADER_KU + "✨ **یا فەتاح یا عەلیم یا ڕەزاق یا کەریم** ✨\n\nبەخێربێن بۆ سیستەمی زیرەکی زێڕینگەری، خێراترین و دقیقترین لە عێراق! 👑\n\n🔢 **ژمارەی فەرمی زێڕینگەر:** `#{shop_num}`\n📍 **دوکانی ئێوە:** `{shop_name}`\n🗺️ **شوێن:** `{shop_location}`\n📞 **ژمارەی مۆبایل:** `{shop_phone}`\n\n👥 **ژمارەی کڕیارانی چالاک ئێستا:** `{count} زێڕینگەر`\n━━━━━━━━━━━━━━━━━━━━━━\nتکایە کردارەکە لە دوگمەکانی خوارەوە هەڵبژێرە 👇",
        "sell": "💰 فرۆشتن بە کڕیار", "buy": "⚖️ کڕین لە کڕیار", "settings": "⚙️ ڕێکخستنەکانی بەیانی", "back": "⬅️ گەڕانەوە بۆ سەرەکی", "lang_saved": "🎉 زمانی کوردی بە سەرکەوتوویی چالاککرا!",
        "req_shop_name": BRAND_HEADER_KU + "📝 **هەنگاوی تۆمارکردنی فەرمی دوکان**\n\nتکایە زانیاری دوکانەکەت بە یەک نامە بنێرە و نیشانەی (-) دابنێ لە نێوانیان بەم شێوازە:\n\n`[ناوی دوکان] - [شوێن یان شار] - [ژمارەی مۆبایل]`",
        "shop_saved": "🎉 دوکانەکەت بە ناوی **{shop_name}** بە سەرکەوتوویی تۆمارکرا! 🌸",
        "morning_title": BRAND_HEADER_KU + "☀️ **بەیانیت باش و پڕ لە بەرەکەت بێت هاوڕێی ئازیز!** ☀️\n\n📋 **ڕێکخستنەکانی بەیانی ئێستای دوکانەکەت:**\n━━━━━━━━━━━━━━━━━━\n🔹 نرخی مسقاڵی ٢١: `{mithqal_21:,.0f} دينار`\n🔹 نرخی مسقاڵی ١٨: `{mithqal_18:,.0f} دينار`\n🔨 کرێی دروستکردنی گرام ٢١: `{labor_21:,.0f} دینار`\n🔨 کرێی دروستکردنی گرام ١٨: `{labor_18:,.0f} دینار`\n💵 نرخی ١٠٠ دۆلار: `{usd_100:,.0f} دینار`\n━━━━━━━━━━━━━━━━━━\n💡 بۆ نوێکردنەوەی نرخەکان، کلیک لەسەر دوگمەی خوارەوە بکە! 👇",
        "update_btn": "📝 نوێکردنەوەی نرخەکان بە یەکجار",
        "wizard_prompt": "⚙️ **نوێکردنەوەی نرخەکانی بەیانی بە یەک نامە**\n\nنرخە نوێیەکان بە یەک نامە بنێرە بەم ڕیزبەندییە:\n`[مسقاڵ ٢١] [مسقاڵ ١٨] [کرێی ٢١] [کرێی ١٨] [دۆلار]`",
        "sweet_success": "🎉 **نرخەکان بە سەرکەوتوویی پاشەکەوت کران** 🌸✨", "error_format": "⚠️ هەڵە لە نووسیندا هەیە! تکایە ٥ ژمارەی دروست بنێرە.",
        "choose_karat": "💰 **فرۆشتن بە کڕیار**", "choose_karat_buy": "⚖️ **کڕین لە کڕیار**",
        "karat_21_g": "گرام عەیار 21", "karat_18_g": "گرام عەیار 18", "karat_21_m": "مسقاڵ عەیار 21", "karat_18_m": "مسقاڵ عەیار 18",
        "req_weight": "⚖️ تۆ **{text}**ت هەڵبژارد. کێشی داواکراو بنێرە ({unit_text}):",
        "req_weight_buy": "⚖️ کێشی کڕین لە کڕیار بنێرە ({unit_text}):",
        "req_price_buy": "💰 تکایە نرخی کڕینی مسقاڵ بنێرە بە دینار:",
        "use_morning_price": "بەکارهێنانی نرخی بەیانی ({price:,} دینار)", "use_morning_labor": "بەکارهێنانی کرێی بەیانی ({labor:,} دینار)",
        "req_labor_buy": "🔥 تێچووی توانەوە بۆ هەر گرامێک بنێرە:", "req_labor_sell": "🔨 کرێی دروستکردنی هەر گرامێک بنێرە:",
        "loading_sell": "⚖️ کێش و بڕی پارە حیساب دەکرێت...", "loading_buy": "🔥 پشکنینی زێڕ و داشکاندنی تێچووی توانەوە...",
        "invalid_price": "⚠️ تەنها ژمارە بنووسە!", "invalid_labor": "⚠️ کرێ تەنها بە ژمارە بنووسە!", "invalid_weight": "⚠️ هەڵە! کێش بە ژمارە بنێرە:",
        "expired_msg": BRAND_HEADER_KU + "🚫 **ماوەی تاقیکردنەوەی سیستەم کۆتایی هات!**\n\nتکایە بڕی **105,000 دینار** بنێرە بۆ ئەم ماستەرکارتە فەرمییە:\n`910400201646`\n\n📞 **پشتیوانی بەپەلە:** `{support_phone}`",
        "send_receipt_btn": "📸 ناردنی پسوڵەی پارەدان", "awaiting_receipt": "📝 تکایە ئێستا وێنەی پسوڵەکە بنێرە 👇",
        "receipt_sent_admin": "🎉 پسوڵەکەت بە سەرکەوتوویی نێردرا! لە کەمترین کاتدا کارەکەت چالاک دەکرێت. 🌸",
        "sell_invoice": BRAND_HEADER_KU + "🧾 **فاکتۆری فرۆشتنی زێڕ بە کڕیار**\n━━━━━━━━━━━━━━━━━━\n🔹 **زێڕینگەری**: `{shop_name}`\n🔹 **عەیار**: عەیار {karat} ({unit_arabic})\n🔹 **کێش**: `{weight}` {unit_text}\n⚖️ **کۆی گشتی کێش بە گرام**: `{total_grams:.3f}` گرام\n🔨 **کرێی دروستکردنی گرام**: `{labor:,.0f} دینار`\n━━━━━━━━━━━━━━━━━━\n💰 **کۆی گشتی بە دیناری عێراقی**:\n👉 **`{total_iqd:,.0f} دينار`**\n👉 **`{paper_and_dinar_text}`**",
        "buy_invoice": BRAND_HEADER_KU + "🧾 **فاکتۆری کڕینی زێڕ لە کڕیار**\n━━━━━━━━━━━━━━━━━━\n🔹 **زێڕینگەری**: `{shop_name}`\n🔹 **عەیار**: عەیار {karat}\n🔹 **کێش**: `{weight}` {unit_text}\n⚖️ **کۆی گشتی کێش**: `{total_grams:.3f}` گرام\n━━━━━━━━━━━━━━━━━━\n💵 **کۆی گشتی بڕی پارەی دراو**:\n👉 **`{total_iqd:,.0f} دينار`**\n👉 **`{paper_and_dinar_text}`**"
    }
}

def get_data():
    default_settings = {"mithqal_21": 450000, "mithqal_18": 380000, "labor_21": 10000, "labor_18": 10000, "usd_100": 150000}
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try: shutil.copy(DATA_FILE, DATA_FILE + '.bak')
        except: pass
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        if os.path.exists(DATA_FILE + '.bak') and os.path.getsize(DATA_FILE + '.bak') > 0:
            shutil.copy(DATA_FILE + '.bak', DATA_FILE)
        else:
            default_data = {"base_count": 166, "trial_days": 7, "system_broadcast": "", "support_phone": "07872180902", "users": {}, "settings": default_settings}
            save_data(default_data)
            return default_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    except:
        if os.path.exists(DATA_FILE + '.bak'):
            try:
                with open(DATA_FILE + '.bak', 'r', encoding='utf-8') as f: data = json.load(f)
                shutil.copy(DATA_FILE + '.bak', DATA_FILE)
            except: data = {}
        else: data = {}
    if 'settings' not in data: data['settings'] = default_settings
    if 'base_count' not in data: data['base_count'] = 166
    if 'trial_days' not in data: data['trial_days'] = 7
    if 'system_broadcast' not in data: data['system_broadcast'] = ""
    if 'support_phone' not in data: data['support_phone'] = "07872180902"
    if 'users' not in data: data['users'] = {}
    return data

def save_data(data):
    dir_name = os.path.dirname(os.path.abspath(DATA_FILE))
    try:
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, ensure_ascii=False, indent=4)
            temp_name = tf.name
        os.replace(temp_name, DATA_FILE)
    except Exception as e: print(f"❌ Save Error: {e}")

def get_user_lang(user_id):
    data = get_data()
    return data['users'].get(str(user_id), {}).get('lang', 'ar')

def set_user_lang(user_id, lang):
    data = get_data()
    uid = str(user_id)
    if uid not in data['users']: data['users'][uid] = {}
    data['users'][uid]['lang'] = lang
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
    if papers > 0: result.append(f"{papers} ورقة" if lang=='ar' else f"{papers} وەرەقە")
    if remaining_iqd > 0: result.append(f"{remaining_iqd:,.0f} دينار" if lang=='ar' else f"{remaining_iqd:,.0f} دینار")
    return " و ".join(result) if result else "0 دينار"

def get_keyboard(lang="ar"):
    t = TRANSLATIONS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(t["sell"], t["buy"])
    markup.add(t["settings"])
    return markup

def get_karat_unit_keyboard(lang="ar"):
    t = TRANSLATIONS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(t["karat_21_g"], t["karat_18_g"])
    markup.add(t["karat_21_m"], t["karat_18_m"])
    markup.add(t["back"])
    return markup

def send_main_menu(bot, chat_id, text_to_send, lang="ar"):
    data = get_data()
    broadcast = data.get("system_broadcast", "")
    final_text = text_to_send
    if broadcast: final_text = f"📢 **تنويه هام من الإدارة:**\n⚠️ _{broadcast}_\n\n━━━━━━━━━━━━━━━━━━\n\n" + text_to_send
    bot.send_message(chat_id, final_text, parse_mode="Markdown", reply_markup=get_keyboard(lang))
