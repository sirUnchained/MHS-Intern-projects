window.Mana = window.Mana || {};

Mana.tickets = {
    load: async function () {
        const body = Mana.$('#ticketsBody');
        body.innerHTML = `<tr><td colspan="7" class="empty-state"><i class="fas fa-spinner fa-spin"></i>در حال بارگذاری...</td></tr>`;
        try {
            const tickets = await Mana.apiFetch('/admin/tickets');
            if (!Array.isArray(tickets) || tickets.length === 0) {
                body.innerHTML = `<tr><td colspan="7" class="empty-state">هیچ تیکتی وجود ندارد.</td></tr>`;
                return;
            }
            body.innerHTML = '';
            tickets.forEach((t, idx) => {
                const tr = document.createElement('tr');
                const date = t.created_at ? new Date(t.created_at).toLocaleString('fa-IR') : '—';
                tr.innerHTML = `
                    <td>${t.id ?? idx + 1}</td>
                    <td>${t.topic || '—'}</td>
                    <td>${t.building_name || '—'}</td>
                    <td dir="ltr" style="text-align:left;">${t.building_phone || '—'}</td>
                    <td>${t.user_id || '—'}</td>
                    <td>${date}</td>
                    <td><button class="btn-danger-sm" data-id="${t.id}"><i class="fas fa-trash-alt"></i> حذف</button></td>
                `;
                body.appendChild(tr);
            });
            body.querySelectorAll('.btn-danger-sm').forEach(btn => {
                btn.addEventListener('click', () => {
                    if (confirm('این تیکت برای همیشه حذف شود؟')) Mana.tickets.delete(btn.dataset.id);
                });
            });
        } catch (err) {
            body.innerHTML = `<tr><td colspan="7" class="empty-state" style="color:var(--red);">خطا: ${err.message}</td></tr>`;
        }
    },

    delete: async function (id) {
        Mana.showSpinner(true);
        try {
            await Mana.apiFetch(`/admin/tickets/${id}`, { method: 'GET' });
            Mana.showToast('تیکت حذف شد.', 'success');
            Mana.tickets.load();
        } catch (err) {
            Mana.showToast('خطا در حذف تیکت: ' + err.message, 'error');
        } finally { Mana.showSpinner(false); }
    }
};