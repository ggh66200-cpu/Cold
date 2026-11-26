/**
 * ARAMKY Gold OS — Tri-Lingual Engine (العربية / کوردی / English)
 * أرامكي للحلول الرقمية — فرع نواة الذهب
 */
(function (global) {
  'use strict';

  const STORAGE_KEY = 'aramky_gold_v28_lang';

  const DICTIONARY = {
    ar: {
      dir: 'rtl',
      langTag: 'ar',
      label: 'العربية',
      shortCode: 'AR',
      badge: '⚜️ أرامكي v28.3',
      statusActive: 'نشط',
      statusLocked: 'متوقف',
      installBtn: 'تثبيت / APK ⚜️',
      installedBtn: 'مثبت على الجهاز ✓',
      refreshBtn: 'تحديث الذاكرة',
      adminBtn: 'لوحة الأدمن 👑',
      switchTenantBtn: 'تبديل الحساب',
      storefrontBtn: 'معرض الزبائن',
      returnBtn: 'إرجاع فاتورة',
      calcBtn: 'حاسبة آرامكي',
      pricesBtn: 'الأسعار (5)',
      resetBtn: 'تصفير (0)',
      tickerTitle: 'الأسعار والمثاقيل:',
      tickerUsd: 'الورقة (100$):',
      tickerM24: 'عيار 24:',
      tickerM22: 'عيار 22:',
      tickerM21: 'عيار 21:',
      tickerM18: 'عيار 18:',
      tickerM9: 'عيار 9:',
      sidebarTitle: 'لوحة التحكم المؤسسية',
      tabDashboard: 'الرئيسية والخزينة',
      tabPos: 'نقطة البيع (الكاسير)',
      tabScrap: 'شراء ذهب كسر',
      tabInventory: 'المخزن (تعديل وحذف)',
      tabStoreSettings: 'إعدادات المعرض والشعار',
      tabDebts: 'دفتر الديون (تطلبهم ويطلبوك)',
      tabLogs: 'الأرباح وجرد Excel',
      tabSupport: 'الدعم ومراسلة الأدمن',
      dashCash: 'صندوق الكاش (دينار)',
      dashUsd: 'صندوق الدولار ($)',
      dashZain: 'زين كاش والماستر',
      dashProfit: 'صافي أرباح الصياغة',
      expTitle: 'تسجيل مصروف يومي',
      expReasonPh: 'سبب المصروف',
      expAmountPh: 'المبلغ (دينار)',
      expNotesPh: 'ملاحظات...',
      expSaveBtn: 'تسجيل المصروف',
      debtsTitle: 'دفتر الديون الفخم (تطلبهم + ويطلبوك -)',
      debtsSubtitle: 'كارتات مفصولة بوضوح بين ما تطلبه أنت (تطلبهم +) وما هو مطلوب منك (يطلبوك -)، مع زيادة ونقصان للأموال والذهب وتفاصيل كاملة وجرد لكل حركة',
      debtsAllBtn: 'الكل',
      debtsThemBtn: 'كارتات تطلبهم (+)',
      debtsUsBtn: 'كارتات يطلبوك (-)',
      debtsSummaryThem: 'إجمالي ما تطلبه (تطلبهم — لنا عند الناس +)',
      debtsSummaryUs: 'إجمالي ما يطلبوك (مطلوب منك — علينا للناس -)',
      debtsSummaryNet: 'صافي ميزان الديون العام (تطلبهم - يطلبوك)',
      debtsCustomerPh: 'اسم الزبون / التاجر',
      debtsPhonePh: 'رقم الهاتف (07XXXXXXXXX)',
      debtsAmountPh: 'المبلغ (د.ع) أو الوزن (غرام)',
      debtsNotesPh: 'ملاحظات إضافية للحركة أو الحساب...',
      debtsSaveBtn: 'حفظ الحركة وتحديث كارت الديون الفخم 📖',
      lockTitle: 'الاشتراك متوقف!',
      lockDesc: 'اشتراكك متوقف أو منتهي في نظام ARAMKY Gold OS. يمكنك فقط التواصل مع الدعم الفني.',
      lockSupportBtn: 'التواصل مع الدعم الفني 🛟',
      lockSwitchBtn: 'تبديل الحساب / تسجيل الخروج 🔄',
      loginTitle: 'تسجيل دخول المعرض / المشترك',
      loginDesc: 'الدخول متاح فقط للحسابات المعتمدة من الأدمن (الكود، رقم الهاتف، وكلمة المرور)',
      loginCodeLabel: 'معرف الحساب / الكود',
      loginPhoneLabel: 'رقم الهاتف المرتبط بالحساب',
      loginPassLabel: 'كلمة المرور',
      loginSubmitBtn: 'دخول إلى النظام 🔓'
    },
    ku: {
      dir: 'rtl',
      langTag: 'ckb',
      label: 'کوردی',
      shortCode: 'KU',
      badge: '⚜️ ئارامکی v28.3',
      statusActive: 'چالاکە',
      statusLocked: 'ڕاگیراوە',
      installBtn: 'دامەزراندن / APK ⚜️',
      installedBtn: 'دامەزراوە ✓',
      refreshBtn: 'نوێکردنەوەی بیرگە',
      adminBtn: 'پانێڵی ئەدمین 👑',
      switchTenantBtn: 'گۆڕینی هەژمار',
      storefrontBtn: 'پێشانگای کڕیاران',
      returnBtn: 'گەڕاندنەوەی پسوولە',
      calcBtn: 'ژمێرەری ئارامکی',
      pricesBtn: 'نرخەکان (5)',
      resetBtn: 'سفرکردن (0)',
      tickerTitle: 'نرخ و مسقاڵەکان:',
      tickerUsd: 'وەرەقە (100$):',
      tickerM24: 'عیار 24:',
      tickerM22: 'عیار 22:',
      tickerM21: 'عیار 21:',
      tickerM18: 'عیار 18:',
      tickerM9: 'عیار 9:',
      sidebarTitle: 'پانێڵی بەڕێوەبردنی دامەزراوەیی',
      tabDashboard: 'سەرەکی و قاسە',
      tabPos: 'خاڵی فرۆشتن (کاشێر)',
      tabScrap: 'کڕینی زێڕی شکاو',
      tabInventory: 'کۆگا (دەستکاری و سڕینەوە)',
      tabStoreSettings: 'ڕێکخستنی پێشانگا و لۆگۆ',
      tabDebts: 'دەفتەری قەرز (داوایان دەکەیت / داوات دەکەن)',
      tabLogs: 'قازانج و جەردی Excel',
      tabSupport: 'پشتیوانی و پەیوەندی بە ئەدمین',
      dashCash: 'قاسەی کاش (دینار)',
      dashUsd: 'قاسەی دۆلار ($)',
      dashZain: 'زین کاش و ماستەر',
      dashProfit: 'پاکێتی قازانجی دارشتن',
      expTitle: 'تۆمارکردنی خەرجی ڕۆژانە',
      expReasonPh: 'هۆکاری خەرجی',
      expAmountPh: 'بڕی پارە (دینار)',
      expNotesPh: 'تێبینی...',
      expSaveBtn: 'تۆمارکردنی خەرجی',
      debtsTitle: 'دەفتەری قەرزی شاهانە (داوایان دەکەیت + / داوات دەکەن -)',
      debtsSubtitle: 'کارتەکان جیاکراونەتەوە لە نێوان ئەوەی داوایان دەکەیت (+) و ئەوەی لەسەرتە (-)، لەگەڵ زیادکردن و کەمکردنەوەی پارە و زێڕ و وردەکاری هەر جووڵەیەک',
      debtsAllBtn: 'هەمووی',
      debtsThemBtn: 'کارتەکانی داوایان دەکەیت (+)',
      debtsUsBtn: 'کارتەکانی داوات دەکەن (-)',
      debtsSummaryThem: 'کۆی ئەوەی داوایان دەکەیت (بۆ ئێمە لای خەڵک +)',
      debtsSummaryUs: 'کۆی ئەوەی داوات دەکەن (لەسەر ئێمە بۆ خەڵک -)',
      debtsSummaryNet: 'پوختەی باڵانسی قەرزەکان',
      debtsCustomerPh: 'ناوی کڕیار / بازرگان',
      debtsPhonePh: 'ژمارەی مۆبایل (07XXXXXXXXX)',
      debtsAmountPh: 'بڕ (دینار) یان کێش (گرام)',
      debtsNotesPh: 'تێبینی زیادە بۆ جووڵە یان هەژمار...',
      debtsSaveBtn: 'پاشەکەوتکردنی جووڵە و نوێکردنەوەی کارتی قەرز 📖',
      lockTitle: 'بەشداریکردن ڕاگیراوە!',
      lockDesc: 'بەشداریکردنەکەت لە سیستەمی ARAMKY Gold OS ڕاگیراوە یان بەسەرچووە. تەنها دوگمەی پشتیوانی کارایە.',
      lockSupportBtn: 'پەیوەندی بە پشتیوانی 🛟',
      lockSwitchBtn: 'گۆڕینی هەژمار / چوونەدەرەوە 🔄',
      loginTitle: 'چوونەژوورەوەی پێشانگا / بەشداربوو',
      loginDesc: 'چوونەژوورەوە تەنها بۆ هەژمارە پەسەندکراوەکانی ئەدمینە (کۆد، ژمارەی مۆبایل، وشەی نهێنی)',
      loginCodeLabel: 'ناسنامەی هەژمار / کۆد',
      loginPhoneLabel: 'ژمارەی مۆبایلی هەژمار',
      loginPassLabel: 'وشەی نهێنی',
      loginSubmitBtn: 'چوونە ناو سیستەم 🔓'
    },
    en: {
      dir: 'ltr',
      langTag: 'en',
      label: 'English',
      shortCode: 'EN',
      badge: '⚜️ ARAMKY v28.3',
      statusActive: 'Active',
      statusLocked: 'Suspended',
      installBtn: 'Install / APK ⚜️',
      installedBtn: 'Installed ✓',
      refreshBtn: 'Clear & Sync',
      adminBtn: 'Admin Console 👑',
      switchTenantBtn: 'Switch Account',
      storefrontBtn: 'Customer Showcase',
      returnBtn: 'Return Invoice',
      calcBtn: 'ARAMKY Calc',
      pricesBtn: 'Rates (5)',
      resetBtn: 'Reset (0)',
      tickerTitle: 'Rates & Mithqals:',
      tickerUsd: '100 USD:',
      tickerM24: '24K:',
      tickerM22: '22K:',
      tickerM21: '21K:',
      tickerM18: '18K:',
      tickerM9: '9K:',
      sidebarTitle: 'Enterprise Control Panel',
      tabDashboard: 'Overview & Vault',
      tabPos: 'Point of Sale (POS)',
      tabScrap: 'Buy Scrap Gold',
      tabInventory: 'Inventory (Edit & Delete)',
      tabStoreSettings: 'Store & Branding',
      tabDebts: 'Debt Ledger (Owed to You / You Owe)',
      tabLogs: 'Profits & Excel Audit',
      tabSupport: 'Support & Admin Chat',
      dashCash: 'Cash Vault (IQD)',
      dashUsd: 'USD Vault ($)',
      dashZain: 'ZainCash & MasterCard',
      dashProfit: 'Net Craftsmanship Profit',
      expTitle: 'Record Daily Expense',
      expReasonPh: 'Expense reason',
      expAmountPh: 'Amount (IQD)',
      expNotesPh: 'Notes...',
      expSaveBtn: 'Save Expense',
      debtsTitle: 'Luxury Debt Ledger (Owed to You + / You Owe -)',
      debtsSubtitle: 'Clear cards separating amounts owed to you (+) and amounts you owe (-), with money & gold adjustments, full card details, and movement audit',
      debtsAllBtn: 'All',
      debtsThemBtn: 'Owed to You (+)',
      debtsUsBtn: 'You Owe (-)',
      debtsSummaryThem: 'Total Owed to You (Receivables +)',
      debtsSummaryUs: 'Total You Owe (Payables -)',
      debtsSummaryNet: 'Net Debt Balance (Receivables - Payables)',
      debtsCustomerPh: 'Customer / Merchant Name',
      debtsPhonePh: 'Phone Number (07XXXXXXXXX)',
      debtsAmountPh: 'Amount (IQD) or Weight (Grams)',
      debtsNotesPh: 'Additional movement or account notes...',
      debtsSaveBtn: 'Save Movement & Update Debt Card 📖',
      lockTitle: 'Subscription Suspended!',
      lockDesc: 'Your ARAMKY Gold OS subscription is expired or suspended. Only Support remains accessible.',
      lockSupportBtn: 'Contact Support 🛟',
      lockSwitchBtn: 'Switch Account / Logout 🔄',
      loginTitle: 'Store / Subscriber Login',
      loginDesc: 'Access is restricted to admin-approved accounts (Code, Phone, and Password)',
      loginCodeLabel: 'Account Code / ID',
      loginPhoneLabel: 'Registered Phone Number',
      loginPassLabel: 'Password',
      loginSubmitBtn: 'Sign In to System 🔓'
    }
  };

  let activeLang = 'ar';

  function normalizeLang(lang) {
    const l = String(lang || '').toLowerCase().trim();
    if (l === 'ku' || l === 'ckb' || l.startsWith('ku')) return 'ku';
    if (l === 'en' || l.startsWith('en')) return 'en';
    return 'ar';
  }

  function getLanguage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) activeLang = normalizeLang(saved);
    } catch (_) {}
    return activeLang;
  }

  function setLanguage(lang) {
    activeLang = normalizeLang(lang);
    try {
      localStorage.setItem(STORAGE_KEY, activeLang);
    } catch (_) {}
    applyLanguageToDom(activeLang);
    return activeLang;
  }

  function cycleLanguage() {
    const order = ['ar', 'ku', 'en'];
    const idx = order.indexOf(getLanguage());
    const next = order[(idx + 1) % order.length];
    return setLanguage(next);
  }

  function t(key, fallback = '') {
    const pack = DICTIONARY[getLanguage()] || DICTIONARY.ar;
    return pack[key] !== undefined ? pack[key] : (DICTIONARY.ar[key] !== undefined ? DICTIONARY.ar[key] : fallback);
  }

  function setTextById(id, value) {
    const el = document.getElementById(id);
    if (el && value) el.textContent = value;
  }

  function setPlaceholderById(id, value) {
    const el = document.getElementById(id);
    if (el && value) el.placeholder = value;
  }

  function applyLanguageToDom(lang) {
    const code = normalizeLang(lang || getLanguage());
    const pack = DICTIONARY[code] || DICTIONARY.ar;

    document.documentElement.setAttribute('lang', pack.langTag);
    document.documentElement.setAttribute('dir', pack.dir);
    document.body.setAttribute('dir', pack.dir);

    setTextById('aramky-install-badge', pack.badge);
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    setTextById('pwa-install-label', isStandalone ? pack.installedBtn : pack.installBtn);

    setTextById('i18n-refresh-label', pack.refreshBtn);
    setTextById('i18n-admin-label', pack.adminBtn);
    setTextById('i18n-switch-label', pack.switchTenantBtn);
    setTextById('i18n-storefront-label', pack.storefrontBtn);
    setTextById('i18n-return-label', pack.returnBtn);
    setTextById('i18n-calc-label', pack.calcBtn);
    setTextById('i18n-prices-label', pack.pricesBtn);
    setTextById('i18n-reset-label', pack.resetBtn);
    setTextById('i18n-lang-label', `${pack.label} (${pack.shortCode})`);

    setTextById('i18n-ticker-title', pack.tickerTitle);
    setTextById('i18n-ticker-usd', pack.tickerUsd);
    setTextById('i18n-ticker-m24', pack.tickerM24);
    setTextById('i18n-ticker-m22', pack.tickerM22);
    setTextById('i18n-ticker-m21', pack.tickerM21);
    setTextById('i18n-ticker-m18', pack.tickerM18);
    setTextById('i18n-ticker-m9', pack.tickerM9);

    setTextById('i18n-sidebar-title', pack.sidebarTitle);
    setTextById('i18n-tab-dashboard', pack.tabDashboard);
    setTextById('i18n-tab-pos', pack.tabPos);
    setTextById('i18n-tab-scrap', pack.tabScrap);
    setTextById('i18n-tab-inventory', pack.tabInventory);
    setTextById('i18n-tab-store-settings', pack.tabStoreSettings);
    setTextById('i18n-tab-debts', pack.tabDebts);
    setTextById('i18n-tab-logs', pack.tabLogs);
    setTextById('i18n-tab-support', pack.tabSupport);

    setTextById('i18n-dash-cash', pack.dashCash);
    setTextById('i18n-dash-usd', pack.dashUsd);
    setTextById('i18n-dash-zain', pack.dashZain);
    setTextById('i18n-dash-profit', pack.dashProfit);
    setTextById('i18n-exp-title', pack.expTitle);
    setPlaceholderById('exp-reason', pack.expReasonPh);
    setPlaceholderById('exp-amount', pack.expAmountPh);
    setPlaceholderById('exp-notes', pack.expNotesPh);
    setTextById('i18n-exp-save-btn', pack.expSaveBtn);

    setTextById('i18n-debts-title', pack.debtsTitle);
    setTextById('i18n-debts-subtitle', pack.debtsSubtitle);
    setTextById('debt-filter-all', pack.debtsAllBtn);
    setTextById('debt-filter-them', pack.debtsThemBtn);
    setTextById('debt-filter-us', pack.debtsUsBtn);
    setTextById('i18n-debts-summary-them', pack.debtsSummaryThem);
    setTextById('i18n-debts-summary-us', pack.debtsSummaryUs);
    setTextById('i18n-debts-summary-net', pack.debtsSummaryNet);
    setPlaceholderById('debt-customer', pack.debtsCustomerPh);
    setPlaceholderById('debt-phone', pack.debtsPhonePh);
    setPlaceholderById('debt-amount', pack.debtsAmountPh);
    setPlaceholderById('debt-notes', pack.debtsNotesPh);
    setTextById('i18n-debts-save-btn', pack.debtsSaveBtn);

    setTextById('i18n-lock-title', pack.lockTitle);
    setTextById('i18n-lock-desc', pack.lockDesc);
    setTextById('i18n-lock-support-btn', pack.lockSupportBtn);
    setTextById('i18n-lock-switch-btn', pack.lockSwitchBtn);

    setTextById('i18n-login-title', pack.loginTitle);
    setTextById('i18n-login-desc', pack.loginDesc);
    setTextById('i18n-login-code-label', pack.loginCodeLabel);
    setTextById('i18n-login-phone-label', pack.loginPhoneLabel);
    setTextById('i18n-login-pass-label', pack.loginPassLabel);
    setTextById('i18n-login-submit-btn', pack.loginSubmitBtn);
  }

  const api = {
    version: '1.1',
    languages: ['ar', 'ku', 'en'],
    getLanguage,
    setLanguage,
    cycleLanguage,
    applyLanguageToDom,
    t
  };

  global.ARAMKY_I18N = api;
})(window);
