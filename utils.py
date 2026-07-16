import json, os, time
from telebot import types

DATA_FILE = 'data.json'

# القاموس المترجم بالكامل للغات الثلاث بكلام يفتح النفس
TRANSLATIONS = {
    "ar": {
        "welcome": "✨ **يا فتاح يا عليم يا رزاق يا كريم** ✨\n\nمرحباً بك في نظام الصياغة الذكي الأسرع والأدق في العراق! 👑\n\n👥 **عدد الصاغة النشطين في النظام حالياً:** `{count} صائغ`\n\nنسأل الله العلي القدير أن يبارك في تجارتكم ويفتح لكم أبواب الرزق الحلال الوفير. 🌸\nيرجى اختيار العملية المطلوبة من الأزرار أدناه 👇",
        "sell": "💰 بيع للزبون",
        "buy": "⚖️ شراء من زبون",
        "settings": "⚙️ إعدادات الصباح",
        "back": "⬅️ الرجوع للرئيسية",
        "lang_saved": "🎉 تم تفعيل اللغة العربية بنجاح يا طيب! عساها فاتحة خير عليك ورزق وفير. 🌸",
        "morning_title": "☀️ **صباح الرزق والبركة والسعادة يا طيب!** ☀️\n\nنسأل الله أن يجعل هذا اليوم يوماً مباركاً، مليئاً بالزبائن والخير الوفير لعملكم وحلالكم الطيب. 🌸✨\n\n📋 **إعدادات الصباح الحالية لمحلك:**\n━━━━━━━━━━━━━━━━━━\n🔹 سعر مثقال عيار 21: `{mithqal_21:,.0f} دينار`\n🔹 سعر مثقال عيار 18: `{mithqal_18:,.0f} دينار`\n🔨 أجور صياغة غرام 21: `{labor_21:,.0f} دينار`\n🔨 أجور صياغة غرام 18: `{labor_18:,.0f} دينار`\n💵 سعر الـ 100 دولار: `{usd_100:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💡 لتحديث جميع هذه الأسعار بلمحة بصر وسؤال واحد، اضغط على الزر أدناه! 👇",
        "update_btn": "📝 تحديث الأسعار دفعة واحدة",
        "wizard_prompt": "⚙️ **تحديث أسعار الصباح بلمحة واحدة**\n\nيا مية هلا بيك! أرسل لي الأسعار الـ 5 الجديدة في رسالة واحدة متباعدة بمسافات بهذا الترتيب الدقيق:\n\n`[مثقال 21] [مثقال 18] [صياغة 21] [صياغة 18] [الدولار]`\n\n**مثال للنسخ والتعديل عليه:**\n`450000 380000 10000 10000 153000`",
        "sweet_success": "🎉 **يا مية هلا وغلا بعيوني! تم حفظ الأسعار والحمد لله بنجاح تام** 🌸✨\n\nتم تحديث كافة أسعار الصباح في السيرفر وتأمينها بالكامل.\n\nعساها فاتحة خير ورزق وفير يملي حلالك وأيامك بركة وسعادة! 💸💛\nربي يفتحها بوجهك ويجعل كل عملية تسويها اليوم عملية مباركة تسعد خاطرك الطيب وتفرح گلبك الدافئ! 🥰☕",
        "error_format": "⚠️ خطأ في الصيغة! يرجى إدخال 5 أرقام صحيحة متباعدة بمسافات فقط.\nمثال:\n`450000 380000 10000 10000 153000`",
        "choose_karat": "💰 **بيع للزبون**\n\nاختر طريقة الحساب والعيار المطلوب من الأزرار أدناه 👇",
        "choose_karat_buy": "⚖️ **شراء من زبون**\n\nاختر طريقة الحساب والعيار المطلوب من الأزرار أدناه 👇",
        "karat_21_g": "غرام عيار 21",
        "karat_18_g": "غرام عيار 18",
        "karat_21_m": "مثقال عيار 21",
        "karat_18_m": "مثقال عيار 18",
        "req_weight": "⚖️ لقد اخترت **{text}**.\n\nالرجاء إرسال الوزن المطلوب بيعه لزبون ({unit_text}):",
        "req_weight_buy": "⚖️ أدخل الوزن المراد شراؤه من الزبون ({unit_text}):",
        "req_price_buy": "💰 لقد اخترت **{text}**.\n\nالرجاء إدخال سعر شراء المثقال المتفق عليه حالياً بالدينار:\n(أو اضغط على زر السعر الصباحي المقترح أدناه 👇)",
        "use_morning_price": "استخدام السعر الصباحي ({price:,} دينار)",
        "use_morning_labor": "استخدام الأجور الصباحية ({labor:,} دينار)",
        "req_labor_buy": "🔥 أدخل أجور الخصم أو الصهر للغرام الواحد بالدينار:\n(اكتب 0 إذا لا يوجد خصم)",
        "req_labor_sell": "🔨 أرسل أجور صياغة الغرام الواحد بالدينار:\n(أو اضغط على زر الصياغة الصباحية المعتادة أدناه 👇)",
        "loading_sell": "⚖️ جاري حساب الوزن الإجمالي والورق والدينار الحالي... ⚡📊",
        "loading_buy": "🔥 جاري فحص الذهب وخصم أجور الصهر والورق... ⚖️✨",
        "invalid_price": "⚠️ يرجى كتابة السعر كأرقام فقط (مثال: 450000) أو الضغط على السعر المقترح!",
        "invalid_labor": "⚠️ يرجى كتابة الأجور كأرقام فقط (مثال: 10000)!",
        "invalid_weight": "⚠️ خطأ! يرجى إدخال رقم صحيح للوزن (مثال: 12.5):",
        "sell_invoice": "🧾 **فاتورة بيع ذهب للزبون**\n━━━━━━━━━━━━━━━━━━\n🔹 **العيار وطريقة الحساب**: عيار {karat} ({unit_arabic})\n🔹 **الوزن المطلوب**: `{weight}` {unit_text}\n⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.2f}` غرام\n🔨 **أجور صياغة الغرام**: `{labor:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💰 **سعر غرام الذهب الصافي**: `{gram_price:,.0f} دينار`\n💵 **السعر الكلي بالدينار العراقي**:\n👉 **`{total_iqd:,.0f} دينار`**\n\n💵 **صافي الحساب بالورق والدينار**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **ألف مبروك وحلال عليكم! ربي يجعلها فاتحة خير وبركة ورزق واسع ومبارك لمحلك الطيب!** ✨💛",
        "buy_invoice": "🧾 **فاتورة شراء ذهب من زبون**\n━━━━━━━━━━━━━━━━━━\n🔹 **العيار وطريقة الشراء**: عيار {karat} ({unit_arabic})\n🔹 **الوزن المستلم**: `{weight}` {unit_text}\n⚖️ **الوزن الإجمالي بالجرام**: `{total_grams:.2f}` غرام\n🔥 **خصم الصهر/أجور الجرام**: `{labor:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💰 **سعر الشراء المعتمد للمثقال**: `{mithqal_price:,.0f} دينار`\n💰 **سعر غرام الشراء الصافي**: `{net_gram_price:,.0f} دينار`\n━━━━━━━━━━━━━━━━━━\n💵 **المبلغ الكلي المدفوع بالدينار العراقي**:\n👉 **`{total_iqd:,.0f} دينار`**\n\n💵 **صافي الحساب بالورق والدينار**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **تمت عملية الشراء بنجاح وشفافية مطلقة! ربي يعوضكم بالخير والرزق الوفير!** ✨"
    },
    "ku": {
        "welcome": "✨ **یا فەتاح یا عەلیم یا ڕەزاق یا کەریم** ✨\n\nبەخێربێن بۆ سیستەمی زیرەکی زێڕینگەری، خێراترین و دقیقترین لە عێراق! 👑\n\n👥 **ژمارەی کڕیارانی چالاک لە سیستەمەکەدا ئێستا:** `{count} زێڕینگەر`\n\nداواکارین لە خوای گەورە بەرەکەت بخاتە ناو بازرگانییەکەتانەوە. 🌸\nتکایە کردارەکە لە دوگمەکانی خوارەوە هەڵبژێرە 👇",
        "sell": "💰 فرۆشتن بە کڕیار",
        "buy": "⚖️ کڕین لە کڕیار",
        "settings": "⚙️ ڕێکخستنەکانی بەیانی",
        "back": "⬅️ گەڕانەوە بۆ سەرەکی",
        "lang_saved": "🎉 زمانی کوردی بە سەرکەوتوویی چالاککرا! هیوای سەرکەوتنت بۆ دەخوازم لە کار و کاسبیتدا. 🌸",
        "morning_title": "☀️ **بەیانیت باش و پڕ لە بەرەکەت بێت هاوڕێی ئازیز!** ☀️\n\nداواکارین لە خودا ئەم ڕۆژە بکاتە ڕۆژێکی پیرۆز و پڕ لە کڕیار و خێر بۆ کارەکەتان. 🌸✨\n\n📋 **ڕێکخستنەکانی بەیانی ئێستای دوکانەکەت:**\n━━━━━━━━━━━━━━━━━━\n🔹 نرخی مسقاڵی ٢١: `{mithqal_21:,.0f} دینار`\n🔹 نرخی مسقاڵی ١٨: `{mithqal_18:,.0f} دینار`\n🔨 کرێی دروستکردنی گرام ٢١: `{labor_21:,.0f} دینار`\n🔨 کرێی دروستکردنی گرام ١٨: `{labor_18:,.0f} دینار`\n💵 نرخی ١٠٠ دۆلار: `{usd_100:,.0f} دینار`\n━━━━━━━━━━━━━━━━━━\n💡 بۆ نوێکردنەوەی هەموو ئەم نرخانە بە ئاسانی بە یەک نامە، کلیک لەسەر دوگمەی خوارەوە بکە! 👇",
        "update_btn": "📝 نوێکردنەوەی نرخەکان بە یەکجار",
        "wizard_prompt": "⚙️ **نوێکردنەوەی نرخەکانی بەیانی بە یەک نامە**\n\nبەخێر بێیت چاوەکانم! هەر ٥ نرخە نوێیەکە لە یەک نامەدا بنێرە کە بە بۆشایی لێک جیاکرابێتنەوە بەم ڕیزبەندییە:\n\n`[مسقاڵ ٢١] [مسقاڵ ١٨] [کرێی ٢١] [کرێی ١٨] [دۆلار]`\n\n**نموونە بۆ کۆپیکردن و دەستکاریکردن:**\n`450000 380000 10000 10000 153000`",
        "sweet_success": "🎉 **بژیت چاوەکانم! نرخەکان بە سەرکەوتوویی پاشەکەوت کران** 🌸✨\n\nهەموو نرخەکانی بەیانی لە سێرڤەردا نوێکرانەوە و پارێزراون.\n\nهیوادارم ببێتە مایەی خێر و دەروازەی ڕۆزییەکی فراوان بۆتان! 💸💛\nخودا دەرگای خێرتان لێ بکاتەوە و هەموو مامەڵەیەکتان پڕ لە بەرەکەت بکات! 🥰☕",
        "error_format": "⚠️ هەڵە لە نووسیندا هەیە! تکایە ٥ ژمارەی دروست بنێرە کە تەنها بە بۆشایی جیاکرابێتنەوە.\nنموونە:\n`450000 380000 10000 10000 153000`",
        "choose_karat": "💰 **فرۆشتن بە کڕیار**\n\nشێوازی حیسابکردن و عەیاری داواکراو لە دوگمەکانی خوارەوە هەڵبژێرە 👇",
        "choose_karat_buy": "⚖️ **کڕین لە کڕیار**\n\nشێوازی حیسابکردن و عەیاری داواکراو لە دوگمەکانی خوارەوە هەڵبژێرە 👇",
        "karat_21_g": "گرام عەیار 21",
        "karat_18_g": "گرام عەیار 18",
        "karat_21_m": "مسقاڵ عەیار 21",
        "karat_18_m": "مسقاڵ عەیار 18",
        "req_weight": "⚖️ تۆ **{text}**ت هەڵبژارد.\n\nتکایە کێشی داواکراو بنێرە بۆ فرۆشتن ({unit_text}):",
        "req_weight_buy": "⚖️ کێشی کڕین لە کڕیار بنێرە ({unit_text}):",
        "req_price_buy": "💰 تۆ **{text}**ت هەڵبژارد.\n\nتکایە نرخی کڕینی مسقاڵی ڕێککەوتوو بنێرە بە دینار:\n(یاخود کلیک لەسەر نرخی پێشنیارکراوی بەیانی بکە لە خوارەوە 👇)",
        "use_morning_price": "بەکارهێنانی نرخی بەیانی ({price:,} دینار)",
        "use_morning_labor": "بەکارهێنانی کرێی بەیانی ({labor:,} دینار)",
        "req_labor_buy": "🔥 تێچووی توانەوە/داشکاندنی هەر گرامێک بنێرە بە دینار:\n(بنووسە 0 ئەگەر داشکاندن نییە)",
        "req_labor_sell": "🔨 کرێی دروستکردنی هەر گرامێک بنێرە بە دینار:\n(یاخود کلیک لەسەر کرێی بەیانی بکە لە خوارەوە 👇)",
        "loading_sell": "⚖️ کێش و بڕی پارە و دۆلار حیساب دەکرێت... ⚡📊",
        "loading_buy": "🔥 پشکنینی زێڕ و داشکاندنی تێچووی توانەوە... ⚖️✨",
        "invalid_price": "⚠️ تکایە تەنها ژمارە بنووسە (نموونە: 450000) یاخود کلیک لەسەر نرخی پێشنیارکراو بکە!",
        "invalid_labor": "⚠️ تکایە کرێ تەنها بە ژمارە بنووسە (نموونە: 10000)!",
        "invalid_weight": "⚠️ هەڵە! تکایە کێش بە ژمارەیەکی دروست بنێرە (نموونە: 12.5):",
        "sell_invoice": "🧾 **فاکتۆری فرۆشتنی زێڕ بە کڕیار**\n━━━━━━━━━━━━━━━━━━\n🔹 **عەیار و شێوازی حیسابکردن**: عەیار {karat} ({unit_arabic})\n🔹 **کێشی داواکراو**: `{weight}` {unit_text}\n⚖️ **کۆی گشتی کێش بە گرام**: `{total_grams:.2f}` گرام\n🔨 **کرێی دروستکردنی گرام**: `{labor:,.0f} دینار`\n━━━━━━━━━━━━━━━━━━\n💰 **نرخی گرامێکی زێڕی ساف**: `{gram_price:,.0f} دینار`\n💵 **کۆی گشتی بە دیناری عێراقی**:\n👉 **`{total_iqd:,.0f} دینار`**\n\n💵 **کۆی گشتی بە دەفتەر (وەرەقە) و دینار**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **پیرۆز بێت و بەخێر بێت! خوای گەورە بەرەکەت بخاتە کار و کاسبیتانەوە!** ✨💛",
        "buy_invoice": "🧾 **فاکتۆری کڕینی زێڕ لە کڕیار**\n━━━━━━━━━━━━━━━━━━\n🔹 **عەیار و شێوازی کڕین**: عەیار {karat} ({unit_arabic})\n🔹 **کێشی وەرگیراو**: `{weight}` {unit_text}\n⚖️ **کۆی گشتی کێش بە گرام**: `{total_grams:.2f}` گرام\n🔥 **داشکاندنی توانەوە بۆ گرام**: `{labor:,.0f} دینار`\n━━━━━━━━━━━━━━━━━━\n💰 **نرخی کڕینی ڕێککەوتوو بۆ مسقاڵ**: `{mithqal_price:,.0f} دینار`\n💰 **نرخی گرامێکی ساف بۆ کڕین**: `{net_gram_price:,.0f} دینار`\n━━━━━━━━━━━━━━━━━━\n💵 **کۆی گشتی بڕی پارەی دراو بە دیناری عێراقی**:\n👉 **`{total_iqd:,.0f} دینار`**\n\n💵 **کۆی گشتی بە دەفتەر (وەرەقە) و دینار**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **کرداری کڕین بە سەرکەوتوویی و بە تەواوی ڕوونی ئەنجامدرا! خوای گەورە قەرەبووتان بکاتەوە بە خێر!** ✨"
    },
    "en": {
        "welcome": "✨ **Welcome to the Smart Goldsmith System** ✨\n\nThe fastest and most accurate system in Iraq! 👑\n\n👥 **Active users in the system:** `{count}`\n\nMay Allah bless your trade and grant you success. 🌸\nPlease select your operation from the menu below 👇",
        "sell": "💰 Sell to Customer",
        "buy": "⚖️ Buy from Customer",
        "settings": "⚙️ Morning Settings",
        "back": "⬅️ Back to Main",
        "lang_saved": "🎉 English language activated successfully! 🌸",
        "morning_title": "☀️ **Good morning, wishing you a blessed and successful day!** ☀️\n\nMay Allah bless your trade and business. 🌸✨\n\n📋 **Current Morning Settings:**\n━━━━━━━━━━━━━━━━━━\n🔹 Price of Mithqal 21: `{mithqal_21:,.0f} IQD`\n🔹 Price of Mithqal 18: `{mithqal_18:,.0f} IQD`\n🔨 Labor per Gram 21: `{labor_21:,.0f} IQD`\n🔨 Labor per Gram 18: `{labor_18:,.0f} IQD`\n💵 USD 100 Rate: `{usd_100:,.0f} IQD`\n━━━━━━━━━━━━━━━━━━\n💡 To update all settings in one go without typing complex codes, click the button below! 👇",
        "update_btn": "📝 Update All Prices at Once",
        "wizard_prompt": "⚙️ **Update Morning Prices in One Message**\n\nWelcome! Please send the 5 new prices separated by spaces (or new lines) in this exact order:\n\n`[Mithqal 21] [Mithqal 18] [Labor 21] [Labor 18] [USD 100 Rate]`\n\n**Example to copy and edit:**\n`450000 380000 10000 10000 153000`",
        "sweet_success": "🎉 **Awesome! Prices saved successfully** 🌸✨\n\nAll morning prices have been updated in the server.\n\nMay this be the start of abundant success and blessings for your business! 💸💛 🥰☕",
        "error_format": "⚠️ Format error! Please enter exactly 5 numbers separated by spaces.\nExample:\n`450000 380000 10000 10000 153000`",
        "choose_karat": "💰 **Sell to Customer**\n\nSelect calculation method and Karat below 👇",
        "choose_karat_buy": "⚖️ **Buy from Customer**\n\nSelect calculation method and Karat below 👇",
        "karat_21_g": "Gram Karat 21",
        "karat_18_g": "Gram Karat 18",
        "karat_21_m": "Mithqal Karat 21",
        "karat_18_m": "Mithqal Karat 18",
        "req_weight": "⚖️ You selected **{text}**.\n\nPlease enter the weight to sell ({unit_text}):",
        "req_weight_buy": "⚖️ Enter the weight to buy from customer ({unit_text}):",
        "req_price_buy": "💰 You selected **{text}**.\n\nPlease enter the agreed purchase price of Mithqal in IQD:\n(Or click the suggested morning price button below 👇)",
        "use_morning_price": "Use Morning Price ({price:,} IQD)",
        "use_morning_labor": "Use Morning Labor ({labor:,} IQD)",
        "req_labor_buy": "🔥 Enter melting/discount cost per gram in IQD:\n(Enter 0 if no discount)",
        "req_labor_sell": "🔨 Send labor per gram in IQD:\n(Or click the suggested morning labor button below 👇)",
        "loading_sell": "⚖️ Calculating total weight, papers, and IQD... ⚡📊",
        "loading_buy": "🔥 Checking gold and deducting melting cost... ⚖️✨",
        "invalid_price": "⚠️ Please enter numbers only (e.g., 450000) or press the suggested price button!",
        "invalid_labor": "⚠️ Please enter labor as numbers only (e.g., 10000)!",
        "invalid_weight": "⚠️ Error! Please enter a valid weight (e.g., 12.5):",
        "sell_invoice": "🧾 **Gold Sale Invoice**\n━━━━━━━━━━━━━━━━━━\n🔹 **Karat & Method**: Karat {karat} ({unit_arabic})\n🔹 **Requested Weight**: `{weight}` {unit_text}\n⚖️ **Total Weight in Grams**: `{total_grams:.2f}` grams\n🔨 **Labor per Gram**: `{labor:,.0f} IQD`\n━━━━━━━━━━━━━━━━━━\n💰 **Pure Gold Gram Price**: `{gram_price:,.0f} IQD`\n💵 **Total Price in Iraqi Dinar**:\n👉 **`{total_iqd:,.0f} IQD`**\n\n💵 **Total in Papers and Dinar**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **Congratulations! May Allah bless your purchase and trade!** ✨💛",
        "buy_invoice": "🧾 **Gold Purchase Invoice**\n━━━━━━━━━━━━━━━━━━\n🔹 **Karat & Method**: Karat {karat} ({unit_arabic})\n🔹 **Received Weight**: `{weight}` {unit_text}\n⚖️ **Total Weight in Grams**: `{total_grams:.2f}` grams\n🔥 **Melting/Gram Discount**: `{labor:,.0f} IQD`\n━━━━━━━━━━━━━━━━━━\n💰 **Agreed Mithqal Purchase Price**: `{mithqal_price:,.0f} IQD`\n💰 **Net Gram Purchase Price**: `{net_gram_price:,.0f} IQD`\n━━━━━━━━━━━━━━━━━━\n💵 **Total Amount Paid in Iraqi Dinar**:\n👉 **`{total_iqd:,.0f} IQD`**\n\n💵 **Total in Papers and Dinar**:\n👉 **`{paper_and_dinar_text}`**\n━━━━━━━━━━━━━━━━━━\n🌸 **Purchase completed successfully with complete transparency! May Allah bless you with abundance!** ✨"
    }
}

