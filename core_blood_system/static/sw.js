// Service Worker for Blood Management System PWA
const CACHE_NAME = 'blood-bank-v1.0.0';
const urlsToCache = [
  '/',
  '/static/css/design-system.css',
  '/static/css/print-styles.css',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
];

// Install event - cache resources
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.log('[Service Worker] Cache failed:', err))
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        // Clone the request
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(response => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });

          return response;
        }).catch(error => {
          console.log('[Service Worker] Fetch failed:', error);
          // Return offline page if available
          return caches.match('/offline.html');
        });
      })
  );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('[Service Worker] Background sync:', event.tag);
  if (event.tag === 'sync-blood-requests') {
    event.waitUntil(syncBloodRequests());
  }
});

// Push notifications
self.addEventListener('push', event => {
  console.log('[Service Worker] Push received');
  const data = event.data ? event.data.json() : {};
  
  const title = data.title || 'Blood Management System';
  const options = {
    body: data.body || 'New notification',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/badge-72.png',
    vibrate: [200, 100, 200],
    data: data.url || '/',
    actions: [
      {
        action: 'open',
        title: 'View',
        icon: '/static/icons/check.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/close.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification clicked');
  event.notification.close();

  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow(event.notification.data)
    );
  }
});

// Helper function for syncing blood requests
async function syncBloodRequests() {
  try {
    // Get pending requests from IndexedDB
    // Send to server
    console.log('[Service Worker] Syncing blood requests...');
    // Implementation here
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error);
  }
}
