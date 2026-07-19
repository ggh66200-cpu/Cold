import json, os, time, tempfile
from telebot import types

DATA_FILE = 'data.json'
SYSTEM_USERNAME = "@GoldenCalc_Bot"

BRAND_HEADER_AR = (
    "👑 **ARAMKY | أرامكي للحلول الرقمية** 👑\n"
    "⚜️ _منظومة نواة الذهب الذكية لشيوخ الصاغة_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

TRANSLATIONS = {
    "ar": {
        "welcome": BRAND_HEADER_AR + "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\nأهلاً ومرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة! 🌸\n🎁 رزقكم مبارك، وتم تفعيل **الفترة التجريبية المجانية المدتها {trial_days} أيام** لك تجتاح بها السوق ميدانياً!\n\n🔢 **رقم الصائغ المعتمد:** `#{shop_num}`\n📍 **المحل العامر:** `{shop_name}`\n🗺️ **الموقع:** `{shop_location}`\n📞 **الهاتف:** `{shop_phone}`\n\n👥 **المشتركين النشطين في الكار الآن:** `{count} صائغ`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇",
        "sell": "💰 بيع للزبون", "buy": "⚖️ شراء سريع", "settings": "⚙️ أسعار الصباح", "back": "⬅️ الرجوع للرئيسية",
        "req_shop_name": BRAND_HEADER_AR + "📝 **خطوة تفعيل المحل وتأمين البيانات**\n\nأخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر **كل معلومة في سطر منفصل (اضغط Enter للانتقال لسطر جديد)** بهذا الترتيب لتسجيلك بالسيرفر:\n\n1️⃣ اسم المحل الرسمي\n2️⃣ المحافظة والمنطقة (مثل: بغداد، الكاظمية)\n3️⃣ رقم هاتف المحل المعتمد",
        "shop_saved": "🎉 ما شاء الله، تم تسجيل محلك باسم **{shop_name}** وتأمين حسابك بنجاح تام! عساه فاتحة خير وبركة ورزق لا ينتهي. 🌸",
        "morning_title": BRAND_HEADER_AR + "☀️ **إعدادات أسعار الصباح المبارك لمكتبكم:**\n━━━━━━━━━━━━━━━━━━\n🔹 سعر مثقال عيار 21: `{mithqal_21:,.0f} دينار`\n🔹 سعر مثقال عيار 18: `{mithqal_18:,.0f} دينار`\n🔨 أجور غرام 21: `{labor_21:,.0f} دينار`\n🔨 أجور غرام 18: `{labor_18:,.0f} دينار`\n💵 سعر الـ 100 دولار (الورقة): `{usd_100:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💡 لتحديث الأسعار بلمحة بصر، اضغط على الزر أدناه! 👇",
        "update_btn": "📝 تحديث الأسعار دفعة واحدة",
        "wizard_prompt": "⚙️ أرسل الأسعار الـ 5 الجديدة في رسالة واحدة متباعدة بمسافات:\n`[مثقال 21] [مثقال 18] [صياغة 21] [صياغة 18] [الدولار]`\n⚠️ للعلم: يجب أن يكون سعر عيار 18 أقل من عيار 21 دائماً برمجياً!",
        "sweet_success": "🎉 **تم حفظ وتحديث أسعار الصباح بنجاح، المنظومة جاهزة للحساب الفوري الآن** 🌸✨",
        "error_format": "⚠️ خطأ في الترتيب يا طيب! يرجى إدخال أرقام صحيحة وتأكد أن سعر 18 أقل من 21!",
        "choose_karat": "💰 **واجهة البيع الفوري للزبون**\nاختر طريقة الحساب والعيار المطلوب لتصفية الفاتورة 👇",
        "choose_karat_buy": "⚖️ **واجهة الشراء المبسط والسريع من زبون**\nاختر العيار والوحدة لتبدأ التصفية الفورية 👇",
        "karat_21_g": "غرام عيار 21", "karat_18_g": "غرام عيار 18", "karat_21_m": "مثقال عيار 21", "karat_18_m": "مثقال عيار 18",
        "req_weight": "⚖️ لقد اخترت **{text}**.\nالرجاء إرسال الوزن الصافي المراد حسابه ({unit_text}):",
        "req_weight_buy": "⚖️ أرسل الآن الوزن الإجمالي المراد شراؤه مباشرة لتصفية سعره المعتمد:",
        "use_morning_labor": "استخدام الأجور الصباحية ({labor:,} دينار)",
        "req_labor_sell": "🔨 أرسل أجور صياغة الغرام الواحد بالدينار العراقي حالياً:",
        "invalid_labor": "⚠️ يرجى كتابة الأجور كأرقام فقط يا غالي!",
        "invalid_weight": "⚠️ خطأ في الصيغة! يرجى إدخال رقم صحيح للوزن (مثال: 12.450):",
        
        # رسالة قفل الحسابات العذبة مع الخصم المغري والكلام الطيب شيوخ الكار
        "expired_msg": BRAND_HEADER_AR + "✨ **أخي الغالي، تاج راسنا وصاحب الكار المحترم** ✨\n\nنسأل الله أن يفتح لكم أبواب الرزق الحلال الواسع، وتظل محلاتكم تفيض بالخير والبركة دائماً وأبدًا 🌸.\n\nنود إعلامكم بأن **الفترة التجريبية المخصصة للمنظومة الذكية قد انتهت مدتها**، ولأنكم من شركاء النجاح الأوائل في سوق العراق العريق، قدمنا لكم هذا العرض الاستثنائي:\n\n🎁 💥 **عـرض خـصـم الـبـركـة والـتـأسـيـس الحصري:**\nالاشتراك الرسمي للمنظومة هو **105,000 دينار عراقي** شهرياً... **ولكن!** إذا قمت بالتفعيل اليوم، ستحصل على **خصم مباشر وتفعيل لمدة 45 يوماً كاملة** (شهر ونصف) بنفس سعر الشهر الواحد! كأقل تقدير ومحبة من شركة أرامكي لشخصكم الكريم. 🤝👑\n\n⚜️💳 **حساب الإيداع المالي الذهبي المباشر (Zain Cash المعتمد):**\nرقم المحفظة الرسمي المباشر للتفعيل التلقائي:\n`910400201646`\n\n📸 بعد إتمام عملية التحويل المباركة، اضغط على الزر بالأسفل وأرسل صورة الوصل، وسيتولى السيرفر فتح النظام لك برميّاً في أقل من دقيقة! دمت بألف خير وبركة 🌸👇",
        
        "send_receipt_btn": "📸 اضغط هنا لإرسال وصل التحويل والتفعيل الفوري",
        "awaiting_receipt": "📝 على الرحب والسعة يا غالي، يرجى الآن إرسال صورة الوصل مباشرة من المعرض ليتم اعتماد حسابك برميّاً 👇",
        "receipt_sent_admin": "🎉 **تم إرسال وصل الدفع بنجاح إلى قسم التدقيق المالي لشركة أرامكي!**\nثوانٍ معدودة ويتم تحديث حسابك وفتح الصلاحيات بالكامل يا طيب. شكراً لثقتكم الغالية بنا! 🌸",
        "sell_invoice": BRAND_HEADER_AR + "🧾 **فاتورة بيع ذهب رقمية**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل:** `{shop_name}`\n🔹 **النوع:** عيار {karat} ({unit_arabic})\n⚖️ **الوزن الصافي:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔨 **أجور الصياغة للجرام:** `{labor:,.0f}` د.ع\n💰 **سعر الغرام الصافي:** `{gram_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **الحساب الإجمالي بالدينار:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **صافي الحساب بالورقة والدينار العراقي:**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت بدقة مطلقة عبر نظام: {sys_user}\n🌸 **بالبركة والحلال الطيب لعملكم وزبائنكم!** ✨💛",
        "buy_invoice": BRAND_HEADER_AR + "🧾 **فاتورة شراء ذهب رقمية (شراء مبسط)**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل:** `{shop_name}`\n🔹 **النوع:** شراء عيار {karat} ({unit_arabic})\n⚖️ **الوزن المستلم:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔥 **خصم الصهر/الأجور:** `{labor:,.0f}` د.ع\n💰 **سعر شراء المثقال المعتمد:** `{mithqal_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **المبلغ الكلي الصافي المدفوع لكم:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **توزيع الحساب بالورقة والدينار العراقي:**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت بدقة مطلقة عبر نظام: {sys_user}\n🌸 **ربي يعوضكم بالخير والرزق الواسع الوفير!** ✨"
    }
}

# وراثة اللغات لحماية التشغيل من أي نقص مفاجئ في الملفات
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
