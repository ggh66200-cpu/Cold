(function () {
  const TRANSLATIONS = {
    ar: {
      dir: "rtl",
      lang: "ar",
      brandSubtitle: "أرامكي للحلول الرقمية • نظام إدارة الذهب والديون",
      installBtn: "تثبيت التطبيق",
      refreshBtn: "تحديث الذاكرة",
      switchAccountBtn: "تبديل / كود العميل",
      storefrontBtn: "معرض الزبائن",
      returnBtn: "إرجاع فاتورة",
      calcBtn: "حاسبة آرامكي",
      pricesBtn: "الأسعار",
      resetBtn: "تصفير (0)",
      adminBtn: "لوحة الأدمن",
      navDashboard: "الرئيسية والخزينة",
      navPos: "نقطة البيع",
      navScrap: "شراء ذهب كسر",
      navInventory: "المخزن",
      navStoreSettings: "إعدادات المعرض",
      navDebts: "دفتر الديون (+ / -)",
      navLogs: "الأرباح والتقارير",
      navSupport: "الدعم والإدارة",
      debtThemTitle: "تطلبهم (+ لنا عند الناس)",
      debtUsTitle: "يطلبوك / مطلوب منك (- علينا للناس)",
      saveDebtBtn: "حفظ الحركة في الدفتر",
      clientCodeHint: "لكل عميل كود وشغل مستقل — الاسم المعروض للعميل هو ARAMKY"
    },
    en: {
      dir: "ltr",
      lang: "en",
      brandSubtitle: "ARAMKY Digital Solutions • Gold & Ledger OS",
      installBtn: "Install App",
      refreshBtn: "Clear Cache",
      switchAccountBtn: "Switch / Client Code",
      storefrontBtn: "Showcase",
      returnBtn: "Return Invoice",
      calcBtn: "Calculator",
      pricesBtn: "Gold Rates",
      resetBtn: "Reset (0)",
      adminBtn: "Admin Panel",
      navDashboard: "Dashboard & Vault",
      navPos: "Point of Sale",
      navScrap: "Buy Scrap Gold",
      navInventory: "Inventory",
      navStoreSettings: "Store Settings",
      navDebts: "Debt Ledger (+ / -)",
      navLogs: "Profits & Reports",
      navSupport: "Support & Admin",
      debtThemTitle: "Owed to You (+ Receivable)",
      debtUsTitle: "You Owe (- Payable)",
      saveDebtBtn: "Save Ledger Entry",
      clientCodeHint: "Each client has a dedicated workspace code — public brand is ARAMKY"
    },
    ku: {
      dir: "rtl",
      lang: "ckb",
      brandSubtitle: "ئارامکی بۆ چارەسەری دیجیتاڵی • سیستەمی زێڕ و قەرز",
      installBtn: "دامەزراندنی ئەپ",
      refreshBtn: "نوێکردنەوەی کاش",
      switchAccountBtn: "گۆڕینی کۆدی کڕیار",
      storefrontBtn: "پێشانگای کڕیاران",
      returnBtn: "گەڕاندنەوەی پسوڵە",
      calcBtn: "ژمێرەری ئارامکی",
      pricesBtn: "نرخی زێڕ",
      resetBtn: "سفرکردنەوە (0)",
      adminBtn: "پانێڵی ئەدمین",
      navDashboard: "سەرەکی و قاسە",
      navPos: "خاڵی فرۆشتن",
      navScrap: "کڕینی زێڕی شکاو",
      navInventory: "کۆگا",
      navStoreSettings: "ڕێکخستنی پێشانگا",
      navDebts: "دەفتەری قەرز (+ / -)",
      navLogs: "قازانج و ڕاپۆرت",
      navSupport: "پشتگیری و بەڕێوەبردن",
      debtThemTitle: "داواکراو لای خەڵک (+)",
      debtUsTitle: "داواکراو لە تۆ (-)",
      saveDebtBtn: "پاشەکەوتکردنی قەرز",
      clientCodeHint: "هەر کڕیارێک کۆد و کاری تایبەتی خۆی هەیە — ناوی سەرەکی ARAMKY"
    }
  };

  function getLang() {
    const saved = localStorage.getItem("aramky_lang") || "ar";
    return TRANSLATIONS[saved] ? saved : "ar";
  }

  function applyLanguage(langCode) {
    const code = TRANSLATIONS[langCode] ? langCode : "ar";
    const pack = TRANSLATIONS[code];
    localStorage.setItem("aramky_lang", code);
    document.documentElement.lang = pack.lang;
    document.documentElement.dir = pack.dir;

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (pack[key]) {
        el.textContent = pack[key];
      }
    });

    document.querySelectorAll("[data-lang-btn]").forEach((btn) => {
      const isActive = btn.getAttribute("data-lang-btn") === code;
      btn.classList.toggle("bg-gold", isActive);
      btn.classList.toggle("text-darkbg", isActive);
      btn.classList.toggle("font-black", isActive);
    });

    if (typeof window.onAramkyLangChanged === "function") {
      window.onAramkyLangChanged(code, pack);
    }
  }

  window.ARAMKY_I18N = {
    applyLanguage,
    getLang,
    t: (key) => {
      const pack = TRANSLATIONS[getLang()] || TRANSLATIONS.ar;
      return pack[key] || TRANSLATIONS.ar[key] || key;
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    applyLanguage(getLang());
  });
})();
