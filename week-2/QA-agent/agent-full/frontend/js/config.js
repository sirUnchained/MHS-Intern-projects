window.Mana = window.Mana || {};

Mana.BASE_URL = (window._env_ && window._env_.BASE_URL) || 'http://127.0.0.1:8000';
Mana.WS_URL = (window._env_ && window._env_.WS_URL) || 'ws://127.0.0.1:8000/chat/ws/chat';

Mana.ASSETS = {
    gold: { label: 'طلای جهانی', icon: 'fa-coins' },
    dxy: { label: 'شاخص دلار', icon: 'fa-dollar-sign' },
    silver: { label: 'نقره', icon: 'fa-gem' },
    oil: { label: 'نفت WTI', icon: 'fa-oil-can' },
    sp500: { label: 'S&P 500', icon: 'fa-chart-bar' }
};