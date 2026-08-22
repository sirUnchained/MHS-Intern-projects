window.Mana = window.Mana || {};

Mana.admin = {
    initUpload: function () {
        const uploadArea = Mana.$('#uploadArea');
        const fileInput = Mana.$('#fileInput');
        const selectedFileName = Mana.$('#selectedFileName');

        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', () => {
            selectedFileName.textContent = fileInput.files.length ? fileInput.files[0].name : 'هیچ فایلی انتخاب نشده (فقط txt/md)';
        });
        ['dragover'].forEach(ev => uploadArea.addEventListener(ev, (e) => { e.preventDefault(); uploadArea.classList.add('drag'); }));
        ['dragleave', 'drop'].forEach(ev => uploadArea.addEventListener(ev, () => uploadArea.classList.remove('drag')));
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                selectedFileName.textContent = fileInput.files[0].name;
            }
        });

        Mana.$('#uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) { Mana.showToast('لطفاً یک فایل انتخاب کنید.', 'error'); return; }
            const name = fileInput.files[0].name.toLowerCase();
            if (!name.endsWith('.txt') && !name.endsWith('.md')) {
                Mana.showToast('فقط فایل‌های .txt و .md پذیرفته می‌شوند.', 'error');
                return;
            }
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            Mana.showSpinner(true);
            try {
                const res = await Mana.apiFetch('/admin/upload-file', { method: 'POST', body: formData });
                Mana.showToast(`فایل آپلود شد — ${res.chunks_stored} بخش ذخیره شد.`, 'success');
                fileInput.value = '';
                selectedFileName.textContent = 'هیچ فایلی انتخاب نشده (فقط txt/md)';
            } catch (err) {
                Mana.showToast('آپلود ناموفق بود: ' + err.message, 'error');
            } finally { Mana.showSpinner(false); }
        });
    }
};