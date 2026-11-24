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

  function deriveKey(context = 'DEFAULT') {
    const raw = `${SECRET_SALT}|${String(context || 'DEFAULT').toUpperCase()}`;
    let h1 = 0x811c9dc5;
    let h2 = 0x01000193;
    for (let i = 0; i < raw.length; i++) {
      const c = raw.charCodeAt(i);
      h1 ^= c;
      h1 = Math.imul(h1, 0x01000193);
      h2 = Math.imul(h2 ^ c, 0x27d4eb2d);
    }
    return `${(h1 >>> 0).toString(16)}${(h2 >>> 0).toString(16)}ARAMKY_KEY`;
  }

  function toBase64Utf8(str) {
    const bytes = new TextEncoder().encode(String(str));
    let bin = '';
    for (let i = 0; i < bytes.length; i++) {
      bin += String.fromCharCode(bytes[i]);
    }
    return btoa(bin);
  }

  function fromBase64Utf8(b64) {
    const bin = atob(String(b64));
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) {
      bytes[i] = bin.charCodeAt(i);
    }
    return new TextDecoder().decode(bytes);
  }

  const ARAMKY_CORE = {
    version: 'v28.1',
    brand: 'أرامكي للحلول الرقمية — فرع نواة الذهب',
    supportPhone: '07766083622',
    whatsappUrl: 'https://wa.me/9647801103129',
    masterCardNumber: '910400201646',
    storageBucket: 'gold-media',
    storesTable: 'admin_stores_inventory',
    keys: {
      activeTenant: 'aramky_active_tenant',
      subscribersMaster: 'aramky_subscribers_master',
      adminAccount: 'aramky_admin_account',
      supportTickets: 'aramky_global_support_tickets',
      supabaseConfig: 'aramky_supabase_config',
      cloudSyncConfig: 'aramky_cloud_sync_config',
      adminSession: 'aramky_admin_unlocked'
    },

    /* ==========================================
       🔐 التشفير وفك التشفير لحماية البيانات
       ========================================== */
    encryptPayload(data, context = 'STORE') {
      try {
        const json = typeof data === 'string' ? data : JSON.stringify(data);
        const key = deriveKey(context);
        const utf8 = new TextEncoder().encode(json);
        const out = new Uint8Array(utf8.length);
        for (let i = 0; i < utf8.length; i++) {
          const kByte = key.charCodeAt(i % key.length);
          const rot = ((i * 7) % 5) + 1;
          const b = utf8[i] ^ kByte;
          out[i] = ((b << rot) | (b >>> (8 - rot))) & 0xff;
        }
        let bin = '';
        for (let i = 0; i < out.length; i++) {
          bin += String.fromCharCode(out[i]);
        }
        return CIPHER_PREFIX + btoa(bin);
      } catch (_) {
        return typeof data === 'string' ? data : JSON.stringify(data);
      }
    },

    decryptPayload(cipherText, context = 'STORE') {
      if (!cipherText || typeof cipherText !== 'string') return null;
      try {
        if (!cipherText.startsWith(CIPHER_PREFIX)) {
          return JSON.parse(cipherText);
        }
        const b64 = cipherText.slice(CIPHER_PREFIX.length);
        const bin = atob(b64);
        const key = deriveKey(context);
        const out = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) {
          const kByte = key.charCodeAt(i % key.length);
          const rot = ((i * 7) % 5) + 1;
          const v = bin.charCodeAt(i) & 0xff;
          const unrot = ((v >>> rot) | (v << (8 - rot))) & 0xff;
          out[i] = unrot ^ kByte;
        }
        const json = new TextDecoder().decode(out);
        return JSON.parse(json);
      } catch (_) {
        return null;
      }
    },

    writeSecureStorage(storageKey, value, context = 'STORE') {
      try {
        const encrypted = this.encryptPayload(value, context);
        localStorage.setItem(storageKey, encrypted);
        return true;
      } catch (_) {
        return false;
      }
    },

    readSecureStorage(storageKey, context = 'STORE', fallback = null) {
      try {
        const raw = localStorage.getItem(storageKey);
        if (!raw) return fallback;
        const decrypted = this.decryptPayload(raw, context);
        return decrypted !== null ? decrypted : fallback;
      } catch (_) {
        return fallback;
      }
    },

    /* ==========================================
       🧭 عزل حسابات الصاغة والزبائن وروابط المعرض
       ========================================== */
    getTenantDataKey(code) {
      const clean = String(code || 'ARAMKY-01').trim().toUpperCase();
      return `aramky_gold_data_${clean}`;
    },

    getCustomerLedgerKey(tenantCode, customerKey) {
      const tClean = String(tenantCode || 'ARAMKY-01').trim().toUpperCase();
      const cClean = String(customerKey || 'GENERAL').trim().toUpperCase().replace(/[^A-Z0-9_-]/g, '_');
      return `aramky_customer_ledger_${tClean}_${cClean}`;
    },

    encodeCatalogRef(storeCode) {
      const clean = String(storeCode || 'ARAMKY-01').trim().toUpperCase();
      return toBase64Utf8(clean).replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
    },

    decodeCatalogRef(token) {
      if (!token) return null;
      try {
        let b64 = String(token).replace(/-/g, '+').replace(/_/g, '/');
        while (b64.length % 4) b64 += '=';
        const decoded = fromBase64Utf8(b64).trim().toUpperCase();
        return decoded || null;
      } catch (_) {
        return String(token).trim().toUpperCase() || null;
      }
    },

    getPublicStorefrontUrl(storeCode) {
      const baseUrl = window.location.href.split('#')[0].split('?')[0];
      const ref = this.encodeCatalogRef(storeCode);
      return `${baseUrl}?catalog=${encodeURIComponent(ref)}&view=showcase`;
    },

    resolveStorefrontCodeFromQuery(searchString = window.location.search) {
      const params = new URLSearchParams(searchString || '');
      const catalogParam = params.get('catalog');
      if (catalogParam) {
        return this.decodeCatalogRef(catalogParam);
      }
      const legacyStoreParam = params.get('store');
      if (legacyStoreParam) {
        return String(legacyStoreParam).trim().toUpperCase();
      }
      return null;
    },

    getContactInfo() {
      return {
        supportPhone: this.supportPhone,
        whatsappUrl: this.whatsappUrl,
        masterCardNumber: this.masterCardNumber
      };
    },

    /* ==========================================
       ☁️ مزامنة سحابية آمنة بدون مفاتيح مكشوفة في الكود
       ========================================== */
    getCloudSyncConfig() {
      const cfg = this.readSecureStorage(this.keys.cloudSyncConfig, 'CLOUD_SYNC', null);
      if (cfg && cfg.enabled && cfg.endpointUrl) {
        return {
          enabled: true,
          endpointUrl: String(cfg.endpointUrl).trim()
        };
      }
      return { enabled: false, endpointUrl: '' };
    },

    configureCloudSync(endpointUrl, enabled = true) {
      const cleanUrl = String(endpointUrl || '').trim();
      return this.writeSecureStorage(
        this.keys.cloudSyncConfig,
        { enabled: Boolean(enabled && cleanUrl), endpointUrl: cleanUrl },
        'CLOUD_SYNC'
      );
    },

    async pushTenantSnapshot(tenantCode, snapshotObj) {
      const cfg = this.getCloudSyncConfig();
      if (!cfg.enabled || !cfg.endpointUrl || typeof fetch !== 'function') {
        return { ok: false, skipped: true };
      }
      try {
        const cleanCode = String(tenantCode || 'ARAMKY-01').trim().toUpperCase();
        const sealedPayload = this.encryptPayload(
          {
            tenantCode: cleanCode,
            syncedAt: new Date().toISOString(),
            data: snapshotObj
          },
          `SYNC_${cleanCode}`
        );
        const res = await fetch(cfg.endpointUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ref: this.encodeCatalogRef(cleanCode),
            envelope: sealedPayload
          })
        });
        return { ok: res.ok, status: res.status };
      } catch (err) {
        return { ok: false, error: String(err && err.message ? err.message : err) };
      }
    },

    async pullTenantSnapshot(tenantCode) {
      const cfg = this.getCloudSyncConfig();
      if (!cfg.enabled || !cfg.endpointUrl || typeof fetch !== 'function') {
        return { ok: false, skipped: true };
      }
      try {
        const cleanCode = String(tenantCode || 'ARAMKY-01').trim().toUpperCase();
        const ref = encodeURIComponent(this.encodeCatalogRef(cleanCode));
        const sep = cfg.endpointUrl.includes('?') ? '&' : '?';
        const res = await fetch(`${cfg.endpointUrl}${sep}ref=${ref}`, { method: 'GET' });
        if (!res.ok) return { ok: false, status: res.status };
        const json = await res.json();
        const envelope = json && (json.envelope || json.data || null);
        const opened = envelope ? this.decryptPayload(envelope, `SYNC_${cleanCode}`) : null;
        if (opened && opened.data) {
          return { ok: true, data: opened.data, syncedAt: opened.syncedAt };
        }
        return { ok: false };
      } catch (err) {
        return { ok: false, error: String(err && err.message ? err.message : err) };
      }
    },

    async loadSafeSupabaseConfig() {
      const saved = this.readSecureStorage(this.keys.supabaseConfig, 'SUPABASE_CFG', null);
      if (saved && saved.url && saved.key) {
        return { url: saved.url, anonKey: saved.key };
      }
      try {
        const rawFallback = localStorage.getItem(this.keys.supabaseConfig);
        if (rawFallback) {
          const parsed = JSON.parse(rawFallback);
          if (parsed && parsed.url && (parsed.key || parsed.anonKey)) {
            return { url: parsed.url, anonKey: parsed.key || parsed.anonKey };
          }
        }
      } catch (_) {}
      return null;
    },

    setAdminUnlocked(unlocked) {
      try {
        if (unlocked) {
          localStorage.setItem(this.keys.adminSession, '1');
        } else {
          localStorage.removeItem(this.keys.adminSession);
        }
      } catch (_) {}
      this.syncAdminUiVisibility();
    },

    isAdminUnlocked() {
      try {
        const activeCode = String(localStorage.getItem(this.keys.activeTenant) || '').trim().toUpperCase();
        const flag = localStorage.getItem(this.keys.adminSession) === '1';
        const authFlag = sessionStorage.getItem('aramky_admin_auth') === '1';
        return Boolean(flag || authFlag || activeCode === 'ARAMKY-01' || activeCode === 'ADMIN');
      } catch (_) {
        return false;
      }
    },

    syncAdminUiVisibility() {
      const btnContainer = document.getElementById('admin-btn-container');
      if (btnContainer) {
        if (this.isAdminUnlocked()) {
          btnContainer.classList.remove('hidden');
        } else {
          btnContainer.classList.add('hidden');
        }
      }
    },

    /* ==========================================
       🖼️ محرك الصور الموحد داخل aramky-core.js
       ========================================== */
    getFallbackImage(variant = 'logo') {
      return variant === 'crown' ? FALLBACK_BRAND_SVG : FALLBACK_LOGO_SVG;
    },

    applyImageFallback(imgEl, variant = 'logo') {
      if (!imgEl) return;
      const nextSrc = imgEl.getAttribute('data-next-src');
      if (nextSrc) {
        imgEl.removeAttribute('data-next-src');
        imgEl.src = nextSrc;
        return;
      }
      if (imgEl.dataset.aramkyFallbackApplied === '1') return;
      imgEl.dataset.aramkyFallbackApplied = '1';
      imgEl.onerror = null;
      imgEl.src = this.getFallbackImage(variant);
    },

    compressImageFile(file, options = {}) {
      const maxWidth = options.maxWidth || 1024;
      const maxHeight = options.maxHeight || 1024;
      const quality = typeof options.quality === 'number' ? options.quality : 0.78;
      const mimeType = options.mimeType || 'image/jpeg';

      return new Promise((resolve) => {
        if (!file) return resolve(null);
        const reader = new FileReader();
        reader.onload = () => {
          const rawDataUrl = reader.result;
          if (!rawDataUrl || typeof document === 'undefined') return resolve(rawDataUrl || null);

          const img = new Image();
          img.onload = () => {
            try {
              let { width, height } = img;
              if (width > maxWidth || height > maxHeight) {
                const ratio = Math.min(maxWidth / width, maxHeight / height);
                width = Math.max(1, Math.round(width * ratio));
                height = Math.max(1, Math.round(height * ratio));
              }
              const canvas = document.createElement('canvas');
              canvas.width = width;
              canvas.height = height;
              const ctx = canvas.getContext('2d');
              if (!ctx) return resolve(rawDataUrl);
              ctx.drawImage(img, 0, 0, width, height);
              const compressed = canvas.toDataURL(mimeType, quality);
              resolve(compressed || rawDataUrl);
            } catch (_) {
% !important;
            margin: 0 auto !important;
            background: #ffffff !important;
            color: #000000 !important;
            box-shadow: none !important;
          }
          .no-print { display: none !important; }
        }
      `;
      window.print();
    },

    isAndroidApkEnvironment() {
      const ua = navigator.userAgent || '';
      return /wv|Android.*Version\/[\d.]+/i.test(ua) || window.matchMedia('(display-mode: standalone)').matches;
    }
  };

  global.ARAMKY_CORE = ARAMKY_CORE;
  document.addEventListener('DOMContentLoaded', () => {
    ARAMKY_CORE.syncAdminUiVisibility();
  });
})(window);
        
