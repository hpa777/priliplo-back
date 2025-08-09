// Register event listener for the 'push' event.
self.addEventListener('push', function (event) {
    const eventInfo = event.data.text();
    const data = JSON.parse(eventInfo);
    const head = data.head || 'New Notification';
    const body = data.body || 'This is default content. Your notification didn\'t have one';

    // Keep the service worker alive until the notification is created.
    event.waitUntil(
        self.registration.showNotification(head, {
            body: body,
            icon: 'https://lk.priliplo.ru/static/metronic/html/theme/demo1/dist/assets/media/logos/logo-1-dark.png'
        })
    );
});