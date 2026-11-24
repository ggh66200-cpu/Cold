/* ARAMKY Gold OS - Core Bridge (aramky-core.js) */
(function (global) {
  'use strict';

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
      supportTickets: 'aramky_global_support_tickets',
      supabaseConfig: 'aramky_supabase_config',
      adminSession: 'aramky_admin_unlocked'
    },

    getTenantDataKey(code) {
      const clean = String(code || 'ARAMKY-01').trim().toUpperCase();
      return `aramky_gold_data_${clean}`;
    },

    getContactInfo() {
      return {
        supportPhone: this.supportPhone,
        whatsappUrl: this.whatsappUrl,
        masterCardNumber: this.masterCardNumber
      };
    },

    async loadSafeSupabaseConfig() {
      try {
        const saved = localStorage.getItem(this.keys.supabaseConfig);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (parsed && parsed.url && parsed.anonKey) return parsed;
        }
      } catch (_) {}

      try {
        const res = await fetch('/api/supabase-config', { cache: 'no-store' });
        if (res.ok) {
          const data = await res.json();
          if (data && data.url && data.anonKey) return data;
        }
      } catch (_) {}

      try {
        const resJson = await fetch('supabase-config.json', { cache: 'no-store' });
        if (resJson.ok) {
          const data = await resJson.json();
          if (data && data.url && data.anonKey) return data;
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
        return Boolean(flag || activeCode === 'ARAMKY-01' || activeCode === 'ADMIN');
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

    printReceiptOnly(paperWidthMm = 80) {
      const styleId = 'aramky-thermal-print-style';
      let styleEl = document.getElementById(styleId);
      if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = styleId;
        document.head.appendChild(styleEl);
      }
      styleEl.textContent = `
        @media print {
          @page { size: ${paperWidthMm}mm auto; margin: 2mm; }
          body * { visibility: hidden !important; }
          #invoice-modal, #invoice-modal * { visibility: visible !important; }
          #invoice-modal {
            position: fixed !important;
            inset: 0 !important;
            width: ${paperWidthMm}mm !important;
            max-width: 100% !important;
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
