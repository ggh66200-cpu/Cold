import json, os, time, tempfile
from telebot import types

DATA_FILE = 'data.json'
SYSTEM_USERNAME = "@GoldenCalc_Bot"

BRAND_HEADER_AR = (
    "👑 **ARAMKY | أرامكي للحلول الرقمية** 👑\n"
    "⚜️ _منظومة نواة الذهب الذكية لشيوخ الصاغة_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

BRAND_HEADER_KU = (
    "👑 **ARAMKY | چارەسەرە دیجیتاڵییەکان** 👑\n"
    "⚜️ _سیستەمی زیرەکی ناوکی زێڕ بۆ گەورەی زێڕینگران_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

BRAND_HEADER_EN = (
    "👑 **ARAMKY | Digital Solutions** 👑\n"
    "⚜️ _Gold Nucleus Intelligent System for Elite Jewelers_ ⚜️\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
)

TRANSLATIONS = {
    "ar": {
        "welcome": BRAND_HEADER_AR + "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\nأهلاً ومرحباً بك يا طيب في منظومتك الإدارية الأسرع والأدق بالأسواق العريقة! 🌸\n🎁 رزقكم مبارك، وتم تفعيل **الفترة التجريبية المجانية المدتها {trial_days} أيام** لك تجتاح بها السوق ميدانياً!\n\n🔢 **رقم الصائغ المعتمد:** `#{shop_num}`\n📍 **المحل العامر:** `{shop_name}`\n🗺️ **الموقع:** `{shop_location}`\n📞 **الهاتف:** `{shop_phone}`\n\n👥 **المشتركين النشطين في الكار الآن:** `{count} صائغ`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 يرجى اختيار العملية المطلوبة من الأزرار أدناه وتوكل على الرزاق 👇",
        "sell": "💰 بيع للزبون", "buy": "⚖️ شراء سريع", "settings": "⚙️ أسعار الصباح", "back": "⬅️ الرجوع للرئيسية",
        "req_shop_name": BRAND_HEADER_AR + "📝 **خطوة تفعيل المحل وتأمين البيانات**\n\nأخي الغالي وصاحب الكار المحترم، يرجى إرسال معلومات محلك العامر **كل معلومة في سطر منفصل (اضغط Enter للانتقال لسطر جديد)** بهذا الترتيب لتسجيلك بالسيرفر:\n\n1️⃣ اسم المحل الرسمي\n2️⃣ المحافظة والمنطقة\n3️⃣ رقم هاتف المحل المعتمد",
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
        "unit_gram": "حساب بالغرام", "unit_mithqal": "حساب بالمثقال",
        "expired_msg": BRAND_HEADER_AR + "✨ **أخي الغالي وصاحب الكار المحترم** ✨\n\nنسأل الله العلي القدير أن يفتح لكم أبواب الرزق الحلال الواسع من حيث لا تحتسبون، وتظل محلاتكم تفيض بالخير والبركة والنجاح دائماً وأبدًا 🌸.\n\nنود إعلامكم بأن **الفترة التجريبية المجانية المخصصة للمنظومة قد انتهت مدتها**، ولأنكم من النواة الأولى وشركاء نجاح الأوائل، يسعدنا تقديم هذا العرض الاستثنائي لشخصكم الكريم:\n\n🎁 💥 **عـعرض خـصـم الـتـأسـيـس والـبـركـة:**\n• الاشتراك الشهري الرسمي العام: ~~133,000 دينار عراقي~~ للشهر.\n• القيمة الحالية الحصرية لكم: ✨ **105,000 دينار عراقي فقط!** ✨\n⚠️ _(تنويه هام: هذا التخفيض الخاص متاح **لفترة محدودة جداً**، وللإدارة الحق في إلغاء العرض والعودة للسعر الرسمي المقدر بـ 133,000 د.ع أو أكثر في أي وقت مستقبلاً)_\n\n━━━━━━━━━━━━━━━━━━━━━━\n💳 **قنوات الإيداع والتحويل المالي الرسمية للتفعيل الفوري:**\n\n🔹 **بطاقة الـ MasterCard الإلكترونية المعتمدة للشركة:**\n» رقم البطاقة المباشر: `{mastercard}`\n━━━━━━━━━━━━━━━━━━━━━━\n\n📞 🚨 **خط الطوارئ لقسم الدعم الفني (أرامكي):**\n» رقم التواصل الفوري: `{emergency_phone}`\n\n📸 بعد إتمام عملية التحويل، اضغط على الزر بالأسفل وأرسل صورة الوصل وسيقوم السيرفر بتفعيل الحساب فوراً 👇",
        "send_receipt_btn": "📸 اضغط هنا لإرسال وصل التحويل والتفعيل الفوري",
        "awaiting_receipt": "📝 على الرحب والسعة يا غالي، يرجى الآن إرسال صورة الوصل مباشرة من المعرض ليتم اعتماد حسابك برميّاً 👇",
        "receipt_sent_admin": "🎉 **تم إرسال وصل الدفع بنجاح إلى قسم التدقيق المالي لشركة أرامكي!**\nثوانٍ معدودة ويتم تحديث حسابك وفتح الصلاحيات بالكامل يا طيب. شكراً لثقتكم الغالية بنا! 🌸",
        "sell_invoice": BRAND_HEADER_AR + "🧾 **فاتورة بيع ذهب رقمية معتمدة**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل العامر:** `{shop_name}`\n🔹 **نوع العملية:** عيار {karat} ({unit_arabic})\n⚖️ **الوزن الصافي الموزون:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔨 **أجور الصياغة المعتمدة للجرام:** `{labor:,.0f}` د.ع\n💰 **سعر الغرام الصافي بدون أجور:** `{gram_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **الحساب الإجمالي الكلي بالدينار:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **صافي وتوزيع الحساب بنظام السوق (الورقة والدينار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت بدقة مطلقة عبر نظام: {sys_user}\n🌸 **بالبركة والحلال الطيب لعملكم وزبائنكم! جعلها الله فاتحة خير مستمرة** ✨💛",
        "buy_invoice": BRAND_HEADER_AR + "🧾 **فاتورة شراء ذهب رقمية مبسطة**\n━━━━━━━━━━━━━━━━━━\n🏪 **المحل العامر:** `{shop_name}`\n🔹 **نوع العملية:** شراء عيار {karat} ({unit_arabic})\n⚖️ **الوزن المستلم من الزبون:** `{weight}`\n📊 **الإجمالي بالجرام:** `{total_grams:.3f}` غرام\n🔥 **خصم الصهر أو الأجور:** `{labor:,.0f}` د.ع\n💰 **سعر شراء المثقال المعتمد:** `{mithqal_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **المبلغ الكلي الصافي المدفوع لكم:**\n👉 **`{total_iqd:,.0f}` دينار عراقي**\n\n💵 **توزيع الحساب بنظام السوق (الورقة والدينار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 حُسبت بدقة مطلقة عبر نظام: {sys_user}\n🌸 **ربي يعوضكم بالخير والبركة والرزق الواسع الوفير!** ✨"
    },
    "ku": {
        "welcome": BRAND_HEADER_KU + "✨ **یا فتاح یا علیم یا رزاق یا کریم** ✨\n\nبەخێربێیت برا گیان بۆ سیستەمی بەڕێوەبردنی خۆت کە خێراترین و وردترینە لە بازاڕدا! 🌸\n🎁 ڕزقتان پیرۆز بێت، **ماوەی تاقیکاری بێبەرامبەر بۆ {trial_days} ڕۆژ** بۆتان چالاککرا بۆ بەکارهێنانی مەیدانی!\n\n🔢 **ژمارەی زێڕینگری پەسەندکراو:** `#{shop_num}`\n📍 **دووکان:** `{shop_name}`\n🗺️ **شوێن:** `{shop_location}`\n📞 **تەلەفۆن:** `{shop_phone}`\n\n👥 **بەشداربووانی چالاک ئێستا لە بازاڕدا:** `{count} زێڕینگر`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 تکایە پرۆسەی داواکراو لە دوگمەکانی خوارەوە هەڵبژێرە و پشت بە خودا ببە 👇",
        "sell": "💰 فرۆشتن بە کڕیار", "buy": "⚖️ کڕینی خێرا", "settings": "⚙️ نرخەکانی بەیانی", "back": "⬅️ گەڕانەوە بۆ سەرەکی",
        "req_shop_name": BRAND_HEADER_KU + "📝 **هەنگاوی چالاککردنی دووکان و پاراستنی زانیارییەکان**\n\nبرا و هاوکارە بەڕێزەکەم، تکایە زانیاری دووکانەکەت بنێرە **هەر زانیارییەک لە دێڕێکی جیاواز (Enter دابگرە بۆ دێڕی نوێ)** بەم ڕیزبەندییە:\n\n1️⃣ ناوی فەرمی دووکان\n2️⃣ پارێزگا و ناوچە\n3️⃣ ژمارەی تەلەفۆنی پەسەندکراو",
        "shop_saved": "🎉 ماخۆ، دووکانەکەت بە ناوی **{shop_name}** تۆمارکرا و هەژمارەکەت پارێزرا! هیوادارم ببێتە مایەی خێر و بەرەکەت. 🌸",
        "morning_title": BRAND_HEADER_KU + "☀️ **ڕێکخستنی نرخەکانی بەیانی بۆ نووسینگەکەت:**\n━━━━━━━━━━━━━━━━━━\n🔹 نرخی مسقاڵ عەیار 21: `{mithqal_21:,.0f} دینار`\n🔹 نرخی مسقاڵ عەیار 18: `{mithqal_18:,.0f} دینار`\n🔨 کرێی گرام 21: `{labor_21:,.0f} دینار`\n🔨 کرێی گرام 18: `{labor_18:,.0f} دینار`\n💵 نرخی 100 دۆلار (وەرەقە): `{usd_100:,.0f} دینار`\n━━━━━━━━━━━━━━━━━━\n💡 بۆ نوێکردنەوەی نرخەکان، کلیک لەسەر دوگمەی خوارەوە بکە! 👇",
        "update_btn": "📝 نوێکردنەوەی نرخەکان بە یەکجار",
        "wizard_prompt": "⚙️ هەر 5 نرخە نوێیەکە لە یەک نامەدا بنێرە کە بە بۆشایی جیاکراونەتەوە:\n`[مسقاڵ 21] [مسقاڵ 18] [کرێی 21] [کرێی 18] [دۆلار]`\n⚠️ تێبینی: دەبێت نرخی عەیار 18 هەمیشە کەمتر بێت لە عەیار 21!",
        "sweet_success": "🎉 **نرخەکانی بەیانی بە سەرکەوتوویی نوێکرانەوە، سیستەمەکە ئامادەیە بۆ حیسابکردن** 🌸✨",
        "error_format": "⚠️ هەڵە لە ڕیزبەندی! تکایە ژمارەی دروست بنێرە و دڵنیابە نرخی 18 کەمترە لە 21!",
        "choose_karat": "💰 **ڕووکاری فرۆشتنی خێرا بە کڕیار**\nشێوازی حیسابکردن و عەیاری داواکراو هەڵبژێرە 👇",
        "choose_karat_buy": "⚖️ **ڕووکاری کڕینی خێرا لە کڕیار**\nعەیار و یەکە هەڵبژێرە بۆ دەستپێکردنی حیسابکردن 👇",
        "karat_21_g": "گرام عەیار 21", "karat_18_g": "گرام عەیار 18", "karat_21_m": "مسقاڵ عەیار 21", "karat_18_m": "مسقاڵ عەیار 18",
        "req_weight": "⚖️ تۆ **{text}**ت هەڵبژارد.\nتکایە کێشی تەواو بنێرە ({unit_text}):",
        "req_weight_buy": "⚖️ ئێستا کێشی گشتی بنێرە بۆ کڕینەوەی ڕاستەوخۆ:",
        "use_morning_labor": "بەکارهێنانی کرێی بەیانی ({labor:,} دینار)",
        "req_labor_sell": "🔨 کرێی دروستکردنی یەک گرام بە دیناری عێراقی بنێرە:",
        "invalid_labor": "⚠️ تکایە تەنها ژمارە بنووسە بێ کێشە!",
        "invalid_weight": "⚠️ هەڵە لە شێواز! تکایە ژمارەیەکی دروست بۆ کێش بنێرە (نموونە: 12.450):",
        "unit_gram": "حساب بە گرام", "unit_mithqal": "حساب بە مسقاڵ",
        "expired_msg": BRAND_HEADER_KU + "✨ **برا و هاوکاری بەڕێزم** ✨\n\nداواکارین لە خوای گەورە دەرگای ڕزقی حەڵاڵتان بۆ بکاتەوە و دووکانەکانتان هەمیشە پڕ بن لە خێر و سەرکەوتوویی 🌸.\n\nپێتان ڕادەگەیەنین کە **ماوەی تاقیکاری بێبەرامبەری سیستەمە زیرەکەکە کۆتایی هاتووە**، و لەبەر ئەوەی ئێوە لە یەکەمین هاوبەشانی سەرکەوتنمانن، خۆشحاڵین ئەم ئۆفەرە تایبەتە پێشکەش بکەین:\n\n🎁 💥 **ئۆفەری داشکاندنی دامەزراندن و بەرەکەت:**\n• بەشداریکردنی مانگانەی فەرمی گشتی: ~~133,000 دیناری عێراقی~~ بۆ مانگێک.\n• نرخی تایبەتی ئێستا بۆ ئێوە: ✨ **تەنها 105,000 دیناری عێراقی!** ✨\n⚠️ _(تێبینی گرنگ: ئەم داشکاندنە تایبەتە **بۆ ماوەیەکی سنووردارە**، و ئیدارە مافی هەیە ئۆفەرەکە هەڵبوەشێنێتەوە و بگەڕێتەوە سەر نرخی فەرمی 133,000 د.ع یان زیاتر لە هەر کاتێکدا)_\n\n━━━━━━━━━━━━━━━━━━━━━━\n💳 **کەناڵەکانی گواستنەوەی دارایی فەرمی بۆ چالاککردنی خێرا:**\n\n🔹 **کارتە پەسەندکراوەکانی MasterCard ی کۆمپانیا:**\n» ژمارەی کارت: `{mastercard}`\n━━━━━━━━━━━━━━━━━━━━━━\n\n📞 🚨 **هێڵی گەرمی بەشی پشتگیری تەکنیکی (ئارامکی):**\n» ژمارەی پەیوەندی خێرا: `{emergency_phone}`\n\n📸 دوای تەواوبوونی پرۆسەی گواستنەوەکە، کلیک لەسەر دوگمەی خوارەوە بکە و وێنەی پسوڵەکە بنێرە. دمتم بەخێر 🌸👇",
        "send_receipt_btn": "📸 لێرە کلیک بکە بۆ ناردنی پسوڵە و چالاککردنی خێرا",
        "awaiting_receipt": "📝 بەسەر چاو برا گیان، تکایە ئێستا وێنەی پسوڵەکە ڕاستەوخۆ بنێرە بۆ ئەوەی هەژمارەکەت چالاک بکرێت 👇",
        "receipt_sent_admin": "🎉 **پسوڵەی پارەدان بە سەرکەوتوویی نێردرا بۆ بەشی وردبینی دارایی ئارامكي!**\nچەند چرکەیەکی کەم و هەژمارەکەت نوێ دەکرێتەوە و دەسەڵاتەکان بە تەواوی دەکرێنەوە. سوپاس بۆ متمانەتان! 🌸",
        "sell_invoice": BRAND_HEADER_KU + "🧾 **پسوڵەی دیجیتاڵی فەرمی فرۆشتنی زێڕ**\n━━━━━━━━━━━━━━━━━━\n🏪 **دووکان:** `{shop_name}`\n🔹 **جۆری پرۆسە:** عەیار {karat} ({unit_arabic})\n⚖️ **کێشی دیاریکراو:** `{weight}`\n📊 **کۆیی گشتی بە گرام:** `{total_grams:.3f}` گرام\n🔨 **کرێی دیاریکراو بۆ هەر گرامێک:** `{labor:,.0f}` د.ع\n💰 **نرخی گرام بەبێ کرێ:** `{gram_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **حیسابی کۆتایی گشتی بە دینار:**\n👉 **`{total_iqd:,.0f}` دیناری عێراقي**\n\n💵 **دابەشکردنی حیساب بە سیستەمی بازاڕ (وەرەقە و دینار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 بە وردی حیسابکراوە لە ڕێگەی سیستەمی: {sys_user}\n🌸 **پیرۆزبێت و خێری لێببینن! خوای گەورە بیکاتە مایەی بەرەکەت** ✨💛",
        "buy_invoice": BRAND_HEADER_KU + "🧾 **پسوڵەی دیجیتاڵی کڕینەوەی زێڕ**\n━━━━━━━━━━━━━━━━━━\n🏪 **دووکان:** `{shop_name}`\n🔹 **جۆری پرۆسە:** کڕینەوەی عەیار {karat} ({unit_arabic})\n⚖️ **کێشی وەرگیراو لە کڕیار:** `{weight}`\n📊 **کۆیی گشتی بە گرام:** `{total_grams:.3f}` گرام\n🔥 **داشکاندنی حیساب یان کرێ:** `{labor:,.0f}` د.ع\n💰 **نرخی کڕینەوەی مسقاڵ:** `{mithqal_price:,.0f}` د.ع\n━━━━━━━━━━━━━━━━━━\n💵 **بڕی پارەی کۆتایی پێدراو بە ئێوە:**\n👉 **`{total_iqd:,.0f}` ديناری عێراقي**\n\n💵 **دابەشکردنی حیساب بە سیستەمی بازاڕ (وەرەقە و دینار):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 بە وردی حیسابکراوە لە ڕێگەی سیستەمی: {sys_user}\n🌸 **خوای گەورە قەرەبووتان بکاتەوە بە خێر و بەرەکەت!** ✨"
    },
    "en": {
        "welcome": BRAND_HEADER_EN + "✨ **In the Name of Allah, the Provider** ✨\n\nWelcome to your corporate management dashboard, the fastest system in the gold market! 🌸\n🎁 Your **{trial_days}-day free trial** is fully active for your live field operations!\n\n🔢 **Authorized Jeweler ID:** `#{shop_num}`\n📍 **Shop Name:** `{shop_name}`\n🗺️ **Location:** `{shop_location}`\n📞 **Phone:** `{shop_phone}`\n\n👥 **Active Jewelers Transacting Now:** `{count} Jewelers`\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 Please select your required operation from the buttons below 👇",
        "sell": "💰 Sell to Customer", "buy": "⚖️ Quick Buy", "settings": "⚙️ Morning Prices", "back": "⬅️ Back to Main",
        "req_shop_name": BRAND_HEADER_EN + "📝 **Shop Activation & Data Security Step**\n\nPlease send your official shop details **each item on a separate line (Press Enter for a new line)** in this exact order:\n\n1️⃣ Official Shop Name\n2️⃣ Governorate & District\n3️⃣ Authorized Phone Number",
        "shop_saved": "🎉 Mashallah! Your shop has been registered as **{shop_name}** and your account secured! May it bring endless blessings and prosperity. 🌸",
        "morning_title": BRAND_HEADER_EN + "☀️ **Morning Prices Configurations for Your Office:**\n━━━━━━━━━━━━━━━━━━\n🔹 21K Mithqal Price: `{mithqal_21:,.0f} IQD`\n🔹 18K Mithqal Price: `{mithqal_18:,.0f} IQD`\n🔨 21K Making Fee/Gram: `{labor_21:,.0f} IQD`\n🔨 18K Making Fee/Gram: `{labor_18:,.0f} IQD`\n💵 100 USD Rate (Paper): `{usd_100:,.0f} IQD`\n━━━━━━━━━━━━━━━━━━\n💡 To update all prices instantly, press the button below! 👇",
        "update_btn": "📝 Update All Prices At Once",
        "wizard_prompt": "⚙️ Send the 5 new prices in a single space-separated message:\n`[21 Mithqal] [18 Mithqal] [21 Labor] [18 Labor] [USD Rate]`\n⚠️ Mathematically: 18K price must be lower than 21K!",
        "sweet_success": "🎉 **Morning prices updated successfully! System is ready for live calculations.** 🌸✨",
        "error_format": "⚠️ Input format error! Please enter numbers only and verify 18K is lower than 21K!",
        "choose_karat": "💰 **Customer Quick Sell Interface**\nSelect calculation method and required karat below 👇",
        "choose_karat_buy": "⚖️ **Customer Quick Buy Interface**\nSelect karat and unit to begin live calculation 👇",
        "karat_21_g": "21 Karat Gram", "karat_18_g": "18 Karat Gram", "karat_21_m": "21 Karat Mithqal", "karat_18_m": "18 Karat Mithqal",
        "req_weight": "⚖️ You selected **{text}**.\nPlease send the net weight to calculate ({unit_text}):",
        "req_weight_buy": "⚖️ Send total weight to purchase immediately:",
        "use_morning_labor": "Use Morning Fee ({labor:,} IQD)",
        "req_labor_sell": "🔨 Send making fee per gram in Iraqi Dinars (IQD):",
        "invalid_labor": "⚠️ Digits only please!",
        "invalid_weight": "⚠️ Invalid decimal format! (e.g., 12.450):",
        "unit_gram": "Calculated in Grams", "unit_mithqal": "Calculated in Mithqals",
        "expired_msg": BRAND_HEADER_EN + "✨ **Dear Respected Business Partner** ✨\n\nWe pray that Almighty Allah grants you abundant lawful wealth and continuous success in your trade 🌸.\n\nWe would like to inform you that your **Free Trial Period has expired**. Since you are one of our elite founding partners in the Iraqi market, we are pleased to offer this exclusive discount:\n\n🎁 💥 **Founding Blessing Discount:**\n• Official Subscription Rate: ~~133,000 IQD~~ / month.\n• Exclusive Price for You: ✨ **105,000 IQD Only!** ✨\n⚠️ _(Important Notice: This special discount is available **for a limited time only**. Management reserves the right to revert to the official price of 133,000 IQD or higher at any time in the future)_\n\n━━━━━━━━━━━━━━━━━━━━━━\n💳 **Official Payment Channels for Instant Activation:**\n\n🔹 **Company MasterCard details:**\n» Card Number: `{mastercard}`\n━━━━━━━━━━━━━━━━━━━━━━\n\n📞 🚨 **Technical Support Hotline (Aramky):**\n» Contact Number: `{emergency_phone}`\n\n📸 After completing your payment transfer, click the button below to upload the receipt image 👇",
        "send_receipt_btn": "📸 Click Here to Upload Receipt for Instant Activation",
        "awaiting_receipt": "📝 Certainly! Please upload the receipt image directly to activate your account 👇",
        "receipt_sent_admin": "🎉 **Receipt successfully sent to Aramky Financial Audit Department!**\nYour account will be updated and full permissions unlocked within seconds. Thank you for your trust! 🌸",
        "sell_invoice": BRAND_HEADER_EN + "🧾 **Official Digital Gold Sales Invoice**\n━━━━━━━━━━━━━━━━━━\n🏪 **Shop Name:** `{shop_name}`\n🔹 **Operation Type:** Karat {karat} ({unit_arabic})\n⚖️ **Net Weight:** `{weight}`\n📊 **Total Weight (Grams):** `{total_grams:.3f}` g\n🔨 **Making Fee/Gram:** `{labor:,.0f}` IQD\n💰 **Net Gram Price (Excl. Fee):** `{gram_price:,.0f}` IQD\n━━━━━━━━━━━━━━━━━━\n💵 **Total Amount Due in IQD:**\n👉 **`{total_iqd:,.0f}` Iraqi Dinars**\n\n💵 **Market Standard Breakdown (Papers & Dinars):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 Calculated precisely via system: {sys_user}\n🌸 **May it bring continuous blessings and prosperity to your trade!** ✨💛",
        "buy_invoice": BRAND_HEADER_EN + "🧾 **Official Digital Gold Purchase Invoice**\n━━━━━━━━━━━━━━━━━━\n🏪 **Shop Name:** `{shop_name}`\n🔹 **Operation Type:** Purchase Karat {karat} ({unit_arabic})\n⚖️ **Weight Received:** `{weight}`\n📊 **Total Weight (Grams):** `{total_grams:.3f}` g\n🔥 **Melting Discount / Fee:** `{labor:,.0f}` IQD\n💰 **Mithqal Purchase Price:** `{mithqal_price:,.0f}` IQD\n━━━━━━━━━━━━━━━━━━\n💵 **Net Amount Paid to You:**\n👉 **`{total_iqd:,.0f}` Iraqi Dinars**\n\n💵 **Market Standard Breakdown (Papers & Dinars):**\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🤖 Calculated precisely via system: {sys_user}\n🌸 **May Allah compensate you with immense blessings and wealth!** ✨"
    }
}

def get_data():
    default_settings = {"mithqal_21": 450000, "mithqal_18": 380000, "labor_21": 10000, "labor_18": 10000, "usd_100": 150000}
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        default_data = {
            "base_count": 166, "trial_days": 7, "system_broadcast": "", 
            "emergency_phone": "07872180902", "mastercard": "5249 7112 8894 2026",
            "users": {}, "settings": default_settings
        }
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
    if usd_100_rate <= 0: return f"{total_iqd:,.0f}"
    papers = int(total_iqd // usd_100_rate)
    remaining_iqd = int(total_iqd % usd_100_rate)
    result = []
    if lang == 'ku':
        if papers > 0: result.append(f"`{papers}` وەرەقە")
        if remaining_iqd > 0: result.append(f"`{remaining_iqd:,.0f}` دینار")
        return " و ".join(result) if result else "0"
    elif lang == 'en':
        if papers > 0: result.append(f"`{papers}` Papers ($100)")
        if remaining_iqd > 0: result.append(f"`{remaining_iqd:,.0f}` IQD")
        return " and ".join(result) if result else "0"
    else:
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
