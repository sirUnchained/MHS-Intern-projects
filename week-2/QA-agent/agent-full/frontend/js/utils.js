window.Mana = window.Mana || {};

Mana.$ = (s) => document.querySelector(s);
Mana.$$ = (s) => document.querySelectorAll(s);

Mana.showToast = function (message, type = 'info', duration = 4000) {
    const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle' };
    const el = document.createElement('div');
    el.className = `toast-custom ${type}`;
    el.innerHTML = `<span><i class="fas ${icons[type] || icons.info}"></i></span><span>${message}</span><button class="toast-close">&times;</button>`;
    el.querySelector('.toast-close').addEventListener('click', () => el.remove());
    Mana.$('#toastContainer').prepend(el);
    setTimeout(() => { if (el.parentNode) el.remove(); }, duration);
};

Mana.showSpinner = function (show) {
    Mana.$('#spinnerOverlay').classList.toggle('show', show);
};

Mana.decodeJwt = function (token) {
    try {
        const payload = token.split('.')[1];
        const json = decodeURIComponent(atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
            .split('').map(c => '%' + c.charCodeAt(0).toString(16).padStart(2, '0')).join(''));
        return JSON.parse(json);
    } catch (_) { return null; }
};

Mana.escapeHtml = function (text) {
    return String(text).replace(/[&<>"']/g, function (m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
    });
};

Mana.renderMarkdown = function (text) {
    try { return marked.parse(text); } catch (_) { return text; }
};