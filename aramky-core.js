function normalizePhone(phone) {
  return String(phone || '').replace(/\D+/g, '').replace(/^00/, '').replace(/^964/, '0');
}

function getTenantsRegistry() {
  return readSecureStorage(KEYS.tenantsRegistry, 'TENANTS_REGISTRY', []);
}

function saveTenantsRegistry(list) {
  return writeSecureStorage(KEYS.tenantsRegistry, Array.isArray(list) ? list : [], 'TENANTS_REGISTRY');
}

function isSubscriberApproved(code) {
  const clean = String(code || '').trim().toUpperCase();
  if (!clean) return false;
  const reg = getTenantsRegistry();
  return reg.some(t => String(t.code || '').trim().toUpperCase() === clean);
}

function authenticateSubscriber(code, phone, password) {
  const cleanCode = String(code || '').trim().toUpperCase();
  const cleanPhone = normalizePhone(phone);
  const cleanPass = String(password || '').trim();
  const reg = getTenantsRegistry();
  const found = reg.find(t => {
    const tCode = String(t.code || '').trim().toUpperCase();
    const tPhone = normalizePhone(t.phone || '');
    const tPass = String(t.password || '').trim();
    return tCode === cleanCode && tPhone && tPhone === cleanPhone && tPass && tPass === cleanPass;
  });
  if (!found) {
    return { ok: false, message: 'الكود أو رقم الهاتف أو كلمة المرور غير صحيحة أو الحساب غير مضاف من الأدمن' };
  }
  return { ok: true, tenant: found };
}

function isSubscriptionExpired(tenantObj) {
  if (!tenantObj) return false;
  if (String(tenantObj.status || '').trim() === 'متوقف') return true;
  if (tenantObj.expiresAt) {
    const exp = new Date(tenantObj.expiresAt).getTime();
    if (!isNaN(exp) && Date.now() > exp) return true;
  }
  return false;
}

function normalizeTenantPayload(raw, code) {
  const base = {
    code: String(code || (raw && raw.code) || 'ARAMKY-01').trim().toUpperCase(),
    status: (raw && raw.status) || 'نشط',
    cash: Number((raw && raw.cash) || 0),
    usd: Number((raw && raw.usd) || 0),
    zain: Number((raw && raw.zain) || 0),
    makingProfit: Number((raw && raw.makingProfit) || 0),
    prices: Object.assign({ usd: 150000, m24: 640000, m22: 585000, m21: 560000, m18: 480000, m9: 240000 }, (raw && raw.prices) || {}),
    inventory: Array.isArray(raw && raw.inventory) ? raw.inventory : [],
    debts: Array.isArray(raw && raw.debts) ? raw.debts : [],
    logs: Array.isArray(raw && raw.logs) ? raw.logs : [],
    supportTickets: Array.isArray(raw && raw.supportTickets) ? raw.supportTickets : [],
    store: Object.assign({
      name: 'ARAMKY | أرامكي للحلول الرقمية — فرع نواة الذهب',
      phone: supportPhone,
      address: 'بغداد — سوق الكاظمية',
      openTime: '09:00 صباحاً',
      closeTime: '09:00 مساءً',
      bio: 'نظام إدارة صياغة الذهب والمعرض الرقمي الذكي',
      logo: 'icon.png',
      cover: 'icon.png'
    }, (raw && raw.store) || {}),
    updatedAt: (raw && raw.updatedAt) || new Date().toISOString()
  };
  return base;
}

function mergeArrayById(localArr, remoteArr) {
  const map = new Map();
  (Array.isArray(remoteArr) ? remoteArr : []).forEach((item, i) => {
    const key = item && (item.id || item.code) ? String(item.id || item.code) : `R_${i}`;
    map.set(key, item);
  });
  (Array.isArray(localArr) ? localArr : []).forEach((item, i) => {
    const key = item && (item.id || item.code) ? String(item.id || item.code) : `L_${i}`;
    if (!map.has(key)) {
      map.set(key, item);
    } else {
      const prev = map.get(key);
      const tPrev = prev && prev.updatedAt ? new Date(prev.updatedAt).getTime() : 0;
      const tCurr = item && item.updatedAt ? new Date(item.updatedAt).getTime() : 0;
      map.set(key, tCurr >= tPrev ? item : prev);
    }
  });
  return Array.from(map.values());
}

function mergeTenantStates(localState, remoteState, code) {
  const loc = normalizeTenantPayload(localState || {}, code);
  const rem = normalizeTenantPayload(remoteState || {}, code);
  const tLoc = new Date(loc.updatedAt || 0).getTime() || 0;
  const tRem = new Date(rem.updatedAt || 0).getTime() || 0;
  const newer = tLoc >= tRem ? loc : rem;

  return normalizeTenantPayload({
    ...newer,
    status: rem.status || loc.status,
    cash: newer.cash,
    usd: newer.usd,
    zain: newer.zain,
    makingProfit: newer.makingProfit,
    prices: Object.assign({}, rem.prices, loc.prices),
    store: Object.assign({}, rem.store, loc.store),
    inventory: mergeArrayById(loc.inventory, rem.inventory),
    debts: mergeArrayById(loc.debts, rem.debts),
    logs: mergeArrayById(loc.logs, rem.logs),
    supportTickets: mergeArrayById(loc.supportTickets, rem.supportTickets),
    updatedAt: new Date(Math.max(tLoc, tRem, Date.now())).toISOString()
  }, code);
}
