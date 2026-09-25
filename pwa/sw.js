// Ba Nghin Tu - service worker: luu toan bo app de chay offline
const VERSION = 'bnt-86a3cf3a11';
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
"img/t40.jpg",
"fonts.css",
"fonts/-F63fjptAgt5VM-kVkqdyU8n1i8q1w-d196e8.woff2",
"fonts/-F63fjptAgt5VM-kVkqdyU8n1iAq129k-d41ec0.woff2",
"fonts/-F63fjptAgt5VM-kVkqdyU8n1iEq129k-7f25d9.woff2",
"fonts/-F6qfjptAgt5VM-kVkqdyU8n3twJwl5FgtIU-b42080.woff2",
"fonts/-F6qfjptAgt5VM-kVkqdyU8n3twJwl9FgtIU-0bd1c2.woff2",
"fonts/-F6qfjptAgt5VM-kVkqdyU8n3twJwlBFgg-a7544c.woff2",
"fonts/3y9K6as8bTXq_nANBjzKo3IeZx8z6up5BeSl9D4dj_x9PpZBMlGGInHEVA-a4fe79.woff2",
"fonts/3y9K6as8bTXq_nANBjzKo3IeZx8z6up5BeSl9D4dj_x9PpZBMlGHInHEVA-25c61c.woff2",
"fonts/3y9K6as8bTXq_nANBjzKo3IeZx8z6up5BeSl9D4dj_x9PpZBMlGIInE-a97232.woff2",
"fonts/nwpDtKy2OAdR1K-IwhWudF-R3woAa8opPOrG97lwqLlOxCYSmrfB-32b28d.woff2",
"fonts/nwpDtKy2OAdR1K-IwhWudF-R3woAa8opPOrG97lwqLlOxCcSmrfB-44588f.woff2",
"fonts/nwpDtKy2OAdR1K-IwhWudF-R3woAa8opPOrG97lwqLlOxCkSmg-abd974.woff2",
"fonts/nwpStKy2OAdR1K-IwhWudF-R3w8aZQ-29afb6.woff2",
"fonts/nwpStKy2OAdR1K-IwhWudF-R3wAaZfrc-17cf42.woff2",
"fonts/nwpStKy2OAdR1K-IwhWudF-R3wEaZfrc-e951ce.woff2"
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