def get_data():
    default_settings = {
        "mithqal_21": 450000,
        "mithqal_18": 380000,
        "labor_21": 10000,
        "labor_18": 10000,
        "usd_100": 150000
    }
    
    if not os.path.exists(DATA_FILE):
        default_data = {
            "total_count": 166,
            "users": {},
            "settings": default_settings
        }
        save_data(default_data)
        return default_data
        
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: 
            data = json.load(f)
    except:
        data = {
            "total_count": 166,
            "users": {},
            "settings": default_settings
        }

    if 'settings' not in data:
        data['settings'] = default_settings
    else:
        for k, v in default_settings.items():
            if k not in data['settings']:
                data['settings'][k] = v
                
    if 'total_count' not in data:
        data['total_count'] = 166
    if 'users' not in data:
        data['users'] = {}
        
    save_data(data)
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user_lang(user_id):
    data = get_data()
    uid = str(user_id)
    if uid in data['users'] and isinstance(data['users'][uid], dict):
        return data['users'][uid].get('lang', 'ar')
    return 'ar'

def set_user_lang(user_id, lang):
    data = get_data()
    uid = str(user_id)
    if uid not in data['users'] or not isinstance(data['users'][uid], dict):
        data['users'][uid] = {}
    data['users'][uid]['lang'] = lang
    save_data(data)

