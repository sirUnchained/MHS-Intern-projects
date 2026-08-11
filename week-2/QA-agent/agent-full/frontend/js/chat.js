window.Mana = window.Mana || {};

Mana.chat = {
    threadsCache: [],
    currentThreadId: null,
    ws: null,
    messageBuffer: {},
    currentThinkingIndicator: null,

    setStatus: function (connected, text) {
        Mana.$('#chatDot').className = `dot ${connected ? 'online' : 'offline'}`;
        Mana.$('#chatStatusText').textContent = text || (connected ? 'آنلاین' : 'قطع');
    },

    loadThreads: async function () {
        const listEl = Mana.$('#threadList');
        listEl.innerHTML = `<div class="empty-state" style="padding:20px 0;"><i class="fas fa-spinner fa-spin"></i> در حال بارگذاری...</div>`;
        try {
            const threads = await Mana.apiFetch('/chat/threads');
            Mana.chat.threadsCache = Array.isArray(threads) ? threads : [];
            Mana.chat.renderThreadList();
        } catch (err) {
            listEl.innerHTML = `<div class="empty-state" style="padding:20px 0; color:var(--red);">خطا: ${err.message}</div>`;
        }
    },

    renderThreadList: function () {
        const listEl = Mana.$('#threadList');
        if (!Mana.chat.threadsCache.length) {
            listEl.innerHTML = `<div class="empty-state" style="padding:20px 0;">هیچ گفتگویی وجود ندارد.</div>`;
            return;
        }
        listEl.innerHTML = '';
        Mana.chat.threadsCache.forEach(thread => {
            const item = document.createElement('div');
            item.className = `thread-item${thread.thread_id === Mana.chat.currentThreadId ? ' active' : ''}`;
            const dateStr = thread.created_at ? new Date(thread.created_at).toLocaleDateString('fa-IR', { month: 'short', day: 'numeric' }) : '';
            item.innerHTML = `
                <span class="thread-title" title="${thread.title || thread.thread_id}">${thread.title || 'بدون عنوان'}</span>
                ${dateStr ? `<span class="thread-date">${dateStr}</span>` : ''}
                <button class="delete-thread-btn" data-thread-id="${thread.thread_id}" title="حذف"><i class="fas fa-trash-alt"></i></button>
            `;
            item.addEventListener('click', (e) => {
                if (e.target.closest('.delete-thread-btn')) return;
                Mana.chat.selectThread(thread.thread_id);
            });
            item.querySelector('.delete-thread-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm(`گفتگو "${thread.title || thread.thread_id}" حذف شود؟`)) {
                    await Mana.chat.deleteThread(thread.thread_id);
                }
            });
            listEl.appendChild(item);
        });
    },

    selectThread: async function (threadId) {
        if (Mana.chat.currentThreadId === threadId) return;
        Mana.chat.disconnectWebSocket();
        Mana.chat.removeThinkingIndicator();
        Mana.$('#chatMessages').innerHTML = `<div class="system-msg">در حال بارگذاری تاریخچه...</div>`;
        Mana.chat.currentThreadId = threadId;
        document.querySelectorAll('.thread-item').forEach(el => el.classList.remove('active'));
        const activeItem = document.querySelector(`.delete-thread-btn[data-thread-id="${threadId}"]`)?.closest('.thread-item');
        if (activeItem) activeItem.classList.add('active');
        const thread = Mana.chat.threadsCache.find(t => t.thread_id === threadId);
        Mana.$('#chatThreadTitle').textContent = thread?.title || threadId;
        Mana.chat.setStatus(false, 'در حال بارگذاری...');

        try {
            const messages = await Mana.apiFetch(`/chat/threads/${threadId}/messages`);
            Mana.$('#chatMessages').innerHTML = '';
            if (messages.length === 0) {
                Mana.$('#chatMessages').innerHTML = `<div class="system-msg">تاریخچه خالی است — پیام جدید بفرستید.</div>`;
            } else {
                messages.forEach(msg => Mana.chat.addHistoryMessage(msg));
            }
        } catch (err) {
            Mana.$('#chatMessages').innerHTML = `<div class="system-msg" style="color:var(--red);">خطا در بارگذاری پیام‌ها: ${err.message}</div>`;
        }

        Mana.chat.connectWebSocket(threadId);
    },

    addHistoryMessage: function (msg) {
        const container = document.createElement('div');
        if (msg.type === 'human') {
            container.className = 'msg self';
            container.innerHTML = `<div>${Mana.escapeHtml(msg.content)}</div>`;
        } else if (msg.type === 'ai') {
            container.className = 'msg other';
            container.innerHTML = `<div class="markdown-body">${Mana.renderMarkdown(msg.content)}</div>`;
            if (msg.id) Mana.chat.addFeedbackButtons(container, msg.id);
        } else if (msg.type === 'tool') {
            container.className = 'tool-call-msg';
            container.innerHTML = `<i class="fas fa-cogs"></i> نتیجه ابزار <span class="tool-detail">${Mana.escapeHtml(msg.content)}</span>`;
        } else {
            container.className = 'system-msg';
            container.textContent = msg.content;
        }
        if (msg.id) container.dataset.msgId = msg.id;
        Mana.$('#chatMessages').appendChild(container);
        Mana.$('#chatMessages').scrollTop = Mana.$('#chatMessages').scrollHeight;
    },

    createNewThread: async function () {
        const titleInput = Mana.$('#newThreadTitle');
        const title = titleInput.value.trim() || undefined;
        Mana.showSpinner(true);
        try {
            const newThread = await Mana.apiFetch('/chat/threads', {
                method: 'POST',
                body: JSON.stringify({ title }),
            });
            Mana.showToast('گفتگوی جدید ساخته شد.', 'success');
            titleInput.value = '';
            await Mana.chat.loadThreads();
            Mana.chat.selectThread(newThread.thread_id);
        } catch (err) {
            Mana.showToast('ساخت گفتگو ناموفق: ' + err.message, 'error');
        } finally { Mana.showSpinner(false); }
    },

    deleteThread: async function (threadId) {
        Mana.showSpinner(true);
        try {
            await Mana.apiFetch(`/chat/threads/${threadId}`, { method: 'DELETE' });
            Mana.showToast('گفتگو حذف شد.', 'success');
            if (Mana.chat.currentThreadId === threadId) {
                Mana.chat.disconnectWebSocket();
                Mana.chat.currentThreadId = null;
                Mana.chat.removeThinkingIndicator();
                Mana.$('#chatMessages').innerHTML = `<div class="system-msg">گفتگویی انتخاب نشده.</div>`;
                Mana.$('#chatThreadTitle').textContent = 'گفتگویی انتخاب نشده';
                Mana.$('#chatInput').disabled = true;
                Mana.$('#chatSendBtn').disabled = true;
                Mana.chat.setStatus(false);
            }
            await Mana.chat.loadThreads();
        } catch (err) {
            Mana.showToast('حذف گفتگو ناموفق: ' + err.message, 'error');
        } finally { Mana.showSpinner(false); }
    },

    connectWebSocket: function (threadId) {
        if (!Mana.currentUser) { Mana.showToast('لطفاً ابتدا وارد شوید.', 'error'); return; }
        const token = localStorage.getItem('token');
        Mana.chat.disconnectWebSocket();
        Mana.chat.currentThreadId = threadId;

        const wsUrl = `${Mana.WS_URL}?token=${encodeURIComponent(token)}&thread_id=${encodeURIComponent(threadId)}`;
        Mana.chat.ws = new WebSocket(wsUrl);

        Mana.chat.ws.onopen = () => {
            Mana.chat.setStatus(true);
            Mana.$('#chatInput').disabled = false;
            Mana.$('#chatSendBtn').disabled = false;
        };

        Mana.chat.ws.onmessage = (event) => {
            let data;
            try { data = JSON.parse(event.data); } catch (_) { data = { message: event.data }; }
            Mana.chat.removeThinkingIndicator();

            switch (data.type) {
                case 'tool_call':
                    Mana.chat.addToolCallMessage(data.name || 'unknown', data.args || {});
                    break;
                case 'token':
                    Mana.chat.bufferMessage('assistant', data.content || '', false, data.message_id || null);
                    break;
                case 'done':
                    Object.keys(Mana.chat.messageBuffer).forEach(key => Mana.chat.flushBuffer(key));
                    break;
                default:
                    break;
            }
        };

        Mana.chat.ws.onclose = () => {
            Mana.chat.setStatus(false);
            Mana.$('#chatInput').disabled = true;
            Mana.$('#chatSendBtn').disabled = true;
            Mana.chat.removeThinkingIndicator();
            Mana.chat.addSystemMessage('اتصال قطع شد.');
        };

        Mana.chat.ws.onerror = () => { };
    },

    disconnectWebSocket: function () {
        if (Mana.chat.ws) { try { Mana.chat.ws.close(); } catch (_) { } Mana.chat.ws = null; }
        Mana.chat.setStatus(false);
        Mana.$('#chatInput').disabled = true;
        Mana.$('#chatSendBtn').disabled = true;
        Object.keys(Mana.chat.messageBuffer).forEach(k => { clearTimeout(Mana.chat.messageBuffer[k].timer); delete Mana.chat.messageBuffer[k]; });
        Mana.chat.removeThinkingIndicator();
    },

    sendChatMessage: function () {
        const text = Mana.$('#chatInput').value.trim();
        if (!text || !Mana.chat.ws || Mana.chat.ws.readyState !== WebSocket.OPEN) {
            Mana.showToast('اتصال به گفتگو برقرار نیست.', 'error');
            return;
        }
        const msgId = `local-${Date.now()}`;
        Mana.chat.addChatMessage(text, Mana.currentUser.username, true, msgId);
        Mana.chat.ws.send(text);
        Mana.$('#chatInput').value = '';
        Mana.$('#chatInput').focus();
        Mana.chat.showThinkingIndicator();
    },

    addChatMessage: function (text, sender, isSelf, msgId = null) {
        const div = document.createElement('div');
        div.className = `msg ${isSelf ? 'self' : 'other'}`;
        if (msgId) div.dataset.msgId = msgId;
        const time = new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });
        const contentDiv = document.createElement('div');
        if (sender === 'assistant' && !isSelf) {
            contentDiv.className = 'markdown-body';
            contentDiv.innerHTML = Mana.renderMarkdown(text);
        } else {
            contentDiv.textContent = text;
        }
        const meta = document.createElement('span');
        meta.className = 'msg-meta';
        meta.textContent = `${sender} • ${time}`;
        div.appendChild(contentDiv);
        div.appendChild(meta);
        Mana.$('#chatMessages').appendChild(div);
        Mana.$('#chatMessages').scrollTop = Mana.$('#chatMessages').scrollHeight;
        return div;
    },

    addSystemMessage: function (text) {
        const div = document.createElement('div');
        div.className = 'system-msg';
        div.textContent = text;
        Mana.$('#chatMessages').appendChild(div);
        Mana.$('#chatMessages').scrollTop = Mana.$('#chatMessages').scrollHeight;
    },

    addToolCallMessage: function (name, args) {
        const div = document.createElement('div');
        div.className = 'tool-call-msg';
        div.innerHTML = `<i class="fas fa-cogs"></i> فراخوانی ابزار: <strong>${name}</strong><span class="tool-detail">${JSON.stringify(args, null, 2)}</span>`;
        Mana.$('#chatMessages').appendChild(div);
        Mana.$('#chatMessages').scrollTop = Mana.$('#chatMessages').scrollHeight;
    },

    bufferMessage: function (sender, text, isSelf, msgId) {
        const key = msgId || sender;
        if (Mana.chat.messageBuffer[key]) {
            const entry = Mana.chat.messageBuffer[key];
            entry.text += text;
            clearTimeout(entry.timer);
            const contentDiv = entry.container?.querySelector('div');
            if (contentDiv) {
                if (sender === 'assistant' && !isSelf) {
                    contentDiv.className = 'markdown-body';
                    contentDiv.innerHTML = Mana.renderMarkdown(entry.text);
                } else {
                    contentDiv.textContent = entry.text;
                }
            }
            entry.timer = setTimeout(() => Mana.chat.flushBuffer(key), 500);
            return;
        }
        const container = Mana.chat.addChatMessage(text, sender, isSelf, msgId);
        Mana.chat.messageBuffer[key] = { text, timer: setTimeout(() => Mana.chat.flushBuffer(key), 500), container, isSelf, sender, msgId };
    },

    flushBuffer: function (key) {
        const entry = Mana.chat.messageBuffer[key];
        if (!entry) return;
        delete Mana.chat.messageBuffer[key];
        const finalText = entry.text.trim();
        if (!finalText || !entry.container) return;
        const contentDiv = entry.container.querySelector('div');
        if (contentDiv) {
            if (entry.sender === 'assistant' && !entry.isSelf) {
                contentDiv.className = 'markdown-body';
                contentDiv.innerHTML = Mana.renderMarkdown(finalText);
            } else {
                contentDiv.textContent = finalText;
            }
        }
        if (!entry.isSelf && entry.sender === 'assistant' && entry.msgId) {
            Mana.chat.addFeedbackButtons(entry.container, entry.msgId);
        }
    },

    addFeedbackButtons: function (container, msgId) {
        if (container.querySelector('.feedback-buttons')) return;
        const wrapper = document.createElement('div');
        wrapper.className = 'feedback-buttons';
        const likeBtn = document.createElement('button');
        likeBtn.className = 'fb-btn like'; likeBtn.innerHTML = '<i class="fas fa-thumbs-up"></i>';
        const dislikeBtn = document.createElement('button');
        dislikeBtn.className = 'fb-btn dislike'; dislikeBtn.innerHTML = '<i class="fas fa-thumbs-down"></i>';
        wrapper.append(likeBtn, dislikeBtn);
        container.appendChild(wrapper);
        let rated = false;
        const rate = async (rating) => {
            if (rated) return;
            rated = true; likeBtn.disabled = true; dislikeBtn.disabled = true;
            try {
                await Mana.apiFetch('/chat/feedback', {
                    method: 'POST',
                    body: JSON.stringify({ thread_id: Mana.chat.currentThreadId, message_id: msgId, rating, comment: null }),
                });
                (rating === 1 ? likeBtn : dislikeBtn).classList.add('active');
                Mana.showToast('نظر شما ثبت شد!', 'success');
            } catch (err) {
                rated = false; likeBtn.disabled = false; dislikeBtn.disabled = false;
                Mana.showToast('خطا در ثبت نظر: ' + err.message, 'error');
            }
        };
        likeBtn.addEventListener('click', () => rate(1));
        dislikeBtn.addEventListener('click', () => rate(-1));
    },

    removeThinkingIndicator: function () {
        if (Mana.chat.currentThinkingIndicator && Mana.chat.currentThinkingIndicator.parentNode) {
            Mana.chat.currentThinkingIndicator.remove();
            Mana.chat.currentThinkingIndicator = null;
        }
    },

    showThinkingIndicator: function () {
        Mana.chat.removeThinkingIndicator();
        const div = document.createElement('div');
        div.className = 'thinking-indicator';
        div.innerHTML = `
            <span>دستیار در حال فکر کردن</span>
            <div class="thinking-dots">
                <span></span><span></span><span></span>
            </div>`;
        Mana.$('#chatMessages').appendChild(div);
        Mana.$('#chatMessages').scrollTop = Mana.$('#chatMessages').scrollHeight;
        Mana.chat.currentThinkingIndicator = div;
    }
};