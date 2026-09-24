// Ba Nghin Tu - service worker: luu toan bo app de chay offline
const VERSION = 'bnt-333c8acf22';
const ASSETS = [
"./",
"index.html",
"manifest.webmanifest",
"icons/apple-touch-icon.png",
"icons/icon-192.png",
"icons/icon-512.png",
"icons/maskable-192.png",
"icons/maskable-512.png",
"img/t01.jpg",
"img/t02.jpg",
"img/t03.jpg",
"img/t04.jpg",
"img/t05.jpg",
"img/t06.jpg",
"img/t07.jpg",
"img/t08.jpg",
"img/t09.jpg",
"img/t10.jpg",
"img/t11.jpg",
"img/t12.jpg",
"img/t13.jpg",
"img/t14.jpg",
"img/t15.jpg",
"img/t16.jpg",
"img/t17.jpg",
"img/t18.jpg",
"img/t25.jpg",
"img/t30.jpg",
"img/t31.jpg",
"img/t32.jpg",
"img/t33.jpg",
"img/t34.jpg",
"img/t36.jpg",
"img/t37.jpg",
"img/t38.jpg",
"img/t39.jpg",
"img/t40.jpg"
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res && res.status === 200 && res.type === 'basic') {
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match('index.html')))
  );
});