def update_all_settings(vals):
    data = get_data()
    keys = ["mithqal_21", "mithqal_18", "labor_21", "labor_18", "usd_100"]
    for i, k in enumerate(keys):
        data['settings'][k] = int(vals[i])
    save_data(data)

def calculate_paper_and_dinar(total_iqd, usd_100_rate, lang='ar'):
    if usd_100_rate <= 0:
        return f"{total_iqd:,.0f} دينار" if lang in ['ar', 'ku'] else f"{total_iqd:,.0f} IQD"
    
    papers = int(total_iqd // usd_100_rate)
    remaining_iqd = int(total_iqd % usd_100_rate)
    
    result = []
    if papers > 0:
        if lang == 'ar':
            if papers == 1:
                result.append("1 ورقة")
            elif papers == 2:
                result.append("2 ورقة")
            else:
                result.append(f"{papers} ورقة")
        elif lang == 'ku':
            result.append(f"{papers} وەرەقە")
        else:
            result.append(f"{papers} Paper" if papers == 1 else f"{papers} Papers")
            
    if remaining_iqd > 0:
        if lang == 'ar':
            result.append(f"{remaining_iqd:,.0f} دينار")
        elif lang == 'ku':
            result.append(f"{remaining_iqd:,.0f} دینار")
        else:
            result.append(f"{remaining_iqd:,.0f} IQD")
        
    if not result:
        return "0 دينار" if lang in ['ar', 'ku'] else "0 IQD"
        
    return " و ".join(result) if lang in ['ar', 'ku'] else " and ".join(result)

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
    bot.send_message(chat_id, text_to_send, parse_mode="Markdown", reply_markup=get_keyboard(lang))
