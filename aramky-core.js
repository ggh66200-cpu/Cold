(function (global) {
  'use strict';

  const SUPABASE_URL = global.ARAMKY_SUPABASE_URL || '';
  const SUPABASE_ANON_KEY = global.ARAMKY_SUPABASE_ANON_KEY || '';
  const SUPPORT_PHONE = '07766083622';
  const SUPPORT_WHATSAPP = '9647766083622';
  const MASTER_CARD_NUMBER = '910400201646';
  const ADMIN_PASSWORDS = ['waadsdsd', 'ARAMKY2026', 'ADMIN123'];

  const KEYS = {
    activeTenant: 'aramky_active_tenant',
    adminSession: 'aramky_admin_session_v28',
    subscriberSession: 'aramky_subscriber_session_v28',
    tenantsRegistry: 'aramky_tenants_registry_v28',
    supportTickets: 'aramky_support_tickets_v28',
    lang: 'aramky_lang_v28'
  };

  function safeJsonParse(raw, fallback) {
    try {
      if (!raw) return fallback;
      return JSON.parse(raw);
    } catch (_) {
      return fallback;
    }
  }

  function readSecureStorage(key, _salt, fallback) {
    try {
      const raw = global.localStorage.getItem(key);
      if (raw === null || raw === undefined) return fallback;
      return safeJsonParse(raw, fallback);
    } catch (_) {
      return fallback;
    }
  }

  function writeSecureStorage(key, value, _salt) {
    try {
      global.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_) {
      return false;
    }
  }

  function getTenantDataKey(code) {
    const clean = String(code || 'ARAMKY').trim().toUpperCase();
    return `aramky_gold_data_${clean}`;
  }

  function getCustomerLedgerKey(tenantCode, custKey) {
    const cleanTenant = String(tenantCode || 'ARAMKY').trim().toUpperCase();
    const cleanCust = String(custKey || 'GENERAL').trim();
    return `aramky_cust_ledger_${cleanTenant}_${cleanCust}`;
  }

  function encodeCatalogRef(code) {
    const str = String(code || 'ARAMKY').trim().toUpperCase();
    try {
      return btoa(unescape(encodeURIComponent(str))).replace(/=/g, '');
    } catch (_) {
      return str;
    }
  }

  function normalizeTenantPayload(data, code) {
    const cleanCode = String(code || (data && data.code) || 'ARAMKY').trim().toUpperCase();
    const base = {
      code: cleanCode,
      status: 'نشط',
      cash: 0,
      usd: 0,
      zain: 0,
      makingProfit: 0,
      prices: { usd: 150000, m24: 640000, m22: 585000, m21: 560000, m18: 480000, m9: 240000 },
      inventory: [],
      debts: [],
      logs: [],
      supportTickets: [],
      store: {
        name: 'ARAMKY | أرامكي للحلول الرقمية — فرع نواة الذهب',
        phone: SUPPORT_PHONE,
        address: 'بغداد — سوق الكاظمية',
        openTime: '09:00 صباحاً',
        closeTime: '09:00 مساءً',
        bio: 'نظام إدارة صياغة الذهب والمعرض الرقمي الذكي',
        logo: 'icon.png',
        cover: 'icon.png'
      },
      updatedAt: new Date().toISOString()
    };

    const merged = Object.assign({}, base, data || {});
    merged.code = cleanCode;
    merged.prices = Object.assign({}, base.prices, (data && data.prices) || {});
    merged.store = Object.assign({}, base.store, (data && data.store) || {});
    merged.inventory = Array.isArray(merged.inventory) ? merged.inventory : [];
    merged.debts = Array.isArray(merged.debts) ? merged.debts : [];
    merged.logs = Array.isArray(merged.logs) ? merged.logs : [];
    merged.supportTickets = Array.isArray(merged.supportTickets) ? merged.supportTickets : [];
    return merged;
  }

  function verifyAdminPassword(pass) {
    const clean = String(pass || '').trim();
    return ADMIN_PASSWORDS.includes(clean);
  }

  function setAdminSession(active) {
    try {
      if (active) global.localStorage.setItem(KEYS.adminSession, '1');
      else global.localStorage.removeItem(KEYS.adminSession);
    } catch (_) {}
    syncAdminUiVisibility();
  }

  function hasAdminSession() {
    try {
      return global.localStorage.getItem(KEYS.adminSession) === '1';
    } catch (_) {
      return false;
    }
  }

  function setActiveSubscriberSession(code) {
    try {
      global.localStorage.setItem(KEYS.subscriberSession, String(code || 'ARAMKY').trim().toUpperCase());
      global.localStorage.setItem(KEYS.activeTenant, String(code || 'ARAMKY').trim().toUpperCase());
    } catch (_) {}
  }

  function syncAdminUiVisibility() {
    const container = global.document && global.document.getElementById('admin-btn-container');
    const btn = global.document && global.document.getElementById('header-admin-btn');
    if (container) {
      container.classList.remove('hidden');
      container.style.display = 'flex';
    }
    if (btn) {
      btn.classList.remove('hidden');
      btn.style.display = 'inline-flex';
    }
  }

  function getTenantsRegistry() {
    const list = readSecureStorage(KEYS.tenantsRegistry, 'REG', []);
    return Array.isArray(list) ? list : [];
  }

  function saveTenantsRegistry(list) {
    return writeSecureStorage(KEYS.tenantsRegistry, Array.isArray(list) ? list : [], 'REG');
  }

  function authenticateSubscriber(code, phone, pass) {
    const cleanCode = String(code || '').trim().toUpperCase();
    const cleanPhone = String(phone || '').replace(/\D+/g, '');
    const cleanPass = String(pass || '').trim();
    const reg = getTenantsRegistry();
    const found = reg.find(t => String(t.code || '').toUpperCase() === cleanCode);
    if (!found) {
      return { ok: false, message: 'الحساب غير مسجل في قائمة المشتركين' };
    }
    const foundPhone = String(found.phone || '').replace(/\D+/g, '');
    if (foundPhone && cleanPhone && foundPhone !== cleanPhone) {
      return { ok: false, message: 'رقم الهاتف لا يطابق الحساب' };
    }
    if (found.password && cleanPass !== String(found.password)) {
      return { ok: false, message: 'كلمة المرور غير صحيحة' };
    }
    return { ok: true, tenant: found };
  }

  function isSubscriptionExpired(obj) {
    if (!obj) return false;
    if (String(obj.status || '').trim() === 'متوقف') return true;
    if (obj.expiresAt) {
      const exp = new Date(obj.expiresAt).getTime();
      if (!isNaN(exp) && Date.now() > exp) return true;
    }
    return false;
  }

  function getContactInfo() {
    return {
      masterCardNumber: MASTER_CARD_NUMBER,
      supportPhone: SUPPORT_PHONE,
      whatsappUrl: `https://wa.me/${SUPPORT_WHATSAPP}`
    };
  }

  function pushSupportTicketToAdmin(ticket) {
    const current = readSecureStorage(KEYS.supportTickets, 'SUP', []);
    const arr = Array.isArray(current) ? current : [];
    arr.unshift(ticket);
    writeSecureStorage(KEYS.supportTickets, arr, 'SUP');
    return true;
  }

  function getAdminSupportTickets() {
    const current = readSecureStorage(KEYS.supportTickets, 'SUP', []);
    return Array.isArray(current) ? current : [];
  }

  function applyImageFallback(img, _variant) {
    if (!img) return;
    if (img.dataset.fallbackApplied === '1') return;
    img.dataset.fallbackApplied = '1';
    img.src = 'icon.png';
  }

  function filesToDataUrls(fileList, options) {
    const opts = Object.assign({ maxWidth: 1024, maxHeight: 1024, quality: 0.78 }, options || {});
    const files = Array.from(fileList || []);
    return Promise.all(files.map(file => new Promise(resolve => {
      const reader = new FileReader();
      reader.onload = () => {
        const rawUrl = String(reader.result || '');
        if (!rawUrl.startsWith('data:image/')) {
          resolve(rawUrl || null);
          return;
        }
        const img = new Image();
        img.onload = () => {
          let w = img.width || opts.maxWidth;
          let h = img.height || opts.maxHeight;
          const ratio = Math.min(opts.maxWidth / w, opts.maxHeight / h, 1);
          w = Math.max(1, Math.round(w * ratio));
          h = Math.max(1, Math.round(h * ratio));
          try {
            const canvas = global.document.createElement('canvas');
            canvas.width = w;
            canvas.height = h;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, w, h);
            resolve(canvas.toDataURL('image/jpeg', opts.quality));
          } catch (_) {
            resolve(rawUrl);
          }
        };
        img.onerror = () => resolve(rawUrl);
        img.src = rawUrl;
      };
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(file);
    }))).then(list => list.filter(Boolean));
  }

  function renderGalleryThumbnails(container, images, config) {
    if (!container) return;
    const cfg = Object.assign({ onRemoveFn: null }, config || {});
    const arr = Array.isArray(images) ? images : [];
    if (!arr.length) {
      container.innerHTML = '<span class="text-slate-500 text-[11px]">لا توجد صور مرفقة حالياً.</span>';
      return;
    }
    container.innerHTML = arr.map((src, idx) => `
      <div class="relative w-16 h-16 rounded-xl overflow-hidden border border-gold/40 bg-darkbg">
        <img src="${src}" class="w-full h-full object-cover">
        ${cfg.onRemoveFn
          ? `<button type="button" onclick="${cfg.onRemoveFn}(${idx})" class="absolute top-0.5 left-0.5 bg-rose-600 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center">✕</button>`
          : ''}
      </div>
    `).join('');
  }

  function openLightbox(src, title, opts) {
    const modal = global.document.getElementById('image-lightbox-modal');
    const img = global.document.getElementById('lightbox-img');
    const lbl = global.document.getElementById('lightbox-title');
    if (!modal || !img) return;
    delete img.dataset.fallbackApplied;
    img.onerror = () => applyImageFallback(img, (opts && opts.fallbackVariant) || 'logo');
    img.src = src || 'icon.png';
    if (lbl) lbl.textContent = title || 'معاينة الصورة';
    modal.classList.remove('hidden');
  }

  function closeLightbox(modalId) {
    const el = global.document.getElementById(modalId || 'image-lightbox-modal');
    if (el) el.classList.add('hidden');
  }

  function printReceiptOnly(widthMm) {
    const modalBox = global.document.querySelector('#invoice-modal > div');
    if (modalBox) {
      modalBox.style.maxWidth = Number(widthMm) === 58 ? '22rem' : '32rem';
    }
    global.print();
  }

  function isSupabaseReady() {
    return Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);
  }

  async function syncTenantToSupabase(code, payload) {
    if (!isSupabaseReady()) return false;
    try {
      const cleanCode = String(code || 'ARAMKY').trim().toUpperCase();
      const res = await fetch(`${SUPABASE_URL}/rest/v1/tenants?on_conflict=code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Prefer': 'resolution=merge-duplicates'
        },
        body: JSON.stringify({
          code: cleanCode,
          data: payload,
          updated_at: new Date().toISOString()
        })
      });
      return res.ok;
    } catch (_) {
      return false;
    }
  }

  function ensureAdminModalDom() {
    if (global.document.getElementById('aramky-admin-dashboard-modal')) return;
    const modal = global.document.createElement('div');
    modal.id = 'aramky-admin-dashboard-modal';
    modal.className = 'fixed inset-0 bg-slate-950/90 backdrop-blur-md z-[330] flex items-center justify-center hidden p-4';
    modal.innerHTML = `
      <div class="bg-slate-900 border border-amber-400/50 rounded-3xl w-full max-w-3xl p-6 space-y-5 text-right shadow-2xl max-h-[88vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-lg font-black text-amber-300"><i class="fa-solid fa-crown"></i> لوحة إدارة الأدمن — ARAMKY Gold OS</h3>
            <p class="text-[11px] text-slate-400">إدارة الحسابات، حالة الاشتراك، ورسائل الدعم الفني الواردة</p>
          </div>
          <button type="button" onclick="closeAdminDashboard()" class="bg-slate-800 text-slate-300 px-3.5 py-1.5 rounded-xl text-xs font-bold">إغلاق ✕</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs bg-slate-950/70 p-4 rounded-2xl border border-slate-800">
          <input type="text" id="adm-new-code" placeholder="كود المعرض (مثال: BAGHDAD01)" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-amber-300 font-mono uppercase outline-none">
          <input type="text" id="adm-new-name" placeholder="اسم المعرض" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 outline-none">
          <input type="tel" id="adm-new-phone" placeholder="رقم الهاتف" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-emerald-400 font-mono outline-none">
          <button type="button" onclick="aramkyAdminCreateSubscriber()" class="bg-amber-400 text-slate-950 font-black rounded-xl p-2.5">إضافة / تحديث حساب</button>
        </div>

        <div class="space-y-2">
          <h4 class="text-xs font-bold text-amber-300">قائمة المشتركين والحسابات:</h4>
          <div id="adm-subscribers-list" class="space-y-2 text-xs"></div>
        </div>

        <div class="space-y-2">
          <h4 class="text-xs font-bold text-sky-300">رسائل وطلبات الدعم الفني الواردة:</h4>
          <div id="adm-tickets-list" class="space-y-2 text-xs"></div>
        </div>
      </div>
    `;
    global.document.body.appendChild(modal);
  }

  function renderAdminDashboardContent() {
    const subsEl = global.document.getElementById('adm-subscribers-list');
    const tixEl = global.document.getElementById('adm-tickets-list');
    const reg = getTenantsRegistry();

    if (subsEl) {
      if (!reg.length) {
        subsEl.innerHTML = '<div class="bg-slate-950/60 border border-slate-800 p-3 rounded-xl text-slate-400">الحساب الافتراضي النشط: ARAMKY (أدمن / رئيسي). يمكنك إضافة حسابات جديدة من الأعلى.</div>';
      } else {
        subsEl.innerHTML = reg.map((t, idx) => {
          const isLocked = String(t.status || '') === 'متوقف';
          return `
            <div class="bg-slate-950/80 border border-slate-800 p-3 rounded-2xl flex flex-wrap items-center justify-between gap-2">
              <div>
                <strong class="text-amber-300 font-mono">${t.code}</strong>
                <span class="text-slate-200 mr-2">${t.storeName || '--'}</span>
                <span class="text-[11px] text-slate-400 font-mono mr-2">${t.phone || ''}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${isLocked ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'}">${isLocked ? 'متوقف' : 'نشط'}</span>
                <button type="button" onclick="aramkyAdminToggleTenantStatus(${idx})" class="bg-slate-800 text-amber-300 px-2.5 py-1 rounded-lg font-bold">${isLocked ? 'تفعيل' : 'إيقاف'}</button>
                <button type="button" onclick="aramkyAdminLoadTenant('${String(t.code || '').replace(/'/g, "\\'")}')" class="bg-amber-500/20 text-amber-300 px-2.5 py-1 rounded-lg font-bold">فتح الحساب</button>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    if (tixEl) {
      const tickets = getAdminSupportTickets();
      if (!tickets.length) {
        tixEl.innerHTML = '<div class="bg-slate-950/60 border border-slate-800 p-3 rounded-xl text-slate-500">لا توجد رسائل دعم واردة حالياً.</div>';
      } else {
        tixEl.innerHTML = tickets.slice(0, 20).map(tk => `
          <div class="bg-slate-950/80 border border-slate-800 p-3 rounded-2xl space-y-1">
            <div class="flex justify-between">
              <strong class="text-sky-300">${tk.method || 'رسالة'} — <span class="font-mono text-amber-300">${tk.tenant || ''}</span></strong>
              <span class="text-[10px] text-slate-400 font-mono">${tk.time || ''}</span>
            </div>
            ${tk.msg ? `<p class="text-slate-200">${tk.msg}</p>` : ''}
          </div>
        `).join('');
      }
    }
  }

  global.aramkyAdminCreateSubscriber = function () {
    const codeInp = global.document.getElementById('adm-new-code');
    const nameInp = global.document.getElementById('adm-new-name');
    const phoneInp = global.document.getElementById('adm-new-phone');
    const code = (codeInp && codeInp.value || '').trim().toUpperCase();
    const storeName = (nameInp && nameInp.value || '').trim() || `معرض ${code}`;
    const phone = (phoneInp && phoneInp.value || '').trim();
    if (!code) {
      if (typeof global.showToast === 'function') global.showToast('أدخل كود المعرض أولاً', 'warning');
      return;
    }
    const reg = getTenantsRegistry();
    const idx = reg.findIndex(t => String(t.code || '').toUpperCase() === code);
    const record = { code, storeName, phone, status: 'نشط', updatedAt: new Date().toISOString() };
    if (idx !== -1) reg[idx] = Object.assign({}, reg[idx], record);
    else reg.push(record);
    saveTenantsRegistry(reg);
    if (codeInp) codeInp.value = '';
    if (nameInp) nameInp.value = '';
    if (phoneInp) phoneInp.value = '';
    renderAdminDashboardContent();
    if (typeof global.showToast === 'function') global.showToast('تم حفظ بيانات المشترك بنجاح', 'success');
  };

  global.aramkyAdminToggleTenantStatus = function (idx) {
    const reg = getTenantsRegistry();
    if (!reg[idx]) return;
    const nextStatus = reg[idx].status === 'متوقف' ? 'نشط' : 'متوقف';
    reg[idx].status = nextStatus;
    saveTenantsRegistry(reg);
    const tKey = getTenantDataKey(reg[idx].code);
    const tData = readSecureStorage(tKey, `TENANT_${reg[idx].code}`, null);
    if (tData) {
      tData.status = nextStatus;
      writeSecureStorage(tKey, tData, `TENANT_${reg[idx].code}`);
    }
    renderAdminDashboardContent();
    if (typeof global.loadTenantData === 'function' && typeof global.renderAll === 'function') {
      global.loadTenantData(global.activeTenantCode || 'ARAMKY');
      global.renderAll();
    }
  };

  global.aramkyAdminLoadTenant = function (code) {
    if (!code) return;
    setActiveSubscriberSession(code);
    if (typeof global.loadTenantData === 'function') global.loadTenantData(code);
    if (typeof global.renderAll === 'function') global.renderAll();
    global.closeAdminDashboard();
    if (typeof global.showToast === 'function') global.showToast(`تم تحميل الحساب ${code}`, 'success');
  };

  global.openAdminDashboard = function () {
    setAdminSession(true);
    ensureAdminModalDom();
    renderAdminDashboardContent();
    const modal = global.document.getElementById('aramky-admin-dashboard-modal');
    if (modal) modal.classList.remove('hidden');
  };

  global.openAdminModal = global.openAdminDashboard;

  global.closeAdminDashboard = function () {
    const modal = global.document.getElementById('aramky-admin-dashboard-modal');
    if (modal) modal.classList.add('hidden');
  };

  global.ARAMKY_CORE = {
    keys: KEYS,
    supportPhone: SUPPORT_PHONE,
    whatsappNumber: SUPPORT_WHATSAPP,
    masterCardNumber: MASTER_CARD_NUMBER,
    safeJsonParse,
    readSecureStorage,
    writeSecureStorage,
    getTenantDataKey,
    getCustomerLedgerKey,
    encodeCatalogRef,
    normalizeTenantPayload,
    verifyAdminPassword,
    setAdminSession,
    hasAdminSession,
    setActiveSubscriberSession,
    syncAdminUiVisibility,
    getTenantsRegistry,
    saveTenantsRegistry,
    authenticateSubscriber,
    isSubscriptionExpired,
    getContactInfo,
    pushSupportTicketToAdmin,
    getAdminSupportTickets,
    applyImageFallback,
    filesToDataUrls,
    renderGalleryThumbnails,
    openLightbox,
    closeLightbox,
    printReceiptOnly,
    isSupabaseReady,
    syncTenantToSupabase
  };
})(window);
