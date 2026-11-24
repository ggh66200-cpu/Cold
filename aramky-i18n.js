/* ARAMKY Gold OS - Multi-Language Engine (Arabic, English, Kurdish Sorani) */
(function (global) {
  'use strict';

  const STORAGE_KEY = 'aramky_gold_lang_v1';

  const TRANSLATIONS = {
    ar: {
      dir: 'rtl',
      langAttr: 'ar',
      label: 'العربية',
      appName: 'ARAMKY',
      appSub: 'نظام إدارة صياغة الذهب',
      installBtn: 'تثبيت / APK ⚜️',
      refreshBtn: 'تحديث الذاكرة',
      adminBtn: 'لوحة الأدمن 👑',
      switchTenantBtn: 'تبديل الحساب',
      showcaseBtn: 'معرض الزبائن',
      returnBtn: 'إرجاع فاتورة',
      calcBtn: 'حاسبة آرامكي',
      pricesBtn: 'الأسعار (5)',
      resetBtn: 'تصفير (0)',
      menuTitle: 'لوحة التحكم المؤسسية',
      tabDashboard: 'الرئيسية والخزينة',
      tabPos: 'نقطة البيع (الكاسير)',
      tabScrap: 'شراء ذهب كسر',
      tabInventory: 'المخزن (تعديل وحذف)',
      tabStoreSettings: 'إعدادات المعرض والشعار',
      tabDebts: 'دفتر الديون (تطلبهم ويطلبوك)',
      tabLogs: 'الأرباح وجرد Excel',
      tabSupport: 'الدعم ومراسلة الأدمن',
      cashBox: 'صندوق الكاش (دينار)',
      usdBox: 'صندوق الدولار ($)',
      zainBox: 'زين كاش والماستر',
      profitBox: 'صافي أرباح الصياغة',
      debtsTitle: 'دفتر الديون الفخم (تطلبهم + ويطلبوك -)',
      themSection: 'كارتات: تطلبهم (لنا عند الناس +)',
      usSection: 'كارتات: يطلبوك / مطلوب منك (علينا للناس -)',
      adminBarTitle: 'شريط تحكم الأدمن المباشر',
      adminOpenFull: 'فتح لوحة الأدمن الكاملة',
      adminToggleSub: 'تبديل حالة اشتراك الحساب',
      adminCloudSync: 'مزامنة السستم السحابي',
      adminExportAll: 'تصدير جرد الأدمن الكامل'
    },
    en: {
      dir: 'ltr',
      langAttr: 'en',
      label: 'English',
      appName: 'ARAMKY',
      appSub: 'Goldsmith & Jewelry Management OS',
      installBtn: 'Install / APK ⚜️',
      refreshBtn: 'Clear Cache',
      adminBtn: 'Admin Panel 👑',
      switchTenantBtn: 'Switch Account',
      showcaseBtn: 'Storefront',
      returnBtn: 'Return Invoice',
      calcBtn: 'ARAMKY Calc',
      pricesBtn: 'Rates (5)',
      resetBtn: 'Reset (0)',
      menuTitle: 'Enterprise Control Panel',
      tabDashboard: 'Dashboard & Vault',
      tabPos: 'Point of Sale (POS)',
      tabScrap: 'Buy Scrap Gold',
      tabInventory: 'Inventory (Edit / Delete)',
      tabStoreSettings: 'Store & Brand Settings',
      tabDebts: 'Debts Ledger (+ / -)',
      tabLogs: 'Profits & Excel Audit',
      tabSupport: 'Support & Admin',
      cashBox: 'Cash Vault (IQD)',
      usdBox: 'USD Vault ($)',
      zainBox: 'ZainCash & MasterCard',
      profitBox: 'Net Making Profit',
      debtsTitle: 'Luxury Debts Ledger (Owed to You + / You Owe -)',
      themSection: 'Owed to You (+ Receivable)',
      usSection: 'You Owe (- Payable)',
      adminBarTitle: 'Direct Admin Controls',
      adminOpenFull: 'Full Admin Console',
      adminToggleSub: 'Toggle Account Status',
      adminCloudSync: 'Cloud System Sync',
      adminExportAll: 'Export Full Audit'
    },
    ku: {
      dir: 'rtl',
      langAttr: 'ku',
      label: 'کوردی',
      appName: 'ARAMKY',
      appSub: 'سیستەمی بەڕێوەبردنی زێڕنگەری',
      installBtn: 'دامەزراندن / APK ⚜️',
      refreshBtn: 'نوێکردنەوەی بیرگە',
      adminBtn: 'پانێڵی ئەدمین 👑',
      switchTenantBtn: 'گۆڕینی هەژمار',
      showcaseBtn: 'پێشانگای کڕیاران',
      returnBtn: 'گەڕاندنەوەی پسوولە',
      calcBtn: 'حاسیبەی ئارامکی',
      pricesBtn: 'نرخەکان (5)',
      resetBtn: 'سفرکردنەوە (0)',
      menuTitle: 'پانێڵی کۆنتڕۆڵی دامەزراوەیی',
      tabDashboard: 'سەرەکی و قاسە',
      tabPos: 'خاڵی فرۆشتن (کاشێر)',
      tabScrap: 'کڕینی زێڕی شکاو',
      tabInventory: 'کۆگا (دەستکاری و سڕینەوە)',
      tabStoreSettings: 'ڕێکخستنی پێشانگا و لۆگۆ',
      tabDebts: 'دەفتەری قەرز (+ / -)',
      tabLogs: 'قازانج و جەردی Excel',
      tabSupport: 'پشتیوانی و ئەدمین',
      cashBox: 'قاسەی کاش (دینار)',
      usdBox: 'قاسەی دۆلار ($)',
      zainBox: 'زەین کاش و ماستەرکارد',
      profitBox: 'پاکترین قازانجی دەستکرد',
      debtsTitle: 'دەفتەری قەرزەکان (لێت دەخوازن + / لێت داوا دەکرێت -)',
      themSection: 'قەرز لای خەڵک (+ بۆ تۆ)',
      usSection: 'قەرز لەسەر تۆ (- بۆ خەڵک)',
      adminBarTitle: 'کۆنتڕۆڵی ڕاستەوخۆی ئەدمین',
      adminOpenFull: 'کردنەوەی پانێڵی ئەدمین',
      adminToggleSub: 'گۆڕینی دۆخی بەشداریکردن',
      adminCloudSync: 'هاوکاتکردنی سیستەمی هەوری',
      adminExportAll: 'هەناردەکردنی جەردی گشتی'
    }
  };

  function getLang() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return TRANSLATIONS[saved] ? saved : 'ar';
    } catch (_) {
      return 'ar';
    }
  }

  function applyLang(langCode) {
    const code = TRANSLATIONS[langCode] ? langCode : 'ar';
    const dict = TRANSLATIONS[code];
    try {
      localStorage.setItem(STORAGE_KEY, code);
    } catch (_) {}

    document.documentElement.setAttribute('lang', dict.langAttr);
    document.documentElement.setAttribute('dir', dict.dir);
    document.body.setAttribute('dir', dict.dir);

    const setText = (id, text) => {
      const el = document.getElementById(id);
      if (el && text) el.textContent = text;
    };

    setText('i18n-install-text', dict.installBtn);
    setText('i18n-refresh-text', dict.refreshBtn);
    setText('i18n-admin-text', dict.adminBtn);
    setText('i18n-switch-text', dict.switchTenantBtn);
    setText('i18n-showcase-text', dict.showcaseBtn);
    setText('i18n-return-text', dict.returnBtn);
    setText('i18n-calc-text', dict.calcBtn);
    setText('i18n-prices-text', dict.pricesBtn);
    setText('i18n-reset-text', dict.resetBtn);
    setText('i18n-menu-title', dict.menuTitle);
    setText('i18n-tab-dashboard', dict.tabDashboard);
    setText('i18n-tab-pos', dict.tabPos);
    setText('i18n-tab-scrap', dict.tabScrap);
    setText('i18n-tab-inventory', dict.tabInventory);
    setText('i18n-tab-store-settings', dict.tabStoreSettings);
    setText('i18n-tab-debts', dict.tabDebts);
    setText('i18n-tab-logs', dict.tabLogs);
    setText('i18n-tab-support', dict.tabSupport);
    setText('i18n-cash-label', dict.cashBox);
    setText('i18n-usd-label', dict.usdBox);
    setText('i18n-zain-label', dict.zainBox);
    setText('i18n-profit-label', dict.profitBox);
    setText('i18n-debts-title', dict.debtsTitle);
    setText('i18n-them-section-title', dict.themSection);
    setText('i18n-us-section-title', dict.usSection);
    setText('i18n-admin-bar-title', dict.adminBarTitle);
    setText('i18n-admin-open-full', dict.adminOpenFull);
    setText('i18n-admin-toggle-sub', dict.adminToggleSub);
    setText('i18n-admin-cloud-sync', dict.adminCloudSync);
    setText('i18n-admin-export-all', dict.adminExportAll);

    const langBtnLabel = document.getElementById('current-lang-label');
    if (langBtnLabel) langBtnLabel.textContent = dict.label;

    return code;
  }

  function cycleLang() {
    const order = ['ar', 'en', 'ku'];
    const current = getLang();
    const next = order[(order.indexOf(current) + 1) % order.length];
    return applyLang(next);
  }

  global.ARAMKY_I18N = {
    translations: TRANSLATIONS,
    getLang,
    applyLang,
    cycleLang
  };
})(window);
