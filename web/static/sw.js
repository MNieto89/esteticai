// Esteticai Service Worker v2
const CACHE_NAME = 'esteticai-v2';
const STATIC_ASSETS = [
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/favicon.svg',
    '/static/og-image.svg',
    '/static/manifest.json',
    '/static/offline.html'
];

// Install: pre-cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch: cache-first for static assets, network-first for everything else
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Static assets: cache-first
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                if (cached) return cached;
                return fetch(event.request).then((response) => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // API and pages: network-first, no cache
    if (url.pathname.startsWith('/api/') || event.request.method !== 'GET') {
        return;
    }

    // HTML pages: network-first with offline fallback page
    event.respondWith(
        fetch(event.request).catch(() =>
            caches.match(event.request).then((cached) =>
                cached || caches.match('/static/offline.html')
            )
        )
    );
});
