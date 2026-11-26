const CACHE_NAME = "aramky-gold-os-v28-3";
const ASSETS = [
  "/",
  "/index.html",
  "/admin.html",
  "/admin_3.html",
  "/manifest.json",
  "/aramky-i18n.js",
  "/aramky-core.js",
  "/icon.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        ASSETS.map((url) =>
          fetch(url, { cache: "no-store" }).then((res) => {
            if (res && res.ok) return cache.put(url, res);
          })
        )
      );
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  // نجلب من السيرفر أولاً حتى نضمن أحدث نسخة، وإذا ماكو إنترنت نرجع للكاش
  event.respondWith(
    fetch(event.request, { cache: "no-store" })
      .then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(event.request, copy));
        }
        return res;
      })
      .catch(() => caches.match(event.request))
  );
});
