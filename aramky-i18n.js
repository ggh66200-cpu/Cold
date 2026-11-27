(function (global) {
  'use strict';

  const STORAGE_KEY = 'aramky_lang_v28';
  const ORDER = ['ar', 'ku', 'en'];

  const DICTS = {
    ar: {
      label: 'العربية (AR)',
      dir: 'rtl',
      lang: 'ar',
      statusActive: 'نشط',
      statusLocked: 'متوقف',
      'i18n-lang-label': 'العربية (AR)',
      'pwa-install-label': 'تثبيت / APK ⚜️',
      'i18n-refresh-label': 'تحديث الذاكرة',
      'i18n-admin-label': 'لوحة الأدمن 👑',
      'i18n-switch-label': 'تبديل الحساب',
      'i18n-storefront-label': 'معرض الزبائن',
      'i18n-return-label': 'إرجاع فاتورة',
      'i18n-calc-label': 'حاسبة آرامكي',
      'i18n-prices-label': 'الأسعار (5)',
      'i18n-reset-label': 'تصفير (0)',
      'i18n-ticker-title': 'الأسعار والمثاقيل:',
      'i18n-ticker-usd': 'الورقة (100$):',
      'i18n-ticker-m24': 'عيار 24:',
      'i18n-ticker-m22': 'عيار 22:',
      'i18n-ticker-m21': 'عيار 21:',
      'i18n-ticker-m18': 'عيار 18:',
      'i18n-ticker-m9': 'عيار 9:',
      'i18n-sidebar-title': 'لوحة التحكم المؤسسية',
      'i18n-tab-dashboard': 'الرئيسية والخزينة',
      'i18n-tab-pos': 'نقطة البيع (الكاسير)',
      'i18n-tab-scrap': 'شراء ذهب كسر',
      'i18n-tab-inventory': 'المخزن (تعديل وحذف)',
      'i18n-tab-store-settings': 'إعدادات المعرض والشعار',
      'i18n-tab-debts': 'دفتر الديون (يطلبهم ويطلبوني)',
      'i18n-tab-logs': 'الأرباح وجرد Excel',
      'i18n-tab-support': 'الدعم ومراسلة الأدمن',
      'i18n-dash-cash': 'صندوق الكاش (دينار)',
      'i18n-dash-usd': 'صندوق الدولار ($)',
      'i18n-dash-zain': 'زين كاش والماستر',
      'i18n-dash-profit': 'صافي أرباح الصياغة',
      'i18n-exp-title': 'تسجيل مصروف يومي',
      'i18n-exp-save-btn': 'تسجيل المصروف',
      'i18n-debts-title': 'دفتر الديون الفخم (يطلبهم + ويطلبوني -)',
      'i18n-debts-subtitle': 'تنظيم واضح لكارتات (يطلبهم) و(يطلبوني) مع زيادة (+) ونقصان (-) للذهب والأموال وجرد كامل داخل كل كرت',
      'i18n-debts-summary-them': 'إجمالي ما يطلبهم (لنا عند الناس +)',
      'i18n-debts-summary-us': 'إجمالي ما يطلبوني (علينا للناس -)',
      'i18n-debts-summary-net': 'صافي ميزان الديون العام (يطلبهم - يطلبوني)',
      'i18n-debts-save-btn': 'حفظ الحركة وتحديث كارت الديون الفخم 📖',
      'i18n-lock-title': 'الاشتراك متوقف!',
      'i18n-lock-desc': 'اشتراكك متوقف أو منتهي في نظام ARAMKY Gold OS. يمكنك فقط التواصل مع الدعم الفني.',
      'i18n-lock-support-btn': 'التواصل مع الدعم الفني 🛟',
      'i18n-lock-switch-btn': 'تبديل الحساب / تسجيل الخروج 🔄',
      'i18n-login-title': 'تسجيل دخول المعرض / المشترك',
      'i18n-login-desc': 'الدخول متاح فقط للحسابات المعتمدة من الأدمن (الكود، رقم الهاتف، وكلمة المرور)',
      'i18n-login-code-label': 'معرف الحساب / الكود',
      'i18n-login-phone-label': 'رقم الهاتف المرتبط بالحساب',
      'i18n-login-pass-label': 'كلمة المرور',
      'i18n-login-submit-btn': 'دخول إلى النظام 🔓'
    },
    ku: {
      label: 'کوردی (KU)',
      dir: 'rtl',
      lang: 'ku',
      statusActive: 'چالاکە',
      statusLocked: 'وەستاوە',
      'i18n-lang-label': 'کوردی (KU)',
      'pwa-install-label': 'دامەزراندن / APK ⚜️',
      'i18n-refresh-label': 'نوێکردنەوەی یادگە',
      'i18n-admin-label': 'پانێڵی ئەدمین 👑',
      'i18n-switch-label': 'گۆڕینی هەژمار',
      'i18n-storefront-label': 'پیشانگای کڕیاران',
      'i18n-return-label': 'گەڕاندنەوەی پسوولە',
      'i18n-calc-label': 'ژمێرەری ئارامکی',
      'i18n-prices-label': 'نرخەکان (5)',
      'i18n-reset-label': 'سفرکردن (0)',
      'i18n-ticker-title': 'نرخ و مسقاڵەکان:',
      'i18n-ticker-usd': 'وەرەقە (100$):',
      'i18n-ticker-m24': 'عەیار 24:',
      'i18n-ticker-m22': 'عەیار 22:',
      'i18n-ticker-m21': 'عەیار 21:',
      'i18n-ticker-m18': 'عەیار 18:',
      'i18n-ticker-m9': 'عەیار 9:',
      'i18n-sidebar-title': 'پانێڵی بەڕێوەبردنی دامەزراوەیی',
      'i18n-tab-dashboard': 'سەرەکی و قاسە',
      'i18n-tab-pos': 'خاڵی فرۆشتن (کاشێر)',
      'i18n-tab-scrap': 'کڕینی زێڕی شکاو',
      'i18n-tab-inventory': 'کۆگا (دەستکاریکردن و سڕینەوە)',
      'i18n-tab-store-settings': 'ڕێکخستنی پێشانگا و لۆگۆ',
      'i18n-tab-debts': 'تۆماری قەرزەکان (+ داوایان دەکەین / - داوامان دەکەن)',
      'i18n-tab-logs': 'قازانج و ڕاپۆرتی Excel',
      'i18n-tab-support': 'پشتگیری و پەیوەندی بە ئەدمین',
      'i18n-dash-cash': 'قاسەی کاش (دینار)',
      'i18n-dash-usd': 'قاسەی دۆلار ($)',
      'i18n-dash-zain': 'زەین کاش و ماستەر',
      'i18n-dash-profit': 'پاکێتی قازانجی دەستکرد',
      'i18n-exp-title': 'تۆمارکردنی خەرجی ڕۆژانە',
      'i18n-exp-save-btn': 'تۆمارکردنی خەرجی',
      'i18n-debts-title': 'تۆماری قەرزەکان (+ داوایان دەکەین / - داوامان دەکەن)',
      'i18n-debts-subtitle': 'ڕێکخستنی کارتی قەرزەکان بە زیادکردن (+) و کەمکردنەوە (-) بۆ زێڕ و پارە و هەژماردنی تەواو',
      'i18n-debts-summary-them': 'کۆی ئەوەی داوایان دەکەین (+)',
      'i18n-debts-summary-us': 'کۆی ئەوەی داوامان دەکەن (-)',
      'i18n-debts-summary-net': 'پاکێتی هاوسەنگی گشتی قەرزەکان',
      'i18n-debts-save-btn': 'پاشەکەوتکردن و نوێکردنەوەی کارتی قەرز 📖',
      'i18n-lock-title': 'بەشداریکردن وەستاوە!',
      'i18n-lock-desc': 'بەشداریکردنەکەت لە سیستەمی ARAMKY Gold OS وەستاوە یان بەسەرچووە. تەنها دەتوانیت پەیوەندی بە پشتگیری بکەیت.',
      'i18n-lock-support-btn': 'پەیوەندی بە پشتگیری هونەری 🛟',
      'i18n-lock-switch-btn': 'گۆڕینی هەژمار / چوونەدەرەوە 🔄',
      'i18n-login-title': 'چوونەژوورەوەی پێشانگا / بەشداربوو',
      'i18n-login-desc': 'چوونەژوورەوە تەنها بۆ هەژمارە پەسەندکراوەکانی ئەدمینە (کۆد، ژمارەی مۆبایل، وشەی نهێنی)',
      'i18n-login-code-label': 'ناسنامەی هەژمار / کۆد',
      'i18n-login-phone-label': 'ژمارەی مۆبایلی پەیوەست بە هەژمار',
      'i18n-login-pass-label': 'وشەی نهێنی',
      'i18n-login-submit-btn': 'چوونە ناو سیستەم 🔓'
    },
    en: {
      label: 'English (EN)',
      dir: 'ltr',
      lang: 'en',
      statusActive: 'Active',
      statusLocked: 'Suspended',
      'i18n-lang-label': 'English (EN)',
      'pwa-install-label': 'Install / APK ⚜️',
      'i18n-refresh-label': 'Clear Cache',
      'i18n-admin-label': 'Admin Panel 👑',
      'i18n-switch-label': 'Switch Account',
      'i18n-storefront-label': 'Storefront',
      'i18n-return-label': 'Invoice Return',
      'i18n-calc-label': 'ARAMKY Calc',
      'i18n-prices-label': 'Rates (5)',
      'i18n-reset-label': 'Reset (0)',
      'i18n-ticker-title': 'Gold & Rates:',
      'i18n-ticker-usd': '100 USD:',
      'i18n-ticker-m24': '24K:',
      'i18n-ticker-m22': '22K:',
      'i18n-ticker-m21': '21K:',
      'i18n-ticker-m18': '18K:',
      'i18n-ticker-m9': '9K:',
      'i18n-sidebar-title': 'Enterprise Control',
      'i18n-tab-dashboard': 'Dashboard & Vault',
      'i18n-tab-pos': 'Point of Sale (POS)',
      'i18n-tab-scrap': 'Buy Scrap Gold',
      'i18n-tab-inventory': 'Inventory & Edit',
      'i18n-tab-store-settings': 'Store & Brand Settings',
      'i18n-tab-debts': 'Debts Ledger (+/-)',
      'i18n-tab-logs': 'Profits & Excel Audit',
      'i18n-tab-support': 'Support & Admin',
      'i18n-dash-cash': 'Cash Vault (IQD)',
      'i18n-dash-usd': 'USD Vault ($)',
      'i18n-dash-zain': 'ZainCash & Master',
      'i18n-dash-profit': 'Net Making Profit',
      'i18n-exp-title': 'Record Daily Expense',
      'i18n-exp-save-btn': 'Save Expense',
      'i18n-debts-title': 'Debts Ledger (+ Owed to Us / - We Owe)',
      'i18n-debts-subtitle': 'Organized debt cards with (+) increase and (-) decrease for gold and cash with full audit',
      'i18n-debts-summary-them': 'Total Owed to Us (+)',
      'i18n-debts-summary-us': 'Total We Owe (-)',
      'i18n-debts-summary-net': 'Net Debt Balance',
      'i18n-debts-save-btn': 'Save Entry & Update Debt Card 📖',
      'i18n-lock-title': 'Subscription Suspended!',
      'i18n-lock-desc': 'Your subscription in ARAMKY Gold OS is inactive or expired. You can only contact technical support.',
      'i18n-lock-support-btn': 'Contact Technical Support 🛟',
      'i18n-lock-switch-btn': 'Switch Account / Sign Out 🔄',
      'i18n-login-title': 'Store / Subscriber Sign In',
      'i18n-login-desc': 'Access is restricted to admin-approved accounts (Code, Phone, Password)',
      'i18n-login-code-label': 'Account ID / Code',
      'i18n-login-phone-label': 'Registered Phone Number',
      'i18n-login-pass-label': 'Password',
      'i18n-login-submit-btn': 'Sign In 🔓'
    }
  };

  const PHRASES = {
    ku: {
      'تحديث التطبيق وتفريغ الكاش من الذاكرة': 'نوێکردنەوەی ئەپ و پاککردنەوەی کاش لە یادگە',
      'الدخول إلى لوحة إدارة الأدمن': 'چوونە ناو پانێڵی بەڕێوەبردنی ئەدمین',
      'تصفير النظام (0)': 'سفرکردنی سیستەم (0)',
      'تصفير النظام وإعادة الضبط الذكي (0)': 'سفرکردنی سیستەم و ڕێکخستنەوەی زیرەک (0)',
      'اختر نوع التصفير المطلوب:': 'جۆری سفرکردنی داواکراو هەڵبژێرە:',
      '1. تصفير الخزينة والأرباح فقط (جرد يومي):': '1. سفرکردنی قاسە و قازانج تەنها (حسابی ڕۆژانە):',
      'تصفير صناديق الكاش، الدولار، الماستر، وأرباح الصياغة مع بقاء المخزن والديون.': 'سفرکردنی قاسەی کاش، دۆلار، ماستەر، و قازانجی دەستکرد لەگەڵ مانەوەی کۆگا و قەرزەکان.',
      'تصفير الخزينة فقط 🔄': 'سفرکردنی قاسە تەنها 🔄',
      '2. تصفير النظام بالكامل (ضبط مصنع):': '2. سفرکردنی تەواوی سیستەم (دۆخی کارگە):',
      'مسح كل شيء وإرجاع النظام كأنه جديد تماماً.': 'سڕینەوەی هەموو شتێک و گەڕاندنەوەی سیستەم وەک سەرەتا.',
      'تصفير النظام بالكامل 🗑️': 'سفرکردنی تەواوی سیستەم 🗑️',
      'إلغاء': 'هەڵوەشاندنەوە',
      'إغلاق': 'داخستن',
      'تصفح المخزن': 'گەڕان لە کۆگا',
      'إضافة للسلة': 'زیادکردن بۆ سەبەتە',
      'غرام الصافي:': 'گرامی پاک:',
      'أرباح المثقال الواحد (5غ):': 'قازانجی یەک مسقاڵ (5گ):',
      'إجمالي أرباح الصياغة:': 'کۆی قازانجی دەستکرد:',
      'السعر بالدينار:': 'نرخ بە دینار:',
      'المقابل:': 'بەرانبەر:',
      'القطع المضافة للسلة:': 'پارچە زیادکراوەکان بۆ سەبەتە:',
      'السلة فارغة.': 'سەبەتە بەتاڵە.',
      'إجمالي الفاتورة:': 'کۆی گشتی پسوولە:',
      'إتمام البيع النقدي وطباعة': 'تەواوکردنی فرۆشتنی کاش و چاپکردن',
      'تسجيل آجل (يطلبهم +)': 'تۆمارکردنی قەرز (+ داوایان دەکەین)',
      'سبب المصروف': 'هۆکاری خەرجی',
      'المبلغ (دينار)': 'بڕی پارە (دینار)',
      'ملاحظات...': 'تێبینی...',
      'اسم الزبون / التاجر': 'ناوی کڕیار / بازرگان',
      'رقم الهاتف (07XXXXXXXXX)': 'ژمارەی مۆبایل (07XXXXXXXXX)',
      'ملاحظات إضافية للحركة أو الحساب...': 'تێبینی زیاتر بۆ جووڵە یان هەژمار...',
      'أدخل الاسم والقيمة لمعاينة الأثر الفوري على الرصيد': 'ناو و بڕ بنووسە بۆ بینینی کاریگەری ڕاستەوخۆ لەسەر باڵانس',
      'الكل': 'هەمووی',
      'كارتات تطلبهم (+)': 'کارتەکانی داوایان دەکەین (+)',
      'كارتات يطلبوك (-)': 'کارتەکانی داوامان دەکەن (-)',
      'حفظ الإعدادات وإشعار الإدارة بالتحديث 🌐': 'پاشەکەوتکردنی ڕێکخستنەکان و ئاگادارکردنەوەی بەڕێوەبەرایەتی 🌐',
      'إرسال مباشر إلى لوحة الأدمن': 'ناردنی ڕاستەوخۆ بۆ پانێڵی ئەدمین',
      'إرسال عبر واتساب': 'ناردن لە ڕێگەی وەتسئەپ'
    },
    en: {
      'تحديث التطبيق وتفريغ الكاش من الذاكرة': 'Refresh app and clear memory cache',
      'الدخول إلى لوحة إدارة الأدمن': 'Open Admin Management Panel',
      'تصفير النظام (0)': 'Reset System (0)',
      'تصفير النظام وإعادة الضبط الذكي (0)': 'System Reset & Smart Restore (0)',
      'اختر نوع التصفير المطلوب:': 'Select the required reset mode:',
      '1. تصفير الخزينة والأرباح فقط (جرد يومي):': '1. Reset Vault & Profits Only (Daily Audit):',
      'تصفير صناديق الكاش، الدولار، الماستر، وأرباح الصياغة مع بقاء المخزن والديون.': 'Reset cash, USD, ZainCash/Master, and making profit while keeping inventory and debts.',
      'تصفير الخزينة فقط 🔄': 'Reset Vault Only 🔄',
      '2. تصفير النظام بالكامل (ضبط مصنع):': '2. Full System Reset (Factory Reset):',
      'مسح كل شيء وإرجاع النظام كأنه جديد تماماً.': 'Erase everything and restore the system to its initial state.',
      'تصفير النظام بالكامل 🗑️': 'Full System Reset 🗑️',
      'إلغاء': 'Cancel',
      'إغلاق': 'Close',
      'تصفح المخزن': 'Browse Inventory',
      'إضافة للسلة': 'Add to Cart',
      'غرام الصافي:': 'Net Gram:',
      'أرباح المثقال الواحد (5غ):': 'Profit per Mithqal (5g):',
      'إجمالي أرباح الصياغة:': 'Total Making Profit:',
      'السعر بالدينار:': 'Price in IQD:',
      'المقابل:': 'Equivalent:',
      'القطع المضافة للسلة:': 'Items in Cart:',
      'السلة فارغة.': 'Cart is empty.',
      'إجمالي الفاتورة:': 'Invoice Total:',
      'إتمام البيع النقدي وطباعة': 'Complete Cash Sale & Print',
      'تسجيل آجل (يطلبهم +)': 'Record Credit (+ Owed to Us)',
      'سبب المصروف': 'Expense reason',
      'المبلغ (دينار)': 'Amount (IQD)',
      'ملاحظات...': 'Notes...',
      'اسم الزبون / التاجر': 'Customer / Merchant name',
      'رقم الهاتف (07XXXXXXXXX)': 'Phone number (07XXXXXXXXX)',
      'ملاحظات إضافية للحركة أو الحساب...': 'Additional notes for transaction or account...',
      'أدخل الاسم والقيمة لمعاينة الأثر الفوري على الرصيد': 'Enter name and amount to preview live balance impact',
      'الكل': 'All',
      'كارتات تطلبهم (+)': 'Owed to Us Cards (+)',
      'كارتات يطلبوك (-)': 'We Owe Cards (-)',
      'حفظ الإعدادات وإشعار الإدارة بالتحديث 🌐': 'Save Settings & Notify Admin 🌐',
      'إرسال مباشر إلى لوحة الأدمن': 'Send Directly to Admin Panel',
      'إرسال عبر واتساب': 'Send via WhatsApp'
    }
  };

  function getLanguage() {
    try {
      const saved = global.localStorage.getItem(STORAGE_KEY);
      return DICTS[saved] ? saved : 'ar';
    } catch (_) {
      return 'ar';
    }
  }

  function setLanguage(lang) {
    const clean = DICTS[lang] ? lang : 'ar';
    try {
      global.localStorage.setItem(STORAGE_KEY, clean);
    } catch (_) {}
    applyLanguageToDom(clean);
    return clean;
  }

  function cycleLanguage() {
    const cur = getLanguage();
    const idx = ORDER.indexOf(cur);
    const next = ORDER[(idx + 1) % ORDER.length];
    return setLanguage(next);
  }

  function t(key, lang) {
    const active = lang || getLanguage();
    const dict = DICTS[active] || DICTS.ar;
    return dict[key] !== undefined ? dict[key] : (DICTS.ar[key] !== undefined ? DICTS.ar[key] : key);
  }

  function translateTextValue(text, lang) {
    if (!text) return text;
    if (lang === 'ar') return text;
    const map = PHRASES[lang] || {};
    const trimmed = String(text).trim();
    if (map[trimmed]) {
      return String(text).replace(trimmed, map[trimmed]);
    }
    return text;
  }

  function applyLanguageToDom(lang) {
    const active = lang || getLanguage();
    const dict = DICTS[active] || DICTS.ar;
    if (global.document && global.document.documentElement) {
      global.document.documentElement.lang = dict.lang || 'ar';
      global.document.documentElement.dir = dict.dir || 'rtl';
    }
    Object.keys(dict).forEach(id => {
      if (['label', 'dir', 'lang', 'statusActive', 'statusLocked'].includes(id)) return;
      const el = global.document && global.document.getElementById(id);
      if (el) el.textContent = dict[id];
    });

    if (global.document && global.document.body && active !== 'ar') {
      const walker = global.document.createTreeWalker(
        global.document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
      );
      let node;
      while ((node = walker.nextNode())) {
        const parentTag = node.parentElement && node.parentElement.tagName;
        if (!parentTag || ['SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT'].includes(parentTag)) continue;
        const translated = translateTextValue(node.nodeValue, active);
        if (translated !== node.nodeValue) {
          node.nodeValue = translated;
        }
      }

      global.document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(inp => {
        const ph = inp.getAttribute('placeholder');
        const translatedPh = translateTextValue(ph, active);
        if (translatedPh !== ph) inp.setAttribute('placeholder', translatedPh);
      });

      global.document.querySelectorAll('[title]').forEach(el => {
        const titleVal = el.getAttribute('title');
        const translatedTitle = translateTextValue(titleVal, active);
        if (translatedTitle !== titleVal) el.setAttribute('title', translatedTitle);
      });
    }
  }

  global.ARAMKY_I18N = {
    getLanguage,
    setLanguage,
    cycleLanguage,
    t,
    applyLanguageToDom
  };
})(window);
