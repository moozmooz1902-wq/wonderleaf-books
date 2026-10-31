/* Service worker for the Walryvo back office.
 *
 * Its only job is notifications. It deliberately does NOT cache anything:
 * a dashboard that shows yesterday's numbers because a service worker
 * served them from a cache is worse than no dashboard, and every number
 * here is live by definition.
 *
 * THE PUSH ARRIVES EMPTY. See web/site/src/lib/push.ts - encrypting a
 * payload would be several hundred lines of cryptography that is wrong
 * until it is exactly right, and it is not needed: this worker is on the
 * shop's own origin and carries the admin cookie, so it can simply ask
 * what happened. The order details never pass through Apple's or Google's
 * push servers; they are only told that this endpoint should wake up.
 */
self.addEventListener('install', (e) => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

self.addEventListener('push', (event) => {
  event.waitUntil(
    (async () => {
      let n = {
        title: 'Walryvo',
        body: 'Something happened — open the back office',
        tag: 'walryvo',
        url: '/admin',
      };
      try {
        const r = await fetch('/api/notify', {
          credentials: 'same-origin',
          cache: 'no-store',
        });
        if (r.ok) {
          const d = await r.json();
          if (d && d.title) n = d;
        }
      } catch (e) {
        /* A push that cannot be described is still worth showing: the
           fallback above sends the owner to the dashboard, which is the
           whole point. Swallowing it entirely would mean an order arrived
           and the phone stayed silent. */
      }
      await self.registration.showNotification(n.title, {
        body: n.body,
        tag: n.tag,
        renotify: true,
        requireInteraction: false,
        icon: '/admin-icon-192.png',
        badge: '/admin-icon-192.png',
        data: { url: n.url || '/admin' },
      });
    })()
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/admin';
  event.waitUntil(
    (async () => {
      const all = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true,
      });
      for (const c of all) {
        if (c.url.includes('/admin') && 'focus' in c) {
          await c.focus();
          if ('navigate' in c) await c.navigate(url).catch(() => {});
          return;
        }
      }
      if (self.clients.openWindow) await self.clients.openWindow(url);
    })()
  );
});
