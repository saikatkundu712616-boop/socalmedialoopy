// static/js/follow.js
document.addEventListener('DOMContentLoaded', () => {

    function getCookie(name) {
        const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return m ? m.pop() : '';
    }

    // Target ANY element with class="follow-btn" (not #follow-btn)
    document.querySelectorAll('.follow-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();

            if (btn.disabled) return;
            btn.disabled = true;

            const originalText = btn.textContent.trim();

            try {
                const res = await fetch(btn.dataset.url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin',
                });

                if (!res.ok) {
                    console.error('Follow failed:', res.status);
                    return;
                }

                const data = await res.json();

                // Update button text + class
                btn.textContent = data.following ? 'Unfollow' : 'Follow';
                btn.classList.toggle('following', data.following);

                // If we're on the profile page, update the follower counter
                const counter = document.getElementById('followers-count');
                if (counter) counter.textContent = data.followers_count;

            } catch (err) {
                console.error('Follow error:', err);
                btn.textContent = originalText;
            } finally {
                btn.disabled = false;
            }
        });
    });
});