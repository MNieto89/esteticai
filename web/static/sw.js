// Esteticai Service Worker v3 — PWA Premium
const CACHE_NAME = 'esteticai-v3';
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

// Fetch: stale-while-revalidate for statics, network-first for pages
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Skip non-GET and API requests
    if (event.request.method !== 'GET' || url.pathname.startsWith('/api/')) {
        return;
    }

    // Google Fonts: cache-first (immutable)
    if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
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

    // Static assets: stale-while-revalidate
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                const fetchPromise = fetch(event.request).then((response) => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                    }
                    return response;
                }).catch(() => cached);

                return cached || fetchPromise;
            })
        );
        return;
    }

    // HTML pages: network-first with offline fallback
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                if (response.ok && url.pathname === '/dashboard') {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return response;
            })
            .catch(() =>
                caches.match(event.request).then((cached) =>
                    cached || caches.match('/static/offline.html')
                )
            )
    );
});
