document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    const links  = document.getElementById('primary-navigation');

    if (toggle && links) {
        toggle.addEventListener('click', () => {
            const open = links.classList.toggle('open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        document.querySelectorAll('.nav-user[open]').forEach(d => {
            if (!d.contains(e.target)) d.removeAttribute('open');
        });
    });
});