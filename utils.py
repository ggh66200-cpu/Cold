import json, os, time, tempfile, shutil
from telebot import types

DATA_FILE = 'data.json'
SYSTEM_USERNAME = "@GoldenCalc_Bot"

# الهوية المؤسسية الموحدة لشركة أرامكي - فرع نواة الذهب
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
    "⚜️ _Nawat Al-Dhahab Smart Gold System_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

TRANSLATIONS = {
    "ar": {
        "welcome": BRAND_HEADER_AR + "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\nمرحباً بك في نظام الصياغة الأسرع والأدق في الأسواق! 👑\n🎁 تمتلك الآن **فترة تجريبية مجانية مدتها أسبوع كامل** للاختبار الفوري!\n\n🔢 **رقم الصائغ:** `#{shop_num}`\n📍 **المحل العامر:** `{shop_name}`\n🗺️ **الموقع:** `{shop_location}`\n📞 **الهاتف:** `{shop_phone}`\n\n👥 **المشتركين النشطين:** `{count} صائغ`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 معرف النظام الرسمي: {sys_user}\nيرجى اختيار العملية المطلوبة من الأزرار أدناه 👇",
        "sell": "💰 بيع للزبون", "buy": "⚖️ شراء سريع", "settings": "⚙️ أسعار الصباح", "back": "⬅️ الرجوع للرئيسية",
        "lang_saved": "🎉 تم تفعيل اللغة العربية بنجاح يا طيب! عساها فاتحة خير عليك. 🌸",
        "req_shop_name": BRAND_HEADER_AR + "📝 **خطوة التسجيل الرسمية للمحل**\n\nأخي الغالي، يرجى إرسال معلومات محلك الرسمي **كل معلومة في سطر منفصل (اضغط Enter للانتقال لسطر جديد)** بهذا الترتيب:\n\n1️⃣ اسم المحل\n2️⃣ المحافظة أو المدينة\n3️⃣ رقم هاتف المحل\n\n💡 **مثال للإرسال المباشر:**\nصياغة أرامكي الفاخرة\nبغداد، الكاظمية\n07701234567",
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
        "req_price_buy": "💰 أدخل سعر شراء المثقال المتفق عليه حالياً بالدينار العراقي:",
        "use_morning_price": "استخدام السعر الصباحي ({price:,} دينار)",
        "use_morning_labor": "استخدام الأجور الصباحية ({labor:,} دينار)",
        "req_labor_buy": "🔥 أدخل أجور الخصم أو الصهر للغرام الواحد بالدينار:",
        "req_labor_sell": "🔨 أرسل أجور صياغة الغرام الواحد بالدينار:",
        "invalid_price": "⚠️ يرجى كتابة السعر كأرقام فقط أو استخدام المقترح!",
        "invalid_labor": "⚠️ يرجى كتابة الأجور كأرقام فقط!",
        "invalid_weight": "⚠️ خطأ! يرجى إدخال رقم صحيح للوزن (مثال: 14.250):",
        "expired_msg": BRAND_HEADER_AR + "🎫 **باقة شيوخ الكار المطورين (خصم حصري)** 🎫\n\n🚫 انتهت الفترة التجريبية المخصصة للمنظومة.\nللاشتراك وتمديد الصلاحية بالسعر التنافسي المستمر بقيمة **105,000 دينار عراقي** فقط بدلاً من السعر الأساسي `133,000 دينار` (توفير 28,000 دينار عراقي بكل تجديد).\n\n⚜️💳 **حساب الإيداع المالي الذهبي للشركة:**\nرقم الماستر كارد الرسمي المعتمد:\n`910400201646`\n\n📸 بعد التحويل، اضغط على الزر بالأسفل وأرسل صورة الوصل لتفعيل حسابك تلقائياً.\n📞 خط الدعم الفني: `{support_phone}`",
        "send_receipt_btn": "📸 اضغط هنا لإرسال الوصل للتدقيق",
        "awaiting_receipt": "📝 يرجى الآن إرسال صورة الوصل المالي مباشرة للتدقيق الفوري 👇",
        "receipt_sent_admin": "🎉 **تم إرسال وصل الدفع بنجاح إلى قسم التدقيق المالي!**\nجاري مراجعة طلبكم وتفعيل النظام خلال دقائق معدودة يا طيب. شكراً لثقتكم بنا! 🌸",
        "sell_invoice": BRAND_HEADER_AR + "🧾 **فاتورة بيع ذهب رقمية**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل:** `{shop_name}`\n🔹 **النوع:** عيار {karat} ({unit_arabic})\n⚖️ **الوزن الصافي:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔨 **أجور الصياغة للجرام:** `{labor:,.0f}` د.ع\n💰 **سعر الغرام الصافي:** `{gram_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **الحساب الإجمالي بالدينار:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **صافي الحساب (بالورقة والدينار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت عبر نظام: {sys_user}\n🌸 **بالبركة والحلال الطيب لعملكم وزبائنكم!** ✨💛",
        "buy_invoice": BRAND_HEADER_AR + "🧾 **فاتورة شراء ذهب رقمية (شراء مبسط)**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل:** `{shop_name}`\n🔹 **النوع:** شراء عيار {karat} ({unit_arabic})\n⚖️ **الوزن المستلم:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔥 **خصم الصهر/الأجور:** `{labor:,.0f}` د.ع\n💰 **سعر شراء المثقال المعتمد:** `{mithqal_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **المبلغ الكلي الصافي المدفوع لكم:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **توزيع الحساب (بالورقة والدينار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت عبر نظام: {sys_user}\n🌸 **ربي يعوضكم بالخير والرزق الواسع الوفير!** ✨"
    },
    "ku": {
        "welcome": BRAND_HEADER_KU + "✨ **یا فەتاح یا عەلیم یا ڕەزاق یا کەریم** ✨\n\nبەخێربێن بۆ سیستەمی زیرەکی زێڕینگەری! 👑\n🎁 ئێستا تۆ **ماوەی یەک هەفتەی بێبەرامبەرت** هەیە بۆ تاقیکردنەوە!\n\n🔢 **ژمارەی زێڕینگەر:** `#{shop_num}`\n📍 **دوکان:** `{shop_name}`\n🗺️ **شوێن:** `{shop_location}`\n📞 **مۆبایل:** `{shop_phone}`\n\n👥 **زێڕینگەرانی چالاک:** `{count}`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 ناسنامەی فەرمی سیستەم: {sys_user}\nتکایە کردارەکە لە دوگمەکانی خوارەوە هەڵبژێرە 👇",
        "sell": "💰 فرۆشتن بە کڕیار", "buy": "⚖️ کڕینی خێرا", "settings": "⚙️ ڕێکخستنەکانی بەیانی", "back": "⬅️ گەڕانەوە بۆ سەرەکی",
        "lang_saved": "🎉 زمانی کوردی بە سەرکەوتوویی چالاککرا!",
        "req_shop_name": BRAND_HEADER_KU + "📝 **هەنگاوی تۆمارکردنی فەرمی دوکان**\n\nتکایە زانیاری دوکانەکەت بنێرە بە شێوازی دێڕ بە دێڕ (Enter دابگرە بۆ دێڕی نوێ):\n\n1️⃣ ناوی دوکان\n2️⃣ پارێزگا یان شار\n3️⃣ ژمارەی مۆبایل",
        "shop_saved": "🎉 دوکانەکەت بە ناوی **{shop_name}** تۆمارکرا! 🌸",
        "morning_title": BRAND_HEADER_KU + "☀️ **ڕێکخستنەکانی بەیانی ئێستای دوکانەکەت:**\n━━━━━━━━━━━━━━━━━━\n🔹 نرخی مسقاڵی ٢١: `{mithqal_21:,.0f} دينار`\n🔹 نرخی مسقاڵی ١٨: `{mithqal_18:,.0f} دينار`\n🔨 کرێی گرام ٢١: `{labor_21:,.0f} دینار`\n🔨 کرێی گرام ١٨: `{labor_18:,.0f} دینار`\n💵 نرخی ١٠٠ دۆلار: `{usd_100:,.0f} دینار`",
        "update_btn": "📝 نوێکردنەوەی نرخەکان بە یەکجار",
        "wizard_prompt": "⚙️ نرخە نوێیەکان بە یەک نامە بنێرە:\n`[مسقاڵ ٢١] [مسقاڵ ١٨] [کرێی ٢١] [کرێی ١٨] [دۆلار]`",
        "sweet_success": "🎉 **نرخەکان بە سەرکەوتوویی پاشەکەوت کران** 🌸✨",
        "error_format": "⚠️ هەڵە لە نووسیندا هەیە! تکایە نرخەکان بە دروستی بنێرە.",
        "choose_karat": "💰 **فرۆشتن بە کڕیار**", "choose_karat_buy": "⚖️ **کڕینی خێرا لە کڕیار**",
        "karat_21_g": "گرام عەیار 21", "karat_18_g": "گرام عەیار 18", "karat_21_m": "مسقاڵ عەیار 21", "karat_18_m": "مسقاڵ عەیار 18",
        "req_weight": "⚖️ کێشی داواکراو بنێرە ({unit_text}):",
        "req_weight_buy": "⚖️ ئێستا کێشی گشتی زێڕی کڕدراو بنێرە:",
        "req_price_buy": "💰 تکایە نرخی کڕینی مسقاڵ بنێرە بە دینار:",
        "use_morning_price": "بەکارهێنانی نرخی بەیانی ({price:,} دینار)",
        "use_morning_labor": "بەکارهێنانی کرێی بەیانی ({labor:,} دینار)",
        "req_labor_buy": "🔥 تێچووی توانەوە بۆ هەر گرامێک بنێرە:",
        "req_labor_sell": "🔨 کرێی دروستکردنی هەر گرامێک بنێرە:",
        "invalid_price": "⚠️ تەنها ژمارە بنووسە!", "invalid_labor": "⚠️ کرێ تەنها بە ژمارە بنووسە!", "invalid_weight": "⚠️ هەڵە! کێش بە ژمارە بنێرە:",
        "expired_msg": BRAND_HEADER_KU + "🚫 **ماوەی تاقیکردنەوەی سیستەم کۆتایی هات!**\nبۆ چالاککردنەوە بڕی **105,000 دینار** بنێرە بۆ ئەم ماستەرکارتە فەرمییە:\n`910400201646`\n\n🤖 لینک: {sys_user}\n📞 پشتیوانی: `{support_phone}`",
        "send_receipt_btn": "📸 ناردنی پسوڵەی پارەدان", "awaiting_receipt": "📝 تکایە ئێستا وێنەی پسوڵەکە بنێرە 👇",
        "receipt_sent_admin": "🎉 پسوڵەکەت بە سەرکەوتوویی نێردرا! لە کەمترین کاتدا کارەکەت چالاک دەکرێت. 🌸",
        "sell_invoice": BRAND_HEADER_KU + "🧾 **فاکتۆری فرۆشتنی زێڕی دیجیتاڵی**\n━━━━━━━━━━━━━━━━━━\n🏪 **دوکان:** `{shop_name}`\n🔹 **عەیار:** عەیار {karat}\n⚖️ **کێش:** `{weight}`\n📊 **کۆ بە گرام:** `{total_grams:.3f}` گرام\n🔨 **کرێی گرام:** `{labor:,.0f}`\n━━━━━━━━━━━━━━━━━━\n💵 **کۆی گشتی بە دینار:**\n👉 **`{total_iqd:,.0f}` دیناری عێراقی**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 سیستەم: {sys_user}\n🌸 **پیرۆز بێت و پڕ لە بەرەکەت بێت!** ✨💛",
        "buy_invoice": BRAND_HEADER_KU + "🧾 **فاکتۆری کڕینی زێڕی دیجیتاڵی**\n━━━━━━━━━━━━━━━━━━\n🏪 **دوکان:** `{shop_name}`\n🔹 **عەیار:** عەیار {karat}\n⚖️ **کێش:** `{weight}`\n📊 **کۆ بە گرام:** `{total_grams:.3f}` گرام\n━━━━━━━━━━━━━━━━━━\n💵 **کۆی گشتی بڕی پارەی دراو:**\n👉 **`{total_iqd:,.0f}` دينار**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 سیستەم: {sys_user}"
    },
    "en": {
        "welcome": BRAND_HEADER_EN + "✨ **Welcome to the Smart Jewelry System** ✨\n\nExperience the fastest and most accurate system in the market! 👑\n🎁 You have a **1-week completely free trial** active now!\n\n🔢 **Jeweler ID:** `#{shop_num}`\n📍 **Shop Name:** `{shop_name}`\n🗺️ **Location:** `{shop_location}`\n📞 **Phone:** `{shop_phone}`\n\n👥 **Active Jewelers:** `{count}`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 Official System: {sys_user}\nPlease select an option from below 👇",
        "sell": "💰 Sell to Customer", "buy": "⚖️ Quick Buy", "settings": "⚙️ Morning Prices", "back": "⬅️ Back to Main",
        "lang_saved": "🎉 English language activated successfully! Wishing you great success. 🌸",
        "req_shop_name": BRAND_HEADER_EN + "📝 **Official Shop Registration**\n\nPlease send your official shop details, **each on a new line (Press Enter for a new line)** in this order:\n\n1️⃣ Shop Name\n2️⃣ City / Governorate\n3️⃣ Phone Number\n\n💡 **Example:**\nAramky Luxury Gold\nBaghdad, Kadhimiya\n07701234567",
        "shop_saved": "🎉 Your shop **{shop_name}** has been registered successfully on our servers! 🌸",
        "morning_title": BRAND_HEADER_EN + "☀️ **Current Morning Price Settings:**\n━━━━━━━━━━━━━━━━━━\n🔹 Karat 21 Mithqal: `{mithqal_21:,.0f} IQD`\n🔹 Karat 18 Mithqal: `{mithqal_18:,.0f} IQD`\n🔨 Karat 21 Labor/g: `{labor_21:,.0f} IQD`\n🔨 Karat 18 Labor/g: `{labor_18:,.0f} IQD`\n💵 100 USD Rate: `{usd_100:,.0f} IQD`",
        "update_btn": "📝 Update All Prices At Once",
        "wizard_prompt": "⚙️ Send the 5 new prices in one space-separated message:\n`[Mithqal 21] [Mithqal 18] [Labor 21] [Labor 18] [USD]`\n⚠️ Karat 18 price must be lower than Karat 21!",
        "sweet_success": "🎉 **Prices updated and saved successfully!** 🌸✨",
        "error_format": "⚠️ Format error! Enter correct numbers and ensure Karat 18 is lower than 21!",
        "choose_karat": "💰 **Sell to Customer**\nSelect calculation method and Karat below 👇",
        "choose_karat_buy": "⚖️ **Quick Buy From Customer**\nSelect Karat and unit to start processing 👇",
        "karat_21_g": "21 Karat Gram", "karat_18_g": "18 Karat Gram", "karat_21_m": "21 Karat Mithqal", "karat_18_m": "18 Karat Mithqal",
        "req_weight": "⚖️ You selected **{text}**.\nEnter the weight ({unit_text}):",
        "req_weight_buy": "⚖️ Send the total weight to buy directly:",
        "req_price_buy": "💰 Enter the agreed purchase Mithqal price in IQD:",
        "use_morning_price": "Use Morning Price ({price:,} IQD)",
        "use_morning_labor": "Use Morning Labor ({labor:,} IQD)",
        "req_labor_buy": "🔥 Enter smelting/discount fee per Gram in IQD:",
        "req_labor_sell": "🔨 Enter manufacturing labor fee per Gram in IQD:",
        "invalid_price": "⚠️ Please enter digits only or use the suggestion button!",
        "invalid_labor": "⚠️ Please enter digits only!",
        "invalid_weight": "⚠️ Error! Please enter a valid weight (e.g., 14.250):",
        "expired_msg": BRAND_HEADER_EN + "🚫 **Trial Period Expired!**\nTo subscribe and unlock the premium system for **105,000 IQD** monthly (instead of `133,000 IQD`):\n\n⚜️💳 **Golden Master Card Account:**\n`910400201646`\n\n📸 Upload the payment receipt screenshot after transfer.\n🤖 Bot Link: {sys_user}\n📞 Support: `{support_phone}`",
        "send_receipt_btn": "📸 Click Here to Upload Receipt", "awaiting_receipt": "📝 Please send the receipt screenshot now 👇",
        "receipt_sent_admin": "🎉 **Receipt uploaded successfully to finance!**\nYour account will be updated within minutes. Thank you! 🌸",
        "sell_invoice": BRAND_HEADER_EN + "🧾 **Digital Gold Invoice**\n━━━━━━━━━━━━━━━━━━\n🏪 **Shop:** `{shop_name}`\n🔹 **Type:** Karat {karat} ({unit_arabic})\n⚖️ **Weight:** `{weight}`\n📊 **Total Grams:** `{total_grams:.3f}` g\n🔨 **Labor Fee/g:** `{labor:,.0f}` IQD\n💰 **Net Gold Price/g:** `{gram_price:,.0f}` IQD\n━━━━━━━━━━━━━━━━━━\n💵 **Total Amount in Dinars:**\n👉 **`{total_iqd:,.0f}` IQD**\n\n💵 **Total in USD Sheets & IQD:**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 Powered by: {sys_user}\n🌸 **May it bring prosperity to your business!** ✨💛",
        "buy_invoice": BRAND_HEADER_EN + "🧾 **Digital Purchase Invoice**\n━━━━━━━━━━━━━━━━━━\n🏪 **Shop:** `{shop_name}`\n🔹 **Type:** Buy Karat {karat}\n⚖️ **Weight:** `{weight}`\n📊 **Total Grams:** `{total_grams:.3f}` g\n━━━━━━━━━━━━━━━━━━\n💵 **Total Cash Paid to Customer:**\n👉 **`{total_iqd:,.0f}` IQD**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 Powered by: {sys_user}"
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
    
    if lang == 'ar':
        if papers > 0: result.append(f"`{papers}` ورقة")
        if remaining_iqd > 0: result.append(f"`{remaining_iqd:,.0f}` دينار")
    elif lang == 'ku':
        if papers > 0: result.append(f"`{papers}` وەرەقە")
        if remaining_iqd > 0: result.append(f"`{remaining_iqd:,.0f}` دینار")
    else:
        if papers > 0: result.append(f"`{papers}` Note(s)")
        if remaining_iqd > 0: result.append(f"`{remaining_iqd:,.0f}` IQD")
        
    return " & ".join(result) if lang=='en' else " و ".join(result) if result else "0"

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
    if broadcast: final_text = f"📢 **تنويه الإدارة:**\n⚠️ _{broadcast}_\n\n━━━━━━━━━━━━━━━━━━\n\n" + text_to_send
    bot.send_message(chat_id, final_text, parse_mode="Markdown", reply_markup=get_keyboard(lang))
