// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity .4s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 400);
        }, 4000);
    });
});

// Accessible mobile navigation toggle.
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('#primary-navigation');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', () => {
        const expanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!expanded));
        nav.classList.toggle('is-open', !expanded);
    });
});


// Refresh the unread-notification badge for signed-in users.
document.addEventListener('DOMContentLoaded', async () => {
    const badge = document.querySelector('#notif-badge');
    if (!badge) return;
    try {
        const response = await fetch('/core/notifications/count/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        });
        if (!response.ok) return;
        const data = await response.json();
        const count = Number(data.count || 0);
        badge.textContent = count > 99 ? '99+' : String(count);
        badge.hidden = count < 1;
        const link = badge.closest('a');
        if (link) link.setAttribute('aria-label', count ? `Notifications, ${count} unread` : 'Notifications');
    } catch (_) { /* Keep navigation usable if the badge endpoint is unavailable. */ }
});
