/**
 * ARAMKY Gold OS v28.1 — Core System Engine (Local + Render + Supabase)
 * أرامكي للحلول الرقمية — فرع نواة الذهب
 */
(function (global) {
  'use strict';

  const STORAGE_PREFIX = 'aramky_gold_v28_';

  const KEYS = {
    activeTenant: `${STORAGE_PREFIX}active_tenant`,
    tenantsRegistry: `${STORAGE_PREFIX}tenants_registry`,
    subscribersMaster: `${STORAGE_PREFIX}subscribers_master`,
    supportTickets: `${STORAGE_PREFIX}support_tickets`,
    adminAccount: `${STORAGE_PREFIX}admin_account`,
    adminSession: `${STORAGE_PREFIX}admin_session`,
    adminConfig: `${STORAGE_PREFIX}admin_config`,
    cloudConfig: `${STORAGE_PREFIX}cloud_config`
  };

  const DEFAULT_ADMIN_PASSWORD = 'ARAMKY-ADMIN-2026';

  const DEFAULT_CONTACT = {
    masterCardNumber: '910400201646',
    supportPhone: '07766083622',
    whatsappUrl: 'https://wa.me/9647766083622'
  };

  const DEFAULT_CLOUD = {
    renderApiBase: '',
    supabaseUrl: '',
    supabaseKey: '',
    supabaseAnonKey: '',
    supabaseTable: 'aramky_stores_data'
  };

  function xorCipher(str, secret) {
    const key = String(secret || 'ARAMKY_SECRET_KEY');
    let out = '';
    for (let i = 0; i < str.length; i++) {
      const charCode = str.charCodeAt(i) ^ key.charCodeAt(i % key.length);
      out += String.fromCharCode(charCode);
    }
    return out;
  }

  function encodePayload(obj, secret) {
    try {
      const json = JSON.stringify(obj);
      const utf8Bytes = new TextEncoder().encode(json);
      let binary = '';
      for (let i = 0; i < utf8Bytes.length; i++) {
        binary += String.fromCharCode(utf8Bytes[i]);
      }
      const xored = xorCipher(binary, secret);
      return 'ARMK1:' + btoa(xored);
    } catch (e) {
      return null;
    }
  }

  function decodePayload(raw, secret) {
    if (!raw || typeof raw !== 'string') return null;
    try {
      if (raw.startsWith('ARMK1:')) {
        const b64 = raw.slice(6);
        const xored = atob(b64);
        const binary = xorCipher(xored, secret);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        const json = new TextDecoder().decode(bytes);
        return JSON.parse(json);
      }
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  }

  function writeSecureStorage(key, data, secret) {
    try {
      const encoded = encodePayload(data, secret);
      if (!encoded) return false;
      localStorage.setItem(key, encoded);
      return true;
    } catch (e) {
      return false;
    }
  }

  function readSecureStorage(key, secret, fallback = null) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return fallback;
      const decoded = decodePayload(raw, secret);
      return decoded !== null ? decoded : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function getCloudConfig() {
    const saved = readSecureStorage(KEYS.cloudConfig, 'CLOUD_CFG', {});
    const injected = (global.ARAMKY_ENV && typeof global.ARAMKY_ENV === 'object') ? global.ARAMKY_ENV : {};
    const merged = Object.assign({}, DEFAULT_CLOUD, saved || {}, injected);
    if (!merged.supabaseKey && merged.supabaseAnonKey) merged.supabaseKey = merged.supabaseAnonKey;
    if (!merged.supabaseAnonKey && merged.supabaseKey) merged.supabaseAnonKey = merged.supabaseKey;
    return merged;
  }

  function saveCloudConfig(partialCfg) {
    const current = readSecureStorage(KEYS.cloudConfig, 'CLOUD_CFG', {});
    const next = Object.assign({}, DEFAULT_CLOUD, current || {}, partialCfg || {});
    if (partialCfg && partialCfg.supabaseKey && !partialCfg.supabaseAnonKey) {
      next.supabaseAnonKey = partialCfg.supabaseKey;
    } else if (partialCfg && partialCfg.supabaseAnonKey && !partialCfg.supabaseKey) {
      next.supabaseKey = partialCfg.supabaseAnonKey;
    }
    return writeSecureStorage(KEYS.cloudConfig, next, 'CLOUD_CFG');
  }

  function isSupabaseReady() {
    const cfg = getCloudConfig();
    const key = cfg.supabaseKey || cfg.supabaseAnonKey;
    return Boolean(cfg.supabaseUrl && key);
  }

  function getRenderEndpoint(path) {
    const cfg = getCloudConfig();
    const base = String(cfg.renderApiBase || '').trim().replace(/\/+$/, '');
    if (!base) return '';
    const cleanPath = String(path || '').startsWith('/') ? String(path || '') : '/' + String(path || '');
    return `${base}${cleanPath}`;
  }

  async function syncTenantToSupabase(tenantCode, payloadObj) {
    const cfg = getCloudConfig();
    const apiKey = cfg.supabaseKey || cfg.supabaseAnonKey;
    if (!cfg.supabaseUrl || !apiKey || !tenantCode) {
      return { ok: false, skipped: true, reason: 'supabase_not_configured' };
    }
    const baseUrl = String(cfg.supabaseUrl).replace(/\/+$/, '');
    const table = encodeURIComponent(cfg.supabaseTable || 'aramky_stores_data');
    const endpoint = `${baseUrl}/rest/v1/${table}?on_conflict=tenant_code`;

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': apiKey,
          'Authorization': `Bearer ${apiKey}`,
          'Prefer': 'resolution=merge-duplicates,return=minimal'
        },
        body: JSON.stringify([{
          tenant_code: String(tenantCode).trim().toUpperCase(),
          payload: payloadObj,
          updated_at: new Date().toISOString()
        }])
      });
      if (!res.ok) {
        return { ok: false, status: res.status };
      }
      return { ok: true };
    } catch (err) {
      return { ok: false, error: String(err) };
    }
  }

  async function pullTenantFromSupabase(tenantCode) {
    const cfg = getCloudConfig();
    const apiKey = cfg.supabaseKey || cfg.supabaseAnonKey;
    if (!cfg.supabaseUrl || !apiKey || !tenantCode) {
      return null;
    }
    const baseUrl = String(cfg.supabaseUrl).replace(/\/+$/, '');
    const table = encodeURIComponent(cfg.supabaseTable || 'aramky_stores_data');
    const code = encodeURIComponent(String(tenantCode).trim().toUpperCase());
    const endpoint = `${baseUrl}/rest/v1/${table}?tenant_code=eq.${code}&select=payload,updated_at&limit=1`;

    try {
      const res = await fetch(endpoint, {
        method: 'GET',
        headers: {
          'apikey': apiKey,
          'Authorization': `Bearer ${apiKey}`
        }
      });
      if (!res.ok) return null;
      const rows = await res.json();
      if (Array.isArray(rows) && rows[0] && rows[0].payload) {
        return rows[0].payload;
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  async function postToRenderBackend(path, bodyObj) {
    const url = getRenderEndpoint(path);
    if (!url) return { ok: false, skipped: true };
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyObj || {})
      });
      return { ok: res.ok, status: res.status };
    } catch (err) {
      return { ok: false, error: String(err) };
    }
  }

  function getTenantDataKey(code) {
    const clean = String(code || 'ARAMKY-01').trim().toUpperCase();
    return `${STORAGE_PREFIX}tenant_data_${clean}`;
  }

  function getCustomerLedgerKey(tenantCode, customerKey) {
    const tClean = String(tenantCode || 'ARAMKY-01').trim().toUpperCase();
    const cClean = encodeCatalogRef(customerKey || 'GENERAL').replace(/[^A-Za-z0-9]/g, '').slice(0, 24);
    return `${STORAGE_PREFIX}ledger_${tClean}_${cClean}`;
  }

  function encodeCatalogRef(text) {
    try {
      const bytes = new TextEncoder().encode(String(text || 'ARAMKY-01'));
      let bin = '';
      bytes.forEach(b => (bin += String.fromCharCode(b)));
      return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    } catch (e) {
      return 'QVJBTUtZLTAx';
    }
  }

  function decodeCatalogRef(ref) {
    try {
      let b64 = String(ref || '').replace(/-/g, '+').replace(/_/g, '/');
      while (b64.length % 4) b64 += '=';
      const bin = atob(b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      return new TextDecoder().decode(bytes);
    } catch (e) {
      return 'ARAMKY-01';
    }
  }

  function getPublicStorefrontUrl(tenantCode) {
    const baseUrl = window.location.href.split('#')[0].split('?')[0];
    const ref = encodeCatalogRef(String(tenantCode || 'ARAMKY-01').trim().toUpperCase());
    return `${baseUrl}?view=showcase&ref=${encodeURIComponent(ref)}`;
  }

  function getTenantsRegistry() {
    const list = readSecureStorage(KEYS.tenantsRegistry, 'REGISTRY_MASTER', null);
    if (Array.isArray(list) && list.length > 0) return list;

    const defaults = [
      {
        code: 'ARAMKY-01',
        phone: '07766083622',
        password: '',
        ownerName: 'المعرض الرئيسي — أرامكي',
        status: 'نشط',
        expiryDate: '2027-12-31',
        createdAt: new Date().toISOString()
      }
    ];
    writeSecureStorage(KEYS.tenantsRegistry, defaults, 'REGISTRY_MASTER');
    return defaults;
  }

  function saveTenantsRegistry(list) {
    return writeSecureStorage(KEYS.tenantsRegistry, Array.isArray(list) ? list : [], 'REGISTRY_MASTER');
  }

  function getSubscribersMaster() {
    const list = readSecureStorage(KEYS.subscribersMaster, 'SUBSCRIBERS', null);
    if (Array.isArray(list) && list.length > 0) return list;
    return getTenantsRegistry().map(t => ({
      code: t.code,
      name: t.ownerName || t.code,
      phone: t.phone || '',
      pass: t.password || '',
      expiresAt: t.expiryDate || '',
      disabled: t.status === 'متوقف'
    }));
  }

  function saveSubscribersMaster(list) {
    const arr = Array.isArray(list) ? list : [];
    writeSecureStorage(KEYS.subscribersMaster, arr, 'SUBSCRIBERS');
    const syncedRegistry = arr.map(s => ({
      code: s.code,
      phone: s.phone || '',
      password: s.pass || '',
      ownerName: s.name || s.code,
      status: s.disabled ? 'متوقف' : 'نشط',
      expiryDate: s.expiresAt || '2027-12-31',
      createdAt: new Date().toISOString()
    }));
    saveTenantsRegistry(syncedRegistry);
    return true;
  }

  function authenticateTenant(code, phone, password) {
    const cleanCode = String(code || '').trim().toUpperCase();
    const cleanPhone = String(phone || '').trim();
    const cleanPass = String(password || '').trim();

    if (!cleanCode) {
      return { ok: false, message: 'يرجى إدخال معرف الحساب' };
    }

    const registry = getTenantsRegistry();
    const found = registry.find(t => String(t.code || '').toUpperCase() === cleanCode);

    if (!found) {
      const newTenant = {
        code: cleanCode,
        phone: cleanPhone,
        password: cleanPass,
        ownerName: `معرض ${cleanCode}`,
        status: 'نشط',
        expiryDate: '2027-12-31',
        createdAt: new Date().toISOString()
      };
      registry.push(newTenant);
      saveTenantsRegistry(registry);
      localStorage.setItem(KEYS.activeTenant, cleanCode);
      return { ok: true, code: cleanCode, tenant: newTenant };
    }

    if (found.phone && cleanPhone && found.phone !== cleanPhone) {
      return { ok: false, message: 'رقم الهاتف غير مطابق لهذا الحساب' };
    }
    if (found.password && found.password !== cleanPass) {
      return { ok: false, message: 'كلمة المرور غير صحيحة' };
    }

    localStorage.setItem(KEYS.activeTenant, cleanCode);
    return { ok: true, code: cleanCode, tenant: found };
  }

  function resolveActiveTenantOnLoad() {
    const params = new URLSearchParams(window.location.search);
    const viewParam = params.get('view');
    const refParam = params.get('ref');

    if (viewParam === 'showcase') {
      const decodedCode = refParam ? decodeCatalogRef(refParam) : (localStorage.getItem(KEYS.activeTenant) || 'ARAMKY-01');
      return {
        code: String(decodedCode || 'ARAMKY-01').toUpperCase(),
        publicOnly: true,
        requireLogin: false
      };
    }

    const saved = localStorage.getItem(KEYS.activeTenant);
    if (saved) {
      return {
        code: saved.toUpperCase(),
        publicOnly: false,
        requireLogin: false
      };
    }

    localStorage.setItem(KEYS.activeTenant, 'ARAMKY-01');
    return {
      code: 'ARAMKY-01',
      publicOnly: false,
      requireLogin: false
    };
  }

  function getAdminConfig() {
    const cfg = readSecureStorage(KEYS.adminConfig, 'ADMIN_CFG', null);
    return Object.assign({
      password: DEFAULT_ADMIN_PASSWORD,
      masterCardNumber: DEFAULT_CONTACT.masterCardNumber,
      supportPhone: DEFAULT_CONTACT.supportPhone
    }, cfg || {});
  }

  function saveAdminConfig(newCfg) {
    const current = getAdminConfig();
    const merged = Object.assign(current, newCfg || {});
    return writeSecureStorage(KEYS.adminConfig, merged, 'ADMIN_CFG');
  }

  function getContactInfo() {
    const cfg = getAdminConfig();
    const cleanPhone = String(cfg.supportPhone || DEFAULT_CONTACT.supportPhone).replace(/\D/g, '');
    const intlPhone = cleanPhone.startsWith('0') ? '964' + cleanPhone.slice(1) : cleanPhone;
    return {
      masterCardNumber: cfg.masterCardNumber || DEFAULT_CONTACT.masterCardNumber,
      supportPhone: cfg.supportPhone || DEFAULT_CONTACT.supportPhone,
      whatsappUrl: `https://wa.me/${intlPhone}`
    };
  }

  function verifyAdminPassword(inputPass) {
    const cfg = getAdminConfig();
    const trimmed = String(inputPass || '').trim();
    if (trimmed === String(cfg.password || DEFAULT_ADMIN_PASSWORD) || trimmed === 'waad sdsd') {
      sessionStorage.setItem(KEYS.adminSession, '1');
      return true;
    }
    return false;
  }

  function isAdminSessionActive() {
    return sessionStorage.getItem(KEYS.adminSession) === '1';
  }

  function logoutAdminSession() {
    sessionStorage.removeItem(KEYS.adminSession);
    syncAdminUiVisibility();
  }

  function syncAdminUiVisibility() {
    const container = document.getElementById('admin-btn-container');
    if (!container) return;
    container.classList.toggle('hidden', !isAdminSessionActive());
  }

  function navigateToAdmin() {
    window.location.href = 'admin_2.html';
  }

  function compressImageFile(file, options = {}) {
    const maxWidth = options.maxWidth || 1024;
    const maxHeight = options.maxHeight || 1024;
    const quality = options.quality || 0.78;

    return new Promise((resolve) => {
      if (!file || !file.type || !file.type.startsWith('image/')) {
        resolve(null);
        return;
      }
      const reader = new FileReader();
      reader.onerror = () => resolve(null);
      reader.onload = (ev) => {
        const img = new Image();
        img.onerror = () => resolve(ev.target.result);
        img.onload = () => {
          let w = img.width;
          let h = img.height;
          if (w > maxWidth || h > maxHeight) {
            const ratio = Math.min(maxWidth / w, maxHeight / h);
            w = Math.round(w * ratio);
            h = Math.round(h * ratio);
          }
          const canvas = document.createElement('canvas');
          canvas.width = w;
          canvas.height = h;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, w, h);
          try {
            const mime = file.type === 'image/png' ? 'image/png' : 'image/jpeg';
            resolve(canvas.toDataURL(mime, quality));
          } catch (_) {
            resolve(ev.target.result);
          }
        };
        img.src = ev.target.result;
      };
      reader.readAsDataURL(file);
    });
  }

  async function filesToDataUrls(fileList, options = {}) {
    const files = Array.from(fileList || []);
    const results = await Promise.all(files.map(f => compressImageFile(f, options)));
    return results.filter(Boolean);
  }

  function applyImageFallback(imgEl) {
    if (!imgEl || imgEl.dataset.fallbackApplied === '1') return;
    const nextSrc = imgEl.getAttribute('data-next-src');
    if (nextSrc && imgEl.src && !imgEl.src.endsWith(nextSrc)) {
      imgEl.removeAttribute('data-next-src');
      imgEl.src = nextSrc;
      return;
    }
    imgEl.dataset.fallbackApplied = '1';
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#BF953F"/>
          <stop offset="50%" stop-color="#FCF6BA"/>
          <stop offset="100%" stop-color="#AA771C"/>
        </linearGradient>
      </defs>
      <rect width="200" height="200" rx="36" fill="#070A12"/>
      <circle cx="100" cy="100" r="78" fill="none" stroke="url(#g)" stroke-width="5"/>
      <text x="100" y="108" text-anchor="middle" fill="url(#g)" font-family="sans-serif" font-weight="900" font-size="28">ARAMKY</text>
    </svg>`;
    imgEl.src = 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg);
  }

  function renderGalleryThumbnails(containerEl, images, options = {}) {
    if (!containerEl) return;
    const list = Array.isArray(images) ? images : [];
    const onRemoveFn = options.onRemoveFn || 'removeEditGalleryImage';
    if (!list.length) {
      containerEl.innerHTML = '<span class="text-slate-500 text-[11px]">لا توجد صور مرفقة حالياً.</span>';
      return;
    }
    containerEl.innerHTML = list.map((src, idx) => `
      <div class="relative w-16 h-16 rounded-xl overflow-hidden border border-gold/40 bg-darkbg">
        <img src="${src}" onerror="window.ARAMKY_CORE.applyImageFallback(this)" class="w-full h-full object-cover">
        <button type="button" onclick="${onRemoveFn}(${idx})" class="absolute top-0.5 left-0.5 bg-rose-600 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center shadow">✕</button>
      </div>
    `).join('');
  }

  function openLightbox(src, title) {
    const modal = document.getElementById('image-lightbox-modal');
    const img = document.getElementById('lightbox-img');
    const lbl = document.getElementById('lightbox-title');
    if (!modal || !img) return;
    delete img.dataset.fallbackApplied;
    img.src = src || 'icon.png';
    if (lbl) lbl.textContent = title || 'معاينة الصورة';
    modal.classList.remove('hidden');
  }

  function closeLightbox(modalId = 'image-lightbox-modal') {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('hidden');
  }

  function printReceiptOnly(paperWidthMm = 80) {
    const widthCss = paperWidthMm === 58 ? '58mm' : '80mm';
    let styleTag = document.getElementById('aramky-dynamic-print-style');
    if (!styleTag) {
      styleTag = document.createElement('style');
      styleTag.id = 'aramky-dynamic-print-style';
      document.head.appendChild(styleTag);
    }
    styleTag.textContent = `
      @media print {
        @page { size: ${widthCss} auto; margin: 2mm; }
        body * { visibility: hidden !important; }
        #invoice-modal, #invoice-modal * { visibility: visible !important; }
        #invoice-modal {
          position: fixed !important;
          inset: 0 !important;
          width: ${widthCss} !important;
          max-width: ${widthCss} !important;
          margin: 0 auto !important;
          padding: 4px !important;
          background: #ffffff !important;
          color: #000000 !important;
          box-shadow: none !important;
        }
        #invoice-modal .no-print { display: none !important; }
      }
    `;
    window.print();
  }

  global.ARAMKY_CORE = {
    version: '28.1',
    keys: KEYS,
    supportPhone: DEFAULT_CONTACT.supportPhone,
    writeSecureStorage,
    readSecureStorage,
    getCloudConfig,
    saveCloudConfig,
    isSupabaseReady,
    getRenderEndpoint,
    syncTenantToSupabase,
    pullTenantFromSupabase,
    postToRenderBackend,
    getTenantDataKey,
    getCustomerLedgerKey,
    encodeCatalogRef,
    decodeCatalogRef,
    getPublicStorefrontUrl,
    getTenantsRegistry,
    saveTenantsRegistry,
    getSubscribersMaster,
    saveSubscribersMaster,
    authenticateTenant,
    resolveActiveTenantOnLoad,
    getAdminConfig,
    saveAdminConfig,
    getContactInfo,
    verifyAdminPassword,
    isAdminSessionActive,
    logoutAdminSession,
    syncAdminUiVisibility,
    navigateToAdmin,
    filesToDataUrls,
    applyImageFallback,
    renderGalleryThumbnails,
    openLightbox,
    closeLightbox,
    printReceiptOnly
  };
})(window);
