(function () {
  const ADMIN_PASS_HASH = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"; // default: 123456 (sha256)
  const SUPPORT_PHONE = "07766083622";
  const MASTER_CARD = "910400201646";
  const PUBLIC_BRAND = "ARAMKY";

  const KEYS = {
    activeTenant: "aramky_active_tenant_code",
    adminSession: "aramky_admin_session_active",
    supportTickets: "aramky_global_support_tickets",
    tenantPrefix: "aramky_tenant_vault_"
  };

  function obfuscateCode(code) {
    const clean = String(code || "ARAMKY-01").trim().toUpperCase();
    try {
      return btoa(unescape(encodeURIComponent(clean))).replace(/=+$/, "");
    } catch (_) {
      return clean;
    }
  }

  function deobfuscateCode(token) {
    if (!token) return "ARAMKY-01";
    try {
      let padded = String(token).trim();
      while (padded.length % 4) padded += "=";
      const decoded = decodeURIComponent(escape(atob(padded)));
      return /^[A-Z0-9_-]{2,32}$/i.test(decoded) ? decoded.toUpperCase() : "ARAMKY-01";
    } catch (_) {
      return "ARAMKY-01";
    }
  }

  function getTenantStorageKey(code) {
    const safe = String(code || "ARAMKY-01").trim().toUpperCase().replace(/[^A-Z0-9_-]/g, "_");
    return `${KEYS.tenantPrefix}${safe}`;
  }

  function readStorage(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (_) {
      return fallback;
    }
  }

  function writeStorage(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_) {
      return false;
    }
  }

  function simpleSha256Fallback(str) {
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return (h >>> 0).toString(16);
  }

  async function hashText(text) {
    const clean = String(text || "");
    if (window.crypto && window.crypto.subtle) {
      const buf = await window.crypto.subtle.digest("SHA-256", new TextEncoder().encode(clean));
      return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
    }
    return simpleSha256Fallback(clean);
  }

  function isAdminSessionActive() {
    return sessionStorage.getItem(KEYS.adminSession) === "1" || localStorage.getItem(KEYS.adminSession) === "1";
  }

  function setAdminSessionActive(active) {
    if (active) {
      sessionStorage.setItem(KEYS.adminSession, "1");
      localStorage.setItem(KEYS.adminSession, "1");
    } else {
      sessionStorage.removeItem(KEYS.adminSession);
      localStorage.removeItem(KEYS.adminSession);
    }
    syncAdminUiVisibility();
  }

  async function verifyAdminPassword(inputPass) {
    const customHash = localStorage.getItem("aramky_admin_pass_hash");
    const targetHash = customHash || ADMIN_PASS_HASH;
    const h = await hashText(inputPass);
    return h === targetHash;
  }

  function syncAdminUiVisibility() {
    const adminBtnWrap = document.getElementById("admin-btn-container");
    if (adminBtnWrap) {
      adminBtnWrap.classList.toggle("hidden", !isAdminSessionActive());
    }
  }

  function applyImageFallback(img) {
    if (!img) return;
    if (!img.dataset.fallbackApplied) {
      img.dataset.fallbackApplied = "1";
      img.onerror = null;
      img.src = "/icon.png";
    }
  }

  function getClientShareUrl(tenantCode) {
    const base = `${window.location.origin}/index.html`;
    return `${base}?client=${encodeURIComponent(obfuscateCode(tenantCode))}`;
  }

  window.ARAMKY_CORE = {
    PUBLIC_BRAND,
    SUPPORT_PHONE,
    MASTER_CARD,
    KEYS,
    obfuscateCode,
    deobfuscateCode,
    getTenantStorageKey,
    readStorage,
    writeStorage,
    isAdminSessionActive,
    setAdminSessionActive,
    verifyAdminPassword,
    syncAdminUiVisibility,
    applyImageFallback,
    getClientShareUrl
  };

  document.addEventListener("DOMContentLoaded", syncAdminUiVisibility);
})();
