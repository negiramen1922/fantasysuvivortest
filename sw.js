/* 勇者サバイバー Service Worker
   目的：強制リロード／ネット不調・オフラインでも即ロードできるようにする（インストール型PWA対応）。
   方針：HTML はネット優先（更新を確実に反映）＋オフライン時キャッシュ。静的アセットはキャッシュ優先。
   別オリジン（Firebase・Google Fonts・GA）は素通し（触らない）。 */
var CACHE = 'yusha-v1';
var CORE = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-180.png'];

self.addEventListener('install', function (e) {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE).catch(function () {}); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (ks) {
      return Promise.all(ks.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== location.origin) return;   // 別オリジンは素通し（SWで触らない）

  var isDoc = req.mode === 'navigate' || url.pathname === '/' || url.pathname.charAt(url.pathname.length - 1) === '/' || /index\.html$/.test(url.pathname);
  if (isDoc) {
    // HTML：ネット優先（更新反映）→ 失敗時キャッシュ（オフライン）
    e.respondWith(
      fetch(req).then(function (r) {
        var cp = r.clone(); caches.open(CACHE).then(function (c) { c.put(req, cp); });
        return r;
      }).catch(function () {
        return caches.match(req).then(function (m) { return m || caches.match('./index.html'); });
      })
    );
    return;
  }
  // 静的アセット（アイコン・スプライト等）：キャッシュ優先
  e.respondWith(
    caches.match(req).then(function (m) {
      return m || fetch(req).then(function (r) {
        if (r && r.ok) { var cp = r.clone(); caches.open(CACHE).then(function (c) { c.put(req, cp); }); }
        return r;
      }).catch(function () { return m; });
    })
  );
});
