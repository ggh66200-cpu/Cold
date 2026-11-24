/* ARAMKY Gold OS - Core Bridge, Cipher, Image Engine, Cloud Sync & Tenant Isolation (aramky-core.js) */
(function (global) {
  'use strict';

  const CIPHER_PREFIX = 'ARMK_ENC_V1::';
  const SECRET_SALT = 'ARAMKY::NAWAT_AL_DHAHAB::2026::GOLD_OS';

  const FALLBACK_BRAND_SVG =
    'data:image/svg+xml;utf8,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">' +
        '<rect width="256" height="256" rx="48" fill="#070A12"/>' +
        '<rect x="8" y="8" width="240" height="240" rx="42" fill="none" stroke="#D4AF37" stroke-width="6"/>' +
        '<text x="128" y="148" text-anchor="middle" font-size="96" fill="#D4AF37" font-family="Arial, sans-serif">👑</text>' +
      '</svg>'
    );

  const FALLBACK_LOGO_SVG =
    'data:image/svg+xml;utf8,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">' +
        '<rect width="200" height="200" fill="#0F172A"/>' +
        '<circle cx="100" cy="100" r="84" fill="none" stroke="#D4AF37" stroke-width="5"/>' +
        '<text x="100" y="114" text-anchor="middle" fill="#D4AF37" font-family="Arial,sans-serif" font-size="34" font-weight="bold">ARAMKY</text>' +
      '</svg>'
    );

  const KEYS = {
    tenants: 'aramky_tenants_v28',
    activeTenant: 'aramky_active_tenant',
    supportTickets: 'aramky_support_tickets_v28',
    adminSession: 'aramky_admin_auth_v28',
    cloudConfig: 'aramky_cloud_config_v28'
  };

  function deriveKey(context = 'DEFAULT') {
    const raw = `${SECRET_SALT}|${String(context || 'DEFAULT').toUpperCase()}`;
    let h1 = 0x811c9dc5;
    let h2 = 0x01000193;
    for (let i = 0; i < raw.length; i++) {
      const c = raw.charCodeAt(i);
      h1 ^= c;
      h1 = Math.imul(h1, 0x01000193);
      h2 ^= c + i;
      h2 = Math.imul(h2, 0x85ebca6b);
    }
    return ((h1 >>> 0).toString(16).padStart(8, '0') + (h2 >>> 0).toString(16).padStart(8, '0')).repeat(4);
  }

  function xorCipher(text, key) {
    let out = '';
    for (let i = 0; i < text.length; i++) {
      const k = key.charCodeAt(i % key.length) + (i % 31);
      out += String.fromCharCode(text.charCodeAt(i) ^ (k & 0xff));
    }
    return out;
  }

  function encryptPayload(obj, context = 'DEFAULT') {
    const json = JSON.stringify(obj);
    const utf8Bytes = new TextEncoder().encode(json);
    let binary = '';
    for (let i = 0; i < utf8Bytes.length; i++) binary += String.fromCharCode(utf8Bytes[i]);
    const xored = xorCipher(binary, deriveKey(context));
    return CIPHER_PREFIX + btoa(xored);
  }

  function decryptPayload(cipherText, context = 'DEFAULT') {
    if (typeof cipherText !== 'string') return null;
    if (!cipherText.startsWith(CIPHER_PREFIX)) {
      try {
        return JSON.parse(cipherText);
      } catch (_) {
        return null;
      }
    }
    try {
      const b64 = cipherText.slice(CIPHER_PREFIX.length);
      const binary = atob(b64);
      const xored = xorCipher(binary, deriveKey(context));
      const bytes = new Uint8Array(xored.length);
      for (let i = 0; i < xored.length; i++) bytes[i] = xored.charCodeAt(i);
      return JSON.parse(new TextDecoder().decode(bytes));
    } catch (_) {
      return null;
    }
  }

  function readSecureStorage(storageKey, context, fallback = null) {
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw === null || raw === undefined) return fallback;
      const parsed = decryptPayload(raw, context);
      return parsed !== null ? parsed : fallback;
    } catch (_) {
      return fallback;
    }
  }

  function writeSecureStorage(storageKey, value, context) {
    try {
      localStorage.setItem(storageKey, encryptPayload(value, context));
      return true;
    } catch (_) {
      return false;
    }
  }

  function getTenantDataKey(tenantCode) {
    return `aramky_gold_data_${String(tenantCode || 'ARAMKY-01').trim().toUpperCase()}`;
  }

  function getCustomerLedgerKey(tenantCode, customerKey) {
    return `aramky_cust_ledger_${String(tenantCode || 'ARAMKY-01').trim().toUpperCase()}_${String(customerKey || 'GENERAL')}`;
  }

  function encodeCatalogRef(tenantCode) {
    return btoa(unescape(encodeURIComponent(String(tenantCode || 'ARAMKY-01').trim().toUpperCase())));
  }

  function decodeCatalogRef(ref) {
    try {
      return decodeURIComponent(escape(atob(String(ref || '').trim()))).toUpperCase();
    } catch (_) {
      return null;
    }
  }

  function getPublicStorefrontUrl(tenantCode) {
    const base = window.location.href.split('#')[0].split('?')[0];
    return `${base}?catalog=${encodeURIComponent(encodeCatalogRef(tenantCode))}`;
  }

  function applyImageFallback(imgEl, variant = 'brand') {
    if (!imgEl) return;
    if (imgEl.dataset.fallbackApplied === '1') return;
    imgEl.dataset.fallbackApplied = '1';
    imgEl.src = variant === 'logo' ? FALLBACK_LOGO_SVG : FALLBACK_BRAND_SVG;
  }

  function filesToDataUrls(fileList, opts = {}) {
    const files = Array.from(fileList || []);
    const maxWidth = opts.maxWidth || 1024;
    const maxHeight = opts.maxHeight || 1024;
    const quality = opts.quality || 0.78;
    return Promise.all(
      files.map(
        file =>
          new Promise(resolve => {
            const reader = new FileReader();
            reader.onload = () => {
              const img = new Image();
              img.onload = () => {
                let { width, height } = img;
                if (width > maxWidth || height > maxHeight) {
                  const ratio = Math.min(maxWidth / width, maxHeight / height);
                  width = Math.round(width * ratio);
                  height = Math.round(height * ratio);
                }
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                resolve(canvas.toDataURL('image/jpeg', quality));
              };
              img.onerror = () => resolve(reader.result);
              img.src = reader.result;
            };
            reader.onerror = () => resolve(null);
            reader.readAsDataURL(file);
          })
      )
    ).then(list => list.filter(Boolean));
  }

  function getCloudConfig() {
    return readSecureStorage(KEYS.cloudConfig, 'CLOUD_CFG', {
      enabled: false,
      endpointUrl: '',
      apiKey: '',
      lastSync: null
    });
  }

  function saveCloudConfig(cfg) {
    return writeSecureStorage(KEYS.cloudConfig, cfg, 'CLOUD_CFG');
  }

  async function syncTenantToCloud(tenantCode, payload) {
    const cfg = getCloudConfig();
    cfg.lastSync = new Date().toISOString();
    saveCloudConfig(cfg);
    if (!cfg.enabled || !cfg.endpointUrl) {
      return { ok: true, mode: 'local_encrypted', syncedAt: cfg.lastSync };
    }
    try {
      const res = await fetch(cfg.endpointUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(cfg.apiKey ? { Authorization: `Bearer ${cfg.apiKey}` } : {})
        },
        body: JSON.stringify({ tenantCode, payload, syncedAt: cfg.lastSync })
      });
      return { ok: res.ok, mode: 'remote_api', status: res.status, syncedAt: cfg.lastSync };
    } catch (err) {
      return { ok: false, mode: 'remote_api', error: err.message };
    }
  }

  function getTenants() {
    const list = readSecureStorage(KEYS.tenants, 'TENANTS_LIST', null);
    if (Array.isArray(list) && list.length) return list;
    const defaults = [
      { code: 'ARAMKY-01', name: 'صياغة أرامكي - الفرع الرئيسي', phone: '07766083622', pass: '1234', status: 'نشط' }
    ];
    writeSecureStorage(KEYS.tenants, defaults, 'TENANTS_LIST');
    return defaults;
  }

  function saveTenants(list) {
    return writeSecureStorage(KEYS.tenants, list, 'TENANTS_LIST');
  }

  function authenticateTenant(code, phone, pass) {
    const cleanCode = String(code || '').trim().toUpperCase();
    const tenants = getTenants();
    let found = tenants.find(t => String(t.code).toUpperCase() === cleanCode);
    if (!found) {
      found = {
        code: cleanCode,
        name: `معرض ${cleanCode}`,
        phone: String(phone || '').trim(),
        pass: String(pass || '').trim(),
        status: 'نشط'
      };
      tenants.push(found);
      saveTenants(tenants);
    }
    return { ok: true, code: cleanCode, tenant: found };
  }

  function isSubscriptionBlocked(tenant) {
    if (!tenant) return false;
    return String(tenant.status || '') === 'متوقف';
  }

  function isAdminAuthenticated() {
    return readSecureStorage(KEYS.adminSession, 'ADMIN_AUTH', false) === true;
  }

  function setAdminAuthenticated(val) {
    writeSecureStorage(KEYS.adminSession, Boolean(val), 'ADMIN_AUTH');
    syncAdminUiVisibility();
  }

  function verifyAdminPassword(pass) {
    return String(pass || '').trim() === 'ARAMKY2026';
  }

  function syncAdminUiVisibility() {
    const isAdmin = isAdminAuthenticated();
    const btnContainer = document.getElementById('admin-btn-container');
    const bar = document.getElementById('admin-control-bar');
    if (btnContainer) btnContainer.classList.toggle('hidden', !isAdmin);
    if (bar) bar.classList.toggle('hidden', !isAdmin);
  }

  function getContactInfo() {
    return {
      masterCardNumber: '910400201646',
      supportPhone: '07766083622',
      whatsappUrl: 'https://wa.me/9647766083622'
    };
  }

  function printReceiptOnly(paperWidth = 80) {
    document.body.dataset.printWidth = String(paperWidth);
    window.print();
  }

  global.ARAMKY_CORE = {
    keys: KEYS,
    readSecureStorage,
    writeSecureStorage,
    getTenantDataKey,
    getCustomerLedgerKey,
    encodeCatalogRef,
    decodeCatalogRef,
    getPublicStorefrontUrl,
    applyImageFallback,
    filesToDataUrls,
    getCloudConfig,
    saveCloudConfig,
    syncTenantToCloud,
    getTenants,
    saveTenants,
    authenticateTenant,
    isSubscriptionBlocked,
    isAdminAuthenticated,
    setAdminAuthenticated,
    verifyAdminPassword,
    syncAdminUiVisibility,
    getContactInfo,
    printReceiptOnly
  };
})(window);
