document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const currentPathSpan = document.getElementById('current-path');
    const openFolderBtn = document.getElementById('open-folder-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const modelSelector = document.getElementById('model-selector');
    const mobileModelSelector = document.getElementById('mobile-model-selector');
    const aboutBtn = document.getElementById('about-btn');
    const aboutModal = document.getElementById('about-modal');
    const closeAbout = document.getElementById('close-about');

    async function refreshFiles() {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            if (data.work_dir) {
                currentPathSpan.textContent = data.work_dir;
            }
        } catch (error) {
            console.error('Error fetching files:', error);
        }
    }

    refreshFiles(); // Initial load

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = userInput.value.trim();
        if (!prompt) return;

        // Add user message to UI
        addMessage(prompt, 'user');
        userInput.value = '';

        // Typing indicator
        const typingId = addMessage('Thinking...', 'ai', true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, history: [] })
            });

            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();

            if (data.error) {
                addMessage(`Error: ${data.error}`, 'ai');
            } else {
                addMessage(data.response, 'ai');
                // Removed refreshFiles() from here as the explorer is gone
            }
        } catch (error) {
            console.error('Fetch error:', error);
            document.getElementById(typingId).remove();
            addMessage('Error communicating with the server.', 'ai');
        }
    });

    // API Key Setup logic
    const setupModal = document.getElementById('setup-modal');
    const saveKeyBtn = document.getElementById('save-key-btn');
    const apiKeyInput = document.getElementById('api-key-input');

    if (saveKeyBtn) {
        saveKeyBtn.addEventListener('click', async () => {
            const key = apiKeyInput.value.trim();
            if (!key) return;

            saveKeyBtn.textContent = 'Saving...';
            saveKeyBtn.disabled = true;

            try {
                const response = await fetch('/api/setup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: key })
                });

                const data = await response.json();
                if (data.status === 'success') {
                    setupModal.style.display = 'none';
                    addMessage('API Key configured! You can now start using Kun Code.', 'ai');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Connection error. Check backend.');
            } finally {
                saveKeyBtn.textContent = 'Save and Start';
                saveKeyBtn.disabled = false;
            }
        });
    }

    if (openFolderBtn) {
        openFolderBtn.addEventListener('click', async () => {
            const newPath = prompt('Enter the absolute path of the folder you want to open:');
            if (!newPath) return;

            try {
                const response = await fetch('/api/workspace', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: newPath })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    refreshFiles();
                    addMessage(`Switched workspace to: ${data.work_dir}`, 'ai');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Connection error.');
            }
        });
    }

    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            chatHistory.innerHTML = `
                <div class="message ai-message">
                    Hello! I am <strong>Kun Code</strong>. New session started. How can I help you?
                </div>
            `;
            addMessage('Chat history cleared.', 'ai');
        });
    }

    if (modelSelector) {
        modelSelector.addEventListener('change', async () => {
            const selectedModel = modelSelector.value;
            try {
                const response = await fetch('/api/model', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: selectedModel })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    addMessage(`Switched to model: **${selectedModel}**`, 'ai');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Connection error.');
            }
        });
    }

    if (mobileModelSelector) {
        mobileModelSelector.addEventListener('change', async () => {
            const selectedModel = mobileModelSelector.value;
            try {
                const response = await fetch('/api/model', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: selectedModel })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    addMessage(`Switched to model: **${selectedModel}**`, 'ai');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Connection error.');
            }
        });
    }

    if (aboutBtn) {
        aboutBtn.addEventListener('click', () => {
            aboutModal.style.display = 'flex';
        });
    }

    if (closeAbout) {
        closeAbout.addEventListener('click', () => {
            aboutModal.style.display = 'none';
        });
    }

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target === aboutModal) aboutModal.style.display = 'none';
        if (e.target === setupModal) setupModal.style.display = 'none';
    });

    function addMessage(content, role, isTyping = false) {
        const messageDiv = document.createElement('div');
        const id = 'msg-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        messageDiv.id = id;
        messageDiv.classList.add('message');
        messageDiv.classList.add(role === 'user' ? 'user-message' : 'ai-message');
        
        // Handle basic markdown-ish formatting for AI responses
        if (role === 'ai') {
            messageDiv.innerHTML = formatContent(content);
        } else {
            messageDiv.textContent = content;
        }

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return id;
    }

    function formatContent(text) {
        // Very basic markdown formatting for the preview
        return text
            .replace(/\n/g, '<br>')
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }
});
