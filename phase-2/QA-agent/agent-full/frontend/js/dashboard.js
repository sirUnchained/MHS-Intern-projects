window.Mana = window.Mana || {};

Mana.dashboard = {
    loadAssets: async function () {
        const container = Mana.$('#assetCards');
        if (!Mana.currentUser) {
            container.innerHTML = `<div class="empty-state" style="grid-column:1/-1;"><i class="fas fa-lock"></i>برای مشاهده وارد شوید.</div>`;
            Mana.dashboard.renderTicker([]);
            return;
        }
        container.innerHTML = `<div class="empty-state" style="grid-column:1/-1;"><i class="fas fa-spinner fa-spin"></i>در حال بارگذاری...</div>`;

        const results = [];
        for (const [key, meta] of Object.entries(Mana.ASSETS)) {
            try {
                const rows = await Mana.apiFetch(`/data/${key}?rows=2`);
                let price = null, change = 0, date = null;
                if (Array.isArray(rows) && rows.length > 0) {
                    const latest = rows[rows.length - 1];
                    const prev = rows.length > 1 ? rows[rows.length - 2] : null;
                    price = latest.adj_close ?? latest.close;
                    date = latest.date;
                    if (prev) {
                        const prevPrice = prev.adj_close ?? prev.close;
                        if (typeof price === 'number' && typeof prevPrice === 'number' && prevPrice !== 0) {
                            change = ((price - prevPrice) / prevPrice) * 100;
                        }
                    }
                }
                results.push({ key, ...meta, price, change, date, error: null });
            } catch (err) {
                results.push({ key, ...meta, price: null, change: 0, date: null, error: err.message });
            }
        }

        container.innerHTML = '';
        results.forEach(item => {
            const div = document.createElement('div');
            div.className = 'card asset-card';
            const changeClass = item.price !== null ? (item.change >= 0 ? 'pos' : 'neg') : '';
            const changeText = item.price !== null ? `${item.change >= 0 ? '+' : ''}${item.change.toFixed(2)}%` : '—';
            const priceText = item.price !== null ? item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '—';
            div.innerHTML = `
                <div class="asset-label"><i class="fas ${item.icon}"></i> ${item.label}</div>
                <div class="asset-price">${priceText}</div>
                <span class="asset-change ${changeClass}">${changeText}</span>
                ${item.date ? `<div class="asset-date">${item.date}</div>` : ''}
                ${item.error ? `<div style="color:var(--red);font-size:0.72rem;margin-top:8px;">${item.error}</div>` : ''}
            `;
            container.appendChild(div);
        });

        Mana.dashboard.renderTicker(results);
    },

    renderTicker: function (results) {
        const track = Mana.$('#tickerTrack');
        if (!results.length) {
            track.innerHTML = `<span class="ticker-item">برای مشاهدهٔ قیمت زنده وارد حساب کاربری شوید</span>`;
            return;
        }
        const itemsHtml = results.map(r => {
            const cls = r.price === null ? '' : (r.change >= 0 ? 'up' : 'down');
            const arrow = r.price === null ? '' : (r.change >= 0 ? '▲' : '▼');
            const priceTxt = r.price !== null ? r.price.toFixed(2) : 'N/A';
            const changeTxt = r.price !== null ? `${arrow} ${Math.abs(r.change).toFixed(2)}%` : '';
            return `<span class="ticker-item">${r.label.toUpperCase()} <b>${priceTxt}</b> <span class="${cls}">${changeTxt}</span></span>`;
        }).join('');
        track.innerHTML = itemsHtml + itemsHtml;
    }
};