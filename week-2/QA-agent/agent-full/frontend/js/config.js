window.Mana = window.Mana || {};

(function () {
    const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);

    const PROD_BASE_URL = 'https://mhs-intern-projects.onrender.com';
    const LOCAL_BASE_URL = 'http://127.0.0.1:8000';

    Mana.BASE_URL = isLocal ? LOCAL_BASE_URL : PROD_BASE_URL;
    Mana.WS_URL = Mana.BASE_URL.replace(/^http/, 'ws') + '/chat/ws/chat';
})();


Mana.ASSETS = {
    gold: { label: 'طلای جهانی', icon: 'fa-coins' },
    dxy: { label: 'شاخص دلار', icon: 'fa-dollar-sign' },
    silver: { label: 'نقره', icon: 'fa-gem' },
    oil: { label: 'نفت WTI', icon: 'fa-oil-can' },
    sp500: { label: 'S&P 500', icon: 'fa-chart-bar' }
};