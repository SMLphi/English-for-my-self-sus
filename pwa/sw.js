// Ba Nghin Tu - service worker: luu toan bo app de chay offline
const VERSION = 'bnt-3db1d5b3bd';
const ASSETS = [
"./",
"index.html",
"manifest.webmanifest",
"icons/apple-touch-icon.png",
"icons/icon-192.png",
"icons/icon-512.png",
"icons/maskable-192.png",
"icons/maskable-512.png",
"img/t001.jpg",
"img/t002.jpg",
"img/t003.jpg",
"img/t004.jpg",
"img/t005.jpg",
"img/t006.jpg",
"img/t007.jpg",
"img/t008.jpg",
"img/t009.jpg",
"img/t010.jpg",
"img/t011.jpg",
"img/t012.jpg",
"img/t013.jpg",
"img/t014.jpg",
"img/t015.jpg",
"img/t016.jpg",
"img/t017.jpg",
"img/t018.jpg",
"img/t019.jpg",
"img/t020.jpg",
"img/t021.jpg",
"img/t022.jpg",
"img/t023.jpg",
"img/t024.jpg",
"img/t026.jpg",
"img/t027.jpg",
"img/t028.jpg",
"img/t029.jpg",
"img/t030.jpg",
"img/t031.jpg",
"img/t032.jpg",
"img/t033.jpg",
"img/t034.jpg",
"img/t035.jpg",
"img/t036.jpg",
"img/t037.jpg",
"img/t038.jpg",
"img/t039.jpg",
"img/t040.jpg",
"img/t041.jpg",
"img/t042.jpg",
"img/t043.jpg",
"img/t044.jpg",
"img/t045.jpg",
"img/t047.jpg",
"img/t048.jpg",
"img/t049.jpg",
"img/t054.jpg",
"img/t055.jpg",
"img/t056.jpg",
"img/t061.jpg",
"img/t070.jpg",
"img/t071.jpg",
"img/t072.jpg",
"img/t078.jpg",
"img/t082.jpg",
"img/t090.jpg",
"img/t091.jpg",
"img/t092.jpg",
"img/t093.jpg",
"img/t094.jpg",
"img/t095.jpg",
"img/t096.jpg",
"img/t097.jpg",
"img/t098.jpg",
"img/t099.jpg",
"img/t103.jpg",
"img/t104.jpg",
"img/t105.jpg",
"img/t106.jpg",
"img/t111.jpg",
"img/t112.jpg",
"img/t113.jpg",
"img/t114.jpg",
"img/t115.jpg",
"img/t116.jpg",
"img/t117.jpg",
"img/t118.jpg",
"img/t119.jpg",
"img/t124.jpg",
"img/t126.jpg",
"img/t127.jpg",
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
