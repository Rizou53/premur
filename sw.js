// Cache hors ligne de l'app Prémur.
// Changer CACHE en v2, v3… force la mise à jour après une modification de index.html.
const CACHE = "premur-v1";
const FICHIERS = ["./", "./index.html"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(noms => Promise.all(noms.filter(n => n !== CACHE).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

// Réseau d'abord quand il y en a, cache sinon : l'app s'ouvre toujours, connectée ou non.
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request)
      .then(rep => {
        const copie = rep.clone();
        caches.open(CACHE).then(c => c.put(e.request, copie));
        return rep;
      })
      .catch(() => caches.match(e.request).then(r => r || caches.match("./index.html")))
  );
});
