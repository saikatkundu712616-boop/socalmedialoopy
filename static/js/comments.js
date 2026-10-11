// static/js/comments.js
document.addEventListener('DOMContentLoaded', () => {

    function getCookie(name) {
        const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return m ? m.pop() : '';
    }

    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const input = form.querySelector('input[name="content"]');
            const content = input.value.trim();
            if (!content) return;

            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            try {
                const res = await fetch(form.dataset.url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: new URLSearchParams({ content }),
                    credentials: 'same-origin',
                });

                if (res.status === 403) {
                    alert('Session expired. Please refresh.');
                    return;
                }

                const data = await res.json();
                if (!res.ok) {
                    alert(data.error || 'Could not post comment.');
                    return;
                }

                const card = form.closest('.post-card');
                const list = card.querySelector('.comments-list');

                // Remove placeholder
                const placeholder = list.querySelector('.no-comments');
                if (placeholder) placeholder.remove();

                // Append new comment
                const li = document.createElement('li');
                li.innerHTML = `
                    <a href="/accounts/profile/${data.author}/" class="comment-author">${data.author}</a>
                    <span class="comment-text">${data.content}</span>
                `;
                list.appendChild(li);

                input.value = '';
            } catch (err) {
                console.error('Comment failed:', err);
            } finally {
                submitBtn.disabled = false;
            }
        });
    });
});