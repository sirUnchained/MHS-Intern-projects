window.Mana = window.Mana || {};

Mana.auth = {
    updateUI: function () {
        const isAdmin = Mana.currentUser?.role === 'admin';
        Mana.$$('.admin-only').forEach(el => el.classList.toggle('hidden', !isAdmin));
        if (Mana.currentUser) {
            Mana.$('#authButtons').classList.add('hidden');
            Mana.$('#userBadge').classList.remove('hidden');
            Mana.$('#userNameDisplay').textContent = Mana.currentUser.username;
            Mana.$('#userRoleDisplay').textContent = Mana.currentUser.role;
            Mana.$('#userAvatar').textContent = Mana.currentUser.username.charAt(0).toUpperCase();
            Mana.$('#assetsAuthNotice').classList.add('hidden');
        } else {
            Mana.$('#authButtons').classList.remove('hidden');
            Mana.$('#userBadge').classList.add('hidden');
            Mana.$('#assetsAuthNotice').classList.remove('hidden');
            const active = Mana.$('.page.active');
            if (active && ['tickets', 'admin', 'chat'].includes(active.id.replace('page-', ''))) {
                Mana.navigateTo('dashboard');
            }
        }
    },

    loginHandler: async function (e) {
        e.preventDefault();
        const username = Mana.$('#loginUsername').value.trim();
        const password = Mana.$('#loginPassword').value.trim();
        if (!username || !password) { Mana.showToast('لطفاً همه فیلدها را پر کنید.', 'error'); return; }
        Mana.showSpinner(true);
        try {
            const params = new URLSearchParams({ username, password });
            const data = await Mana.apiFetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params, _form: true,
            });
            localStorage.setItem('token', data.access_token);
            const claims = Mana.decodeJwt(data.access_token) || {};
            Mana.currentUser = { username: claims.sub || username, role: claims.role || 'user' };
            Mana.auth.updateUI();
            Mana.showToast(`خوش آمدید ${Mana.currentUser.username}!`, 'success');
            Mana.navigateTo('dashboard');
            e.target.reset();
        } catch (err) {
            Mana.showToast(err.message || 'ورود ناموفق بود.', 'error');
        } finally { Mana.showSpinner(false); }
    },

    signupHandler: async function (e) {
        e.preventDefault();
        const username = Mana.$('#signupUsername').value.trim();
        const password = Mana.$('#signupPassword').value.trim();
        if (!username || !password) { Mana.showToast('لطفاً همه فیلدها را پر کنید.', 'error'); return; }
        Mana.showSpinner(true);
        try {
            const user = await Mana.apiFetch('/auth/signup', { method: 'POST', body: JSON.stringify({ username, password }) });
            Mana.showToast(`ثبت‌نام موفق (نقش: ${user.role}). حالا وارد شوید.`, 'success');
            e.target.reset();
            Mana.navigateTo('login');
        } catch (err) {
            Mana.showToast(err.message || 'ثبت‌نام ناموفق بود.', 'error');
        } finally { Mana.showSpinner(false); }
    },

    logout: function () {
        localStorage.removeItem('token');
        Mana.currentUser = null;
        Mana.chat.disconnectWebSocket();
        Mana.auth.updateUI();
        Mana.showToast('شما خارج شدید.', 'info');
        Mana.navigateTo('dashboard');
    }
};