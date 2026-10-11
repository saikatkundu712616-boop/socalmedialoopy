// static/js/like.js
document.addEventListener('DOMContentLoaded', () => {

    function getCookie(name) {
        const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return m ? m.pop() : '';
    }

    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();

            if (btn.disabled) return;
            btn.disabled = true;

            const url = btn.dataset.url;
            const countEl = btn.querySelector('.likes-count');

            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin',
                });

                if (res.status === 403) {
                    console.error('CSRF error. Refresh the page.');
                    alert('Session expired. Please refresh the page.');
                    return;
                }
                if (!res.ok) {
                    console.error('Server returned', res.status);
                    return;
                }

                const data = await res.json();
                btn.classList.toggle('liked', data.liked);
                if (countEl) countEl.textContent = data.likes_count;

            } catch (err) {
                console.error('Like failed:', err);
            } finally {
                btn.disabled = false;
            }
        });
    });
});