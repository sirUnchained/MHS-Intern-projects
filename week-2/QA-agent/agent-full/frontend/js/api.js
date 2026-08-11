window.Mana = window.Mana || {};

Mana.apiFetch = async function (endpoint, options = {}) {
    const url = `${Mana.BASE_URL}${endpoint}`;
    const headers = { 'Accept': 'application/json', ...(options.headers || {}) };
    const token = localStorage.getItem('token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (options.body && !(options.body instanceof FormData) && !options._form) {
        headers['Content-Type'] = 'application/json';
    }
    const resp = await fetch(url, { ...options, headers });
    const ct = resp.headers.get('content-type') || '';
    const data = ct.includes('application/json') ? await resp.json() : await resp.text();
    if (!resp.ok) {
        const msg = typeof data === 'object' && data?.detail ? data.detail : (data || 'خطا در ارتباط با سرور');
        throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
    return data;
};