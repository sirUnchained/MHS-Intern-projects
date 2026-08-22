window.Mana = window.Mana || {};

// Global state
Mana.currentUser = null;

Mana.pages = {
    dashboard: Mana.$('#page-dashboard'),
    login: Mana.$('#page-login'),
    signup: Mana.$('#page-signup'),
    tickets: Mana.$('#page-tickets'),
    admin: Mana.$('#page-admin'),
    chat: Mana.$('#page-chat'),
};

Mana.navigateTo = function (pageId) {
    Object.values(Mana.pages).forEach(p => p.classList.remove('active'));
    if (Mana.pages[pageId]) Mana.pages[pageId].classList.add('active');
    Mana.$$('.nav-link[data-page]').forEach(l => l.classList.toggle('active', l.dataset.page === pageId));

    if (pageId === 'tickets' && Mana.currentUser?.role === 'admin') Mana.tickets.load();
    if (pageId === 'dashboard') Mana.dashboard.loadAssets();
    if (pageId === 'chat' && Mana.currentUser) Mana.chat.loadThreads();
};

// Event delegation for navigation links (including data-page attributes in navbar, footer etc.)
document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-page]');
    if (!link) return;
    e.preventDefault();
    const page = link.dataset.page;
    if ((page === 'tickets' || page === 'admin') && Mana.currentUser?.role !== 'admin') {
        Mana.showToast('این بخش فقط برای ادمین در دسترس است.', 'error');
        return;
    }
    if (page === 'chat' && !Mana.currentUser) {
        Mana.showToast('لطفاً ابتدا وارد شوید.', 'error');
        Mana.navigateTo('login');
        return;
    }
    if ((page === 'login' || page === 'signup') && Mana.currentUser) {
        Mana.showToast('شما قبلاً وارد شده‌اید.', 'info');
        return;
    }
    Mana.navigateTo(page);
});

// Event listeners for static elements
Mana.$('#loginForm').addEventListener('submit', Mana.auth.loginHandler);
Mana.$('#signupForm').addEventListener('submit', Mana.auth.signupHandler);
Mana.$('#logoutBtn').addEventListener('click', Mana.auth.logout);
Mana.$('#refreshAssetsBtn').addEventListener('click', Mana.dashboard.loadAssets);
Mana.$('#refreshTicketsBtn').addEventListener('click', Mana.tickets.load);
Mana.$('#createThreadBtn').addEventListener('click', Mana.chat.createNewThread);
Mana.$('#newThreadTitle').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') Mana.chat.createNewThread();
});
Mana.$('#chatSendBtn').addEventListener('click', Mana.chat.sendChatMessage);
Mana.$('#chatInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') Mana.chat.sendChatMessage();
});

// Initialise upload functionality when admin page is visited (call once)
Mana.admin.initUpload();

// App init
Mana.init = function () {
    // Configure marked
    marked.setOptions({
        gfm: true,
        tables: true,
        breaks: false,
        pedantic: false,
        sanitize: false,
        smartLists: true,
        smartypants: false
    });

    const token = localStorage.getItem('token');
    if (token) {
        const claims = Mana.decodeJwt(token);
        if (claims?.sub) {
            Mana.currentUser = { username: claims.sub, role: claims.role || 'user' };
        } else {
            localStorage.removeItem('token');
        }
    }

    Mana.auth.updateUI();
    Mana.navigateTo('dashboard');
    Mana.dashboard.loadAssets();
    setInterval(Mana.dashboard.loadAssets, 60000);
};

document.addEventListener('DOMContentLoaded', Mana.init);